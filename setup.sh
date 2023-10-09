#!/bin/bash

# Ensure the script runs with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Run with root privileges."
  exit 1
fi

# Update system's package list
apt-get update

# Install required packages for pyenv, build dependencies, and unzip
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git unzip

# Install pyenv
curl https://pyenv.run | bash

# Configure the shell environment for pyenv
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.11.4 using pyenv and set it as the default version
pyenv install 3.11.4
pyenv global 3.11.4
pyenv local 3.11.4


# Add PostgreSQL repo and install PostgreSQL
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt-get update
apt-get install -y postgresql-15

# Configure PostgreSQL
sudo -u postgres psql -c "CREATE USER raj WITH PASSWORD 'raj_pass05';"
sudo -u postgres psql -c "CREATE DATABASE csye6225_db OWNER raj;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE csye6225_db TO raj;"

# Set up the webapp
#git clone https://github.com/RAJ-SUDHARSHAN/webapp.git
#cd webapp/

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Configure Flask
export FLASK_APP=app
export FLASK_DEBUG=True
export DATABASE_URL=postgresql://raj:raj_pass05@localhost:5432/csye6225_db
export CSV_PATH=/opt/users.csv

flask db init
flask db migrate -m "init"
flask db upgrade
flask populate_db
flask run --host=0.0.0.0

# Install and run ngrok
# wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
# unzip ngrok-stable-linux-amd64.zip
# ./ngrok http 5000

