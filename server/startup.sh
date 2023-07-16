#!/bin/sh

echo "Running Startup.sh"

# NTP service start
# docs: https://chrony.tuxfamily.org/doc/3.5/chronyd.html
#   -x  means that chrony won't try to change the system clock; it acts only as a server
#   -n  means don't detach from terminal. This lets us see any error messages.
# chronyd -x -n -f /etc/chrony/chrony.conf &
chronyd -x -n -f /etc/chrony/chrony.conf &

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