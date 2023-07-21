import cv2
import os
import sys

frame_interval = 45


import tensorflow as tf

model_file = "../../../models/lite-model_efficientdet_lite2_detection_default_1.tflite"
interpreter = tf.lite.Interpreter(model_path=model_file)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()

def save_every_interval_frame(video_file):
    # Open the video file for reading
    cap = cv2.VideoCapture(video_file)

    if not cap.isOpened():
        print("Error: Unable to open video file.")
        sys.exit(1)

    # Get the file name without the extension
    file_name_without_extension = os.path.splitext(os.path.basename(video_file))[0]

    # Create a directory to store the frames
    output_dir = file_name_without_extension + "_frames"
    os.makedirs(output_dir, exist_ok=True)

    frame_count = 0
    skip_frames = 30

    while True:
        # Read the frame from the video
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        #input_shape = tuple(input_details[0]['shape'][1:3])
        #frame = cv2.resize(frame, input_shape)

        # Save every frame_interval frame to the output directory
        if frame_count % frame_interval == skip_frames:
            frame_file_name = os.path.join(output_dir, f"{file_name_without_extension}_frame_{frame_count}.jpg")
            cv2.imwrite(frame_file_name, frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    save_every_interval_frame(video_file)
