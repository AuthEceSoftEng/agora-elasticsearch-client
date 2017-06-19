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

- Download and install elasticsearch (change USERNAME and USERGROUP to your own)
```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.0.tar.gz
tar -zxf elasticsearch-5.2.0.tar.gz
sudo chown -R USERNAME:USERGROUP elasticsearch-5.2.0/
```

- Git clone all repos into your home directory (or any other dir)
```
git clone https://github.com/AuthEceSoftEng/agora-elasticsearch-client.git
git clone https://github.com/AuthEceSoftEng/agora-ast-parser.git
git clone https://github.com/AuthEceSoftEng/agora-web-application.git
```

# Configurations
- Configure elasticsearch Step 1: set elasticsearch.yml configuration file
```
sudo cp agora-elasticsearch-client/configuration/elasticsearch.yml elasticsearch-5.2.0/config/elasticsearch.yml
```

- Configure elasticsearch Step 2: create scripts to start/stop the service
```
echo "./elasticsearch-5.2.0/bin/elasticsearch -d -p pid" > startElastic.sh
echo "kill `cat pid`" > stopElastic.sh
```

- Configure elasticsearch Step 3: add the command `su - USERNAME -c "/home/USERNAME/startElastic.sh"` in file `/etc/rc.local` (change USERNAME to your own)

- Configure apache Step 1: add `Listen 8080` in file `/etc/apache2/ports.conf`
- Configure apache Step 2: use provided agora.conf configuration file
```
sudo mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000.default.conf.bak
sudo cp agora-elasticsearch-client/configuration/agora.conf /etc/apache2/sites-enabled/agora.conf
```
- Configure apache Step 3: enable mods
```
sudo a2enmod proxy
sudo a2enmod proxy_http
```
- Configure apache Step 4: set a password for the admin account
```
sudo mkdir -p /usr/local/apache/passwd/
sudo cd /usr/local/apache/passwd/
sudo htpasswd passwords admin
```
- Configure apache Step 5: restart the service
```
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


