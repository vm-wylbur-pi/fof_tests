## python note: m1 mac requires tensorflow-wmacos and tensorflow-metal
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys

plt.ion()

# starting with https://tfhub.dev/google/object_detection/mobile_object_localizer_v1/1
interpreter = tf.lite.Interpreter(model_path="./models/object_detection_mobile_object_localizer_v1_1_default_1.tflite")
interpreter.allocate_tensors()

# Get the input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

img = cv2.imread("./pics/lperson-close.jpeg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (input_details[0]['shape'][2], input_details[0]['shape'][1]))
img = np.expand_dims(img, axis=0)
img = img.astype(np.uint8) # was float32

# Run inference on the input image
interpreter.set_tensor(input_details[0]['index'], img)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

output_dict = {
    'num_detections': int(interpreter.get_tensor(output_details[3]["index"])),
    'detection_classes': interpreter.get_tensor(output_details[1]["index"]).astype(np.uint8),
    'detection_boxes' : interpreter.get_tensor(output_details[0]["index"]),
    'detection_scores' : interpreter.get_tensor(output_details[2]["index"])
}

boxes = output_dict['detection_boxes']
scores = output_dict['detection_scores']

filtered_boxes = []
filtered_scores = []
filtered_points = []

for i in range(len(scores)):
    for j in range(len(scores[i])):
        # in chatgpt this had a [0] after it, which i removed and it started working
        if scores[i][j] > 0.5: # Only keep detections with confidence score > 0.5
            ymin, xmin, ymax, xmax = boxes[i][j]
            h, w, _ = img[0].shape
            ymin = int(max(1, ymin * h))
            ymax = int(min(h, ymax * h))
            xmin = int(max(1, xmin * w))
            xmax = int(min(w, xmax * w))
            filtered_boxes.append([xmin, ymin, xmax, ymax])
            filtered_scores.append(scores[i][j])
            filtered_points.append([(xmax+xmin)/2,ymax])

fix, ax = plt.subplots()

# Draw the resulting bounding boxes on the input image
for i in range(len(filtered_boxes)):
    box = filtered_boxes[i]
    cv2.rectangle(img[0], (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
    cv2.circle(img[0], (int(filtered_points[i][0]),int(filtered_points[i][1])), radius=2, color=(255,0,0), thickness=-1)

# Display the result
ax.imshow(img[0])
plt.show()