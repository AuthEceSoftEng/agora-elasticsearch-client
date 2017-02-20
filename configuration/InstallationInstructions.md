Installation Instructions
=========================
This file provides installation instructions for AGORA.

# Prerequisites
- Install java and maven using the following commands (Oracle java is recommended):
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
sudo apt-get install maven
```

- Install python and pip using the following commands:
```
sudo apt-get install python3
sudo apt-get install python3-pip
```

- Install bower using the following commands:
```
sudo apt-get install nodejs
sudo apt-get install npm
sudo npm install bower -g
sudo ln -s /usr/bin/nodejs /usr/bin/node`
```

- Install apache web server
```
sudo apt-get install apache2
```

- Download and install elasticsearch
```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.0.deb
sudo dpkg -i elasticsearch-5.2.0.deb
sudo update-rc.d elasticsearch defaults
sudo service elasticsearch start
```

- Git clone all repos into your home directory (or any other dir)
```
git clone https://github.com/AuthEceSoftEng/agora-elasticsearch-client.git
git clone https://github.com/AuthEceSoftEng/agora-ast-parser.git
git clone https://github.com/AuthEceSoftEng/agora-web-application.git
```

# Configurations
- Configure elasticsearch (provided elasticsearch.yml configuration file)
```
sudo cp agora-elasticsearch-client/configuration/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
sudo service elasticsearch restart
```

- Configure apache (provided agora.conf configuration file - first add `Listen 8080` in file `/etc/apache2/ports.conf`)
```
sudo mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000.default.conf.bak
sudo cp agora-elasticsearch-client/configuration/agora.conf /etc/apache2/sites-enabled/agora.conf
sudo a2enmod proxy
sudo a2enmod proxy_http

sudo mkdir -p /usr/local/apache/passwd/
sudo cd /usr/local/apache/passwd/
sudo htpasswd passwords admin

sudo service apache2 restart
```

# Build and Install AGORA

- Build the agora-ast-parser
```
cd agora-ast-parser
mvn install
```

- Install all requirements of the agora-elasticsearch-client
```
cd ../agora-elasticsearch-client
pip3 install -r requirements.txt
```

- Create and populate the index
```
sudo python3 main.py create_index
sudo python3 main.py add_projects ./projectlists/moststars.txt
```

- Copy the contents of agora-web-application in apache web directory
```
sudo mv /var/www/html/index.html /var/www/
cd ../agora-web-application
sudo cp -r . /var/www/html/
```

- Install all requirements of the agora-web-application
```
cd /var/www/html/
sudo bower install --allow-root
```

- Go to the localhost in the browser to check the website


