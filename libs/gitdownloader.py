import subprocess
import os
import sys

class GitDownloader():
	def __init__(self, sourcecodedir, gitcommand):
		self.sourcecodedir = sourcecodedir
		self.gitcommand = gitcommand

	def git_pull(self, repo_url, repo_path, repo_branch):
		subprocess.call([self.gitcommand, 'pull', 'origin', repo_branch], cwd = repo_path)

	def git_clone(self, repo_url, repo_path, repo_branch = None):
		subprocess.call([self.gitcommand, 'clone', repo_url, repo_path])

	def has_project(self, project_id):
		project_path = self.sourcecodedir + os.sep + os.sep.join(project_id.split('/'))
		return os.path.isdir(project_path)

	def git_pull_or_clone(self, project_id, repo_url, repo_path, repo_branch):
		if self.has_project(project_id):
			sys.stdout.write('Pulling project\n')
			self.git_pull(repo_url, repo_path, repo_branch)
		else:
			sys.stdout.write('Cloning project\n')
			self.git_clone(repo_url, repo_path, repo_branch)
		sys.stdout.write('.. Done!\n')
