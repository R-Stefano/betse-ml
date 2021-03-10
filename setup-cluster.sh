#!/bin/bash
#sudo apt-get install git
#git clone https://R-Stefano:M4kemoney100%@github.com/R-Stefano/betse-ml.git

sudo apt update
sudo apt install python3 python3-dev python3-venv
sudo apt install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py

cd betse-ml

pip install pyyaml pandas torch matplotlib betse


echo 'export PATH="~/.local/lib/python3.7/site-packages/:$PATH"' > ~/.bashrc
