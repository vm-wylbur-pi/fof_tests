from collections import OrderedDict
import cv2
import numpy as np
import sys
from person import Person

from charset_normalizer import detect

# Step 0: Initialize variables
FOCUSVID = "perimeter walk 30"
VIDPATH = "./vids/cuts/"
OUTVID = None

inputVideos = OrderedDict([
    ("perimeter short", {
        "boundingCorners": [[(24, 304), (101, 347)], [(591, 208), (643, 260)], [(1197, 248), (1239, 312)], [(566, 678), (614, 709)]],
        "filename": "playa-perimeter-short.mp4"
    }),
    ("perimeter walk 30", {
        "boundingCorners": [[(24, 304), (101, 347)], [(591, 208), (643, 260)], [(1197, 248), (1239, 312)], [(566, 678), (614, 709)]],
        "notes": "need to cut the video before aria gets into the frame and blocks the point at the right.",
        "filename": "playa-perimeter-walk-f30.mp4",
    }),
    ("big test kids", {
        "boundingCorners": [[(545, 298), (606, 341)], [(1160, 342), (1211, 416)], [(0, 311), (63, 383)]],
        "notes": "lots of bouncing around that causes the point on the left to get confused with the splash damage from the light",
        "filename": "playa-big-test-kids-30s.mp4",
    }),
    ("big test adults", {
        "boundingCorners": [[(1, 1), (2, 2)], [(3, 3), (4, 4)], [(5, 5), (6, 6)]],
        "filename": "playa-big-test-adults-60s.mp4",
    }),
    ("crazy walk four", {
        "filename": "playa-crazy-walk-10s-four.mp4",
        "boundingCorners": [[(1, 1), (2, 2)], [(3, 3), (4, 4)], [(5, 5), (6, 6)]],
    }),
    ("final crazy", {
        "filename": "playa-final-crazy-20s.mp4",
        "boundingCorners": [[(1, 1), (2, 2)], [(3, 3), (4, 4)], [(5, 5), (6, 6)]],
    })
])

# Various Debugging functions

# write videofile
def writeFile(frame):
    global OUTVID
    if OUTVID == None:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        OUTVID = cv2.VideoWriter('output.mp4', fourcc, 30.0, (frame_width, frame_height))

    OUTVID.write(frame)


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
    input_pts = np.float32(vidObj['baseCorners'])
    output_pts = np.float32(detectCornerPoints(frame, vidObj))
    M = cv2.getPerspectiveTransform(input_pts,output_pts)
    return cv2.warpPerspective(frame,M,(frame_width, frame_height),flags=cv2.INTER_LINEAR)


def trackHumansCentroid(frame, bg_subtractor, vidObj, next_id, tracked_humans, personTracker):
    fg_mask = bg_subtractor.apply(frame)

    # Perform blob detection
    #contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

    detected_humans = []

    for contour in contours:
        # Filter contours based on size, shape, etc.
        x,y,w,h = cv2.boundingRect(contour)
        if cv2.contourArea(contour) > 200:
            #if( y > 350 and (y/h > 5)):
            #    continue

            # Calculate centroid of the contour
            M = cv2.moments(contour)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            # Add centroid and contour to the detected humans list
            detected_humans.append((cx, cy, contour))

    # Update existing tracked humans and remove lost ones
    for human_id in list(tracked_humans.keys()):
        cx_prev, cy_prev, _ = tracked_humans[human_id]
        closest_human = None
        min_distance = float('inf')

        for cx, cy, contour in detected_humans:
            distance = np.sqrt((cx - cx_prev) ** 2 + (cy - cy_prev) ** 2)

            if distance < min_distance:
                closest_human = (cx, cy, contour)
                min_distance = distance

        if closest_human is not None:
            tracked_humans[human_id] = closest_human
            detected_humans.remove(closest_human)
            personTracker[human_id].update(cv2.boundingRect(closest_human[2]))
        else:
            tracked_humans.pop(human_id)
            personTracker.pop(human_id)

    # Assign new IDs to the remaining detected humans
    for cx, cy, contour in detected_humans:
        tracked_humans[next_id] = (cx, cy, contour)
        personTracker[next_id] = Person(pid=next_id, bb=cv2.boundingRect(contour))
        next_id += 1

    # Draw bounding boxes and IDs on the frame
    for human_id, (cx, cy, contour) in tracked_humans.items():
        personTracker[human_id].draw(frame)

    # Display the frame
    cv2.imshow('Tracking', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        sys.exit()



# Step 1:  Open the file
vidObj = inputVideos[FOCUSVID]
cap = cv2.VideoCapture(VIDPATH + vidObj['filename'])
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# need to check whether the corners are all valid, run this.
#validateCornerPoints(cap, vidObj)

ret, frame = cap.read()
vidObj['baseCorners'] = detectCornerPoints(frame, vidObj)

# Initialize variables for Centroid tracker.
bg_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows = False, history=100)
#bg_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows = False, dist2Threshold = 2000)

next_id = 1  # Next available ID for tracking humans
tracked_humans = {}  # Dictionary to store tracked humans with their IDs
personTracker = {}

fcnt = 1
while True:
    # Read the next frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    #sframe = stabilizeFrame(frame, vidObj)
    trackHumansCentroid(frame, bg_subtractor, vidObj, next_id, tracked_humans, personTracker)
    writeFile(frame)

print(personTracker)

cap.release()
cv2.destroyAllWindows()

if OUTVID:
    OUTVID.release()

sys.exit()
