import sys
import os

# Tambahkan root project ke PYTHONPATH agar bisa import src
sys.path.append(os.getcwd())

from src.data.items_parser import ItemsParser

def test_parser():
    filepath = "items.dat"
    if not os.path.exists(filepath):
        print(f"[!] File {filepath} tidak ditemukan. Test dibatalkan.")
        sys.exit(1)

    print(f"[*] Mencoba membaca {filepath}...")
    try:
        parser = ItemsParser(filepath)
        parser.load_items()

        print(f"[*] Versi: {parser.version}")
        print(f"[*] Jumlah Item: {parser.item_count}")

        # Validasi sederhana
        # Versi items.dat biasanya > 0
        if parser.version == 0:
            print("[!] Warning: Versi terbaca 0. Mungkin salah format parsing?")

        if parser.item_count == 0:
             print("[!] Warning: Jumlah item 0.")

        print("[+] Items Parser Verified Successfully (Header Read)!")

    except Exception as e:
        print(f"[!] Gagal parsing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_parser()
