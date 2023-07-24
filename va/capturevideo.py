import cv2

def find_available_cameras():
    available_cameras = []

    for i in range(10):  # You can adjust the range as needed (usually 0 to 9)
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()

    return available_cameras



def read_video_frames(cam = 0):
    # Open the default camera (usually the webcam) with device index 0
    cap = cv2.VideoCapture(cam)

    # Check if the camera was opened successfully
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if the frame was read successfully
        if not ret:
            print("Error: Failed to read a frame.")
            break

        # Display the frame (you can perform image processing here)
        cv2.imshow("Camera Feed", frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    read_video_frames(1)
