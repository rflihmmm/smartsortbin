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
YOLO_INPUT_SIZE = 640 # Ukuran input yang lebih seimbang untuk akurasi dan kecepatan

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

# --- Fungsi untuk Thread 2: Deteksi Objek ---
def detection_thread_func(model):
    global ser, last_frame, annotated_frame, running

    print("Mendengarkan trigger dari Arduino...")
    while running:
        if ser and ser.in_waiting > 0:
            try:
                trigger = ser.readline().decode('utf-8').strip()
                if trigger == "3":
                    print("Menerima trigger '3' dari Arduino. Menunggu 2 detik untuk stabilisasi...")
                    time.sleep(2) # Tunggu 2 detik
                    
                    retry_count = 0
                    detection_successful = False
                    while retry_count < 2 and not detection_successful and running:
                        print(f"Mencoba melakukan deteksi... (Percobaan ke-{retry_count + 1})")
                        frame_to_process = None
                        with frame_lock:
                            if last_frame is not None:
                                frame_to_process = last_frame.copy()

                        if frame_to_process is not None:
                            results = model.predict(source=frame_to_process, imgsz=YOLO_INPUT_SIZE, show=False, verbose=False, conf=0.25)
                            
                            detected_classes = []
                            annotated_frame_with_boxes = frame_to_process.copy() # Mulai dengan frame asli

                            # Proses hasil deteksi
                            for result in results:
                                for box in result.boxes.data.tolist():
                                    x1, y1, x2, y2, score, class_id = box
                                    
                                    # Pastikan class_id berada dalam rentang yang valid
                                    if int(class_id) < len(CLASS_NAMES):
                                        class_name = CLASS_NAMES[int(class_id)]
                                        detected_classes.append(class_name)
                                        
                                        # Tampilkan hasil deteksi di terminal
                                        print(f"Objek Terdeteksi: {class_name}, Skor: {score:.2f}")
                                        
                                        # Gambar kotak pembatas dan label pada frame
                                        label = f'{class_name}: {score:.2f}'
                                        cv2.rectangle(annotated_frame_with_boxes, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                        cv2.putText(annotated_frame_with_boxes, label, (int(x1) + 4, int(y1) + 13),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                            with frame_lock:
                                annotated_frame = annotated_frame_with_boxes

                            message_to_send = None 
                            if detected_classes:
                                unique_classes = set(detected_classes)
                                
                                if 'campuran' in unique_classes or ('organik' in unique_classes and 'nonorganik' in unique_classes):
                                    message_to_send = "2"
                                elif 'organik' in unique_classes:
                                    message_to_send = "0"
                                elif 'nonorganik' in unique_classes:
                                    message_to_send = "1"
                            
                            if message_to_send:
                                print(f"Mengirim pesan ke Arduino: {message_to_send}")
                                ser.write(message_to_send.encode())
                                ser.flush()
                                detection_successful = True
                            else:
                                print("Tidak ada objek valid yang terdeteksi.")
                                retry_count += 1
                                if retry_count < 2:
                                    print("Mencoba lagi dalam 2 detik...")
                                    time.sleep(2)
                        else:
                            print("Tidak ada frame yang tersedia. Mencoba lagi...")
                            time.sleep(1)
                    
                    if not detection_successful:
                        print("Deteksi gagal setelah 2 kali percobaan. Mengirim '00' ke Arduino.")
                        ser.write("00".encode())
                        ser.flush()
            except Exception as e:
                print(f"Error dalam thread deteksi: {e}")
        else:
            time.sleep(0.05) # Cegah CPU usage tinggi saat tidak ada data serial

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
    detection_thread = threading.Thread(target=detection_thread_func, args=(model,))
    
    cam_thread.start()
    detection_thread.start()

    print("Program berjalan. Menampilkan umpan kamera...")

    try:
        while running:
            display_frame = None
            with frame_lock:
                # Prioritaskan menampilkan frame yang sudah diannotasi jika ada
                if annotated_frame is not None:
                    display_frame = annotated_frame
                # Jika tidak, tampilkan frame mentah dari kamera
                elif last_frame is not None:
                    display_frame = last_frame
            
            if display_frame is not None:
                cv2.imshow('Realtime Camera Feed', display_frame)
            
            # Keluar dari loop jika 'q' ditekan
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break
            
            # Beri sedikit jeda agar tidak membebani CPU
            time.sleep(0.01)

    finally:
        # Cleanup
        print("Menghentikan program...")
        running = False
        cam_thread.join()
        detection_thread.join()
        
        cap.release()
        cv2.destroyAllWindows()
        if ser and ser.is_open:
            ser.close()
            print("Koneksi serial ditutup.")

if __name__ == "__main__":
    main()
