# Tutorial Membuat Private Server Growtopia di Android (No Root)

Selamat datang! Repo ini berisi alat otomatis untuk membuat server Growtopia sendiri langsung di HP Android Anda menggunakan aplikasi **Termux**. Tidak perlu akses Root!

Server ini menggunakan base **GrowServer (StileDevs)** yang sudah dimodifikasi agar ringan dan menggunakan database **SQLite** (tidak perlu setup Postgres yang rumit).

## Persiapan Bahan

1.  **Aplikasi Termux**: Download di PlayStore atau F-Droid.
2.  **File `items.dat`**: Anda butuh file ini agar server mengenali item. Anda bisa mengambilnya dari folder game Growtopia asli di HP Anda (`Android/data/com.rtsoft.growtopia/files/items.dat`) atau download dari internet.
    *   *Penting:* Letakkan file `items.dat` di folder yang sama dengan script ini nanti, atau ikuti instruksi script.

## Langkah-Langkah Installasi

Buka aplikasi **Termux**, lalu ketik perintah-perintah di bawah ini satu per satu (tekan Enter setiap selesai mengetik satu baris):

### 1. Update Termux & Install Git
```bash
pkg update && pkg upgrade
pkg install git
```

### 2. Download Script Setup
```bash
git clone https://github.com/USERNAME_REPO_ANDA/NAMA_REPO_ANDA.git gtps-android
cd gtps-android
```
*(Ganti link di atas dengan link repository ini)*

### 3. Jalankan Installer
Pastikan Anda sudah menaruh file `items.dat` di folder ini jika ada. Lalu jalankan:
```bash
bash setup_server.sh
```

Tunggu prosesnya berjalan. Script ini akan otomatis:
*   Mendownload source code server terbaru.
*   Menginstall alat-alat yang dibutuhkan (NodeJS, Python, dll).
*   Mengubah database ke SQLite agar ringan.
*   Melakukan "Build" server.

Proses ini bisa memakan waktu 5-15 menit tergantung kecepatan internet dan HP Anda.

## Cara Menyalakan Server

Setelah instalasi selesai (muncul tulisan "Setup Complete!"), Anda bisa menyalakan server kapan saja dengan cara:

1.  Buka Termux.
2.  Masuk ke folder server:
    ```bash
    cd gtps-android/GrowServer-Termux
    ```
3.  Nyalakan server:
    ```bash
    npm start
    ```

Jika berhasil, akan muncul pesan bahwa server sudah berjalan di port **17091**.

## Cara Main (Menghubungkan ke Server)

1.  Edit file `hosts` di HP Anda (butuh aplikasi Virtual Hosts atau edit manual jika root) untuk mengarahkan `growtopia1.com` dan `growtopia2.com` ke IP HP Anda (biasanya `127.0.0.1` jika main di HP yang sama).
2.  Buka Growtopia.
3.  Login!

## Tips Tambahan

*   **Database**: Data player tersimpan di file `packages/db/data/data.db`. Jangan hapus file ini.
*   **Agar Termux tidak mati**: Saat menjalankan server, tarik notifikasi bar Termux dan pilih "Acquire Wakelock" agar server tidak mati saat layar HP mati.

Selamat bermain!
