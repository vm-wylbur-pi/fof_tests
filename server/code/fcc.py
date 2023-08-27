from flask import Flask, send_from_directory, Response
import os
import csv

# config parsing
import json
import yaml

# state
import subprocess
import ntplib
from datetime import datetime

FCC_PATH = '/app/flower_control_center'
DEPLOYMENT_PATH = '/app/fake_field/playa_deployment.yaml'
INVENTORY_PATH = '/app/config/inventory.csv'

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory(FCC_PATH, 'index.html')

# Serve the main FCC code out of its directory
@app.route('/<path:path>')
def static_file(path):
    print(f"Client connected")  # prints the client's IP address
    return send_from_directory(FCC_PATH, path)

# Executes Unit tests in the state.py and presents them in pretty format
@app.route('/api/state/test/<dtype>')
def status_report(dtype):
    status_result = subprocess.run(['python3', 'code/state.py'], capture_output=True, text=True)

    if dtype == 'text':
        return Response(status_result.stderr, content_type='text/plain')
    elif dtype == 'json':
        return Response(status_result.stdout, content_type='text/plain')
    else:
        return Response("Unknown data type, your options are json or text")

@app.route('/api/config/<dtype>')
def status_cache(dtype):
    if dtype == 'deployment':
        inventory_data = {}
        with open(INVENTORY_PATH, 'r') as file:
            csv_reader = csv.DictReader(file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Append the row to the data array
                inventory_data[row['mac']] = row

            # Load the YAML data
        with open(DEPLOYMENT_PATH, 'r') as file:
            deployment_data = yaml.safe_load(file)

        for fid in deployment_data['flowers']:
            print(fid)
            if fid in inventory_data:
                deployment_data['flowers'][fid].update(inventory_data[fid])

        return Response(json.dumps(deployment_data), content_type='application/json')
    elif dtype == 'inventory':
        data = {}
        with open(INVENTORY_PATH, 'r') as file:
            # Create a CSV reader
            csv_reader = csv.DictReader(file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Append the row to the data array
                data[row['FoF Mac']] = row

            return Response(json.dumps(data), content_type='application/json')
    elif dtype == 'flowers':
        return Response({}, content_type='application/json')
    else:
        return Response("Unknown config type")

@app.route('/api/state/time')
def time_check():
    try:
        # Create an NTP client instance and query the server
        client = ntplib.NTPClient()
        response = client.request('server')

        # Get the NTP server's response time
        ntp_time = datetime.fromtimestamp(response.tx_time)

        # Format the time string to a format easily parsed by JavaScript
        time_string = ntp_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return Response(time_string, content_type='text/plain')

    except Exception as e:
        return Response('Error:' + str(e), content_type='text/plain')

if __name__ == "__main__":
    print("FCC Starting Up")
    app.run(host='0.0.0.0', port=80, debug=True)
    print ("FCC Shutting down....which is weird.")