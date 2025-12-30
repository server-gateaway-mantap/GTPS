import struct
import time
import socket
import collections

# Constants
ENET_PROTOCOL_MINIMUM_MTU = 576
ENET_PROTOCOL_MAXIMUM_MTU = 4096
ENET_PROTOCOL_MAXIMUM_PACKET_COMMANDS = 32
ENET_PROTOCOL_MINIMUM_WINDOW_SIZE = 4096
ENET_PROTOCOL_MAXIMUM_WINDOW_SIZE = 65536
ENET_PROTOCOL_MINIMUM_CHANNEL_COUNT = 1
ENET_PROTOCOL_MAXIMUM_CHANNEL_COUNT = 255
ENET_PROTOCOL_MAXIMUM_PEER_ID = 0xFFF
ENET_PROTOCOL_MAXIMUM_FRAGMENT_COUNT = 1024 * 1024

ENET_PROTOCOL_COMMAND_NONE = 0
ENET_PROTOCOL_COMMAND_ACKNOWLEDGE = 1
ENET_PROTOCOL_COMMAND_CONNECT = 2
ENET_PROTOCOL_COMMAND_VERIFY_CONNECT = 3
ENET_PROTOCOL_COMMAND_DISCONNECT = 4
ENET_PROTOCOL_COMMAND_PING = 5
ENET_PROTOCOL_COMMAND_SEND_RELIABLE = 6
ENET_PROTOCOL_COMMAND_SEND_UNRELIABLE = 7
ENET_PROTOCOL_COMMAND_SEND_FRAGMENT = 8
ENET_PROTOCOL_COMMAND_SEND_UNSEQUENCED = 9
ENET_PROTOCOL_COMMAND_BANDWIDTH_LIMIT = 10
ENET_PROTOCOL_COMMAND_THROTTLE_CONFIGURE = 11
ENET_PROTOCOL_COMMAND_SEND_UNRELIABLE_FRAGMENT = 12
ENET_PROTOCOL_COMMAND_COUNT = 13

ENET_PROTOCOL_COMMAND_MASK = 0x0F
ENET_PROTOCOL_COMMAND_FLAG_ACKNOWLEDGE = (1 << 7)
ENET_PROTOCOL_COMMAND_FLAG_UNSEQUENCED = (1 << 6)

ENET_PROTOCOL_HEADER_FLAG_COMPRESSED = (1 << 14)
ENET_PROTOCOL_HEADER_FLAG_SENT_TIME = (1 << 15)
ENET_PROTOCOL_HEADER_FLAG_MASK = ENET_PROTOCOL_HEADER_FLAG_COMPRESSED | ENET_PROTOCOL_HEADER_FLAG_SENT_TIME

class ENetPeer:
    def __init__(self, addr, peer_id):
        self.addr = addr
        self.peer_id = peer_id
        self.outgoing_reliable_sequence_number = 1
        self.incoming_reliable_sequence_number = 0
        self.outgoing_unsequenced_group = 0
        self.mtu = 1400  # Default
        self.state = "DISCONNECTED"
        self.connect_id = 0
        self.incoming_session_id = 0
        self.outgoing_session_id = 0

        # Fragmentation
        self.outgoing_fragments = {} # Key: start_sequence_number -> data

    def next_reliable_seq(self):
        seq = self.outgoing_reliable_sequence_number
        self.outgoing_reliable_sequence_number = (seq + 1) & 0xFFFF
        return seq

class ENetServer:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port))
        self.peers = {} # addr -> ENetPeer
        self.peer_counter = 0

    def get_time(self):
        return int(time.time() * 1000) & 0xFFFF

    def send_raw(self, addr, data):
        self.sock.sendto(data, addr)

    def process_packet(self, data, addr):
        if len(data) < 4:
            return []

        # Parse Header
        # PeerID (Big Endian)
        peer_id, sent_time = struct.unpack(">HH", data[:4])

        header_flags = peer_id & ENET_PROTOCOL_HEADER_FLAG_MASK
        peer_id = peer_id & ~(ENET_PROTOCOL_HEADER_FLAG_MASK | (3 << 12))

        offset = 4

        events = []

        while offset < len(data):
            if offset + 4 > len(data): break

            # Command Header
            cmd_type, chan_id, rel_seq = struct.unpack(">BBH", data[offset:offset+4])
            offset += 4

            cmd_raw = cmd_type & ENET_PROTOCOL_COMMAND_MASK
            cmd_flags = cmd_type & ~ENET_PROTOCOL_COMMAND_MASK

            length = 0

            if cmd_raw == ENET_PROTOCOL_COMMAND_CONNECT:
                # 44 bytes payload
                length = 44
                if offset + length > len(data): break

                # Parse Connect
                (out_peer, in_sess, out_sess, mtu, win, chan, in_bw, out_bw, inter, acc, dec, conn_id, data_val) = \
                    struct.unpack(">HBBIIIIIIIIII", data[offset:offset+length])
                offset += length

                # Create Peer
                peer = self.peers.get(addr)
                if not peer:
                    self.peer_counter += 1
                    peer = ENetPeer(addr, self.peer_counter)
                    self.peers[addr] = peer

                peer.state = "CONNECTED"
                peer.connect_id = conn_id
                peer.mtu = min(mtu, ENET_PROTOCOL_MAXIMUM_MTU)
                peer.incoming_session_id = out_sess
                peer.outgoing_session_id = in_sess

                # Send Verify Connect
                self.send_verify_connect(peer)

            elif cmd_raw == ENET_PROTOCOL_COMMAND_SEND_RELIABLE:
                # Payload follows until next command? No, SendReliable struct has dataLength.
                # struct: header(4), dataLength(2)
                if offset + 2 > len(data): break
                data_len = struct.unpack(">H", data[offset:offset+2])[0]
                offset += 2

                payload = data[offset:offset+data_len]
                offset += data_len

                # We should queue Acknowledgement
                peer = self.peers.get(addr)
                if peer:
                     self.send_ack(peer, rel_seq, sent_time)
                     events.append({"type": "packet", "peer": peer, "data": payload})

            elif cmd_raw == ENET_PROTOCOL_COMMAND_PING:
                # Just Ack
                peer = self.peers.get(addr)
                if peer and (cmd_flags & ENET_PROTOCOL_COMMAND_FLAG_ACKNOWLEDGE):
                     self.send_ack(peer, rel_seq, sent_time)
                # No payload

            elif cmd_raw == ENET_PROTOCOL_COMMAND_DISCONNECT:
                 # Remove peer
                 if addr in self.peers:
                     del self.peers[addr]
                 # Payload 4 bytes
                 offset += 4

            elif cmd_raw == ENET_PROTOCOL_COMMAND_SEND_FRAGMENT:
                # header(4) done.
                # startSeq(2), dataLen(2), fragCount(4), fragNum(4), totalLen(4), fragOff(4)
                # Total 20 bytes payload
                if offset + 20 > len(data): break
                (start_seq, data_len, frag_count, frag_num, total_len, frag_off) = \
                    struct.unpack(">HHIIII", data[offset:offset+20])
                offset += 20
                payload = data[offset:offset+data_len]
                offset += data_len

                # Handle Reassembly (Simplistic)
                pass

            else:
                 break

        return events

    def build_header(self, peer, flag_time=True):
        pid = 0xFFFF
        if peer and peer.state == "CONNECTED":
             pass

        t = self.get_time()

        # Flags
        flags = 0
        if flag_time: flags |= ENET_PROTOCOL_HEADER_FLAG_SENT_TIME

        return struct.pack(">HH", pid | flags, t)

    def send_verify_connect(self, peer):
        # Header
        # VerifyConnect: header(4) + 40 bytes

        cmd_header = struct.pack(">BBH",
            ENET_PROTOCOL_COMMAND_VERIFY_CONNECT | ENET_PROTOCOL_COMMAND_FLAG_ACKNOWLEDGE,
            0xFF, # Channel
            peer.next_reliable_seq()
        )

        # Body
        # outgoingPeerID(2), inSess(1), outSess(1), mtu(4), win(4), chan(4), inBand(4), outBand(4), interval(4), acc(4), dec(4), connID(4)
        # Correct format: 9 Integers.

        body = struct.pack(">HBBIIIIIIIII",
            peer.peer_id,
            peer.incoming_session_id,
            peer.outgoing_session_id,
            peer.mtu,
            ENET_PROTOCOL_MAXIMUM_WINDOW_SIZE,
            ENET_PROTOCOL_MINIMUM_CHANNEL_COUNT,
            0, 0, 1000, 0, 0, peer.connect_id
        )

        pkt = self.build_header(peer) + cmd_header + body
        self.send_raw(peer.addr, pkt)

    def send_ack(self, peer, rel_seq, sent_time):
        cmd_header = struct.pack(">BBH",
            ENET_PROTOCOL_COMMAND_ACKNOWLEDGE,
            0,
            0
        )
        # Ack Body: recvRelSeq(2), recvSentTime(2)
        body = struct.pack(">HH", rel_seq, sent_time)

        pkt = self.build_header(peer, flag_time=False) + cmd_header + body
        self.send_raw(peer.addr, pkt)

    def send_reliable_packet(self, peer, data):
        # Check size for fragmentation
        if len(data) > peer.mtu - 100:
            self.send_fragmented_packet(peer, data)
            return

        cmd_header = struct.pack(">BBH",
            ENET_PROTOCOL_COMMAND_SEND_RELIABLE | ENET_PROTOCOL_COMMAND_FLAG_ACKNOWLEDGE,
            0, # Channel 0
            peer.next_reliable_seq()
        )

        length_header = struct.pack(">H", len(data))

        pkt = self.build_header(peer) + cmd_header + length_header + data
        self.send_raw(peer.addr, pkt)

    def send_fragmented_packet(self, peer, data):
        total_len = len(data)
        fragment_size = 1024

        import math
        frag_count = math.ceil(total_len / fragment_size)
        start_seq = peer.next_reliable_seq()

        for i in range(frag_count):
            start = i * fragment_size
            end = min(start + fragment_size, total_len)
            chunk = data[start:end]

            cmd_header = struct.pack(">BBH",
                ENET_PROTOCOL_COMMAND_SEND_FRAGMENT | ENET_PROTOCOL_COMMAND_FLAG_ACKNOWLEDGE,
                0,
                peer.next_reliable_seq()
            )

            body = struct.pack(">HHIIII",
                start_seq,
                len(chunk),
                frag_count,
                i,
                total_len,
                start
            )

            pkt = self.build_header(peer) + cmd_header + body + chunk
            self.send_raw(peer.addr, pkt)
