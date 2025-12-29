# GTPS Python Termux (Khusus Non-Root)

Proyek ini adalah implementasi Private Server Growtopia (GTPS) berbasis Python yang dioptimalkan untuk Android Termux, **khususnya untuk perangkat Non-Root**.

## Fitur Utama
1. **Server Core**: Python 3.11+, Asyncio, ENet, SQLite.
2. **Kompatibilitas**: Protokol Binary C++ (60 bytes struct), VariantList, Enkripsi XOR.
3. **Gameplay Dasar**: Login, Join World, Chat, Punch (Visual Log).
4. **Non-Root Friendly**: Menggunakan port tinggi (8000 & 17091) dan panduan Virtual Hosts.

## Instalasi (Termux)

1. **Persiapan**:
   - Install Termux dari F-Droid atau Play Store.
   - Install aplikasi **Virtual Hosts** dari Play Store (untuk redirect domain tanpa root).

2. **Setup Server**:
   ```bash
   # Clone repo ini (atau copy file)
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Jalankan Server**:
   ```bash
   python main.py
   ```
   *Server Login berjalan di port 8000, Game Server di 17091.*

## Panduan Koneksi (Non-Root / Virtual Hosts)

Karena HP Non-Root tidak bisa menggunakan port 80 (standard HTTP) dan tidak bisa edit `/etc/hosts` sistem, kita gunakan aplikasi "Virtual Hosts".

1. **Buka Aplikasi Virtual Hosts**.
2. **Buat File Hosts Baru** (misal `hosts.txt`) di penyimpanan internal HP.
3. **Isi File hosts.txt**:
   ```
   127.0.0.1 growtopia1.com
   127.0.0.1 growtopia2.com
   ```
   *(Pastikan tidak ada www)*
4. **PENTING: Port Redirection**:
   Aplikasi Virtual Hosts biasanya hanya membelokkan domain ke IP.
   Client GT asli akan mencoba connect ke `http://growtopia1.com/growtopia/server_data.php` (Port 80).

   **Masalah**: Termux Anda listen di Port 8000 (Non-root cannot bind 80).

   **Solusi Alternatif**:
   1. **Gunakan Parallel Space / Virtual Space** yang support redirect port (Advanced).
   2. **Gunakan Modified Client (Mod)**: Gunakan client GT yang sudah dimodifikasi (banyak di internet) yang mengizinkan custom Server IP & Port (misal menargetkan `127.0.0.1:8000`).
   3. **Edit APK**: Jika Anda bisa decompile APK, ubah URL server data ke `http://127.0.0.1:8000/`.

   *Untuk panduan ini, kita asumsikan Anda menggunakan metode Hosts file + Client yang fleksibel atau environment dev.*

## Struktur Proyek

- `src/`: Source code utama.
- `data.db`: Database player (SQLite).
- `logs/`: (Opsional) File log.

## Lisensi
Edukasi Only.
