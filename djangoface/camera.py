import cv2
import base64

def capture_photo():
    cap = cv2.VideoCapture(0)  # Open webcam
    success, frame = cap.read()
    
    if success:
        _, buffer = cv2.imencode('.jpg', frame)  # Convert frame to JPEG
        img_base64 = base64.b64encode(buffer).decode("utf-8")  # Encode to base64
    else:
        img_base64 = None

    cap.release()
    return img_base64
