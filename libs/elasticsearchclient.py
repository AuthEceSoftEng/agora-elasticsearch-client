import os
import sys
from elasticsearch.client import SnapshotClient
from libs.filefunctions import load_file_to_json
from elasticsearch.client.indices import IndicesClient
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError, TransportError

class SafeRequestsHttpConnection(RequestsHttpConnection):
	def perform_request(self, method, url, params=None, body=None, timeout=None, ignore=()):
		try:
			return RequestsHttpConnection.perform_request(self, method, url, params=params, body=body, timeout=timeout, ignore=ignore)
		except TransportError as e:
			if e.status_code == 403 or e.status_code == 401:
				sys.stdout.write('Action \'%s\' on url \'%s\' is %s (%d) for these credentials!\n' %(method, url, e.error.split()[1].lower(), e.status_code))
				return e.status_code, None, None
			else:
				raise e

class ElasticSearchClient:
	def __init__(self, host, port, username, password, indexname):
		self.indexname = indexname
		self.client = Elasticsearch(connection_class=SafeRequestsHttpConnection, host=host, port=int(port), http_auth=[username, password])
		self.snapshotclient = SnapshotClient(self.client)
		self.indicesclient = IndicesClient(self.client)

	def delete_index_and_mappings(self):
		try:
			self.client.indices.delete(index = self.indexname)
		except NotFoundError:
			pass

	def create_index_and_mappings(self, update_mappings = False):
		if not self.client.indices.exists(self.indexname):
			self.client.indices.create(index=self.indexname, body=load_file_to_json("properties/indexsettings.json"))
		mappings = {}
		if self.indexname in self.client.indices.get_mapping(self.indexname):
			mappings = self.client.indices.get_mapping(self.indexname)[self.indexname]['mappings']
		if update_mappings:
			self.client.indices.close(self.indexname)
		if 'files' not in mappings or update_mappings:
			self.client.indices.put_mapping(index=self.indexname, doc_type='files',
				body=load_file_to_json("properties/filesproperties.json"))
		if 'projects' not in mappings or update_mappings:
			self.client.indices.put_mapping(index=self.indexname, doc_type='projects',
				body=load_file_to_json("properties/projectsproperties.json"))
		if update_mappings:
			self.client.indices.open(self.indexname)

	def has_project(self, project_id):
		return self.client.exists(index=self.indexname, doc_type='projects', id=project_id)

	def has_file(self, file_id):
		return self.client.exists(index=self.indexname, doc_type='files', id=file_id)

	def create_project(self, project):
		self.client.create(index=self.indexname, doc_type='projects', id=project['fullname'], body=project)

	def create_file(self, afile):
		self.client.create(index=self.indexname, doc_type='files', id=afile['fullpathname'], parent=afile['project'], body=afile)

	def update_file(self, afile):
		self.client.update(index=self.indexname, doc_type='files', id=afile['fullpathname'], parent=afile['project'], body={'doc': afile})

	def delete_file(self, afileid):
		self.client.delete(index=self.indexname, doc_type='files', id=afileid)

	def delete_project(self, project_id):
		self.client.delete(index=self.indexname, doc_type='projects', id=project_id)
		self.client.delete_by_query(index=self.indexname, doc_type='files', body={"query": { "filtered": { "query": { "match_all": {} }, "filter": { "term": { "_routing": project_id } } } } } )

	def get_project_fileids_and_shas(self, project_id):
		sourcefiles = self.client.search(index=self.indexname, doc_type='files', 
			body={"query": { "term" : { "_routing": project_id } } }, routing=project_id, size = 100000000)['hits']['hits'] #Limitation! Each project must have no more than 100000000 files
		fileidsandshas = {}
		for afile in sourcefiles:
			fileidsandshas[afile['_id']] = afile['_source']['sha']
		return fileidsandshas

	def execute_query(self, query, doc_type = 'files'):
		return self.client.search(index = self.indexname, doc_type = doc_type, body = query)

	def test_analyzer(self, analyzer, text):
		result = self.indicesclient.analyze(index = self.indexname, analyzer = analyzer, body = text)
		return [r['token'] for r in result['tokens']]

	def backup(self, backupdir):
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
		repositoryname = os.path.basename("backup" + self.indexname)
		try:
			self.snapshotclient.delete(repository = repositoryname, snapshot = self.indexname + "snapshot")
		except:
			pass

	def restore_backup(self):
		repositoryname = os.path.basename("backup" + self.indexname)
		if not self.client.indices.exists(self.indexname):
			self.client.indices.create(index=self.indexname, body=load_file_to_json("properties/indexsettings.json"))
		self.client.indices.close(self.indexname)
		self.snapshotclient.restore(repository = repositoryname, snapshot = self.indexname + "snapshot", body = {"indices": self.indexname}, wait_for_completion = True)
		self.client.indices.open(self.indexname)

	def flush(self):
		self.indicesclient.flush(index=self.indexname)
