#!/bin/bash

# Setup Script untuk GTPS Python di Termux
# Script ini akan menginstal dependensi yang diperlukan.

echo "=== Memulai Instalasi Dependensi GTPS Python untuk Termux ==="

# 1. Update paket Termux
echo "[*] Mengupdate paket Termux..."
pkg update -y && pkg upgrade -y

# 2. Instal dependensi build dan Python
echo "[*] Menginstal Python, Clang, dan Build Tools..."
pkg install python python-dev clang make libffi-dev openssl-dev -y

# 3. Instal dependensi ENet (jika tersedia di repositori standar, jika tidak perlu compile)
# Catatan: Di beberapa versi Termux, libenet mungkin perlu dikompilasi manual.
# Kita akan mencoba menginstal jika ada, atau script ini harus disesuaikan untuk compile dari source.
echo "[*] Mencoba menginstal libenet..."
pkg install libenet -y || echo "[!] libenet tidak ditemukan di pkg, mungkin perlu build manual atau sudah terinstal via pip build."

# Pastikan pip wheel terinstall untuk compile pyenet
pip install wheel cython

# Export CFLAGS agar pyenet bisa menemukan header libenet di Termux
export CFLAGS="-I/data/data/com.termux/files/usr/include"
export LDFLAGS="-L/data/data/com.termux/files/usr/lib"

# 4. Instal pip packages
echo "[*] Menginstal library Python via pip..."
pip install -r requirements.txt

echo "=== Instalasi Selesai! ==="
echo "Jalankan server dengan perintah: python main.py"
