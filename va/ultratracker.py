from ultralytics import YOLO
import cv2
from person import Person

#MODEL_FILE = "models/fof-yolov5su-fullset.pt"
#MODEL_FILE = "models/fof_yolov8n-secondbatch.pt"
# MODEL_FILE = "models/yolov8n-seg.pt"

class UltraTracker:

    def __init__(self, bg_subtractor):
        self.model = YOLO(MODEL_FILE)

    def track(self, frame, detections, conf, hudframe, personTracker):
        results = self.model.track(frame, persist=True, classes=1, tracker="bytetrack.yaml", conf=0.1, iou=0.3)
        for res in results:
            if  results[0].boxes.id !=  None:
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                hboxes = results[0].boxes.xywh.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)

                for idx in range(len(ids)):
                    id = int(ids[idx])
                    bb = boxes[idx]
                    bbarray = [int(bb[0]),int(bb[1]),int(bb[2]),int(bb[3])]
                    if id in personTracker:
                        personTracker[id].update(bbarray)
                    else:
                        personTracker[id] = Person(pid=id,bb=bbarray)

                    personTracker[id].draw(hudframe)

        return hudframe