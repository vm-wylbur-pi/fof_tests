import cv2
from ultralytics import YOLO
import argparse

vid_default = "../../../vids/ptest2/lots-adults-six-lights.mp4"
mod_default = "models/fof-yolov8n-secondbatch.pt"
show_default = True

parser = argparse.ArgumentParser(description='Process model and video filenames.')
parser.add_argument('-m', dest='model_file', type=str, help='Path to the model file', default=mod_default)
parser.add_argument('-f', dest='video_file', type=str, help='Path to the video file',default=vid_default)
parser.add_argument('--show', action='store_true', help='To viz or not to viz', default=show_default)
args = parser.parse_args()

# Load the given YOLOv8 model
model = YOLO(args.model_file)

# Open the video file
cap = cv2.VideoCapture(args.video_file)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        # results = model(frame, stream=True)
        results = model.track(frame, persist=True, show=args.show, classes=1, tracker="bytetrack.yaml", conf=0.05)
        # results = model(frame, show=True, classes=1)

cap.close()
        # Visualize the results on the frame
        #annotated_frame = results[0].plot()

        # Display the annotated frame
        #cv2.imshow("YOLOv8 Inference", annotated_frame)
