import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from ultralytics import YOLO

# Trained AI Model
model = YOLO("web_app\FoodLink.pt")
# Boolean toggle for scanning mode
ai_mode = False

def process_frame(frame_data):
    """The function opens the byte-encoded frame using PIL
       so that it can be passed to either the YOLO object detection model
       or Pyzbar. The name is then returned.

       Args:
           frame_data (bytes): Frame data in bytes.

       Returns:
            item_name/barcode/none (str/none): Item name or barcode used to match the item with one in the database. None returned if nothing is identified.
    """

    # Convert byte data to image (from PIL format to Open CV format).
    image = Image.open(BytesIO(frame_data))
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # AI mode: Object detection using YOLO trained on a custom dataset.
    if ai_mode:
        results = model(frame, verbose=False)
        # Gets the name of the with highest confidence value from the first items detected.
        if len(results[0].boxes.cls) > 0:
            boxes = results[0].boxes
            confidences = boxes.conf
            classes = boxes.cls
            max_conf_index = confidences.argmax()
            class_id = int(classes[max_conf_index])
            item_name = model.names[class_id]
            return item_name
    else:
        # Barcode scanning mode using Pyzbar.
        decoded = decode(frame)
        if decoded:
            # Barcode data is in utf-8 format so must be decoded.
            barcode = decoded[0].data.decode('utf-8')
            return barcode
    # Returns none if not found.
    return None

def toggle_mode(value):
    """This function requests the image file that was posted to this route
       and passes it to the scanner module's process frame function so that
       the barcode or object can be identified.

       Args:
            value (Bool): True / False value used to determine scanning the mode
    """
    global ai_mode
    ai_mode = value
