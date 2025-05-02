import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from ultralytics import YOLO

# Trained AI Model
model = YOLO("FoodLink.pt")
# Boolean toggle for scanning mode
ai_mode = False

# Process the frame and analyze it
def process_frame(frame_data):
    """Process the uploaded frame (image) and return barcode or object name."""

    # Convert byte data to image (from PIL format to Open CV format)
    image = Image.open(BytesIO(frame_data))
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

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
            return item_name
    else:
        # Barcode scanning mode
        decoded = decode(frame)
        if decoded:
            # Barcode data is in utf-8 format so must be decoded.
            barcode = decoded[0].data.decode('utf-8')
            return barcode
    # returns none if not found
    return None

def toggle_mode(value):
    """Toggle between barcode and object AI recognition modes."""
    global ai_mode
    ai_mode = value
