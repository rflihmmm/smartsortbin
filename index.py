from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import numpy as np
import time

# Inisialisasi kamera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Load model YOLOv8
model = YOLO('yolov8n.pt')  # Gunakan versi nano agar ringan di Pi

# Loop deteksi
try:
    while True:
        frame = picam2.capture_array()

        # Deteksi objek
        results = model.predict(frame, conf=0.4, verbose=False)

        # Gambar bounding box
        annotated_frame = results[0].plot()

        # Tampilkan hasil
        cv2.imshow("YOLOv8 Detection", annotated_frame)

        if cv2.waitKey(1) == ord('q'):
            break

except KeyboardInterrupt:
    pass

# Bersihkan
cv2.destroyAllWindows()
picam2.stop()
