import cv2
from pyzbar.pyzbar import decode

class barcode():
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.number = None

    def get_barcode(self):
        return self.number
    
    def clear_barcode(self):
        self.number = None

    def decode_barcode(self):
        self.number = None
        self.capture = cv2.VideoCapture(0)
        while True:
            # Ret is a boolean variable signifying if a frame was successfully or 
            # unsuccessfully read.
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

                # Yields part of a multipart HTTP response so that the indivdual frames
                # are sent to the browser and are interpreted as a motion JPEG video.
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def release_capture(self):
        if self.capture.isOpened:
            self.capture.release()

    

