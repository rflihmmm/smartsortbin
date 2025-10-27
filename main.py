import cv2
from ultralytics import YOLO
import numpy as np
import serial
import time
import threading
from collections import Counter

# --- Konfigurasi ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
MODEL_PATH = 'best.pt' # Menggunakan model nano yang lebih ringan untuk performa lebih baik
CLASS_NAMES = ['organik', 'nonorganik', 'campuran']
YOLO_INPUT_SIZE = 416 # Ukuran input yang lebih seimbang untuk akurasi dan kecepatan

# --- Variabel Global untuk Threading ---
last_frame = None
frame_lock = threading.Lock()
ser = None
running = True  # Flag untuk menghentikan thread
annotated_frame = None

# --- Fungsi untuk Thread 1: Akses Kamera Realtime ---
def camera_thread_func(cap):
    global last_frame, running
    while running:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                last_frame = frame.copy()
        else:
            print("Gagal membaca frame dari webcam.")
            time.sleep(0.5) # Beri jeda jika gagal membaca frame
    print("Camera thread stopped.")

# --- Fungsi Utama ---
def main():
    global ser, running, last_frame, annotated_frame

    # Inisialisasi Serial
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Berhasil terhubung ke Arduino di port {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Gagal terhubung ke Arduino: {e}. Program berjalan tanpa komunikasi serial.")

    # Muat model YOLO
    model = YOLO(MODEL_PATH)

    # Inisialisasi Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Gagal membuka webcam.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Webcam dimulai dengan resolusi: {width}x{height}")

    # Buat dan mulai threads
    cam_thread = threading.Thread(target=camera_thread_func, args=(cap,))
    
    cam_thread.start()

    print("Program berjalan. Memantau kamera secara realtime...")

    try:
        while running:
            frame_to_process = None
            with frame_lock:
                if last_frame is None:
                    time.sleep(0.01) # Tunggu sebentar jika belum ada frame
                    continue
                frame_to_process = last_frame.copy()

            # --- Logika Deteksi Realtime ---
            results = model.predict(source=frame_to_process, imgsz=YOLO_INPUT_SIZE, show=False, verbose=False, conf=0.5)
            
            # Gambar bounding box pada frame hasil deteksi
            annotated_frame_with_boxes = results[0].plot()
            with frame_lock:
                annotated_frame = annotated_frame_with_boxes

            message_to_send = None # Pesan default, tidak ada yang dikirim

            if results and results[0].boxes:
                detected_objects = results[0].boxes.data.tolist()
                
                if detected_objects:
                    detected_classes = []
                    for obj in detected_objects:
                        conf = obj[4]
                        class_id = int(obj[5])
                        if class_id < len(CLASS_NAMES):
                            class_name = CLASS_NAMES[class_id]
                            detected_classes.append(class_name)

                    unique_classes = set(detected_classes)
                    final_class_name = None

                    if 'campuran' in unique_classes:
                        final_class_name = 'campuran'
                    elif 'organik' in unique_classes and 'nonorganik' in unique_classes:
                        final_class_name = 'campuran'
                    elif 'organik' in unique_classes:
                        final_class_name = 'organik'
                    elif 'nonorganik' in unique_classes:
                        final_class_name = 'nonorganik'
                    
                    # Hanya kirim pesan jika deteksi valid (bukan campuran/tidak ada)
                    if final_class_name == 'organik':
                        message_to_send = "0"
                    elif final_class_name == 'nonorganik':
                        message_to_send = "1"
            
            # Kirim hasil ke Arduino hanya jika ada pesan yang valid
            if ser and message_to_send:
                try:
                    print(f"Mengirim pesan ke Arduino: {message_to_send}")
                    ser.write(message_to_send.encode())
                    ser.flush()
                except serial.SerialException as e:
                    print(f"Error saat mengirim ke serial: {e}")
>>>>>>>
            # Jika tidak ada deteksi yang valid, loop akan berlanjut (deteksi ulang)
            # tanpa mengirim pesan apapun.

            # Tampilkan frame dari kamera untuk visualisasi
            display_frame = None
            with frame_lock:
                # Always display the annotated frame if available, otherwise the raw frame
                if annotated_frame is not None:
                    display_frame = annotated_frame
                elif last_frame is not None:
                    display_frame = last_frame
            
            if display_frame is not None:
                cv2.imshow('Realtime Camera Feed', display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break
    
    finally:
        # Cleanup
        print("Menghentikan program...")
        running = False
        cam_thread.join()
        
        cap.release()
        cv2.destroyAllWindows()
        if ser and ser.is_open:
            ser.close()
            print("Koneksi serial ditutup.")

if __name__ == "__main__":
    main()
