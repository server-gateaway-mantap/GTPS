import struct

class PacketUtils:
    @staticmethod
    def pack_variant_list(variant_list: list) -> bytes:
        """
        Mengemas list of variants menjadi bytearray untuk dikirim dalam TankPacket.
        Struktur Variant List sederhana:
        [byte index] [byte type] [value...]
        """
        data = bytearray()
        data += struct.pack("B", len(variant_list)) # Total variants count

        for variant in variant_list:
            v_index = variant.get('index', 0)
            v_type = variant.get('type', 0)
            v_value = variant.get('value')

            data += struct.pack("BB", v_index, v_type)

            if v_type == 1: # Float
                data += struct.pack("f", float(v_value))
            elif v_type == 2: # String
                str_bytes = str(v_value).encode('utf-8')
                data += struct.pack("I", len(str_bytes)) # String length
                data += str_bytes
            elif v_type == 5: # UInt
                data += struct.pack("I", int(v_value))
            elif v_type == 9: # Int
                data += struct.pack("i", int(v_value))

        return bytes(data)

    @staticmethod
    def create_text_packet(text: str) -> bytes:
        """Membuat raw data untuk Generic Text Packet (Type 2/3)."""
        return text.encode('utf-8') + b'\x00'

    @staticmethod
    def xor_cipher(data: bytes, key: int = 0) -> bytes:
        """
        Melakukan operasi XOR pada data packet.
        """
        key_bytes = key.to_bytes(4, 'little')
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = data[i] ^ key_bytes[i % 4]

        return bytes(result)

    @staticmethod
    def create_map_data(world) -> bytes:
        """
        Membuat payload untuk packet SEND_MAP_DATA (Type 4, Obj 4).
        Format Simplified (Minimalis agar client masuk):
        [Version: 2 bytes] [Reserved: 2 bytes] -> 4 bytes
        [NameLen: 2 bytes] [Name: NameLen bytes]
        [Width: 4 bytes] [Height: 4 bytes]
        [TileCount: 4 bytes]
        [Tiles Data...]

        Tile Data Structure (Simple, ver 0):
        [Foreground: 2 bytes] [Background: 2 bytes] [Parent: 2 bytes] [Flags: 2 bytes]
        """
        data = bytearray()

        # Version (misal 5)
        data += struct.pack("<H", 5)
        data += struct.pack("<H", 0) # Reserved

        # World Name
        name_bytes = world.name.encode('utf-8')
        data += struct.pack("<H", len(name_bytes))
        data += name_bytes

        # Width, Height, TileCount
        data += struct.pack("<III", world.width, world.height, world.width * world.height)

        # Tiles Loop
        # Untuk skeleton, kita isi tile kosong (0) dan bedrock (8) di pinggir?
        # Atau simple flat world:
        # Row 0-Height/2: Empty (0)
        # Row Height/2: Dirt (2)
        # Row > Height/2: Dirt/Bedrock

        # Agar payload kecil dan cepat, kita loop sederhana.
        # Tile Structure (Standard GT): int fg, int bg, int parent, int flags?
        # Tergantung versi map. Versi 5 cukup simple.
        # [FG:2][BG:2][Parent:2][Flags:2] = 8 bytes per tile.

        for y in range(world.height):
            for x in range(world.width):
                fg = 0
                bg = 0

                # Logic Simple World Gen
                if y >= world.height // 2:
                    fg = 2 # Dirt
                    if y == world.height - 1:
                        fg = 8 # Bedrock

                # Border bedrock
                if x == 0 or x == world.width - 1:
                    fg = 8

                parent = 0
                flags = 0

                data += struct.pack("<HHHH", fg, bg, parent, flags)

        return bytes(data)
