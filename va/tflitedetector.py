import cv2
import numpy as np
import sys
from person import Person
import tensorflow as tf

#import tflite_runtime.interpreter as tf
import norfair
from norfair import Detection, Paths, Tracker, Video

class TFLiteDetector:

    def __init__(self, bg_subtractor, frame_width, frame_height):
        self.next_id = 1
        self.tracked_humans = {}
        self.bg_subtractor = bg_subtractor
        self.threshold = 0.3
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Load the TensorFlow Lite model
        # https://tfhub.dev/tensorflow/lite-model/efficientdet/lite2/detection/default/1
        # self.model_file = "models/lite-model_efficientdet_lite2_detection_default_1.tflite"
        # self.model_file = "models/model-edet0-fof.tflite"
        self.model_file = "models/lite-model_efficientdet_lite0_detection_default_1.tflite"
        # self.model_file = "models/fof-edet2-wtf1.tflite"

        # self.model_file = "models/object_detection_mobile_object_localizer_v1_1_default_1.tflite"
        #self.model_file = "../../../models/efficientdet_lite2_448_ptq_edgetpu.tflite"
        #self.interpreter = interpreter = tf.Interpreter(self.model_file,
        #                                                    experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])
        self.interpreter = tf.lite.Interpreter(model_path=self.model_file)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.output_width = frame_width
        self.output_height = frame_height

        self.nt = Tracker(
            distance_function='iou',
            distance_threshold=5,
        )


    def detect(self, frame, personTracker, hudframe, medianFrame):
        fg_mask = self.bg_subtractor.apply(frame)

        # shoehorn the missing dimensions back into the frame
        # perhaps this should be np.squeeze?
        fg_mask = cv2.merge([fg_mask, fg_mask, fg_mask])

        ##### let's mask some stuff
        #dframe = cv2.absdiff(frame, medianFrame)
        # Treshold to binarize
        #th, frame = cv2.threshold(dframe, 30, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,)

        # Preprocess the image for input to the model
        input_shape = tuple(self.input_details[0]['shape'][1:3])
        resized_frame = cv2.resize(fg_mask, input_shape)
        input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)

        # Run the model on the input image
        #print(int(self.input_details[0]['index']), input_data)
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

        detections = []
        for i in range(len(scores)):
            if scores[i] >= self.threshold:
                ymin, xmin, ymax, xmax = boxes[i]
                xmin = int(xmin * self.frame_width)
                xmax = int(xmax * self.frame_width)
                ymin = int(ymin * self.frame_height)
                ymax = int(ymax * self.frame_height)
                w = xmax - xmin
                h = ymax - ymin
                cx = xmin + xmax / 2
                cy = ymin + ymax / 2

                bbox = np.array([
                    [xmin,ymin],
                    [xmax,ymax],
                ])
                npscores = np.array([scores[i], scores[i]])
                label = 'person'
                detections.append(Detection(points=bbox, scores=npscores, label=label))

                # simple filter for size mismatches
                #if (w < h):
                #    cv2.rectangle(hudframe, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                #    cv2.putText(hudframe, str(round(scores[i],2)) + "x " + str(xmax) + "y " + str(ymax), (xmax,ymin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0),1,2)

        self.tracked_objects = self.nt.update(detections=detections)
        norfair.draw_boxes(hudframe, detections)
        norfair.draw_tracked_boxes(hudframe, self.tracked_objects)
        return (hudframe, detections)

