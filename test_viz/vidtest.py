import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

#from vidstab.VidStab import VidStab
#stabilizer = VidStab()

# pip install opencv-python, tensorflow-macos, matplotlib
video_file = "./vids/final-crazy.mp4"

# convert mov:
#  ./ffmpeg -i short-movement-test.mov -vcodec h264 -acodec mp2 short-movement-test.mp4
# https://tfhub.dev/tensorflow/lite-model/efficientdet/lite2/detection/default/1
model_file = "./models/lite-model_efficientdet_lite2_detection_default_1.tflite"
threshold = 0.3
RMIN = 1
RMAX = 10000009

# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path=model_file)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Open the video file and get the frame dimensions
video = cv2.VideoCapture(video_file)
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (frame_width, frame_height))

################################################################
# Randomly select 25 frames
frameIds = video.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=100)

# Store selected frames in an array
frames = []
for fid in frameIds:
    video.set(cv2.CAP_PROP_POS_FRAMES, fid)
    ret, frame = video.read()
    frames.append(frame)

# Calculate the median along the time axis
medianFrame = np.median(frames, axis=0).astype(dtype=np.uint8)

# Display median frame
#cv2.imshow('frame', medianFrame)
#cv2.waitKey(0)

# Reset frame number to 0
video.set(cv2.CAP_PROP_POS_FRAMES, 0)

# Convert background to grayscale
# grayMedianFrame = cv2.cvtColor(medianFrame, cv2.COLOR_BGR2GRAY)

# Loop over all frames
#ret = True
#cnt = 0
#while(ret):
    # Read frame
#    ret, frame = cap.read()
#    if not ret:
#        break
    # Convert current frame to grayscale
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Calculate absolute difference of current frame and
    # the median frame
 #   dframe = cv2.absdiff(frame, medianFrame)
#    # Treshold to binarize
#    th, dframe = cv2.threshold(dframe, 30, 255, cv2.THRESH_BINARY)
#    # Display image
#    # Display median frame
#    cv2.imshow('frame', dframe)
#    cv2.waitKey(0)
#    print(cnt)
#    cnt += 1

# Release video object
#cap.release()
#out.release()

# Destroy all windows
#cv2.destroyAllWindows()

# sys.exit()
################################################################


counter = 0
# Loop over each frame in the video
while True:
    counter = counter + 1

    if counter < RMIN:
        print('counter is: %d' % counter)
        continue

    if counter > RMAX:
        print('breaking out')
        break

    # Read the next frame from the video
    ret, frame = video.read()
    if not ret:
        break

    ##### let's mask some stuff
    dframe = cv2.absdiff(frame, medianFrame)
    # Treshold to binarize
    th, frame = cv2.threshold(dframe, 30, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,)

    # Preprocess the image for input to the model
    input_shape = tuple(input_details[0]['shape'][1:3])
    resized_frame = cv2.resize(frame, input_shape)
    input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)

    # Run the model on the input image
    interpreter.set_tensor(int(input_details[0]['index']), input_data)
    interpreter.invoke()
    #output_data = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]

    output_dict = {
        'detection_boxes' : interpreter.get_tensor(output_details[0]["index"]),
        'detection_classes': interpreter.get_tensor(output_details[1]["index"]).astype(np.uint8),
        'detection_scores' : interpreter.get_tensor(output_details[2]["index"]),
        'num_detections': int(interpreter.get_tensor(output_details[3]["index"]))
    }

    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    pindex = np.where(output_dict['detection_classes'] == 2)[0]

    #if len(pindex) == 0:
    #    continue

    # Draw bounding boxes around humans in the image
    for i in range(len(scores)):
        if scores[i] >= threshold:
            ymin, xmin, ymax, xmax = boxes[i]
            xmin = int(xmin * frame_width)
            xmax = int(xmax * frame_width)
            ymin = int(ymin * frame_height)
            ymax = int(ymax * frame_height)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame, str(round(scores[i],2)) + "x " + str(xmax) + "y " + str(ymax), (xmax,ymin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1,2)

    # Write the processed frame to the output video file
    out.write(frame)
    if(counter % 1000 == 0):
        plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        plt.show()

# Release the video capture and output video objects
video.release()
out.release()

print("okay we're done here")

# Display the output video
# output_video = cv2.VideoCapture('output.mp4')

# while True:
#    ret, frame = output_video.read()
#    if not ret:
#        break
#    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#    plt.show()
#    break


