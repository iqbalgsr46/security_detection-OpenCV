"""
SISTEM KEAMANAN DETEKSI PENCURI DAN BARANG
==========================================
Program ini akan:
1. Mendeteksi manusia dan membunyikan alarm "Awas ada pencuri masuk"
2. Mendeteksi barang-barang dan melacaknya
3. Memberikan peringatan "Barang telah dicuri" ketika barang hilang/dipindahkan

Author: Security Detection System
Version: 2.1 (HD Resolution + Adjustable)
"""

import cv2
from ultralytics import YOLO
import pygame
import time
import os
import threading

class SecuritySystem:
    def __init__(self):
        """Inisialisasi sistem keamanan"""
        print("="*60)
        print("SISTEM KEAMANAN DETEKSI PENCURI DAN BARANG")
        print("="*60)
        
        # Cek apakah file audio sudah ada
        if not os.path.exists('audio/pencuri.mp3') or not os.path.exists('audio/barang_dicuri.mp3'):
            print("\n❌ File audio tidak ditemukan!")
            print("Silakan jalankan 'buat_audio.py' terlebih dahulu")
            exit()
        
        # Inisialisasi YOLO model
        print("\n[1/3] Memuat model YOLO...")
        try:
            self.model = YOLO('yolov8n.pt')
            print("✓ Model YOLO berhasil dimuat")
        except Exception as e:
            print(f"❌ Error memuat model: {e}")
            exit()
        
        # Inisialisasi pygame untuk audio
        print("[2/3] Inisialisasi audio system...")
        pygame.mixer.init()
        print("✓ Audio system siap")
        
        # Status tracking
        self.last_person_alert = 0
        self.alert_cooldown = 5
        
        # Tracking barang dengan posisi
        self.tracked_objects = []
        self.calibrated = False
        self.calibration_frames = 0
        self.calibration_required = 30
        
        # Deteksi pencurian
        self.last_theft_alert = 0
        self.theft_cooldown = 3
        
        # Flag audio
        self.audio_playing = False
        
        # Window size - DEFAULT HD 720p
        self.display_width = 1280
        self.display_height = 720
        
        print("[3/3] Sistem tracking barang siap")
        print("\n✅ Sistem keamanan berhasil diinisialisasi!\n")
    
    def play_audio_non_blocking(self, audio_file):
        """Memutar audio di thread terpisah"""
        def play():
            try:
                self.audio_playing = True
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                self.audio_playing = False
            except Exception as e:
                print(f"⚠️ Error audio: {e}")
                self.audio_playing = False
        
        if not self.audio_playing:
            threading.Thread(target=play, daemon=True).start()
    
    def get_box_center(self, box):
        """Hitung center point dari bounding box"""
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def calibrate_objects(self, results):
        """Kalibrasi: Simpan semua objek dengan posisinya"""
        temp_objects = []
        
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                class_id = int(boxes.cls[i])
                class_name = self.model.names[class_id]
                confidence = float(boxes.conf[i])
                bbox = boxes.xyxy[i].cpu().numpy()
                
                if class_name != 'person' and confidence > 0.35:
                    center = self.get_box_center(bbox)
                    temp_objects.append({
                        'name': class_name,
                        'bbox': bbox,
                        'center': center,
                        'id': f"{class_name}_{len(temp_objects)}"
                    })
        
        for obj in temp_objects:
            self.tracked_objects.append(obj)
        
        self.calibration_frames += 1
        
        if self.calibration_frames >= self.calibration_required:
            self.calibrated = True
            
            # Hitung rata-rata untuk setiap objek unik
            unique_objects = {}
            for obj in self.tracked_objects:
                name = obj['name']
                if name not in unique_objects:
                    unique_objects[name] = []
                unique_objects[name].append(obj)
            
            # Ambil objek yang konsisten terdeteksi
            self.tracked_objects = []
            for name, objs in unique_objects.items():
                if len(objs) >= self.calibration_required * 0.7:
                    self.tracked_objects.append(objs[0])
            
            print("\n" + "="*60)
            print("✅ KALIBRASI SELESAI!")
            print("="*60)
            if self.tracked_objects:
                print("Barang yang dipantau:")
                for obj in self.tracked_objects:
                    print(f"  • {obj['name']} di posisi {obj['center']}")
            else:
                print("⚠️ Tidak ada barang terdeteksi")
            print("="*60)
            print("\n🔒 SISTEM AKTIF\n")
    
    def check_theft(self, current_detections):
        """Cek apakah ada barang yang hilang"""
        current_time = time.time()
        
        if current_time - self.last_theft_alert < self.theft_cooldown:
            return False, None
        
        # Buat list objek yang terdeteksi saat ini
        current_objects = []
        for result in current_detections:
            boxes = result.boxes
            for i in range(len(boxes)):
                class_id = int(boxes.cls[i])
                class_name = self.model.names[class_id]
                confidence = float(boxes.conf[i])
                bbox = boxes.xyxy[i].cpu().numpy()
                
                if class_name != 'person' and confidence > 0.35:
                    center = self.get_box_center(bbox)
                    current_objects.append({
                        'name': class_name,
                        'center': center
                    })
        
        # Cek setiap tracked object
        for tracked in self.tracked_objects:
            found = False
            tracked_name = tracked['name']
            tracked_center = tracked['center']
            
            for current in current_objects:
                if current['name'] == tracked_name:
                    dx = tracked_center[0] - current['center'][0]
                    dy = tracked_center[1] - current['center'][1]
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < 150:
                        found = True
                        break
            
            if not found:
                print(f"\n[THEFT] {tracked_name} HILANG dari posisi {tracked_center}!")
                return True, tracked_name
        
        return False, None
    
    def draw_info_panel(self, frame):
        """Draw info panel - Sesuaikan dengan ukuran HD"""
        height, width = frame.shape[:2]
        
        # Panel lebih besar untuk HD
        panel_width = min(400, width - 20)
        panel_height = 180
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (panel_width, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        if not self.calibrated:
            status_text = f"KALIBRASI: {self.calibration_frames}/{self.calibration_required}"
            status_color = (0, 255, 255)
        else:
            status_text = "SISTEM AKTIF"
            status_color = (0, 255, 0)
        
        # Font scale untuk HD
        font_scale = max(0.5, min(0.8, width / 1200))
        
        cv2.putText(frame, status_text, (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, status_color, 2)
        
        if self.calibrated:
            items = len(self.tracked_objects)
            cv2.putText(frame, f"Memantau: {items} barang", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, (255, 255, 255), 2)
        
        # Resolusi info
        cv2.putText(frame, f"Resolusi: {self.display_width}x{self.display_height}", (20, 105), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (200, 200, 200), 1)
        
        # Controls
        cv2.putText(frame, "q=keluar | r=reset", (20, 135), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (200, 200, 200), 1)
        cv2.putText(frame, "+/- zoom | 1=480p | 2=720p | 3=1080p", (20, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (200, 200, 200), 1)
    
    def draw_tracked_objects(self, frame):
        """Gambar marker untuk objek yang dipantau - Marker lebih besar untuk HD"""
        for obj in self.tracked_objects:
            cx, cy = obj['center']
            cx, cy = int(cx), int(cy)
            
            # Crosshair lebih besar untuk HD
            cv2.drawMarker(frame, (cx, cy), (0, 255, 0), 
                          cv2.MARKER_CROSS, 30, 3)
            
            # Label dengan background
            label = obj['name']
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(frame, (cx - 5, cy - label_size[1] - 35), 
                         (cx + label_size[0] + 5, cy - 30), (0, 255, 0), -1)
            cv2.putText(frame, label, (cx, cy - 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    def resize_frame(self, frame):
        """Resize frame"""
        return cv2.resize(frame, (self.display_width, self.display_height))
    
    def set_resolution(self, preset):
        """Set resolusi ke preset tertentu"""
        presets = {
            1: (640, 480, "480p"),    # SD
            2: (1280, 720, "720p"),   # HD
            3: (1920, 1080, "1080p")  # Full HD
        }
        
        if preset in presets:
            self.display_width, self.display_height, name = presets[preset]
            print(f"\n📐 Resolusi diubah ke {name} ({self.display_width}x{self.display_height})")
    
    def run(self):
        """Main loop"""
        cap = cv2.VideoCapture(1)
        
        if not cap.isOpened():
            print("❌ Error: Kamera tidak dapat diakses!")
            return
        
        # Set capture resolution ke 720p untuk kualitas lebih baik
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("="*60)
        print("🎥 KAMERA AKTIF - HD MODE")
        print("="*60)
        print(f"📐 Resolusi: {self.display_width}x{self.display_height} (HD 720p)")
        print("\n⌨️  KONTROL UKURAN:")
        print("  • 1 = 640x480 (SD)")
        print("  • 2 = 1280x720 (HD) ← Default")
        print("  • 3 = 1920x1080 (Full HD)")
        print("  • + = Zoom In")
        print("  • - = Zoom Out")
        print("  • ↑↓←→ = Adjust manual (+/- 50px)")
        print("\n⌨️  KONTROL LAIN:")
        print("  • q = Keluar")
        print("  • r = Reset/Kalibrasi Ulang")
        print("\n⏳ Kalibrasi...")
        print("   ⚠️  PENTING:")
        print("   1. Letakkan barang di tempat yang JELAS")
        print("   2. JANGAN ada manusia saat kalibrasi")
        print("   3. Tunggu sampai selesai\n")
        
        show_person_alert = False
        show_theft_alert = False
        alert_timer = 0
        stolen_item_name = ""
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            results = self.model(frame, verbose=False, conf=0.35)
            annotated_frame = results[0].plot()
            
            person_detected = False
            
            for result in results:
                boxes = result.boxes
                for i in range(len(boxes)):
                    class_id = int(boxes.cls[i])
                    class_name = self.model.names[class_id]
                    if class_name == 'person':
                        person_detected = True
                        break
            
            # KALIBRASI
            if not self.calibrated:
                self.calibrate_objects(results)
            
            # SISTEM AKTIF
            else:
                current_time = time.time()
                
                # ALERT PENCURI
                if person_detected and (current_time - self.last_person_alert) > self.alert_cooldown:
                    print("\n🚨 PENCURI TERDETEKSI!\n")
                    self.play_audio_non_blocking('audio/pencuri.mp3')
                    show_person_alert = True
                    alert_timer = time.time()
                    self.last_person_alert = current_time
                
                if show_person_alert and (time.time() - alert_timer < 2):
                    h, w = annotated_frame.shape[:2]
                    cv2.putText(annotated_frame, "PENCURI!", (w//3, h//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
                else:
                    show_person_alert = False
                
                # ALERT BARANG DICURI
                theft_detected, stolen_item = self.check_theft(results)
                
                if theft_detected:
                    print("\n" + "🚨"*30)
                    print(f"⚠️⚠️⚠️  BARANG DICURI: {stolen_item.upper()}  ⚠️⚠️⚠️")
                    print("🚨"*30 + "\n")
                    
                    self.play_audio_non_blocking('audio/barang_dicuri.mp3')
                    show_theft_alert = True
                    alert_timer = time.time()
                    stolen_item_name = stolen_item
                    self.last_theft_alert = current_time
                    
                    self.tracked_objects = [obj for obj in self.tracked_objects 
                                           if obj['name'] != stolen_item]
                    print(f"ℹ️  {stolen_item} dihapus dari tracking\n")
                
                if show_theft_alert and (time.time() - alert_timer < 3):
                    h, w = annotated_frame.shape[:2]
                    cv2.putText(annotated_frame, f"DICURI: {stolen_item_name}!", 
                               (50, h//2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
                else:
                    show_theft_alert = False
                
                # Gambar tracked objects
                self.draw_tracked_objects(annotated_frame)
            
            # Info panel
            self.draw_info_panel(annotated_frame)
            
            # Display
            display_frame = self.resize_frame(annotated_frame)
            cv2.imshow('Sistem Keamanan - HD', display_frame)
            
            # Keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n🛑 Sistem dihentikan")
                break
            
            elif key == ord('r'):
                print("\n🔄 Reset kalibrasi...")
                self.calibrated = False
                self.calibration_frames = 0
                self.tracked_objects = []
            
            # Preset resolutions
            elif key == ord('1'):
                self.set_resolution(1)  # 480p
            elif key == ord('2'):
                self.set_resolution(2)  # 720p (default)
            elif key == ord('3'):
                self.set_resolution(3)  # 1080p
            
            # Zoom controls
            elif key == ord('+') or key == ord('='):
                self.display_width = min(1920, int(self.display_width * 1.1))
                self.display_height = min(1080, int(self.display_height * 1.1))
                print(f"\n Zoom In: {self.display_width}x{self.display_height}")
            
            elif key == ord('-') or key == ord('_'):
                self.display_width = max(320, int(self.display_width * 0.9))
                self.display_height = max(240, int(self.display_height * 0.9))
                print(f"\n Zoom Out: {self.display_width}x{self.display_height}")
            
            # Arrow keys (adjust by 50px)
            elif key == 82 or key == 0:  # Up
                self.display_height = min(1080, self.display_height + 50)
                print(f"\n Tinggi: {self.display_height}px")
            
            elif key == 84 or key == 1:  # Down
                self.display_height = max(240, self.display_height - 50)
                print(f"\n Tinggi: {self.display_height}px")
            
            elif key == 83 or key == 2:  # Right
                self.display_width = min(1920, self.display_width + 50)
                print(f"\n Lebar: {self.display_width}px")
            
            elif key == 81 or key == 3:  # Left
                self.display_width = max(320, self.display_width - 50)
                print(f"\n Lebar: {self.display_width}px")
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    try:
        security = SecuritySystem()
        security.run()
    except KeyboardInterrupt:
        print("\n🛑 Dihentikan (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
