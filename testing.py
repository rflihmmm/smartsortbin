import cv2
from ultralytics import YOLO
import sys

# Muat model YOLOv8 kustom Anda
model = YOLO('best.pt')

# Definisikan nama-nama kelas
# PENTING: Urutan ini harus sama persis dengan urutan kelas saat model dilatih.
# Jika model dilatih dengan urutan ['non-organik', 'organik', ...], maka urutan di sini harus disesuaikan.
# --- URUTAN DITUKAR UNTUK PENGUJIAN ---
class_names = ['non-organik', 'organik', 'campuran']

# Tentukan path ke gambar yang ingin dideteksi
# Ganti nama file di bawah ini untuk menguji dengan gambar yang berbeda (misal: 'gambar_2.jpeg', 'gambar_3.jpeg', dll.)
image_path = 'gambar_1.jpeg' 

# Muat gambar dari file
frame = cv2.imread(image_path)

# Periksa apakah gambar berhasil dimuat
if frame is None:
    print(f"Error: Tidak dapat memuat gambar dari path: {image_path}")
    sys.exit()

# Lakukan prediksi pada gambar (verbose=False untuk output yang lebih bersih)
results = model.predict(source=frame, show=False, verbose=False)

print(f"--- Hasil Deteksi untuk Gambar: '{image_path}' ---")
detection_found = False

# Proses hasil deteksi dan tampilkan di terminal
for result in results:
    for box in result.boxes.data.tolist():
        detection_found = True
        x1, y1, x2, y2, score, class_id = box
        class_name = class_names[int(class_id)]
        
        # Tampilkan hasil deteksi ke terminal, termasuk Class ID mentah untuk diagnosis
        print(f"  - Objek Terdeteksi: {class_name} (Class ID: {int(class_id)}), Skor Kepercayaan: {score:.2f}")
        
        # Gambar kotak dan label pada frame untuk visualisasi
        label = f'{class_name} (ID: {int(class_id)})'
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, label, (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

if not detection_found:
    print("  Tidak ada objek yang terdeteksi dalam gambar.")

print("----------------------------------------------------")

# Fungsi untuk menghentikan program dengan paksa
try:
    # Tampilkan gambar hasil deteksi dengan instruksi yang jelas di judul jendela
    window_title = 'Hasil Deteksi - Tekan tombol apa saja untuk keluar'
    cv2.imshow(window_title, frame)
    
    print(f"Menampilkan gambar. Tekan tombol apa saja pada jendela '{window_title}' atau Ctrl+C di terminal untuk keluar.")

    # Tunggu hingga ada tombol keyboard yang ditekan
    cv2.waitKey(0)

except KeyboardInterrupt:
    # Ini akan dieksekusi jika Anda menekan Ctrl+C di terminal
    print("\nProgram dihentikan oleh pengguna (Ctrl+C).")

finally:
    # Pastikan semua jendela OpenCV ditutup dengan benar
    cv2.destroyAllWindows()
    print("Jendela ditutup. Program selesai.")
