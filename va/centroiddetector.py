import cv2
import numpy as np
import sys
from person import Person


class CentroidDetector:

    def __init__(self, bg_subtractor, frame_width, frame_height):
        self.next_id = 1
        self.tracked_humans = {}
        self.bg_subtractor = bg_subtractor
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.output_width = frame_width
        self.output_height = frame_height

        self.tracker_type = 'iou'

    def detect(self, frame, personTracker, hudframe, medianFrame):
        fg_mask = self.bg_subtractor.apply(frame)

        # Perform blob detection
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_humans = []

        for contour in contours:
            # Filter contours based on size, shape, etc.
            x,y,w,h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 100:
                #if( y > 350 and (y/h > 5)):
                #    continue

                # Calculate centroid of the contour
                M = cv2.moments(contour)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])

                # Add centroid and contour to the detected humans list
                detected_humans.append((cx, cy, contour))

        # Update existing tracked humans and remove lost ones
        for human_id in list(self.tracked_humans.keys()):
            cx_prev, cy_prev, _ = self.tracked_humans[human_id]
            closest_human = None
            min_distance = float('inf')

            for cx, cy, contour in detected_humans:
                distance = np.sqrt((cx - cx_prev) ** 2 + (cy - cy_prev) ** 2)

                if distance < min_distance:
                    closest_human = (cx, cy, contour)
                    min_distance = distance

            if closest_human is not None:
                self.tracked_humans[human_id] = closest_human
                detected_humans.remove(closest_human)
                personTracker[human_id].update(cv2.boundingRect(closest_human[2]))
            else:
                self.tracked_humans.pop(human_id)
                personTracker.pop(human_id)

        # Assign new IDs to the remaining detected humans
        for cx, cy, contour in detected_humans:
            self.tracked_humans[self.next_id] = (cx, cy, contour)
            personTracker[self.next_id] = Person(pid=self.next_id, bb=cv2.boundingRect(contour))
            self.next_id += 1

        # Draw bounding boxes and IDs on the frame
        for human_id, (cx, cy, contour) in self.tracked_humans.items():
            personTracker[human_id].draw(hudframe)

        return hudframe

