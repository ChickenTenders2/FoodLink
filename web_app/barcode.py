import cv2
from pyzbar.pyzbar import decode

class barcode():
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.number = None
        self.pause = False

    def get_barcode(self):
        return self.number
    
    def clear_barcode(self):
        self.number = None
    
    def unpause_scanner(self):
        self.pause = False

    def decode_barcode(self):
        self.number = None
        self.capture = cv2.VideoCapture(0)
        while True:
            ret, frame = self.capture.read()
            if not ret:
                break
            decoded = decode(frame)
            # pausing the scanner after finding a barcode makes sure the 
            # barcode number is not stored whilst barcode checking is stopped
            # which stops duplicate popup after action is performed
            if decoded and not self.pause:
                self.number = decoded[0].data.decode('utf-8')
                self.pause = True
            else:
                # Encode the frame to JPEG
                ret, buffer = cv2.imencode('.jpeg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def release_capture(self):
        if self.capture.isOpened:
            self.capture.release()

    

