import sys
import json
import time
import datetime
import requests

class GithubDownloader:
    def __init__(self, username, password, check = False):
        self.remaining_requests = -1
        self.resettime = -1
        self.credentials = (username, password)
        if check and not self.check_credentials():
            sys.stdout.write("Wrong Credentials!\n")
            exit()

    def set_request_number(self, number, resettime, is_search = False):
        self.remaining_requests = int(number)
        self.resettime = datetime.datetime.fromtimestamp(float(resettime)).strftime('%H:%M')
        if (is_search and self.remaining_requests < 5) or ((not is_search) and self.remaining_requests < 100):
            sys.stdout.write('\nOops! You have exceeded the requests limit!\nYou have to wait until ' + self.resettime + '..\n')
            waitsecs = int(resettime) - int(time.time())
            waitsecs += (20 if is_search else 60)
            while waitsecs > 0:
                time.sleep(1)
                sys.stdout.write('\rRemaining time: %d seconds' %waitsecs)
                waitsecs -= 1
            sys.stdout.write('\nDone!!')

    def set_credentials(self, username, password):
        self.credentials = (username, password)

    def check_credentials(self):
        try:
            r = requests.get("https://api.github.com/rate_limit", auth = self.credentials)
            if int(r.status_code) == 200:
                content = json.loads(r.text or r.content)
                self.set_request_number(content["resources"]["core"]["remaining"], content["resources"]["core"]["reset"])
                return True
            else:
                #self.set_request_number("-", "Not connected")
                return False
        except:
            #self.set_request_number("-", "Not connected")
            return False

    def download_request(self, address, parameters = None, headers = None):
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
        r = self.download_request(address, parameters, headers)
        if r.ok:
            content = json.loads(r.text or r.content)
            if type(content) == dict and 'ETag' in r.headers:
                content['ETag'] = r.headers['ETag']
            return content# if not isinstance(content, list) else content[0]

    def update_object(self, originalobject, address, parameters = None):
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
