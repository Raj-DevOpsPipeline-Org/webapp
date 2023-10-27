#!/bin/bash

# Update system's package list and upgrade
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y build-essential libssl-dev zlib1g-dev wget \
libreadline-dev libsqlite3-dev curl libbz2-dev xz-utils tk-dev libffi-dev \
unzip python3.11 python3.11-venv python3-pip python-is-python3

# Check Python version
python --version

# Create the User and Group for the Application
sudo groupadd csye6225
sudo useradd -s /bin/false -g csye6225 -d /opt/csye6225 -m csye6225

# install postgresql client
sudo apt-get install -y postgresql-client-15

sudo unzip /tmp/webapp.zip -d /opt/webapp/
sudo mv /opt/webapp/users.csv /opt/users.csv

ls -l /tmp/
ls -la /opt/

cd /opt/webapp/

# Install Python packages
pip install --upgrade pip
pip install -r /opt/webapp/requirements.txt


flask db upgrade
flask populate_db