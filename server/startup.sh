#!/bin/sh

# Start mosquitto
mosquitto -c config/mosquitto.conf &

# pull configurations and store in redis
python3 code/cdc.py

# Start flask webserver
python3 code/fcc.py

echo "Shutting down now"