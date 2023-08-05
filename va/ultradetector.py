from ultralytics import YOLO
import cv2
from person import Person

MODEL_FILE = "models/fof-yolov5su-fullset.pt"
PERSON_CLASS = 1
PERSON_CONF = 0.4
#MODEL_FILE = "models/yolov8n.pt"

class UltraDetector:

    def __init__(self, bg_subtractor):
        self.model = YOLO(MODEL_FILE)

    def detect(self, frame):
        prediction = self.model(frame, stream=True, classes=PERSON_CLASS, conf=PERSON_CONF)
        result = []
        conf = []
        for p in prediction:
            boxes = p.boxes.cpu().numpy()
            for box in boxes:
                result.append(box.xyxy[0].astype(int))
                conf.append(box.conf)

        return result, conf