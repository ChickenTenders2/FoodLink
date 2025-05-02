import cv2
from pyzbar.pyzbar import decode
from ultralytics import YOLO

# Removed OpenCV video capture initialization
barcode = None
item_name = None
pause = False
ai_mode = False

# Custom model trained on pre-labeled fruit/veg datasets obtained from RoboFlow
model = YOLO("trained_AI_model\FoodLink.pt")

# Global variables for MJPEG stream
camera_feed = None  # This will store the camera feed to be streamed

def get_scanned():
    """Returns the barcode or object name found"""
    return item_name if ai_mode else barcode

def clear_scanned():
    """Resets the object name or barcode found"""
    global barcode, item_name
    barcode = None
    item_name = None

def unpause_scanner():
    """Allows for analysis of frames after pausing"""
    global pause
    pause = False

def toggle_mode(value):
    """Toggles what is analyzed in each frame (barcode or object) based on value (True or False)"""
    global ai_mode
    ai_mode = value

def scan():
    """Yield a video stream of user's camera. It also analyzes each frame for a barcode (using pyzbar) if ai_mode is False, or for an object (using YOLO)."""
    global barcode, item_name, pause, camera_feed

    clear_scanned()

    while True:
        if camera_feed is None:
            break  # Ensure video feed exists before proceeding

        read, frame = camera_feed.read()
        if not read:
            break

        if not pause:
            if ai_mode:
                results = model(frame, verbose=False)
                if len(results[0].boxes.cls) > 0:
                    boxes = results[0].boxes
                    confidences = boxes.conf
                    classes = boxes.cls
                    max_confidence_index = confidences.argmax()
                    class_id = int(classes[max_confidence_index])

                    item_name = model.names[class_id]
                    pause = True
            else:
                decoded = decode(frame)
                if decoded:
                    barcode = decoded[0].data.decode('utf-8')
                    pause = True

        _, buffer = cv2.imencode('.jpeg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def release_capture():
    """Release camera feed if it was opened"""
    global camera_feed
    if camera_feed:
        camera_feed.release()
        camera_feed = None
