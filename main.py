import os
import socket
import ssl
import threading
import struct
import time
from flask import Flask, Response, request
from werkzeug.serving import run_simple
from enet_server import ENetServer, ENET_PROTOCOL_COMMAND_SEND_RELIABLE
import items_manager

# --- KONFIGURASI ---
PORT_LOGIN = 8443
PORT_GAME = 17091
VERSION = "5.39"
ITEMS_DAT = "items.dat"
ITEMS_SAFE = "items_safe.dat"
META_VAL = "131661873"
KLV_KEY = ".audio/mp3/theme4.mp3"

app = Flask(__name__)

# --- 1. OTOMATIS FIX DATABASE ---
def prepare_items_dat():
    """
    Ensures a valid items.dat exists.
    If the provided items.dat is likely Version 24 (large), we generate a safe Version 19 fallback
    to prevent the client from hanging.
    """
    if os.path.exists(ITEMS_DAT):
        size = os.path.getsize(ITEMS_DAT)
        print(f"[*] Found items.dat: {size} bytes.")

        # Heuristic: V24 is usually > 5MB. V19 might be smaller?
        # If it's the large file provided by user, we assume it's V24.
        # User said "Client v5.39 usually expects Version 14-19".
        # We try to use the safe one by default to guarantee login success.

        if not os.path.exists(ITEMS_SAFE):
            print("[*] Generating safe fallback items.dat (V19)...")
            items_manager.create_minimal_items_dat(ITEMS_SAFE)

    else:
        print("[-] items.dat not found! Generating safe fallback.")
        items_manager.create_minimal_items_dat(ITEMS_SAFE)

def get_items_dat_content():
    # Prefer safe version for stability
    target = ITEMS_SAFE if os.path.exists(ITEMS_SAFE) else ITEMS_DAT

    if os.path.exists(target):
        with open(target, "rb") as f:
            print(f"[*] Loading items database from {target}")
            return f.read()
    return b""

# --- 2. LOGIN SERVER (Pemicu UI Login) ---
@app.route('/growtopia/server_data.php', methods=['POST', 'GET'])
def server_data():
    print(f"\n[HTTPS] Request Login! Mengirim pemicu UI v5.39...")

    # Strict key set requested by user
    config = {
        "beta3_type": "1",
        "beta3_maint": "0",
        "fhash": META_VAL,
        "Version": VERSION,
        "klv": KLV_KEY,
        "nls": "1",
        "epp": "1"
    }

    body = "\n".join([f"{k}|{v}" for k, v in config.items()])
    return Response(body, mimetype='text/plain')

# --- 3. GAME SERVER (UDP + ENet) ---
class GrowtopiaServer(ENetServer):
    def __init__(self, port):
        super().__init__(port)
        print(f"[*] Game Server (ENet) Aktif di Port {port}")

    def run(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                events = self.process_packet(data, addr)

                for event in events:
                    if event['type'] == 'packet':
                        self.handle_game_packet(event['peer'], event['data'])

            except BlockingIOError:
                pass
            except Exception as e:
                print(f"[-] UDP Error: {e}")
                # import traceback
                # traceback.print_exc()

    def handle_game_packet(self, peer, data):
        if len(data) < 4: return

        msg_type = struct.unpack("<I", data[:4])[0]

        print(f"[*] Recv Game Packet Type: {msg_type}")

        if msg_type == 2: # NET_MESSAGE_GENERIC_TEXT (Login)
            content = data[4:-1].decode('utf-8', errors='ignore')
            print(f"    Login Data: {content[:50]}...")

            # Send Hello (NET_MESSAGE_SERVER_HELLO)
            response_body = b"action|logon_confirmed\n"
            response_body += b"account_id|1\nuser|1\n"
            response_body += b"token|0\n"

            pkt = struct.pack("<I", 3) + response_body + b"\x00"
            self.send_reliable_packet(peer, pkt)
            print("[+] Sent Logon Confirmed")

            # Send Items Dat
            items_content = get_items_dat_content()
            if items_content:
                # 0x10 = NET_GAME_PACKET_SEND_ITEM_DATABASE_DATA
                # Packet Type 4 (Game Packet)
                # Tank Packet Type 0x10

                tank_header = struct.pack("<I", 0x10) + \
                              struct.pack("<I", 0) + \
                              struct.pack("<I", 0xFFFFFFFF) + \
                              b'\x00' * 40 + \
                              struct.pack("<I", len(items_content))

                full_pkt = struct.pack("<I", 4) + tank_header + items_content

                print(f"[+] Sending items.dat ({len(items_content)} bytes)...")
                self.send_reliable_packet(peer, full_pkt)

if __name__ == "__main__":
    prepare_items_dat()

    # Start UDP Server in separate thread
    udp_server = GrowtopiaServer(PORT_GAME)
    t = threading.Thread(target=udp_server.run)
    t.daemon = True
    t.start()

    # Start HTTPS Server
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.set_ciphers('ALL:@SECLEVEL=0')
    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        context.load_cert_chain("cert.pem", "key.pem")
        run_simple("0.0.0.0", PORT_LOGIN, app, ssl_context=context)
    else:
        print("[-] SSL Certs not found. Login server not started.")
        while True: time.sleep(1)
