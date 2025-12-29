#!/bin/bash

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GrowServer Termux Installer ===${NC}"
echo -e "${BLUE}Created by Jules for StileDevs Port${NC}"

# 1. Update Termux
echo -e "${GREEN}[1/7] Mengupdate paket Termux...${NC}"
pkg update -y && pkg upgrade -y

# 2. Install dependencies
echo -e "${GREEN}[2/7] Menginstall dependencies (Node.js, Python, Git, dll)...${NC}"
pkg install nodejs python make clang build-essential git python-pip -y

# 3. Clone Repository
echo -e "${GREEN}[3/7] Cloning GrowServer...${NC}"
if [ -d "GrowServer" ]; then
    echo "GrowServer directory already exists. Skipping clone."
else
    git clone https://github.com/StileDevs/GrowServer.git
fi

cd GrowServer || exit

# 4. Apply Patches
echo -e "${GREEN}[4/7] Applying SQLite & Termux Patches...${NC}"
# Copy patcher script from parent directory
cp ../patcher.js .
# Run patcher
node patcher.js

# 5. Install PNPM
echo -e "${GREEN}[5/7] Menginstall pnpm...${NC}"
npm install -g pnpm

# 6. Install Project Dependencies & Build
echo -e "${GREEN}[6/7] Menginstall project dependencies & Building...${NC}"
pnpm install
pnpm build

# 7. Setup Database
echo -e "${GREEN}[7/7] Menyiapkan database...${NC}"
# Buat folder data jika belum ada
mkdir -p packages/db/data
# Jalankan seed script
pnpm --filter @growserver/db db:seed

echo -e "${BLUE}=== INSTALASI SELESAI ===${NC}"
echo -e "Untuk menjalankan server, ketik:"
echo -e "${GREEN}cd GrowServer/apps/server && pnpm start${NC}"
