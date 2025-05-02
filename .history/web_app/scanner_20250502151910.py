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

def analyse_frames(frame, AI_mode = False):
    """Yields a video stream of a users camera using OpenCV. It also analyses each frame
    for a barcode (using pyzbar) if ai_mode is False, or for an object (using ultralytics YOLO).
    Once an object or barcode is found, the frames are no longer analysed, until a user requests
    for scanning to commence again."""

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
            
    else:
        # searches for barcode in frame
        decoded = decode(frame)
        # if found
        if decoded:
            barcode = decoded[0].data.decode('utf-8')
            # pausing the scanner after finding a barcode makes sure the 
            # barcode number is not stored whilst barcode checking is stopped
            # which stops duplicate popup after action is performed
