import cv2
import numpy as np
import sys
from person import Person
import tensorflow as tf

class TFLiteTracker:

    def __init__(self, bg_subtractor, frame_width, frame_height):
        self.next_id = 1
        self.tracked_humans = {}
        self.bg_subtractor = bg_subtractor
        self.model_file = "../../../models/lite-model_efficientdet_lite2_detection_default_1.tflite"
        self.threshold = 0.5
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Load the TensorFlow Lite model
        self.interpreter = tf.lite.Interpreter(model_path=self.model_file)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()


    def track(self, frame, personTracker, hudframe):
        fg_mask = self.bg_subtractor.apply(frame)

        # Preprocess the image for input to the model
        input_shape = tuple(self.input_details[0]['shape'][1:3])
        resized_frame = cv2.resize(fg_mask, input_shape)
        input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)

        # Run the model on the input image
        print(int(self.input_details[0]['index']), input_data)
        self.interpreter.set_tensor(int(self.input_details[0]['index']), input_data)
        self.interpreter.invoke()
        #output_data = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]

        output_dict = {
            'detection_boxes' : self.interpreter.get_tensor(self.output_details[0]["index"]),
            'detection_classes': self.interpreter.get_tensor(self.output_details[1]["index"]).astype(np.uint8),
            'detection_scores' : self.interpreter.get_tensor(self.output_details[2]["index"]),
            'num_detections': int(self.interpreter.get_tensor(self.output_details[3]["index"]))
        }

        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

        pindex = np.where(output_dict['detection_classes'] == 2)[0]

        detected_humans = []

        for i in range(len(scores)):
            if scores[i] >= self.threshold:
                ymin, xmin, ymax, xmax = boxes[i]
                xmin = int(xmin * self.frame_width)
                xmax = int(xmax * self.frame_width)
                ymin = int(ymin * self.frame_height)
                ymax = int(ymax * self.frame_height)
                cx = xmin + xmax / 2
                cy = ymin + ymax / 2
                boxes[i] = (ymin,xmin,ymax,xmax)
                detected_humans.append((cx,cy, boxes[i]))

        # Update existing tracked humans and remove lost ones
        for human_id in list(self.tracked_humans.keys()):
            cx_prev, cy_prev, _ = self.tracked_humans[human_id]
            closest_human = None
            min_distance = float('inf')

            for cx, cy, box in detected_humans:
                distance = np.sqrt((cx - cx_prev) ** 2 + (cy - cy_prev) ** 2)

                if distance < min_distance:
                    closest_human = (cx, cy, box)
                    min_distance = distance

            if closest_human is not None:
                self.tracked_humans[human_id] = closest_human
                detected_humans.remove(closest_human)
                personTracker[human_id].update(closest_human[2])
            else:
                self.tracked_humans.pop(human_id)
                personTracker.pop(human_id)

        # Assign new IDs to the remaining detected humans
        for cx, cy, box in detected_humans:
            self.tracked_humans[self.next_id] = (cx, cy, box)
            personTracker[self.next_id] = Person(pid=self.next_id, bb=box)
            self.next_id += 1

        # Draw bounding boxes and IDs on the frame
        for human_id, (cx, cy, box) in self.tracked_humans.items():
            personTracker[human_id].draw(hudframe)

        return hudframe

