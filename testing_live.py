import cv2
from ultralytics import YOLO
import sys

# Muat model YOLOv8 kustom Anda
model = YOLO('best.pt')

# Definisikan nama-nama kelas dengan urutan yang sudah diperbaiki
class_names = ['organik', 'nonorganik', 'campuran']

# Inisialisasi webcam
# Angka 0 biasanya merujuk ke webcam default. Ganti jika Anda memiliki beberapa webcam.
cap = cv2.VideoCapture(0)

# Periksa apakah webcam berhasil dibuka
if not cap.isOpened():
    print("Error: Tidak dapat membuka webcam.")
    sys.exit()

print("Webcam berhasil dibuka. Menjalankan deteksi langsung...")
print("Tekan tombol 'q' pada jendela video untuk menghentikan program.")

# Loop utama untuk deteksi secara real-time
while True:
    # Baca satu frame dari webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Gagal membaca frame dari webcam. Menghentikan program.")
        break

    # Lakukan prediksi pada frame yang ditangkap (verbose=False untuk output terminal yang bersih)
    results = model.predict(source=frame, show=False, verbose=False)

    # Proses hasil deteksi
    for result in results:
        for box in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = box
            
            # Pastikan class_id berada dalam rentang yang valid
            if int(class_id) < len(class_names):
                class_name = class_names[int(class_id)]
                
                # Tampilkan hasil deteksi di terminal
                print(f"Objek Terdeteksi: {class_name}, Skor: {score:.2f}")
                
                # Gambar kotak pembatas dan label pada frame
                label = f'{class_name}: {score:.2f}'
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Tampilkan frame hasil deteksi di jendela
    cv2.imshow('Deteksi Langsung - Tekan q untuk keluar', frame)

    # Cek apakah tombol 'q' ditekan untuk keluar dari loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Setelah loop selesai, lepaskan webcam dan tutup semua jendela
cap.release()
cv2.destroyAllWindows()
print("Program dihentikan dan sumber daya dilepaskan.")
