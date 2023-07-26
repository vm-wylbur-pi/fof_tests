import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('models/fof-scratch.pt')

# Open the video file
video_path = "../../../vids/ptest2/lots-adults-six-lights.mp4"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        # results = model(frame, stream=True)
        results = model.track(frame, persist=True, show=True, classes=1, tracker="botsort.yaml", conf=0.05)
        # results = model(frame, show=True, classes=1)


        # Visualize the results on the frame
        #annotated_frame = results[0].plot()

        # Display the annotated frame
        #cv2.imshow("YOLOv8 Inference", annotated_frame)