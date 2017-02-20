import json
import base64

def load_file_to_json(filename):
	datalines = []
	with open(filename) as infile:
		for line in infile:
			comment = line.find('#')
			if comment >= 0:
				line = line[:comment]
			datalines.append(line)
	data = json.loads(''.join(datalines))
	def recurse(tdata):
		for element in tdata:
			if type(tdata[element]) is dict:
				recurse(tdata[element])
			elif type(tdata[element]) is str and tdata[element].startswith('__LOAD__'):
				nestedfilename = "properties/" + tdata[element][8:] + ".json"
				tdata[element] = json.loads(json.dumps(load_file_to_json(nestedfilename)))
	recurse(data)
	return data

def write_json_to_file(filename, data):
	with open(filename, 'w') as outfile:
		json.dump(data, fp = outfile, sort_keys = True, indent = 3, ensure_ascii = False)

def read_ascii_file(file_path):
	with open(file_path, errors='ignore') as infile:
		data = infile.read()
	data = data.encode('ascii', 'ignore')
	data = data.decode('ascii', 'ignore')
	return data

def read_file_in_lines(filename):
	lines = []
	with open(filename) as infile:
		for line in infile:
			if line and not line.startswith('#'):
				lines.append(line.strip())
	return lines

def write_lines_to_file(filename, lines):
	with open(filename, 'w') as outfile:
		outfile.write('\n'.join(lines))

def write_username_and_password_to_file(filename, username, password = None):
	if not password:
		username, password = username
	credentials = username + '===' + password
	credentials = credentials.encode()
	data = base64.b64encode(credentials)
	data = data.decode()
	with open(filename, 'w') as crer:
		crer.write(data)
