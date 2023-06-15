#!/bin/sh

echo "Running Startup.sh"

# NTP service start
chronyd -f /etc/chrony/chrony.conf

# Start mosquitto
mosquitto -c config/mosquitto.conf &

# Start flask webserver
python3 code/fcc.py &

while true
do
    sleep 1
done

echo "Shutting down now...bye"