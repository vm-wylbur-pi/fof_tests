# NOTE WHEN RUNNING STANDALONE:
# You must configure the container to run in --priviliged mode
# this is necessary so that the ntp server can bind to the low port 123

# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
# ADD requirements.txt requirements.txt

# This additional configuration of apt-get is needed to avoid "Hash Sum mismatch" on Jeff's mackbook.
# From https://stackoverflow.com/questions/67732260/how-to-fix-hash-sum-mismatch-in-docker-on-mac
RUN echo "Acquire::http::Pipeline-Depth 0;" > /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::http::No-Cache true;"   >> /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::BrokenProxy    true;" >> /etc/apt/apt.conf.d/99custom

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    mosquitto \
    mosquitto-clients \
    wget \
    gcc \
    python3-dev \
    chrony \
    ntpdate \
    procps \
    lsof \
    screen \
    iputils-ping \
    build-essential \
    vim \
    g++

    # To be added back in once viz system is up.
    #   These are easier to add via apt than requirements.txt on the rpi
    #   since it doesn't require them to be compiled on the host
    # python3-numpy
    # python3-opencv

# install our ntp server config
COPY ./config/chrony.conf /etc/chrony/chrony.conf

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./startup.sh /app/startup.sh
RUN chmod +x startup.sh

# Snag the latest inventory from patrick's gdrive
RUN mkdir inventory
RUN wget -O 'inventory/flower-inventory.csv' "https://docs.google.com/spreadsheets/d/15RZktjWRHCY7ZPbcifEnkpLrTmIMa0Y6HAOzzlcpTQA/export?format=csv&gid=0"

# Run various server apps when the container launches
#  This is now handleded by docker-compose
# CMD ["sh", "./startup.sh"]