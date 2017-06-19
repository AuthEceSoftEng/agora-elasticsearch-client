import os
import sys
from elasticsearch.client import SnapshotClient
from libs.filefunctions import load_file_to_json
from elasticsearch.client.indices import IndicesClient
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError, TransportError

class SafeRequestsHttpConnection(RequestsHttpConnection):
	"""
	Overrides the default RequestsHttpConnection to allow throwing errors when the credentials
	are not correct.
	"""
	def perform_request(self, method, url, params = None, body = None, timeout = None, ignore = ()):
		"""
		Performs an HTTP request.
		
		:param method: the HTTP method of the request.
		:param url: the URL of the request.
		:param body: the body of the request.
		:param timeout: the maximum timeout of the request.
		:param ignore: contains the error codes that should be ignored.
		:returns: the response of the request or an error.
		"""
		try:
			return RequestsHttpConnection.perform_request(self, method, url, params = params, body = body, timeout = timeout, ignore = ())
		except TransportError as e:
			if e.status_code not in ignore:
				if e.status_code == 403 or e.status_code == 401:
					sys.stdout.write('Action \'%s\' on url \'%s\' is %s (%d) for these credentials!\n' % (method, url, e.error.split()[1].lower(), e.status_code))
					return e.status_code, None, None
				else:
					raise e
			else:
				return e.status_code, None, None

class ElasticSearchClient:
	"""
	Class used as a client to the Elasticsearch server.
	"""
	def __init__(self, host, port, username, password, indexname):
		"""
		Initializes this Elasticsearch Client.
		
		:param host: the HTTP address of the Elasticsearch server.
		:param port: the HTTP port of the Elasticsearch server.
		:param username: the username for connecting to the index.
		:param password: the password for connecting to the index.
		:param indexname: the name of the Elasticsearch index.
		"""
		self.indexname = indexname
		self.client = Elasticsearch(connection_class = SafeRequestsHttpConnection, host = host, port = int(port), http_auth = [username, password])
		self.snapshotclient = SnapshotClient(self.client)
		self.indicesclient = IndicesClient(self.client)

	def delete_index_and_mappings(self):
		"""
		Deletes the index and all its mappings.
		"""
		try:
			self.client.indices.delete(index = self.indexname)
		except NotFoundError:
			pass

	def create_index_and_mappings(self, update_mappings = False):
		"""
		Creates or updates the index and its mappings.
		
		:param update_mappings: boolean denoting whether the mappings should be created (False) or updated (True).
		"""
		if not self.client.indices.exists(self.indexname):
			self.client.indices.create(index = self.indexname, body = load_file_to_json("properties/indexsettings.json"))
		mappings = {}
		if self.indexname in self.client.indices.get_mapping(self.indexname):
			mappings = self.client.indices.get_mapping(self.indexname)[self.indexname]['mappings']
		if update_mappings:
			self.client.indices.close(self.indexname)
		if 'files' not in mappings or update_mappings:
			self.client.indices.put_mapping(index = self.indexname, doc_type = 'files',
				body = load_file_to_json("properties/filesproperties.json"))
		if 'projects' not in mappings or update_mappings:
			self.client.indices.put_mapping(index = self.indexname, doc_type = 'projects',
				body = load_file_to_json("properties/projectsproperties.json"))
		if update_mappings:
			self.client.indices.open(self.indexname)

	def has_project(self, project_id):
		"""
		Checks if the index contains a project.
		
		:param project_id: the id of the project to check if it is contained in the index.
		:returns: True if the index contains the project, or False otherwise.
		"""
		return self.client.exists(index = self.indexname, doc_type = 'projects', id = project_id)

	def has_file(self, file_id):
		"""
		Checks if the index contains a file.
		
		:param file_id: the id of the file to check if it is contained in the index.
		:returns: True if the index contains the file, or False otherwise.
		"""
		return self.client.exists(index = self.indexname, doc_type = 'files', id = file_id)

	def create_project(self, project):
		"""
		Creates a project in the index.
		
		:param project: the data of the project in JSON format.
		"""
		self.client.create(index = self.indexname, doc_type = 'projects', id = project['fullname'], body = project)

	def create_file(self, afile):
		"""
		Creates a file in the index.
		
		:param afile: the data of the file in JSON format.
		"""
		self.client.create(index = self.indexname, doc_type = 'files', id = afile['fullpathname'], parent = afile['project'], body = afile)

	def update_file(self, afile):
		"""
		Updates a file in the index.
		
		:param afile: the data of the file in JSON format.
		"""
		self.client.update(index = self.indexname, doc_type = 'files', id = afile['fullpathname'], parent = afile['project'], body = {'doc': afile})

	def delete_file(self, afile_id):
		"""
		Deletes a file from the index.
		
		:param afile_id: the id of the file to be deleted.
		"""
		self.client.delete(index = self.indexname, doc_type = 'files', id = afile_id, routing = '/'.join(afile_id.split('/')[0:2]))

	def delete_project(self, project_id):
		"""
		Deletes a project from the index. Note that this function also deletes all the files of the project.
		
		:param project_id: the id of the project to be deleted.
		"""
		self.client.delete_by_query(index = self.indexname, doc_type = 'files', body = {"query": { "bool": { "must": { "match_all": {} }, "filter": { "term": { "_routing": project_id } } } } })
		self.client.delete(index = self.indexname, doc_type = 'projects', id = project_id)

	def get_project_fileids_and_shas(self, project_id):
		"""
		Returns all the files and their corresponding shas for a project.
		
		:param project_id: the id of the project of which the files and the shas are returned.
		:returns: a dict containing the files of the project as keys and their shas as values.
		"""
		sourcefiles = self.client.search(index = self.indexname, doc_type = 'files',
			body = {"query": { "term" : { "_routing": project_id } } }, routing = project_id, size = 100000000)['hits']['hits']  # Limitation! Each project must have no more than 100000000 files
		fileidsandshas = {}
		for afile in sourcefiles:
			fileidsandshas[afile['_id']] = afile['_source']['sha']
		return fileidsandshas

	def execute_query(self, query, doc_type = 'files'):
		"""
		Executes a query on the index.
		
		:param query: the body of the query.
		:param doc_type: the document type to which the query is executed, either 'projects' or 'files'.
		:returns: the response of the query.
		"""
		return self.client.search(index = self.indexname, doc_type = doc_type, body = query)

	def test_analyzer(self, analyzer, text):
		"""
		Tests an analyzer of the index.
		
		:param analyzer: the analyzer to be tested.
		:param text: the text to be analyzed as a test.
		:returns: the analyzed text.
		"""
		result = self.indicesclient.analyze(index = self.indexname, analyzer = analyzer, body = text)
		return [r['token'] for r in result['tokens']]

	def backup(self, backupdir):
		"""
		Backups the index.
		
		:param backupdir: the directory used to backup the index.
		"""
		repositoryname = os.path.basename("backup" + self.indexname)
		try:
			self.snapshotclient.get_repository(repository = repositoryname)
		except:
			self.snapshotclient.create_repository(repository = repositoryname, body = {"type": "fs", "settings": {"location": backupdir + os.sep + self.indexname}})
		try:
			self.snapshotclient.get(repository = repositoryname, snapshot = self.indexname + "snapshot")
		except:
			self.snapshotclient.create(repository = repositoryname, snapshot = self.indexname + "snapshot", body = {"indices": self.indexname}, wait_for_completion = True)

	def delete_backup(self):
		"""
		Removes any backups of the index. If there are no backups, this function does nothing.
		"""
		repositoryname = os.path.basename("backup" + self.indexname)
		try:
			self.snapshotclient.delete(repository = repositoryname, snapshot = self.indexname + "snapshot")
		except:
			pass

	def restore_backup(self):
		"""
		Restores a backup of the index.
		"""
		repositoryname = os.path.basename("backup" + self.indexname)
		if not self.client.indices.exists(self.indexname):
			self.client.indices.create(index = self.indexname, body = load_file_to_json("properties/indexsettings.json"))
		self.client.indices.close(self.indexname)
		self.snapshotclient.restore(repository = repositoryname, snapshot = self.indexname + "snapshot", body = {"indices": self.indexname}, wait_for_completion = True)
		self.client.indices.open(self.indexname)

	def flush(self):
		"""
		Flushes the index.
		"""
		self.indicesclient.flush(index = self.indexname)
