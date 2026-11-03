# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP/IP model (4 and 5 layer views), OSI vs TCP/IP comparison, and real
encapsulation: build Ethernet + IPv4 + TCP headers with struct, compute the real
Internet checksums, parse them back and count overhead bytes.
Implements the 'TCP/IP model and encapsulation' syllabus topic."""
import ipaddress
import socket
import struct
import zlib


# ===== SECTION 1: TCP/IP LAYERS AND OSI COMPARISON =====
print("===== SECTION 1: TCP/IP LAYERS AND OSI COMPARISON =====")
rows = [
    ("Application (4-layer: includes 5,6,7)", "HTTP, DNS, SMTP, TLS", "L7 + L6 + L5"),
    ("Transport", "TCP, UDP", "L4"),
    ("Internet", "IP, ICMP, ARP*", "L3"),
    ("Network access / link (5-layer: Data link + Physical)", "Ethernet, Wi-Fi", "L2 + L1"),
]
print(f"{'TCP/IP layer':<56}{'protocols':<24}{'OSI layers'}")
for r in rows:
    print(f"{r[0]:<56}{r[1]:<24}{r[2]}")
print("* ARP is placed between the link and Internet layers by most books.")
print("4-layer TCP/IP: Application, Transport, Internet, Network access.")
print("5-layer hybrid (most textbooks): Application, Transport, Network, Data link, Physical.")
cmp_rows = [
    ("layers", "7", "4 (or 5)"),
    ("origin", "ISO reference model, theory first", "DARPA/ARPANET, protocols first"),
    ("session + presentation", "separate layers", "merged into application"),
    ("approach", "generic, protocol independent", "built around TCP and IP"),
    ("in real use", "teaching and troubleshooting vocabulary", "what the Internet runs"),
]
print()
print(f"{'':<24}{'OSI':<44}{'TCP/IP'}")
for r in cmp_rows:
    print(f"{r[0]:<24}{r[1]:<44}{r[2]}")


# ===== SECTION 2: REAL HEADER SIZES WITH struct =====
print("\n===== SECTION 2: REAL HEADER SIZES WITH struct =====")
ETH_FMT = "!6s6sH"                 # dst MAC, src MAC, EtherType
IP_FMT = "!BBHHHBBH4s4s"          # ver/ihl, tos, total len, id, flags/frag, ttl, proto, cksum, src, dst
TCP_FMT = "!HHIIHHHH"             # sport, dport, seq, ack, offset/flags, window, cksum, urgent
UDP_FMT = "!HHHH"                 # sport, dport, length, cksum
for name, fmt in [("Ethernet header", ETH_FMT), ("IPv4 header (no options)", IP_FMT),
                  ("TCP header (no options)", TCP_FMT), ("UDP header", UDP_FMT)]:
    print(f"{name:<26} struct '{fmt}' -> {struct.calcsize(fmt)} bytes")
assert [struct.calcsize(f) for f in (ETH_FMT, IP_FMT, TCP_FMT, UDP_FMT)] == [14, 20, 20, 8]
print("Ethernet trailer FCS = 4 bytes (CRC-32). Preamble+SFD (8 bytes) is sent first but is not part of the frame.")
print("check: OK")


# ===== SECTION 3: INTERNET CHECKSUM (RFC 1071) =====
print("\n===== SECTION 3: INTERNET CHECKSUM (RFC 1071) =====")


def inet_checksum(data: bytes) -> int:
    """16-bit one's-complement sum of 16-bit words, then complemented."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


# A widely used textbook header (checksum field zeroed): expected checksum 0xb861.
textbook = bytes.fromhex("45000073000040004011" + "0000" + "c0a80001c0a800c7")
cks = inet_checksum(textbook)
print(f"textbook IPv4 header (checksum zeroed) -> checksum = 0x{cks:04x} (expected 0xb861)")
assert cks == 0xB861
filled = textbook[:10] + struct.pack("!H", cks) + textbook[12:]
print(f"verifying the filled header gives {inet_checksum(filled)} (a valid header sums to 0)")
assert inet_checksum(filled) == 0
# Trap: forgetting to zero the checksum field before computing.
bad = inet_checksum(filled[:10] + struct.pack("!H", 0x1234) + filled[12:])
print(f"Trap: leaving junk 0x1234 in the checksum field gives 0x{bad:04x} (wrong); zero it first.")
assert bad != 0xB861
print("check: OK")


# ===== SECTION 4: BUILD AND PARSE A REAL FRAME =====
print("\n===== SECTION 4: BUILD AND PARSE A REAL FRAME =====")
payload = b"GET /index.html HTTP/1.1\r\nHost: example.test\r\n\r\n"
SRC_IP, DST_IP = "192.168.1.10", "192.168.1.20"
SRC_MAC = bytes.fromhex("0200000000aa")   # locally administered example MACs
DST_MAC = bytes.fromhex("0200000000bb")


def build_tcp(payload: bytes, sport: int, dport: int, seq: int, ack: int, flags: int) -> bytes:
    offset_flags = (5 << 12) | flags                      # data offset = 5 words (20 bytes)
    pseudo = (ipaddress.IPv4Address(SRC_IP).packed + ipaddress.IPv4Address(DST_IP).packed
              + struct.pack("!BBH", 0, 6, 20 + len(payload)))
    hdr0 = struct.pack(TCP_FMT, sport, dport, seq, ack, offset_flags, 65535, 0, 0)
    cks_ = inet_checksum(pseudo + hdr0 + payload)
    return struct.pack(TCP_FMT, sport, dport, seq, ack, offset_flags, 65535, cks_, 0) + payload


def build_ip(segment: bytes, ident: int = 0x1C46) -> bytes:
    total_len = 20 + len(segment)
    hdr0 = struct.pack(IP_FMT, 0x45, 0, total_len, ident, 0x4000, 64, 6, 0,
                       ipaddress.IPv4Address(SRC_IP).packed, ipaddress.IPv4Address(DST_IP).packed)
    cks_ = inet_checksum(hdr0)
    return hdr0[:10] + struct.pack("!H", cks_) + hdr0[12:] + segment


def build_frame(packet: bytes) -> bytes:
    body = struct.pack(ETH_FMT, DST_MAC, SRC_MAC, 0x0800) + packet
    if len(body) < 60:                       # pad so that frame incl. FCS is >= 64 bytes
        body += b"\x00" * (60 - len(body))
    return body + struct.pack("<I", zlib.crc32(body))   # FCS is a CRC-32; stored little-endian in this demo


SYN, ACK, PSH = 0x02, 0x10, 0x08
segment = build_tcp(payload, 51514, 80, seq=1000, ack=2000, flags=ACK | PSH)
packet = build_ip(segment)
frame = build_frame(packet)
print(f"application data   : {len(payload)} bytes")
print(f"+ TCP header (20)  : segment = {len(segment)} bytes")
print(f"+ IPv4 header (20) : packet  = {len(packet)} bytes")
print(f"+ Eth hdr 14 + FCS 4: frame   = {len(frame)} bytes")
print("first 54 bytes (Ethernet+IP+TCP headers) in hex:")
for label, a, b in [("Ethernet", 0, 14), ("IPv4", 14, 34), ("TCP", 34, 54)]:
    print(f"  {label:<9}{frame[a:b].hex(' ')}")

# Parse it back, layer by layer.
dst, src, etype = struct.unpack(ETH_FMT, frame[:14])
vi, tos, tlen, ident, frag, ttl, proto, cks_ip, sip, dip = struct.unpack(IP_FMT, frame[14:34])
sp, dp, seq, ack, off_flags, win, cks_tcp, urg = struct.unpack(TCP_FMT, frame[34:54])
print(f"Ethernet: dst={dst.hex(':')} src={src.hex(':')} type=0x{etype:04x} (IPv4)")
print(f"IPv4    : version={vi >> 4} ihl={vi & 15} total_length={tlen} ttl={ttl} protocol={proto} (TCP) "
      f"src={socket.inet_ntoa(sip)} dst={socket.inet_ntoa(dip)}")
print(f"TCP     : sport={sp} dport={dp} seq={seq} ack={ack} data_offset={off_flags >> 12} words "
      f"flags=0x{off_flags & 0x3F:02x} (ACK+PSH) window={win}")
assert inet_checksum(frame[14:34]) == 0, "IP header checksum must verify"
pseudo = (sip + dip + struct.pack("!BBH", 0, 6, len(segment)))
assert inet_checksum(pseudo + segment) == 0, "TCP checksum must verify"
assert frame[54:54 + len(payload)] == payload
assert struct.unpack("<I", frame[-4:])[0] == zlib.crc32(frame[:-4])
print("IP checksum, TCP checksum (with pseudo-header) and Ethernet FCS all verify; check: OK")


# ===== SECTION 5: OVERHEAD, MTU, MSS AND PADDING =====
print("\n===== SECTION 5: OVERHEAD, MTU, MSS AND PADDING =====")
MTU = 1500
MSS = MTU - 20 - 20
print(f"Ethernet MTU = {MTU} bytes of IP packet; TCP MSS = {MTU} - 20 - 20 = {MSS}; UDP max payload = {MTU - 20 - 8}")
print("Trap: 1500 is the MTU (IP packet size), not the frame size; the frame is 1518 bytes with header and FCS.")
for n in (1, 10, 100, MSS):
    f = build_frame(build_ip(build_tcp(b"x" * n, 1, 2, 0, 0, ACK)))
    print(f"  {n:>5} B of data -> frame {len(f):>4} B  efficiency {n / len(f):6.1%}")
print("A 1-byte message still costs a 64-byte minimum frame (padding added), so efficiency is tiny.")
assert len(build_frame(build_ip(build_tcp(b"x", 1, 2, 0, 0, ACK)))) == 64
assert len(build_frame(build_ip(build_tcp(b"x" * MSS, 1, 2, 0, 0, ACK)))) == 1518

print("\nWorked example: send 3000 bytes over TCP on Ethernet.")
data, segs = 3000, []
left = data
while left:
    take = min(MSS, left)
    segs.append(take)
    left -= take
wire = sum(len(build_frame(build_ip(build_tcp(b"x" * k, 1, 2, 0, 0, ACK)))) for k in segs)
print(f"segments = {segs} -> {len(segs)} frames, {wire} bytes on the wire, overhead = {wire - data} bytes ({(wire - data) / wire:.1%})")
assert segs == [1460, 1460, 80] and wire == 3000 + 3 * 58
print("check: OK")
