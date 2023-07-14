import cv2
import dlib
import numpy as np

class OpenCVTracker:
    def __init__(self,bg_subtractor):
        self.detector = cv2.HOGDescriptor()
        self.detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.trackers = []
        self.bg_subtractor = bg_subtractor

    def track(self, frame, personTracker):
        fg_mask = self.bg_subtractor.apply(frame)

        boxes = []

        # If no trackers, we must detect objects
        if len(self.trackers) == 0:
            boxes, _ = self.detector.detectMultiScale(fg_mask)

            for (x, y, w, h) in boxes:
                t = dlib.correlation_tracker()
                rect = dlib.rectangle(x, y, x + w, y + h)
                t.start_track(frame, rect)
                self.trackers.append(t)

        # Otherwise, update the trackers
        else:
            for t in self.trackers:
                t.update(frame)
                pos = t.get_position()
                boxes.append((int(pos.left()), int(pos.top()), int(pos.width()), int(pos.height())))

        return boxes

    def draw_boxes(self, frame, boxes):
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame
