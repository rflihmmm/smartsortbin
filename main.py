import cv2
from ultralytics import YOLO
import numpy as np
import serial
import time


# --- Konfigurasi ---
# Konfigurasi Serial
SERIAL_PORT = '/dev/ttyACM0'  # Ganti jika port serial Arduino berbeda
BAUD_RATE = 9600
ser = None  # Inisialisasi variabel ser

try:
    # Timeout diatur ke 5 detik. Jika Arduino tidak merespon dalam 5 detik, readline akan berhenti menunggu.
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
    time.sleep(2)  # Beri waktu agar koneksi serial stabil
    print(f"Berhasil terhubung ke Arduino di port {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Gagal terhubung ke Arduino: {e}. Program berjalan tanpa komunikasi serial.")

MODEL_PATH = 'best.pt'
CLASS_NAMES = ['organik', 'non-organik', 'campuran']
YOLO_INPUT_SIZE = 320             # ukuran input ke YOLO, kecil biar cepat

# Muat model YOLO
model = YOLO(MODEL_PATH)

# Inisialisasi Webcam menggunakan OpenCV
cap = cv2.VideoCapture(0)  # 0 biasanya untuk webcam USB default
if not cap.isOpened():
    print("Gagal membuka webcam. Pastikan terhubung dan tidak digunakan oleh program lain.")
    exit()

# Dapatkan resolusi kamera asli
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
CAMERA_RESOLUTION = (width, height)

print(f"Webcam dimulai dengan resolusi: {CAMERA_RESOLUTION}")
print("Menunggu trigger dari Arduino (pesan '3')...")

# Loop utama program
while True:
    # 1. Tunggu pesan dari Arduino
    if ser and ser.in_waiting > 0:
        message_from_arduino = ser.readline().decode('utf-8').strip()
        
        # 2. Jika pesan adalah "3", jalankan deteksi
        if message_from_arduino == "3":
            print("Trigger '3' diterima. Memulai deteksi...")
            
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Gagal membaca frame dari webcam.")
                continue  # Lanjut ke iterasi berikutnya, tunggu trigger lagi

            # --- Cek kondisi frame putih untuk menghindari deteksi palsu ---
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_frame, 240, 255, cv2.THRESH_BINARY)
            white_pixels = cv2.countNonZero(thresh)
            total_pixels = frame.shape[0] * frame.shape[1]
            white_percentage = (white_pixels / total_pixels) * 100

            if white_percentage > 95:
                print("Permukaan putih terdeteksi, tidak ada objek. Mengirim status 'campuran' (2).")
                if ser:
                    try:
                        ser.write("2".encode())  # Kirim '2' untuk campuran/error case
                        ser.flush()
                    except serial.SerialException as e:
                        print(f"Error saat komunikasi serial: {e}")
                cv2.putText(frame, "Permukaan Putih Terdeteksi", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # --- Proses deteksi ---
                small_frame = cv2.resize(frame, (YOLO_INPUT_SIZE, YOLO_INPUT_SIZE))
                results = model.predict(source=small_frame, imgsz=YOLO_INPUT_SIZE, show=False, verbose=False)
                
                scale_x = CAMERA_RESOLUTION[0] / YOLO_INPUT_SIZE
                scale_y = CAMERA_RESOLUTION[1] / YOLO_INPUT_SIZE

                detected_objects = results[0].boxes.data.tolist() if results and results[0].boxes else []

                if detected_objects:
                    # Ambil objek dengan skor kepercayaan tertinggi
                    best_detection = max(detected_objects, key=lambda x: x[4])
                    class_id = int(best_detection[5])
                    class_name = CLASS_NAMES[class_id]
                    
                    # 3. Kirim hasil klasifikasi ke Arduino
                    message_to_send = None
                    if class_name == 'organik': message_to_send = "0"
                    elif class_name == 'non-organik': message_to_send = "1"
                    elif class_name == 'campuran': message_to_send = "2"

                    if ser and message_to_send:
                        try:
                            print(f"Objek terdeteksi: '{class_name}'. Mengirim pesan: '{message_to_send}'")
                            ser.write(message_to_send.encode())
                            ser.flush()
                        except serial.SerialException as e:
                            print(f"Error saat komunikasi serial: {e}")
                    
                    # Gambar kotak untuk visualisasi
                    for box in detected_objects:
                        x1, y1, x2, y2, score, cid_float = box
                        x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f'{CLASS_NAMES[int(cid_float)]}: {score:.2f}'
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                else:
                    # Jika tidak ada objek terdeteksi, kirim status 'campuran'
                    print("Tidak ada objek terdeteksi. Mengirim status 'campuran' (2).")
                    if ser:
                        try:
                            ser.write("2".encode())
                            ser.flush()
                        except serial.SerialException as e:
                            print(f"Error saat komunikasi serial: {e}")

            # Tampilkan frame hasil deteksi
            cv2.imshow('Deteksi Objek', frame)
            
            # 4. Kembali menunggu trigger berikutnya
            print("Deteksi selesai. Menunggu trigger berikutnya dari Arduino...")

    # Cek tombol 'q' untuk keluar, non-blocking.
    # imshow diperlukan agar waitKey berfungsi.
    # Jika tidak ada imshow, loop akan sulit dihentikan dengan keyboard.
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    
    # Beri sedikit jeda agar loop tidak membebani CPU saat menunggu
    time.sleep(0.1)

cap.release()
cv2.destroyAllWindows()
if ser and ser.is_open:
    ser.close()
    print("Koneksi serial ditutup.")
