import cv2
from ultralytics import YOLO
import sys

# --- Bagian Awal Kode (Tidak Berubah) ---

# Muat model YOLOv8 kustom Anda
model = YOLO('best.pt')

# Definisikan nama-nama kelas
class_names = ['organik', 'non-organik', 'campuran']

# Tentukan path ke gambar yang ingin dideteksi
image_path = 'gambar_1.jpeg'

# Muat gambar dari file
frame = cv2.imread(image_path)

# Periksa apakah gambar berhasil dimuat
if frame is None:
    print(f"Error: Tidak dapat memuat gambar dari path: {image_path}")
    sys.exit() # Keluar dari script jika gambar tidak ada

# Lakukan prediksi pada gambar
results = model.predict(source=frame, show=False)

# Proses hasil deteksi
for result in results:
    for box in result.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = box
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        label = f'{class_names[int(class_id)]}: {score:.2f}'
        cv2.putText(frame, label, (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# --- Bagian Baru dengan Penanganan KeyboardInterrupt ---

try:
    # Tampilkan gambar hasil deteksi
    cv2.imshow('Deteksi Objek Sampah dari Gambar (Tekan tombol apa saja untuk keluar)', frame)

    # Tunggu hingga ada tombol keyboard yang ditekan di jendela gambar
    cv2.waitKey(0)

except KeyboardInterrupt:
    # Ini akan dieksekusi jika Anda menekan Ctrl+C di terminal
    print("\nProgram dihentikan oleh pengguna (Ctrl+C). Menutup...")

finally:
    # Pastikan semua jendela OpenCV ditutup dengan benar
    cv2.destroyAllWindows()
