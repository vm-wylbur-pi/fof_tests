import cv2
from ultralytics import YOLO

cap = cv2.VideoCapture("vids/perimeter-run.mp4")
model = YOLO("yolov8n.pt")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model.track(frame, persist=True)
    boxes = results[0].boxes.xyxy.numpy().astype(int)

    print(boxes)
    if not results[0].boxes:
        continue
    else:
        ids = results[0].boxes.id.cpu().numpy().astype(int)

    print(ids)
    for box, id in zip(boxes, ids):
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"Id {id}",
            (box[0], box[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break