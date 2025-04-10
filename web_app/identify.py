import cv2
from ultralytics import YOLO

class identify():
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.item = None
        self.model = YOLO("yolov8s-worldv2.pt")
        self.model.set_classes(["apple", "banana", "orange", "lettuce", "strawberry", "cake", 
                       "bell pepper", "carrot"])

    def get_item(self):
        return self.item 
    
    def clear_item_name(self):
        self.item = None

    def identify_item(self):
     self.item = None
     self.capture = cv2.VideoCapture(0)
     while True:
        ret, frame = self.capture.read()
        if not ret:
            break
        
        results = self.model(frame, verbose=False)
        names = self.model.names

         # Check if there are any detections
        if len(results[0].boxes.cls) > 0:
            # Get the class ID of the first detected object
            class_id = int(results[0].boxes.cls[0])

            # Get the name corresponding to the first detected class
            self.item = names[class_id]
        
        else:    
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    
    def release_capture(self):
        if self.capture.isOpened:
            self.capture.release()

    

