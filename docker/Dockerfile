ARG ubuntu_version=18.04
FROM ubuntu:${ubuntu_version}

# Needed to run add-apt-repository
RUN apt update

# Package install
RUN apt install libmysqlclient-dev thrift-compiler python2.7 python-pip python-setuptools -y

# Code copy
COPY . /usr/src/ara

# Pip install
# TODO(combacsa): specify necessary requirements here
RUN pip install -r /usr/src/ara/requirements.txt

# Initial configuration
WORKDIR /usr/src/ara
RUN echo '10000' > /tmp/tmp.txt
RUN echo '2' >> /tmp/tmp.txt
RUN echo 'n' >> /tmp/tmp.txt
RUN cat /tmp/tmp.txt | /usr/src/ara/bin/devel_setup_script.sh 

# Execute
EXPOSE 8080
CMD python bin/warara_server.py -p 8080
