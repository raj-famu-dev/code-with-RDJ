# Tags: #Python #ComputerNetworks #TransportLayer #UdpProtocol | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""UDP: the 8-byte header packed/unpacked with struct, the Internet checksum with
the IPv4 pseudo-header computed and verified, a real loopback echo with timeouts,
and the traps (datagram boundaries kept, truncation, no loss/reorder handling)."""
import ipaddress
import random
import socket
import struct
import threading

HOST = "127.0.0.1"


# ===== SECTION 1: THE 8-BYTE UDP HEADER =====
print("===== SECTION 1: THE 8-BYTE UDP HEADER =====")
UDP_HDR = struct.Struct("!HHHH")  # network byte order: 4 unsigned 16-bit fields
print("header size:", UDP_HDR.size, "bytes = 4 fields x 2 bytes")
print("fields: source port | destination port | length (header+data) | checksum")
payload = b"hello"
src_port, dst_port = 54321, 53
length = UDP_HDR.size + len(payload)
hdr = UDP_HDR.pack(src_port, dst_port, length, 0)  # checksum 0 for now
print(f"length = 8 + {len(payload)} = {length}")
print("packed header (hex):", hdr.hex(" "))
print("  54321 = 0x%04x, 53 = 0x%04x, length = 0x%04x" % (src_port, dst_port, length))
sp, dp, ln, ck = UDP_HDR.unpack(hdr)
print("unpacked:", {"src": sp, "dst": dp, "length": ln, "checksum": ck})
assert (sp, dp, ln) == (src_port, dst_port, length)
print("check: pack/unpack round trip: OK")
print("max datagram: length field is 16 bits -> 65535 bytes total, so max payload =",
      65535 - 8, "(IPv4 itself limits it a little more: 65535 - 20 - 8 =", 65535 - 20 - 8, ")")


# ===== SECTION 2: INTERNET CHECKSUM WITH PSEUDO-HEADER =====
print("\n===== SECTION 2: INTERNET CHECKSUM WITH PSEUDO-HEADER =====")


def ones_complement_sum(data: bytes) -> int:
    """16-bit one's-complement sum: add words, fold carries back in."""
    if len(data) % 2:
        data += b"\x00"  # pad odd length with a zero byte (not sent)
    total = 0
    for (word,) in struct.iter_unpack("!H", data):
        total += word
        total = (total & 0xFFFF) + (total >> 16)  # end-around carry
    return total


def internet_checksum(data: bytes) -> int:
    return ~ones_complement_sum(data) & 0xFFFF


# Known textbook vector from RFC 1071 section 3: words 0001 f203 f4f5 f6f7
rfc_words = bytes.fromhex("0001f203f4f5f6f7")
print("RFC 1071 example sum  :", hex(ones_complement_sum(rfc_words)), "(expected 0xddf2)")
print("RFC 1071 example cksum:", hex(internet_checksum(rfc_words)), "(expected 0x220d)")
assert ones_complement_sum(rfc_words) == 0xDDF2 and internet_checksum(rfc_words) == 0x220D
print("check: matches RFC 1071 textbook answer: OK")


def pseudo_header(src_ip: str, dst_ip: str, udp_len: int) -> bytes:
    """IPv4 pseudo-header: src(4) dst(4) zero(1) protocol(1)=17 UDP length(2)."""
    return (ipaddress.IPv4Address(src_ip).packed + ipaddress.IPv4Address(dst_ip).packed
            + struct.pack("!BBH", 0, 17, udp_len))


def udp_checksum(src_ip: str, dst_ip: str, sport: int, dport: int, data: bytes) -> int:
    ln = 8 + len(data)
    segment = UDP_HDR.pack(sport, dport, ln, 0) + data
    ck = internet_checksum(pseudo_header(src_ip, dst_ip, ln) + segment)
    return ck or 0xFFFF  # a computed 0 is sent as all ones (0 means "no checksum")


s_ip, d_ip = "192.168.1.10", "192.168.1.20"
ck = udp_checksum(s_ip, d_ip, 54321, 53, b"hello")
print(f"checksum for {s_ip}:54321 -> {d_ip}:53 payload 'hello': 0x{ck:04x}")
# hand verification of the first words: 192.168 = c0a8, 1.10 = 010a, 192.168 = c0a8, 1.20 = 0114
words = ["c0a8", "010a", "c0a8", "0114", "0011", "000d", "d431", "0035", "000d", "0000", "6865", "6c6c", "6f00"]
manual = 0
for w in words:
    manual += int(w, 16)
    manual = (manual & 0xFFFF) + (manual >> 16)
print("hand sum of 13 words:", f"0x{manual:04x}", "-> complement:", f"0x{~manual & 0xFFFF:04x}")
assert ~manual & 0xFFFF == ck
print("check: hand-computed checksum equals the function: OK")


def verify(src_ip: str, dst_ip: str, segment: bytes) -> bool:
    """Receiver: sum pseudo-header + whole segment INCLUDING the checksum; must be 0xFFFF."""
    return ones_complement_sum(pseudo_header(src_ip, dst_ip, len(segment)) + segment) == 0xFFFF


segment = UDP_HDR.pack(54321, 53, 13, ck) + b"hello"
print("receiver verify (intact):", verify(s_ip, d_ip, segment))
corrupt = bytearray(segment)
corrupt[-1] ^= 0x01  # flip one bit in the payload
print("receiver verify (1 bit flipped):", verify(s_ip, d_ip, bytes(corrupt)))
print("receiver verify (delivered to WRONG dst ip, pseudo-header differs):",
      verify(s_ip, "192.168.1.21", segment))
print("trap: forgetting the pseudo-header still 'works' locally but misses misdelivery:")
no_pseudo = internet_checksum(UDP_HDR.pack(54321, 53, 13, 0) + b"hello")
print(f"  checksum without pseudo-header = 0x{no_pseudo:04x} vs correct 0x{ck:04x} -> different")
print("UDP over IPv4: checksum optional (0 = unused); over IPv6 it is mandatory.")


# ===== SECTION 3: REAL LOOPBACK UDP ECHO =====
print("\n===== SECTION 3: REAL LOOPBACK UDP ECHO (TIMEOUTS) =====")
srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
srv.bind((HOST, 0))
srv.settimeout(0.3)
port = srv.getsockname()[1]
stop = threading.Event()


def echo_server() -> None:
    while not stop.is_set():
        try:
            data, addr = srv.recvfrom(2048)
        except socket.timeout:
            continue
        srv.sendto(data.upper(), addr)


th = threading.Thread(target=echo_server)
th.start()
cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cli.settimeout(2)
for msg in (b"ping", b"udp is simple", b""):
    cli.sendto(msg, (HOST, port))
    reply, _ = cli.recvfrom(2048)
    print(f"sent {msg!r:18} got {reply!r}")
print("note: an EMPTY datagram (b'') is legal in UDP and was delivered as a message.")

# trap A: datagram boundaries are preserved
print("\ntrap A: boundaries are preserved (unlike TCP):")
for m in (b"one", b"two", b"three"):
    cli.sendto(m, (HOST, port))
got = [cli.recvfrom(2048)[0] for _ in range(3)]
print("  3 sends -> 3 separate receives:", got)

# trap B: receive buffer smaller than the datagram silently truncates
print("trap B: recv buffer smaller than the datagram TRUNCATES the rest:")
cli.sendto(b"abcdefghij", (HOST, port))
short, _ = cli.recvfrom(4)
print("  sent 10 bytes, recvfrom(4) returned:", short, "-> the other 6 bytes are gone for good")
print("  fix: always recvfrom(65535) or a size you know is larger than any datagram.")
stop.set()
th.join(timeout=3)
srv.close()

# timeout: nobody listening. On Linux loopback a connected UDP socket may get ICMP refused.
dead = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dead.bind((HOST, 0))
dead_port = dead.getsockname()[1]
dead.close()  # port is now free: nobody listens
cli.settimeout(0.3)
cli.connect((HOST, dead_port))
cli.send(b"anyone?")
try:
    cli.recv(100)
    print("unexpected reply")
except (ConnectionRefusedError, socket.timeout) as e:
    print("send to a port with no listener -> recv raised:", type(e).__name__,
          "(UDP itself never reports it; the OS may relay ICMP port unreachable)")
cli.close()
print("sockets closed, thread joined")


# ===== SECTION 4: LOSS AND REORDERING ARE NOT HANDLED (SEEDED SIMULATION) =====
print("\n===== SECTION 4: LOSS AND REORDERING (SEEDED SIMULATION) =====")
rng = random.Random(42)
sent = [f"pkt{i}" for i in range(10)]
network: list[tuple[float, str]] = []
for i, p in enumerate(sent):
    if rng.random() < 0.3:
        continue  # lost; UDP will never know
    network.append((i + rng.uniform(0, 2.5), p))  # variable delay can reorder
arrived = [p for _, p in sorted(network)]
print("sent    :", sent)
print("arrived :", arrived)
lost = [p for p in sent if p not in arrived]
print("lost    :", lost)
in_order = arrived == sorted(arrived, key=lambda s: int(s[3:]))
print("arrived in original order:", in_order, "-> UDP delivers whatever shows up, as it shows up")
print("If you need reliability over UDP you must add it yourself: sequence numbers, ACKs,")
print("timeouts (this is what QUIC and many game/streaming protocols do).")
print("""
Typical UDP users: DNS (53), DHCP (67/68), NTP (123), TFTP (69), SNMP, VoIP/video
streaming, online games, QUIC (HTTP/3). Reason: low latency, no handshake, small header,
and the application can tolerate or handle loss itself.""")
