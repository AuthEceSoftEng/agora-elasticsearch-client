import json

def load_file_to_json(filename):
	"""
	Loads a file into a JSON object. Apart from loading the file into JSON, this function also removes
	any comments (denoted with #) and imports any other JSON objects (denoted with __LOAD__filename).
	
	:param filename: the filename of the file to be loaded.
	:returns: the JSON object that is contained in the file.
	"""
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
	"""
	Writes a JSON object to file.
	
	:param filename: the filename of the file to be written.
	:param data: the JSON data to be written to file.
	"""
	with open(filename, 'w') as outfile:
		json.dump(data, fp = outfile, sort_keys = True, indent = 3, ensure_ascii = False)

def read_ascii_file(file_path):
	"""
	Reads a file into a string while removing any non-ASCII characters.
	
	:param file_path: the path of the file to be read.
	:returns: the contents of the file as a string.
	"""
	with open(file_path, errors = 'ignore') as infile:
		data = infile.read()
	data = data.encode('ascii', 'ignore')
	data = data.decode('ascii', 'ignore')
	return data

def read_file_in_lines(filename):
	"""
	Reads a file into lines.
	
	:param filename: the filename of the file to be read.
	:returns: a list with the lines of the file.
	"""
	lines = []
	with open(filename) as infile:
		for line in infile:
			if line and not line.startswith('#'):
				lines.append(line.strip())
	return lines

def write_lines_to_file(filename, lines):
	"""
	Writes a list of strings (lines) into a file. The lines as joined using the newline character.
	
	:param filename: the filename of the file to be written.
	:param lines: the list of lines to be written to file.
	"""
	with open(filename, 'w') as outfile:
		outfile.write('\n'.join(lines))
