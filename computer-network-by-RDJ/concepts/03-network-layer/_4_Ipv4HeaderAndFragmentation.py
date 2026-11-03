# Tags: #Python #ComputerNetworks #NetworkLayer #Ipv4HeaderFragmentation | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""IPv4 header: build and parse with struct, header checksum, TTL, flags
DF/MF, fragment offset (8-byte units), MTU fragmentation and reassembly."""
import ipaddress
import random
import struct
from dataclasses import dataclass


def checksum(data: bytes) -> int:
    """16-bit one's complement sum of 16-bit words, then complemented."""
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


@dataclass
class Ipv4Header:
    ihl: int = 5                 # in 32-bit words
    tos: int = 0
    total_length: int = 20
    ident: int = 0
    df: int = 0
    mf: int = 0
    frag_offset: int = 0         # in 8-byte units
    ttl: int = 64
    proto: int = 6
    src: str = "0.0.0.0"
    dst: str = "0.0.0.0"
    csum: int = 0

    def pack(self, fill_checksum: bool = True) -> bytes:
        flags_frag = (self.df << 14) | (self.mf << 13) | self.frag_offset
        def raw(c: int) -> bytes:
            return struct.pack("!BBHHHBBH4s4s", (4 << 4) | self.ihl, self.tos,
                               self.total_length, self.ident, flags_frag,
                               self.ttl, self.proto, c,
                               ipaddress.IPv4Address(self.src).packed,
                               ipaddress.IPv4Address(self.dst).packed)
        return raw(checksum(raw(0)) if fill_checksum else self.csum)

    @staticmethod
    def parse(b: bytes) -> "Ipv4Header":
        (vi, tos, tl, ident, ff, ttl, proto, cs, s, d) = struct.unpack("!BBHHHBBH4s4s", b[:20])
        assert vi >> 4 == 4, "not IPv4"
        return Ipv4Header(vi & 0xF, tos, tl, ident, (ff >> 14) & 1, (ff >> 13) & 1,
                          ff & 0x1FFF, ttl, proto, str(ipaddress.IPv4Address(s)),
                          str(ipaddress.IPv4Address(d)), cs)


# ===== SECTION 1: HEADER FIELDS =====
print("===== SECTION 1: HEADER FIELDS =====")
FIELDS = [("Version", 4, "always 4"), ("IHL", 4, "header length in 32-bit words (min 5 = 20 B)"),
          ("DSCP/ToS", 8, "service/priority bits"), ("Total Length", 16, "header + data in bytes, max 65535"),
          ("Identification", 16, "same for all fragments of a datagram"), ("Flags", 3, "reserved, DF, MF"),
          ("Fragment Offset", 13, "position in 8-byte units"), ("TTL", 8, "hop limit"),
          ("Protocol", 8, "6 TCP, 17 UDP, 1 ICMP"), ("Header Checksum", 16, "covers header only"),
          ("Source Address", 32, ""), ("Destination Address", 32, "")]
total = 0
for name, bits, note in FIELDS:
    total += bits
    print(f"{name:20} {bits:>3} bits  {note}")
print(f"fixed part = {total} bits = {total // 8} bytes; options add up to 40 more (IHL max 15 -> 60 B)")


# ===== SECTION 2: BUILD, PARSE, CHECKSUM =====
print("\n===== SECTION 2: BUILD, PARSE, CHECKSUM =====")
h = Ipv4Header(total_length=60, ident=0x1C46, df=0, mf=0, ttl=64, proto=6,
               src="172.16.10.99", dst="172.16.10.12")
raw = h.pack()
print("header bytes:", raw.hex(" "))
words = struct.unpack("!10H", raw)
print("16-bit words:", " ".join(f"{w:04x}" for w in words))
back = Ipv4Header.parse(raw)
print("parsed       :", back)
print("checksum field = 0x%04x" % back.csum)
print("verify: sum of all 10 words incl. checksum, folded, complemented =", checksum(raw), "(0 means valid)")
assert checksum(raw) == 0
assert back.src == h.src and back.dst == h.dst and back.ttl == 64
print("check: OK")
known = Ipv4Header(total_length=60, ident=0x1C46, df=1, ttl=64, proto=6,
                   src="172.16.10.99", dst="172.16.10.12").pack()
print("same header with DF=1 -> checksum 0x%04x (the widely published textbook value is 0xb1e6)" % struct.unpack("!H", known[10:12])[0])
assert struct.unpack("!H", known[10:12])[0] == 0xB1E6
corrupt = bytearray(raw)
corrupt[8] ^= 0x01       # flip one bit of TTL
print("after flipping 1 bit of TTL, verify =", checksum(bytes(corrupt)), "(non-zero -> drop)")
assert checksum(bytes(corrupt)) != 0


# ===== SECTION 3: TTL AND ROUTER CHECKSUM UPDATE =====
print("\n===== SECTION 3: TTL DECREMENT AT EACH ROUTER =====")
hdr = Ipv4Header.parse(raw)
for hop in range(1, 4):
    hdr.ttl -= 1
    b = hdr.pack()          # router recomputes the checksum because TTL changed
    assert checksum(b) == 0
    print(f"router {hop}: TTL {hdr.ttl}, new checksum 0x{struct.unpack('!H', b[10:12])[0]:04x}")
print("TTL reaching 0 -> router drops the packet and sends ICMP 'time exceeded' to the source")
print("This stops packets looping forever in a routing loop; traceroute exploits it.")


# ===== SECTION 4: FRAGMENTATION AND REASSEMBLY =====
print("\n===== SECTION 4: FRAGMENTATION AND REASSEMBLY =====")


def fragment(hdr: Ipv4Header, payload: bytes, mtu: int) -> list[tuple[Ipv4Header, bytes]]:
    assert not hdr.df, "DF set: router must drop and send ICMP frag-needed"
    max_data = ((mtu - 20) // 8) * 8        # data per fragment must be a multiple of 8
    out, off = [], 0
    while off < len(payload):
        chunk = payload[off:off + max_data]
        last = off + len(chunk) >= len(payload)
        f = Ipv4Header(total_length=20 + len(chunk), ident=hdr.ident, df=0,
                       mf=0 if last else 1, frag_offset=off // 8, ttl=hdr.ttl,
                       proto=hdr.proto, src=hdr.src, dst=hdr.dst)
        out.append((f, chunk))
        off += len(chunk)
    return out


payload = bytes((i * 7) % 256 for i in range(3980))     # 3980 data + 20 header = 4000
orig = Ipv4Header(total_length=4000, ident=0xBEEF, ttl=60, proto=17, src="10.0.0.1", dst="10.0.5.9")
mtu = 1500
frags = fragment(orig, payload, mtu)
print(f"datagram total {orig.total_length} B (20 header + {len(payload)} data), MTU {mtu}")
print(f"max data per fragment = floor((1500-20)/8)*8 = {((mtu - 20) // 8) * 8}")
print(f"{'frag':>4} {'total len':>9} {'data':>5} {'MF':>2} {'offset field':>12} {'byte start':>10}")
for i, (f, d) in enumerate(frags):
    print(f"{i + 1:>4} {f.total_length:>9} {len(d):>5} {f.mf:>2} {f.frag_offset:>12} {f.frag_offset * 8:>10}")


def reassemble(frs: list[tuple[Ipv4Header, bytes]]) -> bytes:
    frs = sorted(frs, key=lambda t: t[0].frag_offset)
    buf, expect = b"", 0
    for f, d in frs:
        assert f.frag_offset * 8 == expect, "hole"
        buf += d
        expect += len(d)
    assert frs[-1][0].mf == 0
    return buf


random.seed(1)
shuffled = frags[:]
random.shuffle(shuffled)
assert reassemble(shuffled) == payload
print("reassembled from shuffled arrival order == original payload")
print("check: OK")
print("Only the destination reassembles; routers on the path never do.")


# ===== SECTION 5: TRAPS =====
print("\n===== SECTION 5: TRAP - OFFSET NOT DIVIDED BY 8 =====")
print(f"second fragment starts at byte {1480}; correct offset field = 1480/8 = {1480 // 8}")
print(f"WRONG: writing 1480 into the field would mean byte {1480 * 8}.")
print("Offset field is 13 bits -> max 8191 units x 8 B = 65528 bytes of start position.")
print("Fragment data size must be a multiple of 8 (except the last): with MTU 1500 use 1480, not 1479.")
mtu2 = 1000
f2 = fragment(orig, payload, mtu2)
print(f"MTU {mtu2}: data per fragment {((mtu2 - 20) // 8) * 8} (980 rounds DOWN to 976), fragments = {len(f2)}")
print("offsets:", [f.frag_offset for f, _ in f2])
assert all((len(d) % 8 == 0) for _, d in f2[:-1])
print("DF=1 case: ", end="")
try:
    fragment(Ipv4Header(df=1, total_length=4000), payload, 1500)
except AssertionError as e:
    print(e, "(this is how Path MTU discovery works)")
