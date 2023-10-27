#!/bin/bash

# Update system's package list and upgrade
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages for pyenv, build dependencies, and unzip
sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git unzip

# Install pyenv
curl https://pyenv.run | bash

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"


# Configure the shell environment for pyenv
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.11.4 using pyenv and set it as the default version
pyenv install 3.11.4
pyenv global 3.11.4
pyenv local 3.11.4

python --version

#remove git
sudo apt-get remove --purge -y git

# Create the User and Group for the Application
sudo groupadd csye6225
sudo useradd -s /bin/false -g csye6225 -d /opt/csye6225 -m csye6225

# install postgresql client
sudo apt-get install -y postgresql-client-15

sudo unzip /tmp/webapp.zip -d /opt/webapp/
sudo mv /opt/webapp/users.csv /opt/users.csv
sudo mv /tmp/webapp/csye6225.service /etc/systemd/system/csye6225.service

ls -l /tmp/
ls -la /opt/

cd /opt/webapp/

# Install Python packages
pip3 install --upgrade pip
pip3 install -r /opt/webapp/requirements.txt

sudo systemctl enable csye6225
sudo systemctl start csye6225