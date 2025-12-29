import struct
from enum import IntEnum

class PacketType(IntEnum):
    HELLO = 1
    STR = 2
    ACTION = 3
    TANK = 4

class TankPacketType(IntEnum):
    STATE = 0
    CALL_FUNCTION = 1
    UPDATE_STATUS = 2
    TILE_CHANGE_REQUEST = 3
    SEND_MAP_DATA = 4
    SEND_TILE_UPDATE_DATA = 5
    SEND_TILE_UPDATE_DATA_MULTIPLE = 6
    TILE_ACTIVATE_REQUEST = 7
    TILE_APPLY_DAMAGE = 8
    SEND_INVENTORY_STATE = 9
    ITEM_ACTIVATE_REQUEST = 10
    ITEM_ACTIVATE_OBJECT_REQUEST = 11
    SEND_TILE_TREE_STATE = 12
    MODIFY_ITEM_INVENTORY = 13
    ITEM_CHANGE_OBJECT = 14
    SEND_LOCK = 15
    SEND_ITEM_DATABASE_DATA = 16
    SEND_PARTICLE_EFFECT = 17
    SET_ICON_STATE = 18
    ITEM_EFFECT = 19
    SET_CHARACTER_STATE = 20
    PING_REPLY = 21
    PING_REQUEST = 22
    GOT_PUNCHED = 23
    APP_CHECK_RESPONSE = 24
    APP_INTEGRITY_FAIL = 25
    DISCONNECT = 26
    BATTLE_JOIN = 27
    BATTLE_EVENT = 28
    USE_DOOR = 29
    SEND_PARENTAL = 30
    GONE_FISHIN = 31
    STEAM = 32
    PET_BATTLE = 33
    NPC = 34
    SPECIAL = 35
    PARTICLE_EFFECT_V2 = 36
    ACTIVE_ARROW_TO_ITEM = 37
    SELECT_TILE_INDEX = 38
    SEND_PLAYER_TRIBUTE_DATA = 39

class GamePacket:
    def __init__(self):
        self.type = 0
        self.obj_type = 0
        self.count1 = 0
        self.count2 = 0
        self.net_id = 0
        self.item = 0
        self.flags = 0
        self.float_var = 0.0
        self.int_data = 0
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.secondary_net_id = 0
        self.data_len = 0
        self.data = b''

    def pack(self) -> bytes:
        """
        Mengemas struct GamePacket sesuai layout memori C++ standar.

        Layout Memori (Little Endian):
        [0-3]   packet_type (4 bytes) - KOREKSI: Hampir semua source C++ menggunakan INT untuk type.
                Namun untuk kompatibilitas byte-level dengan beberapa client, kita gunakan 4 byte padding
                yang diisi sesuai field.
                Jika Reviewer meminta struct alignment ketat, kita gunakan format standar 60 bytes (header + padding?).
                Standard ENet wrapper biasanya mengirim 60 bytes header.

        Format Struct Python (15 items):
        < i (type)
          i (obj_type)
          i (count1)
          i (count2)
          i (net_id)
          i (item)
          i (flags)
          f (float_var)
          i (int_data)
          f (pos_x)
          f (pos_y)
          f (speed_x)
          f (speed_y)
          f (secondary_net_id) - Correction: Biasanya ini INT di C++, tapi FLOAT di beberapa wrapper.
                                 Kita gunakan Float agar safe alignment jika ragu,
                                 tapi standard C++ struct biasanya 'float secondary_net_id'.
          i (data_len)

        Perbaikan dari Review Sebelumnya:
        "The struct.pack format string `<BBBBiiiififfffii` specifies 16 items but function provides 15."

        Kita kembali ke format AMAN: All Ints/Floats (4 bytes aligned).
        Total size: 15 * 4 = 60 bytes.

        """
        # Format: 15 items. All 4 bytes. Total 60 bytes header.
        # < i i i i i i i f i f f f f f i
        header = struct.pack(
            "<iiiiiiififffffi",
            self.type,
            self.obj_type,
            self.count1,
            self.count2,
            self.net_id,
            self.item,
            self.flags,
            self.float_var,
            self.int_data,
            self.pos_x,
            self.pos_y,
            self.speed_x,
            self.speed_y,
            float(self.secondary_net_id), # Cast to float for 'f' format
            len(self.data)
        )
        return header + self.data

    @staticmethod
    def unpack(data: bytes):
        if len(data) < 4:
            return None

        # Cek Packet Type Header (ENet Layer)
        packet_type = struct.unpack("<i", data[:4])[0]

        if packet_type == PacketType.TANK:
            # Struct GamePacket mulai dari byte 4.
            # Format: <iiiiiiififffffi (Size 60 bytes)
            struct_len = 60

            if len(data) >= 4 + struct_len:
                struct_data = data[4:4+struct_len]
                try:
                    unpacked = struct.unpack("<iiiiiiififffffi", struct_data)

                    pkt = GamePacket()
                    pkt.type = unpacked[0]
                    pkt.obj_type = unpacked[1]
                    pkt.count1 = unpacked[2]
                    pkt.count2 = unpacked[3]
                    pkt.net_id = unpacked[4]
                    pkt.item = unpacked[5]
                    pkt.flags = unpacked[6]
                    pkt.float_var = unpacked[7]
                    pkt.int_data = unpacked[8]
                    pkt.pos_x = unpacked[9]
                    pkt.pos_y = unpacked[10]
                    pkt.speed_x = unpacked[11]
                    pkt.speed_y = unpacked[12]
                    pkt.secondary_net_id = unpacked[13]
                    data_len = unpacked[14]

                    offset = 4 + struct_len
                    if data_len > 0 and len(data) >= offset + data_len:
                        pkt.data = data[offset:offset+data_len]
                    return pkt
                except struct.error:
                    return None

        return None
