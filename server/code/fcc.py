from flask import Flask, send_from_directory, Response
import os

# frame viewer
import cv2

# config parsing
import json
import yaml
import redis

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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    global rc
    rc = redis.Redis(host='redis', port=6379)

    global config
    config = json.loads(rc.get('config'))
    app.run(host='0.0.0.0', port=8000, debug=True)