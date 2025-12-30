# Panduan Installasi GrowServer di Termux (SQLite)

Panduan ini akan membantu Anda menginstall Private Server Growtopia menggunakan `GrowServer` yang telah dimodifikasi agar berjalan lancar di Termux menggunakan database SQLite (lebih ringan dan mudah daripada PostgreSQL).

## Persiapan (Prerequisites)

Sebelum memulai, pastikan Termux Anda sudah update dan memiliki tools dasar. Buka Termux dan jalankan perintah berikut:

```bash
pkg update && pkg upgrade
pkg install git nodejs python make clang build-essential
```

Tool-tool di atas (`python`, `make`, `clang`) **WAJIB** ada agar modul database `better-sqlite3` bisa dicompile di HP Anda.

## Cara Install

1.  Download script setup yang sudah saya buatkan. Jika Anda melihat file `setup_server.sh` di folder ini, jalankan perintah berikut:

    ```bash
    bash setup_server.sh
    ```

    Script ini akan otomatis:
    - Mendownload source code server dari GitHub.
    - Menginstall dependency (library) yang dibutuhkan.
    - Mengubah sistem database dari PostgreSQL ke SQLite.
    - Melakukan build project.

2.  Tunggu prosesnya selesai. Ini mungkin memakan waktu beberapa menit tergantung koneksi internet dan kecepatan HP Anda.

## Cara Menjalankan Server

Setelah proses install selesai dan muncul pesan "Setup Complete!", masuk ke folder server dan jalankan:

```bash
cd GrowServer-Termux
npm start
```

Server akan menyala dan siap menerima koneksi.

## Catatan Penting

- **Items.dat**: Pastikan Anda memiliki file `items.dat` yang sesuai di folder `apps/server/assets/`. Script mungkin tidak menyertakan items.dat terbaru, jadi Anda bisa copy dari folder lain jika punya.
- **Port**: Server berjalan di port default Growtopia (biasanya 17091). Pastikan port forwarding di router Anda aktif jika ingin dimainkan online (bukan hanya LAN).
- **SQLite**: Database tersimpan di file `packages/db/data/data.db`. Jangan hapus file ini jika tidak ingin data player hilang.

Selamat mencoba!
