import subprocess
import os
import sys

class GitDownloader():
	"""
	Class that implements a downloader using the git command.
	"""
	def __init__(self, sourcecodedir, gitcommand):
		"""
		Initializes this Git Downloader.
		
		:param sourcecodedir: the path to the directory where repos are cloned.
		:param gitcommand: the path to the git command of the system.
		"""
		self.sourcecodedir = sourcecodedir
		self.gitcommand = gitcommand

	def git_pull(self, repo_url, repo_path, repo_branch):
		"""
		Implements the git pull command.
		
		:param repo_url: the URL of the repository to be pulled.
		:param repo_path: the path of the repository in the file system.
		:param repo_branch: the branch to be pulled.
		"""
		subprocess.call([self.gitcommand, 'pull', 'origin', repo_branch], cwd = repo_path)

	def git_clone(self, repo_url, repo_path, repo_branch = None):
		"""
		Implements the git clone command.
		
		:param repo_url: the URL of the repository to be cloned.
		:param repo_path: the path of the file system to clone the repository.
		:param repo_branch: the branch to be cloned.
		"""
		subprocess.call([self.gitcommand, 'clone', repo_url, repo_path])

	def has_project(self, project_id):
		"""
		Checks if the file system contains a project.
		
		:param project_id: the id of the project to check if it exists in the file system.
		:returns: True if the file system contains the project, or False otherwise.
		"""
		project_path = self.sourcecodedir + os.sep + os.sep.join(project_id.split('/'))
		return os.path.isdir(project_path)

	def git_pull_or_clone(self, project_id, repo_url, repo_path, repo_branch):
		"""
		Clones a repository or pulls it if it already exists.
		
		:param project_id: the id of the project to check if it exists in the file system.
		:param repo_url: the URL of the repository to be cloned or pulled.
		:param repo_path: the path of the file system to clone or pull the repository.
		:param repo_branch: the branch to be cloned or pulled.
		"""
		if self.has_project(project_id):
			sys.stdout.write('Pulling project\n')
			self.git_pull(repo_url, repo_path, repo_branch)
		else:
			sys.stdout.write('Cloning project\n')
			self.git_clone(repo_url, repo_path, repo_branch)
		sys.stdout.write('.. Done!\n')
