import os
import base64
import subprocess
from subprocess import STDOUT, PIPE

class _ASTParser(object):
	"""
	Inner python binding to the ASTParser library. It works by executing the jar file as a subprocess
	and opening pipes to the standard input and standard output so that messages can be sent and received.
	Instead of using this class, it is highly recommended to use the abstracted ASTParser class.
	"""
	def __init__(self, path_to_ASTParser_jar):
		"""
		Initializes this inner parser.
		
		:param path_to_ASTParser_jar: the path to the ASTParser jar.
		"""
		self.cmd = ['java', '-cp', path_to_ASTParser_jar, 'astparser.PythonBinder']
		self.proc = subprocess.Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		self.nummessages = 0
		line = self.send_message("START_OF_TRANSMISSION")
		if line != "START_OF_TRANSMISSION":
			print("Error in Java compiler!!")
			exit()

	def close_parser(self):
		"""
		Closes the parser.
		"""
		return self.send_message("END_OF_TRANSMISSION") == "END_OF_TRANSMISSION"

	def restart_parser(self, force=False):
		"""
		Restarts the parser.
		"""
		if force or self.send_message("END_OF_TRANSMISSION") == "END_OF_TRANSMISSION":
			self.proc = subprocess.Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
			self.nummessages = 0
		else:
			print("Error in Java compiler!!")
			exit()

	def get_ast(self, code_entity, code_entity_properties):
		"""
		Returns the AST of a code_entity.
		
		:param code_entity: the path or the contents of the code entity.
		:param code_entity_properties: the properties of the code entity including its type and expected representation.
		"""
		self.nummessages += 1
		if self.nummessages == 10000:
			self.restart_parser()
		return self.send_message(code_entity_properties + code_entity)

	def send_message(self, message):
		"""
		Sends a new message to the ASTParser jar.
		
		:param message: the message to be sent.
		"""
		decodedbytes = message.encode(encoding='ascii')
		b64encodedbytes = base64.b64encode(decodedbytes)
		self.proc.stdin.write(b64encodedbytes + b"\r\n")
		self.proc.stdin.flush()
		line = self.proc.stdout.readline()
		try:
			b64decodedbytes = base64.b64decode(line)
			decodedline = b64decodedbytes.decode()
		except:
			self.restart_parser(True)
			decodedline = ""
		return decodedline

class ASTParser(_ASTParser):
	"""
	Class used as a python binding to the ASTParser library. It contains functions for parsing java code to AST.
	"""
	def __init__(self, path_to_ASTParser_jar):
		"""
		Initializes this AST Parser.
		
		:param path_to_ASTParser_jar: the path to the ASTParser jar
		"""
		super(ASTParser, self).__init__(path_to_ASTParser_jar)

	def parse_string(self, file_contents):
		"""
		Parses the contents of a java file and returns its AST.

		:param file_contents:  the contents of a java file, given as a string.
		:returns: a string containing the AST of the java file in JSON format.
		"""
		return super(ASTParser, self).get_ast(file_contents, "PARSE_STRING_-_")

	def parse_file(self, filename):
		"""
		Parses a java file and returns its AST.

		:param filename: the filename of the java file to be parsed.
		:returns: a string containing the AST of the java file in JSON format.
		"""
		filename = os.path.abspath(filename)
		return super(ASTParser, self).get_ast(filename, "PARSE_FILE_-_")

	def parse_folder(self, folder_name):
		"""
		Parses all the files of a folder and returns a unified AST.

		:param folder_name: the path of the folder of which the files are parsed.
		:returns: an AST containing all the files of a folder in JSON format.
		"""
		folder_name = os.path.abspath(folder_name)
		return super(ASTParser, self).get_ast(folder_name, "PARSE_FOLDER_-_")

	def close(self):
		"""
		Closes the AST parser. Note that this function must be called after using the class.
		Otherwise, this may result to a memory leak.
		"""
		super(ASTParser, self).close_parser()
