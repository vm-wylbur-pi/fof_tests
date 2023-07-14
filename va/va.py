# Viz system go!
import yaml
import cv2
import numpy as np
import math
import pprint

from tflitetracker import TFLiteTracker

# open up the channel that we're reading from
CHANNEL = '../../../vids/ptest2/permieter-run.mp4'
#CHANNEL = '../../../../vids/ptest2/lots-adults-four-lights.mp4'
CALIBRATION = 'calibration_parameters.npz'
DEPLOYMENT_FILE = '../fake_field/playa_test_2.yaml'
MAX_FRAMES = 165

# max pixels x,y around the initial corner points to search for corners
CORNER_DEFLECTION = [20,35]

# max distance between initial point and found point
CORNER_DRIFT = 20

# min threshold to convert to binary when detecting corner points
CORNER_THRESHOLD = 100

# Set video properties
WRITE_FILE = True
output_file = '/Users/george/Desktop/output_video.avi'
frame_width = 1920
frame_height = 1080
fps = 30.0
if WRITE_FILE:
    video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'MJPG'), fps, (frame_width, frame_height))

pp = pprint.PrettyPrinter(indent=4)

# load calibration prameters from previous calibration test
data = np.load(CALIBRATION)
camera_matrix = data['camera_matrix']
distortion_coeffs = data['distortion_coeffs']

# import the deployment information
with open(DEPLOYMENT_FILE, 'r') as file:
    deployment = yaml.safe_load(file)

bg_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows=True, history=200)


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



# helper function used to identify the corner points
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
            multi_points.append((cx,cy))

        # if there's no contours, revert to the original
        #  if more than one contour, take the one closest to the original
        newpoint = (x,y)
        if len(multi_points) == 0:
            cornerstats[ccnt]['no points'] += 1
            newpoint = (x,y)
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
            newpoint = (x,y)

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


cap = cv2.VideoCapture(CHANNEL)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

cornerstats = {}
states = ['it worked', 'no points', 'contour fail', 'multi-point', 'corner drift']
for c in range(len(deployment['field']['corners'])):
    cornerstats[c] = {}
    for s in states:
        cornerstats[c][s] = 0

fcnt = 0
tracker = TFLiteTracker(bg_subtractor, frame_width, frame_height)
personTracker = {}

# Loop through the video frames
while True:
    # Read a frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    fcnt += 1
    if fcnt > MAX_FRAMES:
        break

    # ignoring undistortion atm because it crops the cornerpoints from the image...
    # frame = undistort(frame)

    corner_points, hudframe = detectCornerPoints(frame)

    hudframe = tracker.track(frame, personTracker, hudframe)

    if WRITE_FILE:
        video_writer.write(hudframe)

cap.release()
if WRITE_FILE:
    video_writer.release()

#print("Frames : ",fcnt)
#pp.pprint(cornerstats)
# draw corners

# detect the center points of the deployment



#