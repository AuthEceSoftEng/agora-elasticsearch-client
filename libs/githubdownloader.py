import sys
import json
import time
import datetime
import requests

class GithubDownloader:
	"""
	Class that implements a downloader for the GitHub API.
	"""
	def __init__(self, username, password, check = False):
		"""
		Initializes this GitHub API Downloader.
		
		:param username: the GitHub username.
		:param password: the GitHub password.
		:param check: boolean indicating whether the credentials should be checked (True) or not (False).
		"""
		self.remaining_requests = -1
		self.resettime = -1
		self.credentials = (username, password)
		if check and not self.check_credentials(self.credentials):
			sys.stdout.write("Wrong Credentials!\n")
			exit()

	def set_request_number(self, number, resettime, is_search = False):
		"""
		Sets the current number of requests in the GitHub API, both for simple and for search requests. If the number
		of remaining requests is less than 100 for API requests or less than 5 for search requests, then this function
		keeps waiting until the allowed number of requests is reset.
		
		:param number: the current number of requests to be set.
		:param resettime: the time until the next renewal of allowed requests.
		:param is_search: boolean indicating whether the last request was a search request (True) or not (False).
		"""
		self.remaining_requests = int(number)
		self.resettime = datetime.datetime.fromtimestamp(float(resettime)).strftime('%H:%M')
		if (is_search and self.remaining_requests < 5) or ((not is_search) and self.remaining_requests < 100):
			sys.stdout.write('\nOops! You have exceeded the requests limit!\nYou have to wait until ' + self.resettime + '..\n')
			waitsecs = int(resettime) - int(time.time())
			waitsecs += (20 if is_search else 60)
			while waitsecs > 0:
				time.sleep(1)
				sys.stdout.write('\rRemaining time: %d seconds' % waitsecs)
				waitsecs -= 1
			sys.stdout.write('\nDone!!')

	def check_credentials(self, credentials):
		"""
		Checks whether the credentials are correct.
		
		:param credentials: the GitHub credentials as a tuple (username, password).
		:returns: True if the credentials are correct, or False otherwise.
		"""
		try:
			r = requests.get("https://api.github.com/rate_limit", auth = credentials)
			if int(r.status_code) == 200:
				content = json.loads(r.text or r.content)
				self.set_request_number(content["resources"]["core"]["remaining"], content["resources"]["core"]["reset"])
				return True
			else:
				# self.set_request_number("-", "Not connected")
				return False
		except:
			# self.set_request_number("-", "Not connected")
			return False

	def download_request(self, address, parameters = None, headers = None):
		"""
		Implements a download request.
		
		:param address: the URL of the request.
		:param parameters: the parameters of the request.
		:param headers: the headers of the request.
		:returns: the response of the request.
		"""
		for _ in range(3):
			try:
				if parameters:
					parameters = '?' + '&'.join(parameters)
				else:
					parameters = ""
				if headers:
					headers = {headers.split(':')[0].strip() : headers.split(':')[1].strip()}
				else:
					headers = None
				r = requests.get(address + parameters, auth = self.credentials, headers = headers)
				self.set_request_number(r.headers['x-ratelimit-remaining'], r.headers['x-ratelimit-reset'], "api.github.com/search" in address)
				return r
			except TimeoutError:
				return None

	def download_object(self, address, parameters = None, headers = None):
		"""
		Downloads an object of the GitHub API.
		
		:param address: the URL of the GitHub request.
		:param parameters: the parameters of the GitHub request.
		:param headers: the headers of the GitHub request.
		:returns: the contents of the response of the request.
		"""
		r = self.download_request(address, parameters, headers)
		if r.ok:
			content = json.loads(r.text or r.content)
			if type(content) == dict and 'ETag' in r.headers:
				content['ETag'] = r.headers['ETag']
			return content  # if not isinstance(content, list) else content[0]

	def update_object(self, originalobject, address, parameters = None):
		"""
		Updates an object of the GitHub API if it has changed.
		
		:param originalobject: the original object containing an Etag indicating whether it has changed.
		:param address: the URL of the GitHub request.
		:param parameters: the parameters of the GitHub request.
		:returns: the contents of the response of the request or the original object if it has not changed.
		"""
		if 'ETag' in originalobject:
			headers = "If-None-Match: " + originalobject['ETag']
			r = self.download_request(address, parameters, headers)
			if int(r.status_code) == 200:
				newobject = json.loads(r.text or r.content)
				if type(newobject) == dict and 'ETag' in r.headers:
					newobject['ETag'] = r.headers['ETag']
				return newobject
			elif int(r.status_code) == 304:
				return originalobject
		else:
			newobject = self.download_object(address, parameters)
			for keyfield in newobject:
				originalobject[keyfield] = newobject[keyfield]
			return originalobject

	def download_paginated_object(self, address, parameters = None, headers = None):
		"""
		Downloads a paginated object of the GitHub API.
		
		:param address: the URL of the GitHub request.
		:param parameters: the parameters of the GitHub request.
		:param headers: the headers of the GitHub request.
		:returns: a generator containing all the pages of the response of the request.
		"""
		if parameters:
			parameters.append("per_page=100")
		else:
			parameters = ["per_page=100"]
			
		r = self.download_request(address, parameters, headers)
		if(r.ok):
			for obj in json.loads(r.text or r.content):
				yield obj
		while True:
			try:
				relnext, _ = map(lambda x: x.split(';')[0][1:-1], r.headers['Link'].split(', '))
			except (KeyError, ValueError):
				break
			r = self.download_request(relnext, parameters, headers)
			if(r.ok):
				for obj in json.loads(r.text or r.content):
					yield obj
