from ultralytics import YOLO
import tensorflow
# Load a model
model = YOLO('models/fof-yolov8n-secondbatch.pt')  # load an official detection model

# Track with the model
results = model.track(source="../../../vids/ptest2/lots-adults-six-lights.mp4", show=True)
#results = model.track(source="https://youtu.be/Zgi9g1ksQHc", show=True, tracker="bytetrack.yaml")
