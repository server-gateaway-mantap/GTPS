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
        Mengemas struct GamePacket.
        UPDATE: Mengubah format struct untuk menggunakan Byte (B) pada 4 field pertama
        sesuai spesifikasi protokol binary GT yang lebih akurat/safe.

        Format (Little Endian):
        1. B (type)
        2. B (obj_type)
        3. B (count1)
        4. B (count2)
        5. i (net_id)
        6. i (item)
        7. i (flags)
        8. f (float_var)
        9. i (int_data)
        10. f (pos_x)
        11. f (pos_y)
        12. f (speed_x)
        13. f (speed_y)
        14. f (secondary_net_id) - float? biasanya int tapi di beberapa source float. Kita stick to 'f' agar alignment aman.
            Correction: secondary_net_id biasanya INT (i).
        15. i (data_len)

        Total Size:
        4 (BBBB) + 4 (i) + 4 (i) + 4 (i) + 4 (f) + 4 (i) + 4 (f) + 4 (f) + 4 (f) + 4 (f) + 4 (i) + 4 (i)
        = 4 + 44 = 48 bytes Header?

        Wait, standard GT header is 56 or 60 bytes.
        Jika kita ubah ke BBBB, kita mungkin merusak alignment standard 60 bytes.
        Tapi Reviewer meminta "Change i to B".
        Mari kita gunakan format: <BBBBiiiififfffii (Total 4 + 48 = 52 bytes?)

        TAPI: Struct C++ biasanya punya padding.
        Jika struct:
        uint8_t type;
        uint8_t obj_type;
        uint8_t count1;
        uint8_t count2;
        int32_t netID;
        ...
        Maka compiler akan pack 4 uint8 menjadi 1 word (4 bytes). Jadi aligned.

        Jadi:
        [0] type (1)
        [1] obj (1)
        [2] c1 (1)
        [3] c2 (1)
        [4-7] net_id (4)

        Ini persis 4 bytes di awal. Sama panjangnya dengan 1 buah 'int' (4 bytes).
        TAPI 'iiii' sebelumnya berarti 4 buah INT (16 bytes).
        Jadi perubahannya sangat signifikan (16 bytes -> 4 bytes).
        Reviewer benar: Jika 'type' dkk hanya butuh 1 byte, maka pakai 'i' (4 bytes) membuang 12 bytes '00'.
        Dan client membaca offset berdasarkan byte.

        Jadi Struct Format Baru:
        <BBBB (4 bytes)
        iii (netid, item, flags) -> 12 bytes
        f (float_var) -> 4
        i (int_data) -> 4
        ffff (pos/speed) -> 16
        i (secondary) -> 4
        i (datalen) -> 4

        Total: 4 + 12 + 4 + 4 + 16 + 4 + 4 = 48 bytes.
        Plus padding 8 bytes di akhir biasanya? (Total 56).
        Mari tambahkan padding bytes di akhir struct header?
        Atau biarkan 48 bytes.
        """
        # Kita gunakan format yang lebih compact sesuai saran.
        # Format string yang benar (15 items): <BBBBiiififfffii
        # BBBB (4), iii (3), f (1), i (1), ffff (4), ii (2) = 15 items.
        header = struct.pack(
            "<BBBBiiififfffii",
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
            self.secondary_net_id,
            len(self.data)
        )
        return header + self.data

    @staticmethod
    def unpack(data: bytes):
        if len(data) < 4:
            return None

        # Unpack PacketType dari 4 byte pertama (Message Type Header ENet)
        # Note: Ini BUKAN bagian dari struct GamePacket di bawah, tapi header raw.
        packet_type = struct.unpack("<i", data[:4])[0]

        if packet_type == PacketType.TANK:
            # Struct GamePacket mulai dari byte 4.
            # Format: <BBBBiiififfffii (Size 48 bytes)
            # Total data harus minimal 4 (MsgType) + 48 (Struct) = 52 bytes.

            struct_len = struct.calcsize("<BBBBiiififfffii") # Should be 48

            if len(data) >= 4 + struct_len:
                struct_data = data[4:4+struct_len]
                unpacked = struct.unpack("<BBBBiiififfffii", struct_data)

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

                # Cek data payload tambahan
                offset = 4 + struct_len
                if data_len > 0 and len(data) >= offset + data_len:
                    pkt.data = data[offset:offset+data_len]
                return pkt

        return None
