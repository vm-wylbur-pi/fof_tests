# NOTE WHEN RUNNING STANDALONE:
# You must configure the container to run in --priviliged mode
# this is necessary so that the ntp server can bind to the low port 123

# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    mosquitto \
    mosquitto-clients \
    wget \
    redis-tools \
    gcc \
    python3-dev \
    chrony \
    ntpdate \
    procps \
    lsof \
    screen \
    iputils-ping

# install our ntp server config
COPY ./config/chrony.conf /etc/chrony/chrony.conf
# RUN update-rc.d chrony defaults
# RUN rm /tmp/chrony.pid

#COPY ./requirements.txt /app/requirements.txt
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#COPY ./startup.sh /app/startup.sh
RUN chmod +x startup.sh

# Snag the latest inventory from patrick's gdrive
RUN mkdir inventory
RUN wget -O 'inventory/flower-inventory.csv' "https://docs.google.com/spreadsheets/d/15RZktjWRHCY7ZPbcifEnkpLrTmIMa0Y6HAOzzlcpTQA/export?format=csv&gid=0"

# FCC web server port
#EXPOSE 8000
# Mosquitto broker port
#EXPOSE 1883 9001
# chrony / ntp port
#EXPOSE 123
#EXPOSE 123/udp

# Define environment variable
#ENV NAME World

# Run various server apps when the container launches
CMD ["sh", "./startup.sh"]