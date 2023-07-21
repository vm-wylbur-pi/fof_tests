import supervision as sv
from ultralytics import YOLO
import cv2

model = YOLO('yolov8s.pt')

cap = cv2.VideoCapture("../../../vids/ptest2/lots-of-people-three-lights.mp4")

while True:
    ret, frame = cap.read()
    result = model(frame)[0]
    detections = sv.Detections.from_yolov8(result)

    len(detections)