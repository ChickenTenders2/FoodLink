import cv2
from pyzbar.pyzbar import decode
from ultralytics import YOLO

capture = cv2.VideoCapture(0)
barcode = None
item_name = None
pause = False
ai_mode = False

model = YOLO("yolov8s-worldv2.pt")
# YOLO world uses a set of classes so the model 'knows' what it needs to try and 
# identify. In this application it is food items often sold without a barcode
model.set_classes([
    "Apple", "Banana", "Orange", "Grapes", "Strawberry", "Blueberry", "Lemon", "Lime",
    "Lettuce", "Bell pepper", "Carrot", "Broccoli", "Cucumber", "Tomato",
    "Potato", "Onion", "Garlic", "Courgette", "Celery", "Corn", "Pear", "Peach", "Plum",
    "Nectarine", "Avocado", "Mango", "Watermelon", "Cantaloupe", "Pineapple"
])

# returns barcode or name of identified object
def get_scanned():
    return item_name if ai_mode else barcode

def clear_scanned():
    global barcode, item_name
    barcode = None
    item_name = None

def unpause_scanner():
    global pause
    pause = False

def toggle_mode(value):
    global ai_mode
    ai_mode = value

def scan():
    global capture, barcode, item_name, pause

    clear_scanned()
    capture = cv2.VideoCapture(0)

    while True:
        # Read is a boolean variable signifying if a frame was successfully or 
        # unsuccessfully read.
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
                    # Get the class ID of the first detected object
                    class_id = int(results[0].boxes.cls[0])

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
        # are sent to the browser and are interpreted as a motion JPEG video.
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def release_capture():
    if capture.isOpened:
        capture.release()
