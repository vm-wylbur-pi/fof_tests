from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.pt')  # load an official detection model
model = YOLO('yolov8n-seg.pt')  # load an official segmentation model
#model = YOLO('path/to/best.pt')  # load a custom model

# Track with the model
results = model.track(source="https://youtu.be/Zgi9g1ksQHc", show=False)
results = model.track(source="https://youtu.be/Zgi9g1ksQHc", show=False, tracker="bytetrack.yaml")
