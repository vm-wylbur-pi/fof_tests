from flask import Flask, send_from_directory, Response
import os

# frame viewer
import cv2

# config parsing
import json
import yaml
import redis

# state
import subprocess
import ntplib
from datetime import datetime

from preconfig import PreConfig

FCC_PATH = '/app/flower_control_center'

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory(FCC_PATH, 'index.html')

@app.route('/<path:path>')
def static_file(path):
    print(f"Client connected")  # prints the client's IP address
    return send_from_directory(FCC_PATH, path)

def generate_frames():
    video_file = "vids/perimeter-adult-track-show-and-tell-output.mp4"
    video = cv2.VideoCapture(video_file)
    while True:
        # Capture frame-by-frame
        ret, frame = video.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# testing video feed plugin, needs a page wrapped around it
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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

# Returns contents of the redis cache, read-only right now.
@app.route('/api/state/cache/<dtype>')
def status_cache(dtype):
    if dtype == 'deployment':
        return Response(rc.get('deployment'), content_type='application/json')
    elif dtype == 'inventory':
        return Response(rc.get('inventory'), content_type='application/json')
    elif dtype == 'flowers':
        lfids = rc.keys(config['redis']['liveflowers'] + '*')

        if not lfids:
            return Response({}, content_type='application/json')

        res = {}
        for lfid in lfids:
            flower = json.loads(rc.get(lfid).decode('utf-8'))
            fid = lfid.decode('utf-8').split(':',1)[1]
            res[fid] = flower
        return Response(json.dumps(res), content_type='application/json')

    elif dtype == 'flowers-dead':
        lfids = rc.keys(config['redis']['deadflowers'] + '*')

        if not lfids:
            return Response({}, content_type='application/json')

        res = {}
        for lfid in lfids:
            flower = json.loads(rc.get(lfid).decode('utf-8'))
            fid = lfid.decode('utf-8').split(':',1)[1]
            res[fid] = flower
        return Response(json.dumps(res), content_type='application/json')

    else:
        return Response("Unknown cache type")

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
    pc = PreConfig()

    global rc
    rc = pc.rc

    global config
    config = pc.config

    print("FCC Starting Up")
    app.run(host='0.0.0.0', port=8000, debug=True)
    print ("FCC Shutting down....which is weird.")