import cv2
from pyzbar.pyzbar import decode


class barcode():
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def decode_barcode(self):
        while True:
            ret, frame = self.video.read()
            if ret:
                decoded = decode(frame)
                if decoded:
                    print(decoded[0].data.decode('utf-8'))
                if not ret:
                    break
                else:
                    # Encode the frame to JPEG
                    ret, buffer = cv2.imencode('.jpeg', frame)
                    frame = buffer.tobytes()

                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')