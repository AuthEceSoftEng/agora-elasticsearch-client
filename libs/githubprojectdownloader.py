import os
import sys
import time
import requests
from libs.githubdownloader import GithubDownloader

class GithubProjectDownloader(GithubDownloader):
	"""
	Implements a project information downloader for GitHub.
	"""
	def download_most_important_repos(self, language, numrepos, sort = "stars", starting_from = 0, use_api = True):
		"""
		Retrieves a list with the most important repositories of GitHub.
		
		:param language: the language of the repositories to be retrieved.
		:param numrepos: the number of the repositories to be retrieved.
		:param sort: the type of repository information used to rank the repos, either "stars" or "forks".
		:param sort: the type of repository information used to rank the repos, either "stars" or "forks".
		:param starting_from: the number of repository to start from.
		:param use_api: boolean indicating whether to useg the GitHub API (True) or the GitHub page (False).
		:returns: a list of the most important repositories of GitHub.
		"""
		repourls = []
		if numrepos + starting_from > 300 or starting_from > 0:
			use_api = False
		if use_api:
			address = "https://api.github.com/search/repositories"
			pagenum = 1
			reponum = 1
			parameters = ["page=" + str(pagenum), "q=language:" + language, "sort=" + sort, "order=desc", "per_page=100"]
			currentpage = self.download_object(address, parameters)
			numrepos = min(300, min(currentpage['total_count'], numrepos))
			while reponum < numrepos:
				for repo in currentpage['items']:
					repourls.append(repo['url'])
					reponum += 1
				if reponum < numrepos:
					pagenum += 1
					parameters = ["page=" + str(pagenum), "q=language:" + language, "sort=" + sort, "order=desc", "per_page=100"]
					currentpage = self.download_object(address, parameters)
		else:
			starting_page = starting_from // 10
			ending_page = (numrepos + starting_from) // 10 + (1 if (numrepos + starting_from) % 10 > 0 else 0)
			bandanger = False
			sys.stdout.write("Donwloading from page %d to page %d\n" % (starting_page + 1, ending_page))
			for i in range(starting_page + 1, ending_page + 1):
				r = requests.get("https://github.com/search?l=" + language + "&p=" + str(i) + "&q=" + sort + "%3A%3E1&s=" + sort + "&type=Repositories")
				if r.status_code == 200:
					sys.stdout.write("Donwloading page %d\n" % i)
					rtext = r.text.split('\n')
					for linenumber, line in enumerate(rtext):
						if 'repolist-name' in line:
							repourls.append('https://api.github.com/repos' + rtext[linenumber + 1].split('\"')[1])
					time.sleep(180)
				else:
					time.sleep(600)
					if bandanger:
						break
					bandanger = True
		return repourls

	def download_project(self, project_address):
		"""
		Downloads GitHub information about a project.
		
		:param project_address: the project address for which information is downloaded.
		:returns: a JSON object containing the main information of the project and a list containing the filenames of its files.
		"""
		project = self.download_object(project_address)
		sys.stdout.write('.')
		if project['default_branch'] == 'master':
			sourcecode = self.download_object(project['trees_url'].split('{')[0] + '/master', ["recursive=1"])
		else:
			branch = self.download_object(project['url'] + '/branches/' + project['default_branch'], ["recursive=1"])
			sys.stdout.write('.')
			sourcecode = self.download_object(project['trees_url'].split('{')[0] + '/' + branch['commit']['sha'], ["recursive=1"])
		projectdoc = {}
		# projectdoc['_id'] = project['owner']['login'] + '/' + project['name']
		projectdoc['fullname'] = project['owner']['login'] + '/' + project['name']
		projectdoc['default_branch'] = project['default_branch']
		projectdoc['trees_url'] = project['trees_url']
		projectdoc['url'] = project['url']
		projectdoc['user'] = project['owner']['login']
		projectdoc['name'] = project['name']
		projectdoc['git_url'] = project['git_url']
		sourcedocs = []
		for afile in sourcecode['tree']:
			newfile = {}
			# newfile['_id'] = project['_id'] + '/' + afile['path']
			newfile['fullpathname'] = projectdoc['fullname'] + '/' + afile['path']
			newfile['project'] = projectdoc['fullname']
			newfile['mode'] = afile['mode']
			newfile['path'] = afile['path']
			newfile['name'] = os.path.basename(afile['path'])
			newfile['sha'] = afile['sha']
			newfile['type'] = afile['type']
			newfile['extension'] = '' if len(afile['path'].split('.')) <= 1 else afile['path'].split('.')[-1]
			newfile['url'] = afile['url'] if 'url' in afile else ''
			sourcedocs.append(newfile)
		return projectdoc, sourcedocs
