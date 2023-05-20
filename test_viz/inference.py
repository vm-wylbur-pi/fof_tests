# Imports
import tflite_support
from tflite_support.task import vision
from tflite_support.task import core
from tflite_support.task import processor

model_path = "./models/lite-model_efficientdet_lite2_detection_default_1.tflite"
image_path = "./pics/ti-field-three-people.png"

# Initialization
base_options = core.BaseOptions(file_name=model_path)
detection_options = processor.DetectionOptions(max_results=2)
options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
detector = vision.ObjectDetector.create_from_options(options)

# Alternatively, you can create an object detector in the following manner:
# detector = vision.ObjectDetector.create_from_file(model_path)

# Run inference
image = vision.TensorImage.create_from_file(image_path)
detection_result = detector.detect(image)
