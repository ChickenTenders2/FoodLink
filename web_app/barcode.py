import cv2
from pyzbar.pyzbar import decode

class barcode():
    def __init__(self):
        self.capture = None
        self.number = None

    def get_barcode(self):
        return self.number
    
    def clear_barcode(self):
        self.number = None

    def decode_barcode(self):
        self.number = None
        self.capture = cv2.VideoCapture(0)
        while True:
            ret, frame = self.capture.read()
            if not ret:
                break
            decoded = decode(frame)
            if decoded:
                self.number = decoded[0].data.decode('utf-8')
            else:
                # Encode the frame to JPEG
                ret, buffer = cv2.imencode('.jpeg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def release_capture(self):
        if self.capture.isOpened:
            self.capture.release()

    

