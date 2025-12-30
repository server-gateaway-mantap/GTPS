# GTPS Python Termux (Untuk APK Mod)

Proyek ini adalah implementasi Private Server Growtopia (GTPS) berbasis Python, dioptimalkan untuk Android Termux. Server ini dirancang khusus untuk bekerja dengan **APK Growtopia yang telah dimodifikasi (Hardcoded)** untuk mengarah ke `127.0.0.1:8000`.

## Persyaratan Sistem
1. **Android Phone** (Non-Root aman).
2. **Termux** (Install dari F-Droid).
3. **APK Growtopia Mod**: APK yang file `libgrowtopia.so`-nya sudah dipatch agar `growtopia1.com` mengarah ke `127.0.0.1:8000`.

## Cara Instalasi Server (Termux)

1. **Setup Environment**:
   Jalankan perintah ini di Termux untuk menginstal Python dan dependensi:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Jalankan Server**:
   ```bash
   python main.py
   ```
   *Terminal akan menampilkan log bahwa Login Server (Port 8000) dan Game Server (Port 17091) aktif.*

## Cara Bermain

1. Pastikan Server berjalan di Termux (jangan tutup terminal).
2. Instal dan Buka **APK Growtopia Mod** di HP yang sama.
3. Pada menu awal, pilih **"Play Online"**.
4. Centang **"Legacy users only"** (Penting!).
5. Masukkan **GrowID** dan **Password** sesuka Anda (Akun akan otomatis dibuat jika belum ada).
6. Tekan **Connect**.

## Struktur Proyek
- `src/`: Logika server (Python).
- `data.db`: Database player (SQLite). Akun Anda tersimpan di sini.

## Troubleshooting
- **Stuck di "Connecting..."**: Pastikan server `main.py` berjalan. Cek apakah IP di APK Mod benar-benar `127.0.0.1:8000`.
- **Error Login**: Pastikan menggunakan mode "Legacy".

## Lisensi
Edukasi Only.
