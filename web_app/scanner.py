import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from ultralytics import YOLO

# Your AI and other variables here
model = YOLO("trained_AI_model/FoodLink.pt")
ai_mode = False
barcode = None
item_name = None
pause = False

# Process the frame and analyze it
def process_frame(frame_data):
    """Process the uploaded frame (image) and return barcode or object name."""
    global barcode, item_name, pause

    # Convert byte data to image (from PIL format to Open CV format)
    image = Image.open(BytesIO(frame_data))
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # If the scanner is paused, skip processing
    if pause:
        return None

    # AI mode: Object detection using YOLO
    if ai_mode:
        results = model(frame, verbose=False)
        # Get the name of the with highest confidence value from the first items detected.
        if len(results[0].boxes.cls) > 0:
            boxes = results[0].boxes
            confidences = boxes.conf
            classes = boxes.cls
            max_conf_index = confidences.argmax()
            class_id = int(classes[max_conf_index])
            item_name = model.names[class_id]
            pause = True
            return item_name

    # Barcode scanning mode
    decoded = decode(frame)
    if decoded:
        # Barcode data is in utf-8 format so must be decoded.
        barcode = decoded[0].data.decode('utf-8')
        pause = True
        return barcode

    return None

def get_scanned():
    """Return the last scanned barcode or object."""
    return item_name if ai_mode else barcode

def clear_scanned():
    """Reset the object or barcode found."""
    global barcode, item_name
    barcode = None
    item_name = None

def unpause_scanner():
    """Unpause the scanner for continued analysis."""
    global pause
    pause = False

def toggle_mode(value):
    """Toggle between barcode and object AI recognition modes."""
    global ai_mode
    ai_mode = value
