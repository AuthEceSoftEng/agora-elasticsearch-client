import json
from libs.astparser import ASTParser

class JavaCompiler:
	def __init__(self, parser_executable):
		self.ast_parser = ASTParser(parser_executable)

	def parse_project(self, project_folder):
		data = self.ast_parser.parse_folder(project_folder)
		data = json.loads(data)
		for afilename in data.keys():
			data[afilename] = self.delete_nested_inner_classes(data[afilename])
		return data

	def parse_file(self, filepath):
		data = self.ast_parser.parse_file(filepath)
		data = json.loads(data)
		data = self.delete_nested_inner_classes(data)
		return data

	def delete_nested_inner_classes(self, data):
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
