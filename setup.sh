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

# Add PostgreSQL repo and install PostgreSQL
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update && sudo apt-get install -y postgresql-15

# Ensure PostgreSQL service is started
sudo service postgresql start

# Configure PostgreSQL
sudo -u postgres psql -c "CREATE USER raj WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE csye6225_db OWNER raj;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE csye6225_db TO raj;"

sudo unzip /tmp/webapp.zip -d /opt/webapp/
ls -l /tmp/
ls -la /opt/

cd /opt/webapp/

# Install Python packages
pip install --upgrade pip
pip install -r /opt/webapp/requirements.txt


flask db upgrade
flask populate_db