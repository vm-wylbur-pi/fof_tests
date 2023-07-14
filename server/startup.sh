#!/bin/sh

echo "Running Startup.sh"

# NTP service start
chronyd -f /etc/chrony/chrony.conf

# Start mosquitto
mosquitto -c config/mosquitto.conf &

# Start flask webserver
python3 code/fcc.py &

python3 gsa/main.py &

# Set up a retained MQTT message containing the flower control reference time.
# This will be read by each flower when it boots.
# See time_sync.h in the flower firmware source code for details.
sleep 5  # Need to give mosquitto enough time to finish starting up.
echo "Publishing flower event reference time."
EVT_REFERENCE_TIME=$(date +%s)
mosquitto_pub \
  --id time_reference_from_docker_startup \
  --topic flower-control/all/time/setEventReference \
  --message ${EVT_REFERENCE_TIME} \
  --retain

while true
do
    sleep 1
done

echo "Shutting down now...bye"