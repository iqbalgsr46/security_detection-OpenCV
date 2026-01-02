# 🔐 Sistem Keamanan Deteksi Pencuri dan Barang

Program Python untuk mendeteksi pencuri dan barang yang hilang menggunakan kamera dan AI.

## 🎯 Fitur

- ✅ Deteksi manusia real-time dengan alert suara "Awas ada pencuri masuk"
- ✅ Tracking barang-barang di area yang dipantau
- ✅ Alert suara "Barang telah dicuri" saat ada barang hilang
- ✅ Menggunakan YOLO v8 untuk deteksi objek yang akurat
- ✅ Interface visual dengan bounding box
- ✅ Sistem kalibrasi otomatis

## 📋 Kebutuhan Sistem

- Python 3.8 atau lebih baru
- Webcam/kamera
- Speaker/audio output
- Koneksi internet (untuk download model pertama kali)

## 🚀 Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

Atau install satu per satu:
```bash
pip install opencv-python --break-system-packages
pip install ultralytics --break-system-packages
pip install gtts --break-system-packages
pip install pygame --break-system-packages
pip install numpy --break-system-packages
```

### 2. Buat File Audio

Jalankan script untuk membuat file audio peringatan:
```bash
python buat_audio.py
```

## 💻 Cara Menggunakan

### Jalankan Program

```bash
python main.py
```

### Proses Kalibrasi (Otomatis)

1. Saat program pertama kali jalan, akan ada fase kalibrasi
2. Pastikan semua barang yang ingin dipantau terlihat kamera
3. Tunggu sampai kalibrasi selesai (~1-2 detik)
4. Sistem akan otomatis aktif setelah kalibrasi

### Kontrol Keyboard

- **q** = Keluar dari program
- **r** = Kalibrasi ulang

## 📸 Screenshot

Program akan menampilkan:
- Video real-time dari kamera
- Bounding box untuk setiap objek terdeteksi
- Panel informasi status sistem
- Alert visual saat ada ancaman

## 🎮 Testing

### Test Deteksi Pencuri
1. Jalankan program
2. Tunggu kalibrasi selesai
3. Berjalan di depan kamera
4. ✅ Akan terdengar: "Awas ada pencuri masuk"

### Test Deteksi Barang Dicuri
1. Jalankan program dengan beberapa barang di depan kamera
2. Tunggu kalibrasi selesai
3. Ambil atau pindahkan salah satu barang
4. ✅ Akan terdengar: "Barang telah dicuri"

## 🔧 Troubleshooting

### Kamera Tidak Terdeteksi
Coba ubah index kamera di `main.py`:
```python
cap = cv2.VideoCapture(1)  # Coba 0, 1, 2, dst
```

### Audio Tidak Keluar
- Pastikan speaker aktif
- Cek volume sistem
- Pastikan file audio sudah dibuat dengan `buat_audio.py`

### Deteksi Kurang Akurat
- Pastikan pencahayaan cukup baik
- Letakkan barang dengan jelas terlihat
- Jangan ada objek yang terlalu berdekatan

### Program Lambat
- Gunakan model lebih ringan (sudah menggunakan `yolov8n.pt` - paling ringan)
- Kurangi resolusi kamera
- Tutup aplikasi lain yang berat

## 📚 Cara Kerja

1. **YOLO v8**: Mendeteksi 80+ jenis objek termasuk manusia
2. **Kalibrasi**: Mencatat barang-barang awal yang ada
3. **Tracking**: Membandingkan kondisi saat ini dengan kondisi awal
4. **Alert**: Membunyikan alarm jika ada anomali

## 🎨 Objek yang Dapat Dideteksi

YOLO dapat mendeteksi 80+ objek, antara lain:
- Manusia (person)
- Elektronik: laptop, cell phone, keyboard, mouse, tv
- Furniture: chair, couch, bed, table
- Peralatan: bottle, cup, bowl, book
- Dan banyak lagi...

## 🔐 Keamanan dan Privacy

- Program hanya berjalan lokal di komputer Anda
- Tidak ada data yang dikirim ke server
- Tidak ada penyimpanan video otomatis

## 📝 Catatan

- Model YOLO akan didownload otomatis saat pertama kali dijalankan (~6MB)
- Untuk deteksi yang lebih akurat di malam hari, gunakan lampu yang cukup
- Sistem bekerja optimal di ruangan dengan pencahayaan baik

## 🤝 Kontribusi

Feel free untuk:
- Report bugs
- Suggest fitur baru
- Improve code

## 📄 Lisensi

Free to use untuk keperluan pribadi dan edukasi.

## 👨‍💻 Pengembangan Lebih Lanjut

Ide untuk pengembangan:
- [ ] Notifikasi ke smartphone
- [ ] Multi-kamera support
- [ ] Rekam video saat ada deteksi
- [ ] Dashboard web monitoring
- [ ] Database log aktivitas
- [ ] Face recognition untuk whitelist
- [ ] Email/Telegram notification

---

**Dibuat dengan menggunakan Python, OpenCV, dan YOLO v8**
