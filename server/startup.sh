#!/bin/sh

echo "Running Startup.sh"
# NTP service start
chronyd -f /etc/chrony/chrony.conf

# Start mosquitto
mosquitto -c config/mosquitto.conf &

# pull configurations and store in redis
python3 code/cdc.py

# Start flask webserver
python3 code/fcc.py &

# Flower dead or alive
python3 code/fda.py

while true
do
    sleep 1
done

echo "Shutting down now...bye"