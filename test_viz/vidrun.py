from collections import OrderedDict
import cv2
import numpy as np
import sys

from charset_normalizer import detect

# Step 0: Initialize variables
FOCUSVID = "perimeter walk first"
VIDPATH = "./vids/cuts/"

inputVideos = OrderedDict([
    ("perimeter walk first", {
        "boundingCorners": [[(24, 304), (101, 347)], [(591, 208), (643, 260)], [(1197, 248), (1239, 312)], [(566, 678), (614, 709)]],
        "notes": "need to cut the video before aria gets into the frame and blocks the point at the right.",
        "filename": "playa-perimeter-walk-f30.mp4",
        "vidLength": 30,
        "minPeople": 1,
        "maxPeople": 1,
    }),
    ("big test kids", {
        "boundingCorners": [[(545, 298), (606, 341)], [(1160, 342), (1211, 416)], [(0, 311), (63, 383)]],
        "notes": "lots of bouncing around that causes the point on the left to get confused with the splash damage from the light",
        "filename": "playa-big-test-kids-30s.mp4",
        "vidLength": 30,
        "minPeople": 2,
        "maxPeople": 3,
    }),
    ("big test adults", {
        "boundingCorners": [[(1, 1), (2, 2)], [(3, 3), (4, 4)], [(5, 5), (6, 6)]],
        "filename": "playa-big-test-adults-60s.mp4",
        "vidLength": 60,
        "minPeople": 2,
        "maxPeople": 4,
    }),
])

# Various Debugging functions
def printBBs(frame, boundingCorners):
    bcnt = 0
    for box in boundingCorners:
        # cv2.rectangle requires coordinates as integers
        pt1 = tuple(map(int, box[0]))
        pt2 = tuple(map(int, box[1]))

        # draw the rectangle on the frame
        # the arguments are the frame, the two points defining the rectangle,
        # the color (in BGR format), and the line thickness
        cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 2)
        cv2.putText(frame, 'box: '+ str(bcnt), (pt1[0], pt1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        bcnt+=1

    # Display the resulting frame with bounding boxes
    cv2.imshow('Frame with bounding boxes', frame)
    cv2.waitKey(0)  # waits until a key is pressed
    cv2.destroyAllWindows()  # destroy all the windows created by cv2.imshow


# Loops through the designated video and verifies that corner points are detected in each frame
#  this validates that there's **something** that comes up as a point in the center of each bounding box
def validateCornerPoints(cap, vidObj):
    fcnt = 1
    while True:
        # Read the next frame from the video
        ret, frame = cap.read()
        if not ret:
            break

        foundPoints = detectCornerPoints(frame, vidObj)

        for i in range(0,len(foundPoints)):
            if foundPoints[i] == (0,0):
                print("\nmissing box is " + str(i))
                print('frame count is ' + str(fcnt))
                printBBs(frame, vidObj['boundingCorners'])
        fcnt += 1




# Step 3: Detect Cornerpoints
def detectCornerPoints(frame, vidObj):
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Initialize foundPoints as an empty list
    foundPoints = []

    # Loop through the bounding boxes
    bcnt = 0
    for box in vidObj['boundingCorners']:
        # Crop the grayscale frame using the bounding box
        crop = grayFrame[box[0][1]:box[1][1], box[0][0]:box[1][0]]

        # Use minMaxLoc to find the brightest point in the cropped image
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(crop)

        # If the maximum value is above a certain threshold (e.g. 200),
        # consider it as a valid point and adjust the location based on the bounding box
        if max_val > 20:
            foundPoints.append((max_loc[0] + box[0][0], max_loc[1] + box[0][1]))
        else:
            foundPoints.append((0, 0))
            print("max threshold: " + str(max_val))
        bcnt += 1

    #debug - let's see where the points are
    #for point in foundPoints:
    #    if point != (0, 0):  # don't draw a circle for (0, 0)
    #        cv2.circle(frame, point, radius=10, color=(0, 255, 0), thickness=2)

    # Now display the image
    #cv2.imshow('Frame with Circles', frame)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    return foundPoints

def stabilizeFrame(frame, vidObj):
    pass


# Step 1:  Open the file
vidObj = inputVideos[FOCUSVID]
cap = cv2.VideoCapture(VIDPATH + vidObj['filename'])
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

#validateCornerPoints(cap, vidObj)

fcnt = 1
while True:
    # Read the next frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    foundPoints = detectCornerPoints(frame, vidObj)
    if('baseCorners' not in vidObj):
        vidObj['baseCorners'] = foundPoints

    sframe = stabilizeFrame(frame, vidObj)






sys.exit()
