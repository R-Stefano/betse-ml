#!/bin/bash
#sudo apt-get install git
#git clone https://R-Stefano:M4kemoney100%@github.com/R-Stefano/betse-ml.git
#cd betse-ml/
#chmod +x setup-cluster.sh
#sudo ./setup-cluster.sh

sudo apt update --yes --force-yes
sudo apt install python3 python3-dev python3-venv
sudo apt install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py

pip install pyyaml pandas betse google-cloud-storage

echo 'export PATH="~/.local/lib/python3.7/site-packages/:$PATH"' > ~/.bashrc

sudo reboot
