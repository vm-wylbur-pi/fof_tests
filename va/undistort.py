import cv2
import numpy as np
import sys
import os

CALIBRATION = 'calibration_parameters.npz'

# load calibration parameters from previous calibration test
data = np.load(CALIBRATION)
camera_matrix = data['camera_matrix']
distortion_coeffs = data['distortion_coeffs']

# command line args
if len(sys.argv) != 2:
    print("Usage: python script.py <file_name>")
    sys.exit(1)

input_file = sys.argv[1]
base_name, ext = os.path.splitext(input_file)
output_file = base_name + ".avi"

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

cap = cv2.VideoCapture(input_file)
frame_width = 1172
frame_height = 570

fps = 32
video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'MJPG'), fps, (frame_width, frame_height))

while True:
    # Read a frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    udframe = undistort(frame)

    #resized_frame = cv2.resize(frame, input_shape)
    #input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)


    video_writer.write(udframe)

video_writer.release()
