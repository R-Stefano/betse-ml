FROM ubuntu

RUN apt-get update && apt-get install -y git
#download repo
RUN apt-get install git
RUN git clone https://R-Stefano:M4kemoney100%@github.com/R-Stefano/betse-ml.git

# Instal python & pip
RUN apt install python3 python3-dev python3-venv -y
RUN apt install wget -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

# Install libraries
RUN pip install pyyaml Pillow pandas google-cloud-storage scipy dill matplotlib ruamel_yaml

RUN echo 'export PATH="~/.local/lib/python3.7/site-packages/:$PATH"' > ~/.bashrc

WORKDIR betse-ml/
CMD python3 run.py generate
