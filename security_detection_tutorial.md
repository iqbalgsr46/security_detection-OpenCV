# Tutorial: Sistem Deteksi Keamanan dengan Python

## Deskripsi Program
Program ini akan:
- Mendeteksi manusia dan membunyikan alarm "Awas ada pencuri masuk"
- Mendeteksi barang-barang dan melacaknya
- Memberikan peringatan "Barang telah dicuri" ketika barang hilang/dipindahkan

---

## Langkah 1: Instalasi Library yang Dibutuhkan

Buka terminal/command prompt dan install library berikut:

```bash
pip install opencv-python --break-system-packages
pip install ultralytics --break-system-packages
pip install gtts --break-system-packages
pip install pygame --break-system-packages
pip install numpy --break-system-packages
```

**Penjelasan Library:**
- `opencv-python`: Untuk mengakses kamera dan memproses video
- `ultralytics`: YOLO v8 untuk deteksi objek
- `gtts`: Google Text-to-Speech untuk menghasilkan suara
- `pygame`: Untuk memutar file audio
- `numpy`: Untuk operasi array dan matematika

---

## Langkah 2: Struktur Folder

Buat folder project dengan struktur:
```
security_system/
├── main.py
├── audio/
│   ├── pencuri.mp3
│   └── barang_dicuri.mp3
└── README.md
```

---

## Langkah 3: Membuat File Audio

Jalankan script ini sekali untuk membuat file audio:

```python
from gtts import gTTS
import os

# Buat folder audio jika belum ada
os.makedirs('audio', exist_ok=True)

# Buat audio untuk deteksi pencuri
tts_pencuri = gTTS('Awas ada pencuri masuk', lang='id')
tts_pencuri.save('audio/pencuri.mp3')

# Buat audio untuk barang dicuri
tts_barang = gTTS('Barang telah dicuri', lang='id')
tts_barang.save('audio/barang_dicuri.mp3')

print("File audio berhasil dibuat!")
```

---

## Langkah 4: Program Utama

Berikut adalah kode lengkap program deteksi keamanan:

```python
import cv2
from ultralytics import YOLO
import pygame
import time
import numpy as np

class SecuritySystem:
    def __init__(self):
        # Inisialisasi YOLO model
        print("Memuat model YOLO...")
        self.model = YOLO('yolov8n.pt')  # Model YOLOv8 nano (ringan)
        
        # Inisialisasi pygame untuk audio
        pygame.mixer.init()
        
        # Status tracking
        self.person_detected = False
        self.last_person_alert = 0
        self.alert_cooldown = 5  # Cooldown 5 detik antara alert
        
        # Tracking barang
        self.initial_objects = {}
        self.calibrated = False
        self.calibration_frames = 0
        self.calibration_required = 30  # 30 frame untuk kalibrasi
        
        print("Sistem keamanan siap!")
    
    def play_audio(self, audio_file):
        """Memutar file audio"""
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error memutar audio: {e}")
    
    def calibrate_objects(self, detections):
        """Kalibrasi awal untuk mendeteksi barang-barang yang ada"""
        for detection in detections:
            class_id = int(detection.boxes.cls[0])
            class_name = self.model.names[class_id]
            
            # Hanya track objek bukan manusia
            if class_name != 'person':
                if class_name not in self.initial_objects:
                    self.initial_objects[class_name] = 0
                self.initial_objects[class_name] += 1
        
        self.calibration_frames += 1
        
        if self.calibration_frames >= self.calibration_required:
            self.calibrated = True
            # Ambil rata-rata jumlah objek
            for obj in self.initial_objects:
                self.initial_objects[obj] = self.initial_objects[obj] // self.calibration_required
            print(f"\nKalibrasi selesai! Objek terdeteksi: {self.initial_objects}")
    
    def check_object_theft(self, current_objects):
        """Cek apakah ada barang yang hilang"""
        for obj_name, initial_count in self.initial_objects.items():
            current_count = current_objects.get(obj_name, 0)
            if current_count < initial_count:
                return True, obj_name
        return False, None
    
    def run(self):
        """Menjalankan sistem keamanan"""
        # Buka kamera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Tidak dapat mengakses kamera!")
            return
        
        print("\n=== SISTEM KEAMANAN AKTIF ===")
        print("Tekan 'q' untuk keluar")
        print("Sedang melakukan kalibrasi awal...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Deteksi objek menggunakan YOLO
            results = self.model(frame, verbose=False)
            
            # Gambar hasil deteksi
            annotated_frame = results[0].plot()
            
            current_objects = {}
            person_detected_now = False
            
            # Proses setiap deteksi
            for result in results:
                for detection in result.boxes:
                    class_id = int(detection.boxes.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(detection.boxes.conf[0])
                    
                    # Deteksi manusia
                    if class_name == 'person' and confidence > 0.5:
                        person_detected_now = True
                    
                    # Hitung objek selain manusia
                    if class_name != 'person' and confidence > 0.5:
                        current_objects[class_name] = current_objects.get(class_name, 0) + 1
            
            # Fase kalibrasi
            if not self.calibrated:
                self.calibrate_objects(results)
                cv2.putText(annotated_frame, 
                           f"KALIBRASI: {self.calibration_frames}/{self.calibration_required}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            else:
                # Sistem aktif
                cv2.putText(annotated_frame, "SISTEM AKTIF", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Alert untuk pencuri
                current_time = time.time()
                if person_detected_now and (current_time - self.last_person_alert) > self.alert_cooldown:
                    print("\n[ALERT] PENCURI TERDETEKSI!")
                    cv2.putText(annotated_frame, "PENCURI TERDETEKSI!", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.play_audio('audio/pencuri.mp3')
                    self.last_person_alert = current_time
                
                # Cek pencurian barang
                theft_detected, stolen_item = self.check_object_theft(current_objects)
                if theft_detected:
                    print(f"\n[ALERT] BARANG DICURI: {stolen_item}")
                    cv2.putText(annotated_frame, f"BARANG DICURI: {stolen_item}", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.play_audio('audio/barang_dicuri.mp3')
                    time.sleep(2)  # Pause sebentar
                    # Update baseline setelah alert
                    self.initial_objects = current_objects.copy()
            
            # Tampilkan frame
            cv2.imshow('Security System', annotated_frame)
            
            # Tekan 'q' untuk keluar
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("\nSistem keamanan dimatikan.")

if __name__ == "__main__":
    # Jalankan sistem
    security = SecuritySystem()
    security.run()
```

---

## Langkah 5: Cara Menjalankan Program

1. **Buat file audio terlebih dahulu**:
   ```bash
   python buat_audio.py
   ```

2. **Jalankan program utama**:
   ```bash
   python main.py
   ```

3. **Proses Kalibrasi**:
   - Saat program mulai, biarkan kamera mendeteksi barang-barang yang ada selama 30 frame
   - Jangan ada gerakan pada fase ini
   - Setelah kalibrasi selesai, sistem akan aktif

4. **Testing**:
   - Berjalan di depan kamera → akan terdengar "Awas ada pencuri masuk"
   - Ambil/pindahkan barang yang terdeteksi → akan terdengar "Barang telah dicuri"

---

## Penjelasan Cara Kerja

### 1. Deteksi Objek dengan YOLO
YOLO (You Only Look Once) adalah algoritma deep learning yang dapat mendeteksi berbagai objek dalam waktu real-time. Program menggunakan YOLOv8 yang dapat mengenali 80+ jenis objek termasuk:
- person (manusia)
- bottle, cup, chair, laptop, cell phone, dll

### 2. Sistem Kalibrasi
- Program melakukan kalibrasi awal untuk "mengingat" barang-barang yang ada
- Setelah kalibrasi, jika jumlah barang berkurang, sistem akan alert

### 3. Text-to-Speech
- Menggunakan Google TTS untuk menghasilkan suara dalam Bahasa Indonesia
- Audio disimpan sebagai file MP3 dan diputar menggunakan pygame

### 4. Cooldown System
- Mencegah alert berulang-ulang dalam waktu singkat
- Default cooldown adalah 5 detik

---

## Tips dan Troubleshooting

### Kamera Tidak Terdeteksi
Jika error "Tidak dapat mengakses kamera", coba ubah parameter:
```python
cap = cv2.VideoCapture(1)  # Coba index 1, 2, dst
```

### Deteksi Kurang Akurat
- Pastikan pencahayaan cukup
- Letakkan barang di tempat yang jelas terlihat kamera
- Gunakan model yang lebih besar (lebih akurat tapi lebih lambat):
  ```python
  self.model = YOLO('yolov8m.pt')  # medium model
  ```

### Audio Tidak Keluar
- Pastikan speaker/audio device aktif
- Cek apakah file audio sudah dibuat di folder `audio/`

### Program Terlalu Lambat
- Gunakan model lebih kecil: `yolov8n.pt` (paling cepat)
- Kurangi resolusi kamera
- Tambahkan frame skipping

---

## Pengembangan Lebih Lanjut

1. **Simpan Rekaman**: Tambahkan fitur untuk menyimpan video saat ada deteksi
2. **Notifikasi**: Kirim notifikasi ke HP via Telegram/WhatsApp
3. **Multi Kamera**: Support untuk beberapa kamera sekaligus
4. **Database**: Simpan log deteksi ke database
5. **Web Interface**: Buat dashboard untuk monitoring

---

## Kesimpulan

Program ini merupakan sistem keamanan sederhana yang dapat:
- ✅ Mendeteksi manusia secara real-time
- ✅ Membunyikan alarm dengan suara bahasa Indonesia
- ✅ Melacak barang-barang yang ada
- ✅ Mendeteksi jika ada barang yang hilang/dipindahkan

Selamat mencoba! 🚀
