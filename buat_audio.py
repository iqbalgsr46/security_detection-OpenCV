"""
Script untuk membuat file audio peringatan
Jalankan script ini SATU KALI sebelum menjalankan program utama
"""

from gtts import gTTS
import os

def create_audio_files():
    """Membuat file audio untuk sistem keamanan"""
    
    # Buat folder audio jika belum ada
    if not os.path.exists('audio'):
        os.makedirs('audio')
        print("✓ Folder 'audio' berhasil dibuat")
    
    try:
        # Buat audio untuk deteksi pencuri
        print("Membuat audio 'pencuri.mp3'...")
        tts_pencuri = gTTS('Awas ada pencuri masuk', lang='id')
        tts_pencuri.save('audio/pencuri.mp3')
        print("✓ File 'pencuri.mp3' berhasil dibuat")
        
        # Buat audio untuk barang dicuri
        print("Membuat audio 'barang_dicuri.mp3'...")
        tts_barang = gTTS('Barang telah dicuri', lang='id')
        tts_barang.save('audio/barang_dicuri.mp3')
        print("✓ File 'barang_dicuri.mp3' berhasil dibuat")
        
        print("\n✅ Semua file audio berhasil dibuat!")
        print("Anda sekarang bisa menjalankan program utama (main.py)")
        
    except Exception as e:
        print(f"❌ Error saat membuat file audio: {e}")
        print("Pastikan Anda sudah install library gtts:")
        print("pip install gtts --break-system-packages")

if __name__ == "__main__":
    print("="*50)
    print("GENERATOR AUDIO SISTEM KEAMANAN")
    print("="*50)
    create_audio_files()
