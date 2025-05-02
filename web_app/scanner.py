import cv2
import numpy as np
from pyzbar.pyzbar import decode
from ultralytics import YOLO

model = YOLO("trained_AI_model/FoodLink.pt")
ai_mode = False  # control from toggle endpoint

def toggle_mode(value):
    global ai_mode
    ai_mode = value

def process_frame(frame_bytes):
    global ai_mode

    np_arr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if ai_mode:
        results = model(frame, verbose=False)
        if len(results[0].boxes.cls) > 0:
            boxes = results[0].boxes
            confidences = boxes.conf
            classes = boxes.cls
            max_confidence_index = confidences.argmax()
            class_id = int(classes[max_confidence_index])
            return model.names[class_id]
    else:
        decoded = decode(frame)
        if decoded:
            return decoded[0].data.decode('utf-8')

    return None
