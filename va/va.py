# Viz system go!
import yaml
import cv2
import numpy as np
import math
import pprint

import norfair
from norfair import Detection, Paths, Tracker, Video

from tflitedetector import TFLiteDetector
from centroiddetector import CentroidDetector

import paho.mqtt.client as paho_mqtt
import datetime
import json

import time
import sys

pp = pprint.PrettyPrinter(indent=4)

# TODO: Read this from config
MQTT_BROKER_IP = "127.0.0.1"
MQTT_PEOPLE_TOPIC = 'people-locations/'

# open up the channel that we're reading from
CHANNEL = 'vids/adult-walk-truncated.mp4'
CALIBRATION = 'calibration_parameters.npz'
DEPLOYMENT_FILE = '../fake_field/playa_test_2.yaml'
MAX_FRAMES = 1000

# consume the first X of these and generate a median frame
MEDIAN_FRAMES = 25

# Corner Detection Params
CORNER_DEFLECTION = [20,35]  # max pixels x,y around the initial corner points to search for corners
CORNER_DRIFT = 20 # max distance between initial point and found point
CORNER_THRESHOLD = 100 # min threshold to convert to binary when detecting corner points

# Set video properties
WRITE_FILE = True
UNDISTORT = True

output_file = 'vids/output_video.avi'
if UNDISTORT:
    frame_width = 1172
    frame_height = 570
else:
    frame_width = 1920
    frame_height = 1080

fps = 30.0

# load calibration parameters from previous calibration test
data = np.load(CALIBRATION)
camera_matrix = data['camera_matrix']
distortion_coeffs = data['distortion_coeffs']

# import the deployment information
with open(DEPLOYMENT_FILE, 'r') as file:
    deployment = yaml.safe_load(file)


bg_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows=True, history=50)

#etector = CentroidDetector(bg_subtractor, frame_width, frame_height)
detector = TFLiteDetector(bg_subtractor, frame_width, frame_height)

#if WRITE_FILE:
#    video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'MJPG'), fps, (tracker.output_width, tracker.output_height))

# object that contains all the peeps as PID: Person Object
personTracker = {}

# shamelessly stolen from the gsa codebase
def SetupMQTTClient():
    # Required by paho, but unused
    def on_pre_connect(unused_arg1, unused_arg2):
        print("Running pre-connect")

    def on_connect(client, unused_userdata, unused_flags, result_code):
        result = "successfull." if result_code == 0 else "FAILED!"
        print(f'Connection to MQTT broker at {MQTT_BROKER_IP} {result}')
        # hashtag is the MQTT wildcard.
        # TODO:  implement vis system control messages.
        #print('Subscribing to viz control messages')
        #client.subscribe("game-control/#")

    def on_message(unused_client, unused_userdata, message):
        print(f"Received message, topic='{message.topic}', content='{message.payload}'")
        HandleMQTTMessage(message, gameState)

    def on_disconnect(unused_client, unused_userdata, result_code):
        if result_code != 0:
            print("Unexpected MQTT disconnection.")

    client = paho_mqtt.Client(client_id="va")
    client.on_pre_connect = on_pre_connect
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    # I'm not sure if this is helpful yet.
    # client.reconnect_delay_set(min_delay=1, max_delay=120)  # time unit is seconds
    client.connect(MQTT_BROKER_IP)

    # Caller is responsible for calling client.loop() to handle received messages
    return client

# removes the fish-eye effect from the camera using pre-defined calibration parameters
def undistort(frame):
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w,h), 1, (w,h))
    frame =  cv2.undistort(frame, camera_matrix, distortion_coeffs, None, newcameramtx)
    x, y, w, h = roi
    frame = frame[y:y+h, x:x+w]

    #cv2.imshow('Undistorted frame', frame)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return frame


# helper function used to initially identify the corner points in a frame
ref_points = []
drawing = False
def draw_corners():
    # Mouse callback function
    def mouse_callback(event, x, y, flags, param):
        global ref_points, drawing

        if event == cv2.EVENT_LBUTTONDOWN:
            ref_points.append((x, y))
            drawing = True

    # Open the video file
    cap = cv2.VideoCapture(CHANNEL)

    # Create a window and set the mouse callback
    cv2.namedWindow('Select Bounding Boxes')
    cv2.setMouseCallback('Select Bounding Boxes', mouse_callback)

    # Read the first frame
    ret, frame = cap.read()
    if UNDISTORT:
        frame = undistort(frame)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Loop until three bounding boxes are selected
    while len(ref_points) < 4:
        cv2.imshow('Select Bounding Boxes', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return ref_points

def detectCornerPoints(frame):
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Initialize foundPoints as an empty list
    foundPoints = []

    # Loop through the corner points
    bcnt = 0
    ccnt = 0
    for cpoint in deployment['field']['corners']:
        x = cpoint[0]
        y = cpoint[1]
        w = CORNER_DEFLECTION[0]
        h = CORNER_DEFLECTION[1]

        x_min = x - w // 2
        y_min = y - h // 2
        x_max = x + w // 2
        y_max = y + h // 2

        # print out the initial points and the search spaces.
        cv2.circle(frame, cpoint, radius=1, color=(0, 255, 0), thickness=-1)
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(frame, str(ccnt), (x, y - h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        crop = grayFrame[y_min:y_max, x_min:x_max]

        # TROUBLE:  the second variable below sets the lower threshold
        #  if you're having trouble with corner detection fiddle with this
        _, crop = cv2.threshold(crop, CORNER_THRESHOLD, 255, cv2.THRESH_BINARY)

        # works but periodically returns divide by zero on m00....for some reason...
        contours, _ = cv2.findContours(crop, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        multi_points = []
        for contour in contours:
            if cv2.contourArea(contour) < 5:
                continue
            #if len(contours) > 1:
            #    print(ccnt, ' - ' ,cv2.contourArea(contour))
            M = cv2.moments(contour)
            if M['m00'] < 1:
                cornerstats[ccnt]['contour fail'] += 1
                cx = x
                cy = y
            else:
                cx = x_min + int(M['m10'] / M['m00'])
                cy = y_min + int(M['m01'] / M['m00'])
            multi_points.append([cx,cy])

        # if there's no contours, revert to the original
        #  if more than one contour, take the one closest to the original
        #  TODO:  track the previous corner points and use those instead of the original
        newpoint = [x,y]
        if len(multi_points) == 0:
            cornerstats[ccnt]['no points'] += 1
            newpoint = [x,y]
        if len(multi_points) == 1:
            cornerstats[ccnt]['it worked'] += 1
            newpoint = multi_points[0]
        elif len(multi_points) > 1:
            cornerstats[ccnt]['multi-point'] += 1
            dset = []
            for point in multi_points:
                distance = math.sqrt((abs(x - cx))**2 + (abs(y - cy))**2)
                dset.append(distance)
            smallest = min(dset)
            index = dset.index(smallest)
            newpoint = multi_points[index]

        newdistance = math.sqrt((abs(x - newpoint[0]))**2 + (abs(y - newpoint[1]))**2)
        if newdistance > CORNER_DRIFT:
            cornerstats[ccnt]['corner drift'] += 1
            newpoint = [x,y]

        foundPoints.append(newpoint)
        bcnt += 1

        ccnt += 1
        if ccnt > 3:
            ccnt = 0


    #debug - let's see where the points are
    for point in foundPoints:
        if point != (0, 0):  # don't draw a circle for (0, 0)
            #cv2.circle(frame, point, radius=15, color=(0, 255, 0), thickness=2)
            cv2.circle(frame, point, radius=2, color=(0, 0, 255), thickness=-1)

    # Now display the image
    # cv2.imshow('Frame with Circles', frame)
    # cv2.waitKey(10)
    # cv2.destroyAllWindows()

    return foundPoints, frame

def getNorfairPayload(M,detections):
    print(detections.getActiveObjects)
    sys.exit()
    pass

def getPeoplePayload(M):
    plist = {}
    for pid in personTracker:
        ppos = personTracker[pid].getPos()
        pt = np.float32([[int(ppos[0]),int(ppos[1])]])
        pt_warp = cv2.perspectiveTransform(pt.reshape(-1,1,2),M)

        plist[pid] = {'x': int(pt_warp[0][0][0]), 'y': int(pt_warp[0][0][1])}

    #print(plist)
    return json.dumps({
        'timestamp': datetime.datetime.now().isoformat(),
        'people': plist
    })


# used when first getting corners for a sample video
#print(draw_corners())
#sys.exit()

cap = cv2.VideoCapture(CHANNEL)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))



cornerstats = {}
states = ['it worked', 'no points', 'contour fail', 'multi-point', 'corner drift']
for c in range(len(deployment['field']['corners'])):
    cornerstats[c] = {}
    for s in states:
        cornerstats[c][s] = 0

# median frame calculations
mframes = []
medianFrame = ''

# TODO:  load from deployment file
output_points = np.float32([[0,0],[0,3300], [3300,3300],[3300,0]])

mqtt_client = SetupMQTTClient()
mqtt_client.connect(MQTT_BROKER_IP)

# benchmark timing
start_time = time.time()

fcnt = 0
video_writer = None
# Loop through the video frames
while True:
    # Read a frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    fcnt+= 1

    if fcnt > MAX_FRAMES:
        break

    if not mqtt_client.is_connected():
        mqtt_client.reconnect()

    if UNDISTORT:
        frame = undistort(frame)

    hudframe = frame
    corner_points, hudframe = detectCornerPoints(frame)
    M = cv2.getPerspectiveTransform(np.float32(corner_points),output_points)

    if fcnt < MEDIAN_FRAMES:
        mframes.append(frame)
        continue

    if fcnt == MEDIAN_FRAMES:
        medianFrame = np.median(mframes, axis=0).astype(dtype=np.uint8)
        mframes = []

    (hudframe, detections) = detector.detect(frame, personTracker, hudframe, medianFrame)

    payload = getNorfairPayload(detections, M)


    if bool(personTracker):
        payload = getPeoplePayload(M)
        res = mqtt_client.publish(MQTT_PEOPLE_TOPIC, payload)
        mqtt_client.loop()

    if WRITE_FILE:
        if video_writer == None:
            hheight, hwidth, dims = hudframe.shape
            video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'MJPG'), fps, (hwidth, hheight))
        video_writer.write(hudframe)

    # stupid simple benchmark
    if fcnt % 100 == 0:
        elapsed_time = time.time() - start_time
        fps = fcnt / elapsed_time
        print(f"FPS: {fps:.2f}")


if WRITE_FILE:
    video_writer.release()

print("out of the loop")
mqtt_client.loop_stop()
cap.release()