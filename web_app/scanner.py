import cv2
from pyzbar.pyzbar import decode
from ultralytics import YOLO

capture = cv2.VideoCapture(0)
barcode = None
item_name = None
pause = False
ai_mode = False

# Custom model trained on pre labeled fruit / veg datasets obtained from RoboFlow
model = YOLO("trained_AI_model/FoodLink.pt")

# returns barcode or name of identified object
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
    """Toggles what is analysed in each frame (barcode or object) based on value (True or False)"""
    global ai_mode
    ai_mode = value

def scan():
    """Yields a video stream of a users camera using OpenCV. It also analyses each frame
    for a barcode (using pyzbar) if ai_mode is False, or for an object (using ultralytics YOLO).
    Once an object or barcode is found, the frames are no longer analysed, until a user requests
    for scanning to commence again."""
    global capture, barcode, item_name, pause

    clear_scanned()
    capture = cv2.VideoCapture(0)

    while True:
        # Read is a boolean variable signifying if a frame was successfully or 
        # unsuccessfully read
        read, frame = capture.read()
        if not read:
            break

        if not pause:
            # if barcode scanning
            if ai_mode:
                # tries to identify if any of items specified are in the frame
                results = model(frame, verbose=False)
                # if there are any detections
                if len(results[0].boxes.cls) > 0:
                    # Get the class ID of the detected object with the highest 
                    # degree of confidence (from its bounding box)
                    boxes = results[0].boxes
                    confidences = boxes.conf
                    classes = boxes.cls
                    max_confidence_index = confidences.argmax()
                    class_id = int(classes[max_confidence_index])

                    # Get the name corresponding to the first detected class
                    item_name = model.names[class_id]                    

                    pause = True
            else:
                # searches for barcode in frame
                decoded = decode(frame)
                # if found
                if decoded:
                    barcode = decoded[0].data.decode('utf-8')
                    # pausing the scanner after finding a barcode makes sure the 
                    # barcode number is not stored whilst barcode checking is stopped
                    # which stops duplicate popup after action is performed
                    pause = True

        # Encode the frame to JPEG
        _, buffer = cv2.imencode('.jpeg', frame)
        frame = buffer.tobytes()
        # Yields part of a multipart HTTP response so that the indivdual frames
        # are sent to the browser and are interpreted as a motion JPEG video
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def release_capture():
    if capture.isOpened:
        capture.release()
