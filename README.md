# GTPS Python Termux

Proyek ini adalah implementasi Private Server Growtopia (GTPS) berbasis Python yang dioptimalkan untuk berjalan di Android menggunakan Termux. Server ini menggunakan arsitektur modular dengan **FastAPI** untuk login server dan **ENet** (via `pyenet`) untuk game server, semuanya berjalan secara asinkronus (`asyncio`).

## Fitur Utama
1. **Login Server (HTTP)**:
   - Menangani request `server_data.php`.
   - Mengarahkan client ke Game Server.
2. **Game Server (UDP/ENet)**:
   - **Protocol**: Handshake lengkap (Hello -> Logon -> OnSuperMainStart).
   - **Encryption**: Implementasi XOR Cipher untuk keamanan dan kompatibilitas client.
   - **Optimization**: Loop efisien (10ms sleep) untuk hemat baterai Android.
3. **Database (SQLite)**:
   - Penyimpanan data Player (Username, Password, Posisi, World, Inventory).
   - Auto-save saat disconnect.
4. **World System**:
   - World Manager dinamis.
   - Fitur Join World (`action|join_request`).
5. **Chat System**:
   - Parsing pesan chat (`action|input`).
   - Feedback log ke client.

## Prasyarat
- Aplikasi Termux (Android).
- Koneksi Internet (untuk instalasi awal).

## Instalasi di Termux

1. **Clone Repositori** (atau salin file proyek ini ke Termux).
2. **Jalankan Script Setup**:
   Script ini akan menginstal Python, Clang, dan library yang dibutuhkan.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   *Catatan: Instalasi `pyenet` mungkin memakan waktu karena proses kompilasi.*

## Cara Menjalankan Server

Jalankan perintah berikut di direktori proyek:
```bash
python main.py
```

Server akan berjalan pada:
- **Login Server**: Port 8000 (HTTP).
- **Game Server**: Port 17091 (UDP).

## Konfigurasi Client (Hosts)
Untuk menyambungkan client Growtopia ke server ini:

Isi file `/system/etc/hosts` (butuh root/virtual hosts):
```
127.0.0.1 growtopia1.com
127.0.0.1 growtopia2.com
```

## Struktur Proyek
- `src/core/`: Logika inti game (Player, World, WorldManager).
- `src/network/`: Networking ENet dan Protokol Paket.
- `src/server/`: HTTP Server (FastAPI).
- `src/data/`: Database (SQLite) dan Parser Items.
- `src/utils/`: Utilitas enkripsi dan helper.
- `tests/`: Unit testing.

## Pengembangan Lebih Lanjut
Langkah selanjutnya:
1. Melengkapi parsing `TankPacket` di `src/network/protocol.py` (Map Data serializer).
2. Implementasi Broadcast Chat penuh (Mapping Peer-to-Player).
3. Implementasi Inventory Logic.
