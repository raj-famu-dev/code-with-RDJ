# Tags: #Python #ComputerNetworks #TransportLayer #TcpHeaderSegments | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP header: every field and its size, flag bits, options (MSS, window scale),
pack/unpack of a real segment with the pseudo-header checksum, sequence numbers as
byte offsets, and the byte-stream-vs-message-boundary trap shown on loopback."""
import ipaddress
import socket
import struct
import threading
import time
from dataclasses import dataclass, field

HOST = "127.0.0.1"


# ===== SECTION 1: HEADER FIELDS AND FLAG BITS =====
print("===== SECTION 1: HEADER FIELDS AND FLAG BITS =====")
FIELDS = [("source port", 16), ("destination port", 16), ("sequence number", 32),
          ("acknowledgment number", 32), ("data offset (header len in 32-bit words)", 4),
          ("reserved", 4), ("flags CWR ECE URG ACK PSH RST SYN FIN", 8),
          ("window size", 16), ("checksum", 16), ("urgent pointer", 16)]
total_bits = sum(b for _, b in FIELDS)
for name, bits in FIELDS:
    print(f"  {name:<42} {bits:>2} bits")
print(f"fixed header = {total_bits} bits = {total_bits // 8} bytes; options add 0..40 bytes")
print("data offset is 4 bits -> max 15 words x 4 = 60 bytes header -> max options = 40 bytes")
assert total_bits // 8 == 20

FLAGS = {"CWR": 0x80, "ECE": 0x40, "URG": 0x20, "ACK": 0x10,
         "PSH": 0x08, "RST": 0x04, "SYN": 0x02, "FIN": 0x01}
print("\nflag bits (one byte):")
for name, bit in FLAGS.items():
    print(f"  {name}  0x{bit:02x}  {bit:08b}")


def flags_to_names(value: int) -> str:
    return "|".join(n for n, b in FLAGS.items() if value & b) or "-"


print("SYN=0x02 ->", flags_to_names(0x02), "; SYN+ACK=0x12 ->", flags_to_names(0x12),
      "; FIN+ACK=0x11 ->", flags_to_names(0x11), "; PSH+ACK=0x18 ->", flags_to_names(0x18))
print("meaning: SYN open/sync seq | ACK ack field valid | FIN sender done | RST abort | PSH deliver now | URG urgent ptr valid")


# ===== SECTION 2: OPTIONS (MSS, WINDOW SCALE) =====
print("\n===== SECTION 2: OPTIONS (MSS, WINDOW SCALE) =====")
OPT_EOL, OPT_NOP, OPT_MSS, OPT_WSCALE, OPT_SACKOK = 0, 1, 2, 3, 4


def build_options(mss: int | None = None, wscale: int | None = None, sack_ok: bool = False) -> bytes:
    out = b""
    if mss is not None:
        out += struct.pack("!BBH", OPT_MSS, 4, mss)  # kind 2, length 4
    if sack_ok:
        out += struct.pack("!BB", OPT_SACKOK, 2)  # kind 4, length 2
    if wscale is not None:
        out += bytes([OPT_NOP]) + struct.pack("!BBB", OPT_WSCALE, 3, wscale)  # NOP aligns it
    while len(out) % 4:
        out += bytes([OPT_NOP])  # pad to a multiple of 4 so data offset is whole words
    return out


def parse_options(raw: bytes) -> list[str]:
    i, found = 0, []
    while i < len(raw):
        kind = raw[i]
        if kind == OPT_EOL:
            break
        if kind == OPT_NOP:
            i += 1
            continue
        length = raw[i + 1]
        body = raw[i + 2:i + length]
        if kind == OPT_MSS:
            found.append(f"MSS={struct.unpack('!H', body)[0]}")
        elif kind == OPT_WSCALE:
            found.append(f"WindowScale={body[0]} (x{2 ** body[0]})")
        elif kind == OPT_SACKOK:
            found.append("SACK-permitted")
        else:
            found.append(f"kind{kind}")
        i += length
    return found


opts = build_options(mss=1460, wscale=7, sack_ok=True)
print("options bytes:", opts.hex(" "), f"({len(opts)} bytes)")
print("parsed       :", parse_options(opts))
print("MSS 1460 = Ethernet MTU 1500 - 20 (IP) - 20 (TCP).  MSS is the max DATA per segment.")
print("Window field is only 16 bits -> max 65535 bytes. Window scale 7 multiplies by 2**7 = 128:")
print("  max scaled window = 65535 x 128 =", 65535 * 128, "bytes (about 8 MB)")
print("Why: on a 100 ms path a 65535-byte window caps throughput at 65535 / 0.1 s =",
      f"{65535 / 0.1 * 8 / 1e6:.2f} Mbit/s, no matter how fast the link is.")


# ===== SECTION 3: PACK AND UNPACK A SEGMENT =====
print("\n===== SECTION 3: PACK AND UNPACK A SEGMENT =====")
TCP_FIXED = struct.Struct("!HHIIBBHHH")


def checksum16(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for (w,) in struct.iter_unpack("!H", data):
        total += w
        total = (total & 0xFFFF) + (total >> 16)
    return total


def pseudo(src: str, dst: str, tcp_len: int) -> bytes:
    return (ipaddress.IPv4Address(src).packed + ipaddress.IPv4Address(dst).packed
            + struct.pack("!BBH", 0, 6, tcp_len))  # protocol 6 = TCP


@dataclass
class Segment:
    sport: int
    dport: int
    seq: int
    ack: int
    flags: int
    window: int
    options: bytes = b""
    data: bytes = b""
    urgent: int = 0
    checksum: int = 0

    def pack(self, src_ip: str, dst_ip: str) -> bytes:
        hdr_len = 20 + len(self.options)
        offset_byte = (hdr_len // 4) << 4  # upper 4 bits: header length in words
        head = TCP_FIXED.pack(self.sport, self.dport, self.seq, self.ack, offset_byte,
                              self.flags, self.window, 0, self.urgent)
        seg = head + self.options + self.data
        ck = ~checksum16(pseudo(src_ip, dst_ip, len(seg)) + seg) & 0xFFFF
        return seg[:16] + struct.pack("!H", ck) + seg[18:]

    @staticmethod
    def unpack(raw: bytes, src_ip: str, dst_ip: str) -> "Segment":
        sp, dp, seq, ack, off, fl, win, ck, urg = TCP_FIXED.unpack(raw[:20])
        hdr_len = (off >> 4) * 4
        ok = checksum16(pseudo(src_ip, dst_ip, len(raw)) + raw) == 0xFFFF
        if not ok:
            raise ValueError("bad TCP checksum")
        return Segment(sp, dp, seq, ack, fl, win, raw[20:hdr_len], raw[hdr_len:], urg, ck)


syn = Segment(sport=49200, dport=80, seq=1000, ack=0, flags=FLAGS["SYN"], window=65535,
              options=build_options(mss=1460, wscale=7, sack_ok=True))
raw = syn.pack("10.0.0.1", "10.0.0.2")
print("SYN segment bytes:", len(raw), "(20 fixed + 12 options + 0 data)")
print("hex:", raw.hex(" "))
off = raw[12] >> 4
print(f"data offset nibble = {off} -> header = {off} x 4 = {off * 4} bytes")
back = Segment.unpack(raw, "10.0.0.1", "10.0.0.2")
print(f"unpacked: {back.sport}->{back.dport} seq={back.seq} ack={back.ack} "
      f"flags={flags_to_names(back.flags)} win={back.window} opts={parse_options(back.options)}")
assert back.seq == 1000 and back.flags == 0x02
print("check: pack/unpack round trip with checksum: OK")
bad = bytearray(raw)
bad[4] ^= 0x01
try:
    Segment.unpack(bytes(bad), "10.0.0.1", "10.0.0.2")
except ValueError as e:
    print("one flipped bit in the sequence number ->", e)
http = Segment(49200, 80, 1001, 5001, FLAGS["PSH"] | FLAGS["ACK"], 64240, data=b"GET / HTTP/1.1\r\n\r\n")
raw2 = http.pack("10.0.0.1", "10.0.0.2")
print(f"data segment: {len(raw2)} bytes total = 20 header + {len(http.data)} data, "
      f"flags {flags_to_names(Segment.unpack(raw2, '10.0.0.1', '10.0.0.2').flags)}")


# ===== SECTION 4: SEQUENCE NUMBERS ARE BYTE OFFSETS =====
print("\n===== SECTION 4: SEQUENCE NUMBERS ARE BYTE OFFSETS =====")
isn, mss, stream = 1000, 1000, 3500
print(f"send {stream} bytes with MSS {mss}; the SYN used up seq {isn}, so data starts at {isn + 1}")
seq = isn + 1
sent_segments = []
remaining = stream
while remaining:
    n = min(mss, remaining)
    sent_segments.append((seq, n))
    seq += n
    remaining -= n
print("  seg   seq     bytes   covers            expected ACK back")
for i, (s, n) in enumerate(sent_segments, 1):
    print(f"  {i:<5} {s:<7} {n:<7} {s}..{s + n - 1:<12}  {s + n}")
print("ACK number = next byte the receiver expects (NOT 'segment number received').")
print("final ACK:", seq, "= ISN + 1 (SYN) +", stream, "bytes: ", isn + 1 + stream)
assert seq == isn + 1 + stream
print("a FIN also consumes one sequence number; a pure ACK consumes none.")
print("32-bit sequence space wraps after 2**32 =", 2 ** 32, "bytes (4 GiB); arithmetic is mod 2**32.")


# ===== SECTION 5: BYTE STREAM, NOT MESSAGES (LOOPBACK TRAP) =====
print("\n===== SECTION 5: BYTE STREAM VS MESSAGE BOUNDARIES (LOOPBACK) =====")
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind((HOST, 0))
srv.listen(1)
srv.settimeout(3)
port = srv.getsockname()[1]
result: dict[str, object] = {}
all_sent = threading.Event()


def receiver() -> None:
    conn, _ = srv.accept()
    conn.settimeout(2)
    all_sent.wait(timeout=3)
    time.sleep(0.2)  # let all three sends land in the receive buffer
    chunks = []
    try:
        while True:
            c = conn.recv(100)
            if not c:
                break
            chunks.append(c)
    except socket.timeout:
        pass
    result["chunks"] = chunks
    conn.close()


th = threading.Thread(target=receiver)
th.start()
cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cli.settimeout(3)
cli.connect((HOST, port))
print("MSS reported by this OS for the loopback connection (a measurement, varies by OS):",
      cli.getsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG))
for m in (b"AAA", b"BBB", b"CCC"):
    cli.sendall(m)
all_sent.set()
th.join(timeout=8)
cli.close()
srv.close()
chunks = result["chunks"]
joined = b"".join(chunks)  # type: ignore[arg-type]
print("sender called send() 3 times: b'AAA', b'BBB', b'CCC'")
print("receiver stream (all chunks joined):", joined)
print("receiver recv() calls that returned data fewer than 3:", len(chunks) < 3,
      "(the OS merged the sends; exact count is timing dependent)")
assert joined == b"AAABBBCCC"
print("TRAP: TCP preserves ORDER and CONTENT, never message boundaries.")
print("FIX: the application adds framing (length prefix or delimiter): see topic 9.")
