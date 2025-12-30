import struct
from enum import IntEnum

# Enum Tipe Varian sesuai source C++ (e.g. Proton SDK)
class VariantType(IntEnum):
    NONE = 0
    FLOAT = 1
    STRING = 2
    VECTOR2 = 3
    VECTOR3 = 4
    UINT = 5
    INT = 9

class PacketFactory:
    """
    Factory class untuk membuat packet data binary yang identik dengan struktur C++.
    Fokus pada manipulasi buffer memori menggunakan struct.
    """

    @staticmethod
    def create_variant_list(variants: list) -> bytes:
        """
        Membuat payload Variant List (Call Function).
        Struktur Memory:
        [1 byte] variant_count
        Loop variants:
           [1 byte] index (biasanya 0-5)
           [1 byte] type (VariantType)
           [Value Bytes] (Tergantung Tipe)
        """
        data = bytearray()
        data += struct.pack("B", len(variants))

        for variant in variants:
            v_index = variant.get('index', 0)
            v_type = variant.get('type', 0)
            v_value = variant.get('value')

            # Pack Header Varian: Index + Type
            data += struct.pack("BB", v_index, v_type)

            # Pack Value berdasarkan Type
            if v_type == VariantType.FLOAT:
                data += struct.pack("f", float(v_value))
            elif v_type == VariantType.STRING:
                # String di VariantList: [4 bytes Length] + [Bytes String]
                str_bytes = str(v_value).encode('utf-8')
                data += struct.pack("I", len(str_bytes))
                data += str_bytes
            elif v_type == VariantType.UINT:
                data += struct.pack("I", int(v_value))
            elif v_type == VariantType.INT:
                data += struct.pack("i", int(v_value))
            elif v_type == VariantType.VECTOR2:
                # Asumsi v_value adalah tuple (x, y)
                x, y = v_value
                data += struct.pack("ff", float(x), float(y))
            elif v_type == VariantType.VECTOR3:
                # Asumsi v_value adalah tuple (x, y, z)
                x, y, z = v_value
                data += struct.pack("fff", float(x), float(y), float(z))

        return bytes(data)

    @staticmethod
    def serialize_map_data(world) -> bytes:
        """
        Membuat payload SEND_MAP_DATA (Type 4, Obj 4).
        Mengikuti struktur binary C++:
        [2 bytes] Version
        [2 bytes] Reserved
        [2 bytes] Name Length
        [N bytes] Name String
        [4 bytes] Width
        [4 bytes] Height
        [4 bytes] Tile Count
        [Loop Tiles]
           [2 bytes] Foreground
           [2 bytes] Background
           [2 bytes] Parent Tile (Lock/Sign)
           [2 bytes] Flags
           (Optional extra data based on flags - skipped for skeleton)
        """
        data = bytearray()

        # Header World
        data += struct.pack("<H", 5) # Version (misal 5)
        data += struct.pack("<H", 0) # Reserved

        name_bytes = world.name.encode('utf-8')
        data += struct.pack("<H", len(name_bytes))
        data += name_bytes

        width = world.width
        height = world.height
        tile_count = width * height

        data += struct.pack("<III", width, height, tile_count)

        # Tile Data Loop (Optimasi: Gunakan memoryview atau pre-packed struct jika statis)
        # Untuk skeleton dinamis:
        for y in range(height):
            for x in range(width):
                # Logika Terrain Sederhana
                fg = 0 # Empty
                bg = 0 # Empty

                if y >= height // 2:
                    fg = 2 # Dirt
                    bg = 14 # Cave background
                    if y == height - 1:
                        fg = 8 # Bedrock

                # Border Bedrock
                if x == 0 or x == width - 1:
                    fg = 8

                parent = 0
                flags = 0 # No Flags

                # Pack Tile (8 bytes)
                data += struct.pack("<HHHH", fg, bg, parent, flags)

        return bytes(data)
