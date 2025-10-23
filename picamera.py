import time
from picamera2 import Picamera2, Preview

# Inisialisasi Picamera2
# Pustaka akan secara otomatis mendeteksi kamera yang terhubung,
# termasuk sensor IMX215 pada Raspberry Pi 5.
picam2 = Picamera2()

# Membuat konfigurasi untuk pratinjau.
# Metode ini akan mengatur resolusi dan format yang sesuai untuk pratinjau.
camera_config = picam2.create_preview_configuration(main={"size": (1640, 1232)}, lores={"size": (1640, 1232)})
picam2.configure(camera_config)
print("Konfigurasi kamera yang aktif:", picam2.camera_configuration())

# Memulai jendela pratinjau.
# `Preview.QTGL` menggunakan backend Qt dengan akselerasi OpenGL,
# yang biasanya memberikan performa terbaik.
# Jika Anda menjalankan skrip tanpa desktop (headless), Anda mungkin perlu
# menggunakan `Preview.DRM` atau `Preview.NULL`.
picam2.start_preview(Preview.QTGL)

# Memulai streaming kamera.
picam2.start()

# Pesan untuk memberitahu pengguna apa yang terjadi.
print("Pratinjau kamera akan ditampilkan selama 10 detik.")
print("Pastikan monitor terhubung ke Raspberry Pi untuk melihat hasilnya.")

# Tunggu selama 10 detik agar pratinjau tetap terlihat.
try:
    time.sleep(10)
except KeyboardInterrupt:
    # Memungkinkan pengguna untuk menghentikan skrip lebih awal dengan Ctrl+C.
    print("\nPratinjau dihentikan oleh pengguna.")

finally:
    # Menghentikan kamera dan menutup jendela pratinjau.
    # Ini adalah langkah penting untuk melepaskan sumber daya kamera.
    picam2.stop_preview()
    picam2.stop()
    print("Kamera dan pratinjau berhasil ditutup.")
