import sys
from configparser import ConfigParser
from libs.filefunctions import read_file_in_lines
from dbmanager import DBManager

def print_usage():
	print("Usage: python main.py arg")
	print("where arg can be one of the following:")
	print("   create_index: creates the index and the mappings")
	print("   add_project name: adds or updates a project given its github url")
	print("   add_projects file: adds or updates projects given a list of github urls (in a txt file)")
	print("   delete_project name: deletes a project given its github url")
	print("   delete_projects file: deletes projects given a list of github urls (in a txt file)")
	print("   delete_index: deletes the index and the mappings")

if __name__ == "__main__":
	conparser = ConfigParser()
	conparser.read("agora.properties")
	properties = conparser["AGORAProperties"]
	dbmanager = DBManager(properties)

	if (not sys.argv):
		print_usage()
	elif(sys.argv[1] == "create_index"):
		dbmanager.create_index()
	elif(sys.argv[1] == "add_project"):
		dbmanager.add_project(sys.argv[2])
	elif(sys.argv[1] == "add_projects"):
		dbmanager.add_projects(read_file_in_lines(sys.argv[2]))
	elif(sys.argv[1] == "delete_project"):
		dbmanager.delete_project(sys.argv[2])
	elif(sys.argv[1] == "delete_projects"):
		dbmanager.delete_projects(read_file_in_lines(sys.argv[2]))
	elif(sys.argv[1] == "delete_index"):
		dbmanager.delete_index()
	else:
		print_usage()
