from ultralytics import YOLO
import tensorflow
# Load a model
model = YOLO('models/fof-scratch.pt')  # load an official detection model

# Track with the model
results = model.track(source="../../../vids/ptest2/big-initial.mp4", show=False, classes=1, tracker="bytetrack.yaml")
#results = model.track(source="https://youtu.be/Zgi9g1ksQHc", show=True, tracker="bytetrack.yaml")