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