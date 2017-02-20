import os
import sys
from libs.filefunctions import read_ascii_file
from libs.gitdownloader import GitDownloader
from libs.githubprojectdownloader import GithubProjectDownloader
from libs.javacompiler import JavaCompiler
from libs.elasticsearchclient import ElasticSearchClient

class DBManager:
	def __init__(self, properties):
		self.properties = properties
		self.sourcecodedir = properties["sourcecodedir"];
		self.gitdownloader = GitDownloader(properties["sourcecodedir"], properties["gitcommand"])
		self.gpdownloader = GithubProjectDownloader(properties["GitHubUsername"], properties["GitHubPassword"])
		self.javaparser = JavaCompiler(properties["ASTParserPath"])
		self.esclient = ElasticSearchClient(host = properties["host"], port = properties["port"], username = properties["AGORAUsername"], password = properties["AGORAPassword"], indexname = properties["indexname"])

	def create_index(self):
		self.esclient.create_index_and_mappings()

	def delete_index(self):
		self.esclient.delete_index_and_mappings()

	def create_backup(self):
		self.esclient.backup(self.properties["backupdir"])

	def delete_backup(self):
		self.esclient.create_index_and_mappings()

	def flush_index(self):
		self.esclient.flush()

	def get_enumerated_files_with_paths(self, project_path, sourcefiles):
		thedots = int(len(sourcefiles)/5), int(2 * len(sourcefiles)/5), int(3 * len(sourcefiles)/5), int(4 * len(sourcefiles)/5)
		for adot, afile in enumerate(sourcefiles):
			if adot in thedots: sys.stdout.write('.')
			yield (project_path + os.sep + os.sep.join(afile['path'].split(os.sep)), afile)
	
	def set_file_code_and_contents(self, file_path, afile, full_compiled_source = None):
		if afile['extension'] == 'java':
			if len(afile['name']) <= 125:
				if full_compiled_source and file_path in full_compiled_source:
					afile['code'] = full_compiled_source[file_path]
				else:
					afile['code'] = self.javaparser.parse_file(file_path)
				try:
					afile['content'] = read_ascii_file(file_path)
					afile['analyzedcontent'] = afile['content']
				except FileNotFoundError:
					afile['extension'] = 'ljava'
			else:
				afile['extension'] = 'ljava'
	
	def add_project(self, project_address):
		project_id = '/'.join(project_address.split('/')[-2:])
		sys.stdout.write('\nDownloading project info for project ' + project_id)
		project, sourcefiles = self.gpdownloader.download_project(project_address)
		sys.stdout.write('. Done!\n')
		project_path = self.sourcecodedir + os.sep + project['user'] + os.sep + project['name']
	
		self.gitdownloader.git_pull_or_clone(project_id, project['git_url'], project_path, project['default_branch'])
	
		if self.esclient.has_project(project_id):
			sys.stdout.write('Project already exists in database!\n')
			fileidsandshas = self.esclient.get_project_fileids_and_shas(project_id)
			sys.stdout.write('Updating database entries')
			for file_path, afile in self.get_enumerated_files_with_paths(project_path, sourcefiles):
				file_id = afile['fullpathname']
				if file_id in fileidsandshas:
					#File exists
					if not afile['sha'] == fileidsandshas[file_id]:
						self.esclient.update_file(afile)
					del fileidsandshas[file_id]
				else:
					#File does not exist
					self.set_file_code_and_contents(file_path, afile)
					self.esclient.create_file(afile)
			sys.stdout.write('.')
			#Delete remaining files
			for oldfileid in fileidsandshas:
				self.esclient.delete_file(oldfileid)
			sys.stdout.write(' Done!\n')
		else:
			sys.stdout.write('Adding project to database!\n')
			sys.stdout.write('Compiling project')
			full_compiled_source = self.javaparser.parse_project(project_path)
			sys.stdout.write('. Done!\n')
			self.esclient.create_project(project)
			sys.stdout.write('Creating database entries')
			for file_path, afile in self.get_enumerated_files_with_paths(project_path, sourcefiles):
				self.set_file_code_and_contents(file_path, afile, full_compiled_source)
				self.esclient.create_file(afile)
			sys.stdout.write(' Done!\n')
	
	def delete_project(self, project_address):
		project_id = '/'.join(project_address.split('/')[-2:])
		if self.esclient.has_project(project_id):
			self.esclient.delete_project()
	
	def add_projects(self, project_addresses):
		for project_address in project_addresses:
			self.add_project(project_address)
	
	def delete_projects(self, project_addresses):
		for project_address in project_addresses:
			self.delete_project(project_address, self.esclient)
