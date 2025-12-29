# GrowServer (Termux Edition Port)

Ini adalah porting spesial dari [GrowServer](https://github.com/StileDevs/GrowServer) agar bisa berjalan lancar di Android menggunakan Termux dengan database SQLite yang ringan.

## Fitur Porting

*   **SQLite Database**: Menggantikan PostgreSQL yang berat dengan SQLite (file-based).
*   **Auto Installer**: Script `setup-termux.sh` yang otomatis menginstall semua dependency dan menerapkan patch.
*   **Optimized**: Siap pakai untuk local server di HP.

## Cara Install (Termux)

1.  Download **Termux** dari F-Droid.
2.  Buka Termux.
3.  Clone repo ini (atau download zip dan extract).
4.  Jalankan perintah berikut:

```bash
chmod +x setup-termux.sh
./setup-termux.sh
```

Tunggu hingga proses selesai. Script akan:
1.  Clone GrowServer asli.
2.  Mengubah kode database menjadi SQLite.
3.  Install dependency.
4.  Build project.
5.  Setup database awal.

## Cara Menjalankan

Setelah instalasi selesai, jalankan perintah ini setiap kali ingin menyalakan server:

```bash
cd GrowServer/apps/server
pnpm start
```

Server akan berjalan di port `17091` (UDP) dan `8000` (HTTP).

## Cara Menyambung (Android)

Karena server berjalan di `127.0.0.1` (localhost):

1.  **Metode APK**: Gunakan APK Growtopia Private Server yang ip-nya diset ke `127.0.0.1`.
2.  **Metode Hosts (Root)**: Tambahkan `127.0.0.1 growtopia1.com` di `/system/etc/hosts`.

## Troubleshooting

*   **Gagal Install `better-sqlite3`**: Pastikan python dan build-essential terinstall (script setup harusnya sudah menginstallnya).
*   **Reset Database**: Hapus file `GrowServer/packages/db/data/database.db` dan jalankan `pnpm --filter @growserver/db db:seed`.

---
*Created by Jules for StileDevs Port Request.*
