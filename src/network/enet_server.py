import enet
import asyncio
import logging
from src.network.protocol import PacketType, GamePacket, TankPacketType
from src.utils.encryption import PacketUtils
from src.utils.packet_factory import PacketFactory, VariantType
from src.data.database import Database
from src.core.player import Player
from src.core.world_manager import WorldManager

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENetServer")

class ENetServer:
    def __init__(self, host_ip="0.0.0.0", port=17091, max_peers=100):
        # Database & World
        self.db = Database()
        self.world_manager = WorldManager()
        self.players = {} # Key: peer.connectID (atau ptr), Value: Player Object

        # ENetwrapper (pyenet) expects bytes for the address, not str
        host_ip_bytes = host_ip.encode('utf-8')
        self.address = enet.Address(host_ip_bytes, port)
        self.host = enet.Host(self.address, max_peers, 2, 0, 0) # 2 channels, no bandwidth limit
        self.running = False

    def handle_connect(self, event):
        logger.info(f"Client connected: {event.peer.address}")

    def handle_disconnect(self, event):
        logger.info(f"Client disconnected: {event.peer.address}")
        # Save player data
        pid = event.peer.connectID
        if pid in self.players:
            p = self.players[pid]
            logger.info(f"Saving data for {p.name}...")
            self.db.save_player(p.name, p.pos_x, p.pos_y, p.current_world, p.inventory)
            del self.players[pid]

    def handle_receive(self, event):
        try:
            packet_data = event.packet.data
            if len(packet_data) < 4:
                return

            # Baca tipe pesan (4 bytes int) - INI TIDAK TERENKRIPSI
            msg_type = int.from_bytes(packet_data[:4], byteorder='little')

            # Payload encryption check
            # Hanya payload (data[4:]) yang dienkripsi untuk tipe tertentu (biasanya Text/Game)
            # Tipe Hello (1) biasanya plain.

            # Jika tipe butuh dekripsi, kita proses payloadnya.
            # Untuk simplifikasi skeleton ini, kita asumsikan Type 2, 3, 4 terenkripsi.
            if msg_type in [PacketType.STR, PacketType.ACTION, PacketType.TANK]:
                 payload = packet_data[4:]
                 decrypted_payload = PacketUtils.xor_cipher(payload, key=12345)
                 # Reconstruct packet data yang "bersih"
                 packet_data = packet_data[:4] + decrypted_payload

            logger.info(f"Received packet type {msg_type} from {event.peer.address}")

            if msg_type == PacketType.HELLO: # Hello Packet (Client discovery)
                logger.info("Handling Hello packet")
                # Balas dengan Hello
                self.send_hello(event.peer)

            elif msg_type == PacketType.STR: # Generic Text (Logon biasanya)
                # Text ada di byte ke-4 sampai akhir
                text_data = packet_data[4:].decode('utf-8', errors='ignore').strip()
                logger.info(f"Generic Text received: {text_data}")

                if "requestedName" in text_data:
                    logger.info("Logon packet detected!")
                    self.handle_logon(event.peer, text_data)
                elif "action|join_request" in text_data:
                    self.handle_join_request(event.peer, text_data)
                elif "action|input" in text_data: # Chat
                    self.handle_chat(event.peer, text_data)

            elif msg_type == PacketType.TANK: # Game Packet
                logger.info("Game/Tank packet received")
                # Implementasi parsing Tank Packet di masa depan

        except Exception as e:
            logger.error(f"Error handling packet: {e}")

    def send_hello(self, peer):
        """Mengirim paket Hello balik ke client."""
        # Tipe 1 (Hello)
        msg = (1).to_bytes(4, byteorder='little')

        # Enkripsi Hello? Biasanya Hello packet plain text atau simple structure.
        # Tapi jika kita menerapkan policy "Standard Encryption from Start",
        # kita coba encrypt. Namun hello packet ENet (discovery) biasanya open.
        # Kita biarkan Hello plain untuk handshake awal.

        packet = enet.Packet(msg, enet.PACKET_FLAG_RELIABLE)
        peer.send(0, packet)

    def handle_logon(self, peer, text_data):
        """
        Menangani logika login.
        Parse data login, load/create di DB, dan init session.
        """
        # Parse text_data sederhana (format: key|val\nkey|val...)
        login_info = {}
        for line in text_data.split('\n'):
            if '|' in line:
                k, v = line.split('|', 1)
                login_info[k] = v

        username = login_info.get('requestedName', 'Guest')
        password = login_info.get('tankIDPass', '')

        # DB Operations
        player_data = self.db.get_player(username)
        if not player_data:
            logger.info(f"Creating new player: {username}")
            self.db.create_player(username, password)
            player_data = (username, password, 0, 0, 'EXIT', '[]')

        # Create Player Object
        player = Player(peer.connectID, username)
        player.peer = peer # Simpan referensi peer untuk komunikasi
        player.load_from_db_data(player_data)

        # Simpan di memori session
        self.players[peer.connectID] = player
        logger.info(f"Player {username} logged in. World: {player.current_world}")

        logger.info("Sending OnSuperMainStart response...")

        # 1. Buat TankPacket dengan tipe CALL_FUNCTION (Variant List)
        packet = GamePacket()
        # FIELD packet.type HARUS TankPacketType (State/Call/etc), BUKAN MessageType
        packet.type = TankPacketType.CALL_FUNCTION
        packet.obj_type = 0 # Biasanya 0 atau mengikuti konteks
        packet.net_id = -1 # System
        packet.flags = 8 # Flag umum untuk variant list (Extended)

        # 2. Buat Variant List: "OnSuperMainStart", "items.dat hash", "uda", "start string", "guest name", ...
        # Untuk skeleton ini, kita kirim variant minimalis agar client accept.
        # [0] String: "OnSuperMainStart"
        # [1] Int: items.dat hash (dummy)
        # [2] String: UDA URL (dummy)
        # [3] String: Start Message
        # [4] String: Guest Name
        # [5] Int: Type

        variants = [
            {'index': 0, 'type': VariantType.STRING, 'value': "OnSuperMainStart"},
            {'index': 1, 'type': VariantType.UINT, 'value': 12345}, # Items Hash Dummy
            {'index': 2, 'type': VariantType.STRING, 'value': "uda_url_dummy"},
            {'index': 3, 'type': VariantType.STRING, 'value': "Welcome to GTPS Python Termux!"},
            {'index': 4, 'type': VariantType.STRING, 'value': "Guest"},
            {'index': 5, 'type': VariantType.UINT, 'value': 0},
        ]

        packet.data = PacketFactory.create_variant_list(variants)

        # 3. Pack dan kirim (Tipe 4 + Struct)
        payload = packet.pack()

        # Enkripsi Payload
        encrypted_payload = PacketUtils.xor_cipher(payload, key=12345)

        # Prepend Message Type Header (Type 4 = TANK)
        # Client butuh [Type:4] + [Encrypted Struct]
        msg_type_header = (4).to_bytes(4, 'little')
        final_packet_data = msg_type_header + encrypted_payload

        enet_packet = enet.Packet(final_packet_data, enet.PACKET_FLAG_RELIABLE)
        peer.send(0, enet_packet)
        logger.info("OnSuperMainStart sent!")

    def handle_join_request(self, peer, text_data):
        """
        Menangani request masuk world.
        Format: action|join_request\nname|WORLDNAME\n...
        """
        # Parse world name
        world_name = "EXIT"
        for line in text_data.split('\n'):
            if line.startswith("name|"):
                world_name = line.split("|")[1]

        logger.info(f"Player requesting join to: {world_name}")

        # Get/Generate World
        world = self.world_manager.get_world(world_name)

        # Update Player Session
        if peer.connectID in self.players:
            self.players[peer.connectID].current_world = world_name

        # 1. Kirim OnSetPos (Spawn Position) - Variant List
        # Spawn di tengah world (roughly)
        spawn_x = (world.width // 2) * 32.0 # Tile size 32
        spawn_y = (world.height // 2) * 32.0

        # Kirim OnSetPos: [0] "OnSetPos", [1] (NetID, x, y) ?
        # Biasa client set local pos via packet khusus atau variant.
        # Kita kirim variant OnSetPos: [0]: "OnSetPos", [1]: (NetID, local player), [2]: x, [3]: y
        # Tapi lebih stabil kirim TankPacket STATE update jika sudah in-world.
        # Untuk transisi world, client mengharapkan SEND_MAP_DATA.

        # Kirim SEND_MAP_DATA (Packet Type 4, Obj Type 4)
        map_payload = PacketFactory.serialize_map_data(world)

        # Buat Map Data Packet
        # Map data dikirim sebagai Tank Packet Type 4 (SEND_MAP_DATA)

        packet = GamePacket()
        packet.type = TankPacketType.SEND_MAP_DATA # Fix: Use TankPacketType
        packet.obj_type = 0
        packet.net_id = -1
        packet.data = map_payload
        # Flags? Usually 0 or extended

        # Note: Map data packet structure might need specific flags or layout
        # But for skeleton we try standard tank packet wrapper.

        payload = packet.pack()

        # ENCRYPT OUTGOING?
        # Jika client butuh enkripsi untuk baca map, kita harus encrypt payload ini.
        # payload = PacketUtils.xor_cipher(payload, key=12345)
        # Tapi ENet layer encrypts?
        # User bilang "Implement encryption since client won't read otherwise".
        # Jadi kita encrypt RAW payload sebelum kirim.

        # Encrypt Raw
        encrypted_payload = PacketUtils.xor_cipher(payload, key=12345)

        # Prepend Message Type Header (Type 4)
        msg_type_header = (4).to_bytes(4, 'little')
        final_data = msg_type_header + encrypted_payload

        peer.send(0, enet.Packet(final_data, enet.PACKET_FLAG_RELIABLE))
        logger.info(f"Map Data sent to {peer.connectID} (Size: {len(payload)} bytes)")

        self.send_log(peer, f"Joining world {world_name}...")

        # Kirim OnSpawn (Posisi)
        # Kita perlu kirim posisi valid setelah map terload.
        # Gunakan Variant List 'OnSetPos'
        variants = [
            {'index': 0, 'type': VariantType.STRING, 'value': "OnSetPos"},
            {'index': 1, 'type': VariantType.FLOAT, 'value': (world.width // 2 * 32.0)}, # X
            {'index': 2, 'type': VariantType.FLOAT, 'value': (world.height // 2 * 32.0)}, # Y
        ]
        pos_packet = GamePacket()
        pos_packet.type = TankPacketType.CALL_FUNCTION # Fix type
        pos_packet.obj_type = 0
        pos_packet.net_id = -1
        pos_packet.flags = 8
        pos_packet.data = PacketFactory.create_variant_list(variants)

        # Encrypt & Send Position
        pos_payload = PacketUtils.xor_cipher(pos_packet.pack(), key=12345)
        # Prepend Header
        final_pos = (4).to_bytes(4, 'little') + pos_payload

        peer.send(0, enet.Packet(final_pos, enet.PACKET_FLAG_RELIABLE))

    def send_log(self, peer, message):
        """Helper untuk kirim pesan console game (OnConsoleMessage)."""
        variants = [
            {'index': 0, 'type': VariantType.STRING, 'value': "OnConsoleMessage"},
            {'index': 1, 'type': VariantType.STRING, 'value': message}
        ]
        packet = GamePacket()
        packet.type = TankPacketType.CALL_FUNCTION # Fix type
        packet.obj_type = 0
        packet.net_id = -1
        packet.flags = 8
        packet.data = PacketFactory.create_variant_list(variants)

        # Pack
        payload = packet.pack()
        # Encrypt
        enc_payload = PacketUtils.xor_cipher(payload, key=12345)
        # Header
        final_data = (4).to_bytes(4, 'little') + enc_payload

        peer.send(0, enet.Packet(final_data, enet.PACKET_FLAG_RELIABLE))

    def handle_chat(self, peer, text_data):
        """
        Menangani chat.
        Format: action|input\ntext|PESAN
        """
        message = ""
        for line in text_data.split('\n'):
            if line.startswith("text|"):
                message = line.split("|", 1)[1]

        if not message:
            return

        # Dapatkan info pengirim
        sender_name = "Guest"
        sender_world = "EXIT"
        if peer.connectID in self.players:
            p = self.players[peer.connectID]
            sender_name = p.name
            sender_world = p.current_world

        full_msg = f"<{sender_name}> {message}"
        logger.info(f"[Chat] {full_msg}")

        # Broadcast ke semua player di world yang sama
        # Format chat bubble: action|log (atau OnConsoleMessage untuk log, OnTalkBubble untuk bubble)
        # Kita pakai OnConsoleMessage dulu untuk skeleton.

        # Update referensi peer jika belum ada (safety)
        if peer.connectID in self.players:
             self.players[peer.connectID].peer = peer

        for pid, p in self.players.items():
            if p.current_world == sender_world and hasattr(p, 'peer') and p.peer:
                try:
                    self.send_log(p.peer, full_msg)
                except Exception as e:
                    logger.error(f"Failed to send chat to {p.name}: {e}")

    async def start(self):
        self.running = True
        logger.info(f"ENet Server started on {self.address}")

        while self.running:
            # Service loop
            event = self.host.service(0)

            if event.type == enet.EVENT_TYPE_CONNECT:
                self.handle_connect(event)
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self.handle_disconnect(event)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self.handle_receive(event)

            # Optimasi Termux: Sleep 10ms (100 ticks/sec) untuk hemat baterai
            await asyncio.sleep(0.01)

    def stop(self):
        self.running = False
