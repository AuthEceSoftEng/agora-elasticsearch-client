import json
from libs.astparser import ASTParser

class JavaCompiler:
	"""
	Implements an API for a Java compiler.
	"""
	def __init__(self, parser_executable):
		"""
		Initializes this Java compiler.
		
		:param parser_executable: the path to the Java Compiler executable.
		"""
		self.ast_parser = ASTParser(parser_executable)

	def parse_project(self, project_folder):
		"""
		Parses all the files of a project and returns a unified AST.

		:param project_folder: the path of the project of which the files are parsed.
		:returns: an AST containing all the files of a project in JSON format.
		"""
		data = self.ast_parser.parse_folder(project_folder)
		data = data.replace('\\', '/')
		data = json.loads(data)
		for afilename in data.keys():
			data[afilename] = self.delete_nested_inner_classes(data[afilename])
		return data

	def parse_file(self, filepath):
		"""
		Parses a java file and returns its AST.

		:param filepath: the filename of the java file to be parsed.
		:returns: a string containing the AST of the java file in JSON format.
		"""
		data = self.ast_parser.parse_file(filepath)
		data = json.loads(data)
		data = self.delete_nested_inner_classes(data)
		return data

	def delete_nested_inner_classes(self, data):
		"""
		Deletes the nested inner classes of an AST.

		:param data: the AST of which the nested inner classes are removed.
		:returns: the given AST with its nested inner classes removed.
		"""
		if 'class' in data:
			if 'innerclasses' in data['class']:
				for innerclass in data['class']['innerclasses']:
					if 'innerclasses' in innerclass:
						del innerclass['innerclasses']
		if 'otherclasses' in data:
			for otherclass in data['otherclasses']:
				if 'innerclasses' in otherclass:
					for innerclass in otherclass['innerclasses']:
						if 'innerclasses' in innerclass:
							del innerclass['innerclasses']
		return data
