# Tags: #Python #Networking #Sockets #BinaryProtocolsStruct | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches binary protocol design with the struct module: a tiny packet header,
pack/unpack, endianness, a checksum, and parsing a handcrafted byte string
entirely OFFLINE. No sockets, no packet capture, no network access at all.
"""
import struct
import zlib
from dataclasses import dataclass

print("=== SECTION 1: struct basics ===")
packed = struct.pack(">HB", 513, 7)                 # '>' big-endian, H = 2-byte uint, B = 1-byte uint
print("pack('>HB', 513, 7):", packed, "| hex:", packed.hex(" "))
print("size:", struct.calcsize(">HB"), "bytes")
print("unpack:", struct.unpack(">HB", packed), "<- always returns a TUPLE")
print("format chars: B=1 byte, H=2, I=4, Q=8 (unsigned); b/h/i/q = signed; s = bytes; ? = bool")

print("\n=== SECTION 2: endianness ===")
n = 0x0102
big = struct.pack(">H", n)
little = struct.pack("<H", n)
print("0x0102 big-endian   :", big.hex(" "), "(most significant byte first, 'network order')")
print("0x0102 little-endian:", little.hex(" "))
print("misread big as little:", hex(struct.unpack("<H", big)[0]), "<- TRAP: silently wrong")
print("Native mode '@' adds alignment padding; '=' and '>' do not:")
print("calcsize('@BI') =", struct.calcsize("@BI"), "| calcsize('>BI') =", struct.calcsize(">BI"))
print("(the '@BI' size is platform-dependent: padding is inserted for alignment)")
print("RULE: for wire formats ALWAYS name the byte order explicitly; use '>' for network order.")

print("\n=== SECTION 3: designing a tiny packet ===")
print("""Our made-up protocol 'RDJ1' (header = 12 bytes, big-endian):
  offset size field
   0     2    magic      0xBEEF  (identifies our protocol)
   2     1    version    1
   3     1    msg_type   1=PING 2=DATA 3=BYE
   4     2    seq        sequence number
   6     2    length     payload length in bytes
   8     4    checksum   CRC-32 of the payload
  12     n    payload""")
HEADER_FMT = ">HBBHHI"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
MAGIC = 0xBEEF
print("HEADER_SIZE computed by struct:", HEADER_SIZE)

print("\n=== SECTION 4: pack a packet with a CRC-32 checksum ===")
def build_packet(msg_type: int, seq: int, payload: bytes) -> bytes:
    checksum = zlib.crc32(payload)                  # standard CRC-32, unsigned 32-bit
    header = struct.pack(HEADER_FMT, MAGIC, 1, msg_type, seq, len(payload), checksum)
    return header + payload

pkt = build_packet(2, 42, b"hello")
print("packet hex:", pkt.hex(" "))
print("total length:", len(pkt), "= header", HEADER_SIZE, "+ payload", len(b"hello"))
print("crc32(b'hello') =", hex(zlib.crc32(b"hello")))

print("\n=== SECTION 5: parse a packet (with validation) ===")
class PacketError(ValueError):
    pass

@dataclass(frozen=True)
class Packet:
    version: int
    msg_type: int
    seq: int
    payload: bytes

def parse_packet(data: bytes) -> Packet:
    if len(data) < HEADER_SIZE:
        raise PacketError(f"too short: {len(data)} < {HEADER_SIZE}")
    magic, version, msg_type, seq, length, checksum = struct.unpack_from(HEADER_FMT, data, 0)
    if magic != MAGIC:
        raise PacketError(f"bad magic {magic:#06x}")
    if version != 1:
        raise PacketError(f"unsupported version {version}")
    payload = data[HEADER_SIZE:HEADER_SIZE + length]
    if len(payload) != length:
        raise PacketError(f"truncated payload: expected {length}, got {len(payload)}")
    if zlib.crc32(payload) != checksum:
        raise PacketError("checksum mismatch")
    return Packet(version, msg_type, seq, payload)

print("round trip:", parse_packet(pkt))

print("\n=== SECTION 6: parse a HANDCRAFTED byte string (offline) ===")
handmade = bytes.fromhex("beef 01 02 0007 0003 352441c2") + b"abc"   # typed out by hand
print("bytes:", handmade.hex(" "))
print("parsed:", parse_packet(handmade))
print("Reading it by hand: be ef=magic, 01=version, 02=DATA, 00 07=seq 7, 00 03=len 3,")
print("35 24 41 c2 = CRC-32 of b'abc', then the payload 61 62 63 = 'abc'.")
print("Cross-check with zlib:", hex(zlib.crc32(b"abc")), "== 0x352441c2:", zlib.crc32(b"abc") == 0x352441C2)
guess = bytes.fromhex("beef 01 02 0007 0003 00000000") + b"abc"
try:
    parse_packet(guess)
except PacketError as e:
    print("TRAP: handcrafting with a wrong/zero CRC ->", e)

print("\n=== SECTION 7: validation catches bad input ===")
cases = {
    "empty": b"",
    "short header": pkt[:5],
    "wrong magic": b"\x00\x00" + pkt[2:],
    "truncated payload": pkt[:-2],
    "flipped payload bit": pkt[:-1] + bytes([pkt[-1] ^ 0x01]),
    "wrong version": pkt[:2] + b"\x09" + pkt[3:],
}
for label, bad in cases.items():
    try:
        parse_packet(bad)
        print(f"{label:20} -> accepted (unexpected!)")
    except PacketError as e:
        print(f"{label:20} -> rejected: {e}")
print("CRC-32 detects accidental corruption. It is NOT security: anyone can recompute it.")
print("For tamper-proofing you need a keyed MAC (hmac) or TLS.")

print("\n=== SECTION 8: struct.error and variable-length data ===")
try:
    struct.unpack(">HB", b"\x00")
except struct.error as e:
    print("struct.error:", e)
try:
    struct.pack(">B", 300)
except struct.error as e:
    print("pack overflow ->", type(e).__name__)
name = b"RDJ"
rec = struct.pack(">B", len(name)) + name           # length-prefixed string
(nlen,) = struct.unpack_from(">B", rec, 0)
print("length-prefixed string decoded:", rec[1:1 + nlen].decode("ascii"))
print("fixed-width text with 's':", struct.pack("4s", b"ab"), "<- padded with NUL bytes")
print("iter_unpack over repeated records:",
      list(struct.iter_unpack(">HB", b"\x00\x01\x02\x00\x03\x04")))
