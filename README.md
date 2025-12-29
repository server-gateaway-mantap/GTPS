# GTPS Python Termux (Porting C++)

Proyek ini adalah implementasi ulang (rewrite) dari Growtopia Private Server (GTPS) berbasis C++ ke dalam Bahasa Python, yang dioptimalkan secara spesifik untuk berjalan di lingkungan **Android Termux**.

Proyek ini meniru struktur paket data binary C++ (seperti `TankPacket` dan `VariantList`) untuk memastikan kompatibilitas penuh dengan client asli Growtopia.

## Fitur Utama

### 1. Networking (Porting C++)
- **Protokol Binary Identik**: Menggunakan modul `struct` Python untuk mereplikasi layout memori `GamePacket` (60 bytes) dan `VariantList` dari source C++.
- **Packet Factory**: Class `PacketFactory` (`src/utils/packet_factory.py`) menangani serialisasi data kompleks seperti Map Data dan Variant List.
- **Enkripsi**: Implementasi algoritma XOR standar untuk keamanan paket.

### 2. Login Server (HTTP)
- **Support GET & POST**: Endpoint `/growtopia/server_data.php` mendukung kedua metode untuk kompatibilitas maksimal.
- **FastAPI**: Menggunakan framework asinkronus modern yang cepat.

### 3. Core Logic
- **Database SQLite**: Penyimpanan data player (Posisi, World, Inventory) yang ringan dan portabel.
- **World System**: Generator map prosedural sederhana dan sistem join world (`SEND_MAP_DATA`).
- **Chat System**: Broadcast chat real-time antar pemain dalam satu world.

### 4. Optimasi Termux
- **Hemat Baterai**: Loop server menggunakan `asyncio.sleep(0.01)` untuk mencegah penggunaan CPU 100%.
- **Setup Otomatis**: Script `setup.sh` menangani instalasi dependensi native (`clang`, `libenet`) dan Python (`pyenet`).

## Struktur Proyek

- `src/core/`: Logika inti (Player, World).
- `src/network/`: Implementasi server ENet dan definisi Protokol.
- `src/server/`: HTTP Login Server.
- `src/data/`: Database dan Parser.
- `src/utils/`: Factory Paket dan Enkripsi.

## Cara Instalasi & Menjalankan (Termux)

1. **Persiapan**:
   Pastikan Anda memiliki koneksi internet.

2. **Jalankan Setup**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   *Script ini akan menginstall Python, Clang, ENet, dan library Python yang dibutuhkan.*

3. **Jalankan Server**:
   ```bash
   python main.py
   ```

4. **Koneksi Client**:
   Arahkan host `growtopia1.com` dan `growtopia2.com` ke IP device Termux Anda (di `/system/etc/hosts`).

## Catatan Porting
- Struktur `GamePacket` di `src/network/protocol.py` menggunakan format `<iiiiiiififffffi` (60 bytes) untuk meniru struct C++ standar.
- Serialisasi `VariantList` meniru logika `eVariantType` dari SDK C++.

## Lisensi
Proyek ini adalah untuk tujuan edukasi dan riset.
