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

LOG_DIR="/var/log/webapp"
sudo mkdir -p ${LOG_DIR}
sudo chown csye6225:csye6225 ${LOG_DIR}
sudo chmod 755 ${LOG_DIR}

# Install the CloudWatch Logs agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/debian/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Install the CloudWatch Logs agent
sudo bash -c 'cat <<EOF > /opt/cloudwatch-config.json
{
  "agent": {
    "metrics_collection_interval": 10,
    "logfile": "/var/logs/amazon-cloudwatch-agent.log"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/webapp/csye6225.log",
            "log_group_name": "csye6225",
            "log_stream_name": "webapp"
          }
        ]
      }
    },
    "log_stream_name": "cloudwatch_log_stream"
  },
  "metrics":{
    "metrics_collected":{
      "statsd":{
        "service_address":":8125",
        "metrics_collection_interval":15,
        "metrics_aggregation_interval":300
      }
    }
  }
}
EOF'

# Configure the CloudWatch Agent to fetch the configuration and start
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/cloudwatch-config.json \
    -s

# Enable the CloudWatch Agent to start on boot
sudo systemctl enable amazon-cloudwatch-agent

# Create the User and Group for the Application
sudo groupadd csye6225
sudo useradd -s /bin/false -g csye6225 -d /opt/csye6225 -m csye6225


sudo unzip /tmp/webapp.zip -d /opt/webapp/
sudo mv /opt/webapp/users.csv /opt/users.csv
sudo mv /tmp/csye6225.service /etc/systemd/system/csye6225.service


ls -l /tmp/
ls -la /opt/

cd /opt/webapp/

# Install Python packages
pip install --upgrade pip
pip install -r /opt/webapp/requirements.txt

sudo systemctl enable csye6225

