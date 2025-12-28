import struct
import os

class ItemsParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.version = 0
        self.item_count = 0
        self.items = []

    def load_items(self):
        """
        Membaca header file items.dat (Versi dan Jumlah Item).
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File {self.filepath} tidak ditemukan.")

        try:
            with open(self.filepath, "rb") as f:
                # Baca Versi (2 bytes, unsigned short, Little Endian)
                data_version = f.read(2)
                if len(data_version) < 2:
                    raise ValueError("File terlalu pendek untuk membaca versi.")

                self.version = struct.unpack("<H", data_version)[0]

                # Baca Jumlah Item (4 bytes, unsigned int, Little Endian)
                data_count = f.read(4)
                if len(data_count) < 4:
                    raise ValueError("File terlalu pendek untuk membaca jumlah item.")

                self.item_count = struct.unpack("<I", data_count)[0]

                print(f"[Info] items.dat loaded. Version: {self.version}, Items: {self.item_count}")

                # TODO: Implementasi loop pembacaan detail item di tahap selanjutnya.
                # Saat ini kita hanya membaca header untuk verifikasi file.
                # Untuk parsing full, kita perlu loop `item_count` kali dan membaca property item.
                # for i in range(self.item_count):
                #     item_id = struct.unpack("<I", f.read(4))[0]
                #     ... (Logic parsing kompleks per versi)

        except Exception as e:
            print(f"[Error] Gagal membaca items.dat: {e}")
            raise e

def load_items(filepath: str):
    parser = ItemsParser(filepath)
    parser.load_items()
    return parser
