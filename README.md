AGORA Client
============
This is the repository of the AGORA Elasticsearch client. The dependencies
required for this python application website can be installed using pip, issuing
the command: <pre><code>pip install -r requirements.txt</code></pre>
To execute the script you must first set the options in file agora.properties.
The structure of the file is the following:
```
[AGORAProperties]

# ASTParser path
ASTParserPath = (path to agora-ast-parser.jar)

# Git system command
gitcommand = (path to git executable)

# GitHub credentials
GitHubUsername = (username of GitHub account)
GitHubPassword = (password of GitHub account)

# AGORA credentials
AGORAUsername = (username of AGORA admin account)
AGORAPassword = (password of AGORA admin account)

# Index options
indexname = agora
host = localhost
port = 9200
sourcecodedir = (location where the cloned code will be stored)
backupdir = (location where the backup of AGORA will be stored)
```

After setting the properties file, you can execute the script. The provided
functionalities are selected using command line arguments. The arguments must
be one of the following:
- create_index: creates the index and the mappings
- add_project name: adds or updates a project given its github url
- add_projects file: adds or updates projects given a list of github urls (in a txt file)
- flush_index: flushes the index
- delete_project name: deletes a project given its github url
- delete_projects file: deletes projects given a list of github urls (in a txt file)
- delete_index: deletes the index and the mappings

