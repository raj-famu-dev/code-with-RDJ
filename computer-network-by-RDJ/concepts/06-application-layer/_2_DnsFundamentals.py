# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches DNS: the name hierarchy, record types, the real DNS wire format
(header, question, resource records, name compression pointers) built and parsed
with struct, and an in-memory iterative resolver with a TTL cache.
Syllabus idea: Domain Name System. NO real DNS queries are made; all data is fake
(RFC 5737 documentation addresses 192.0.2.x, 198.51.100.x, 203.0.113.x).
"""
import ipaddress
import struct
from dataclasses import dataclass

TYPES = {"A": 1, "NS": 2, "CNAME": 5, "SOA": 6, "PTR": 12, "MX": 15, "TXT": 16, "AAAA": 28}
TYPE_NAMES = {v: k for k, v in TYPES.items()}
IN = 1

# ===== SECTION 1: THE NAMESPACE HIERARCHY =====
print("===== SECTION 1: THE NAMESPACE HIERARCHY =====")
print("""            . (root)
       +-------+-------+
      com     org     edu   <- top-level domains (TLDs)
       |
    example              <- second-level domain (owned by someone)
    +---+---+
   www  mail  ns1        <- hosts / subdomains
""")
fqdn = "www.example.com."
print("FQDN:", fqdn, "-> labels (right to left = general to specific):",
      list(reversed(fqdn.rstrip(".").split("."))))
print("Limits: label <= 63 bytes, whole name <= 255 bytes on the wire, case-insensitive.")
print("Root servers know where each TLD is; TLD servers know who runs each domain;")
print("the AUTHORITATIVE server for example.com holds the real answers for it.")
print("A stub resolver (your OS) asks a recursive resolver (ISP or public) to do the work.")

# ===== SECTION 2: RECORD TYPES =====
print("\n===== SECTION 2: RECORD TYPES =====")
ROWS = [
    ("A", 1, "name -> IPv4 address", "www.example.com. A 192.0.2.10"),
    ("AAAA", 28, "name -> IPv6 address", "www.example.com. AAAA 2001:db8::10"),
    ("CNAME", 5, "alias -> canonical name", "web.example.com. CNAME www.example.com."),
    ("NS", 2, "zone -> its name server", "example.com. NS ns1.example.com."),
    ("MX", 15, "domain -> mail server + preference", "example.com. MX 10 mail.example.com."),
    ("TXT", 16, "free text (SPF, verification)", 'example.com. TXT "v=spf1 -all"'),
    ("PTR", 12, "IP -> name (reverse lookup)", "10.2.0.192.in-addr.arpa. PTR www.example.com."),
    ("SOA", 6, "zone start of authority", "example.com. SOA ns1 admin 2024010101 ..."),
]
print(f"{'type':<6}{'code':>5}  {'meaning':<36}example")
for t, code, meaning, example in ROWS:
    print(f"{t:<6}{code:>5}  {meaning:<36}{example}")

# ===== SECTION 3: A DNS QUERY ON THE WIRE =====
print("\n===== SECTION 3: A DNS QUERY ON THE WIRE =====")


class Writer:
    """Builds a DNS message, optionally compressing repeated name suffixes."""

    def __init__(self, compress: bool = True) -> None:
        self.buf = bytearray()
        self.seen: dict[str, int] = {}
        self.compress = compress

    def name(self, name: str) -> None:
        labels = [x for x in name.rstrip(".").split(".") if x]
        while labels:
            key = ".".join(labels).lower()
            if self.compress and key in self.seen:
                self.buf += struct.pack("!H", 0xC000 | self.seen[key])  # pointer
                return
            if len(self.buf) < 0x4000:
                self.seen[key] = len(self.buf)
            raw = labels[0].encode("ascii")
            assert 0 < len(raw) <= 63, "label too long"
            self.buf.append(len(raw))
            self.buf += raw
            labels = labels[1:]
        self.buf.append(0)  # root label ends the name


def make_flags(qr: int = 0, opcode: int = 0, aa: int = 0, tc: int = 0,
               rd: int = 1, ra: int = 0, rcode: int = 0) -> int:
    return (qr << 15) | (opcode << 11) | (aa << 10) | (tc << 9) | (rd << 8) | (ra << 7) | rcode


def decode_flags(flags: int) -> dict[str, int]:
    return {"QR": flags >> 15, "Opcode": (flags >> 11) & 0xF, "AA": (flags >> 10) & 1,
            "TC": (flags >> 9) & 1, "RD": (flags >> 8) & 1, "RA": (flags >> 7) & 1,
            "RCODE": flags & 0xF}


def build_query(txid: int, qname: str, qtype: str) -> bytes:
    w = Writer()
    w.buf += struct.pack("!HHHHHH", txid, make_flags(rd=1), 1, 0, 0, 0)
    w.name(qname)
    w.buf += struct.pack("!HH", TYPES[qtype], IN)
    return bytes(w.buf)


def hexdump(data: bytes, width: int = 16) -> None:
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hexes = " ".join(f"{b:02x}" for b in chunk)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {i:04x}  {hexes:<{width * 3}} {text}")


query = build_query(0x1A2B, "example.com", "A")
print(f"query for example.com A, {len(query)} bytes:")
hexdump(query)
print("header (12 bytes): ID=0x1a2b flags=0x0100 (RD=1) QD=1 AN=0 NS=0 AR=0")
print("question: 07 'example' 03 'com' 00 | QTYPE=0001 (A) | QCLASS=0001 (IN)")
assert query[:12] == bytes.fromhex("1a2b 0100 0001 0000 0000 0000".replace(" ", ""))
assert query[12:] == b"\x07example\x03com\x00\x00\x01\x00\x01"
assert len(query) == 12 + 13 + 4
print("check: OK (matches hand-built bytes, 12 + 13 + 4 = 29)")

# ===== SECTION 4: RESPONSE, RECORDS AND NAME COMPRESSION =====
print("\n===== SECTION 4: RESPONSE, RECORDS AND NAME COMPRESSION =====")


@dataclass
class RR:
    name: str
    rtype: str
    ttl: int
    data: object


def write_rr(w: Writer, rr: RR) -> None:
    w.name(rr.name)
    w.buf += struct.pack("!HHI", TYPES[rr.rtype], IN, rr.ttl)
    len_pos = len(w.buf)
    w.buf += b"\x00\x00"                               # RDLENGTH patched below
    start = len(w.buf)
    d = rr.data
    if rr.rtype == "A":
        w.buf += ipaddress.IPv4Address(d).packed
    elif rr.rtype == "AAAA":
        w.buf += ipaddress.IPv6Address(d).packed
    elif rr.rtype in ("NS", "CNAME", "PTR"):
        w.name(d)
    elif rr.rtype == "MX":
        w.buf += struct.pack("!H", d[0])
        w.name(d[1])
    elif rr.rtype == "TXT":
        for piece in d:
            raw = piece.encode()
            w.buf.append(len(raw))
            w.buf += raw
    elif rr.rtype == "SOA":
        mname, rname, *nums = d
        w.name(mname)
        w.name(rname)
        w.buf += struct.pack("!IIIII", *nums)
    struct.pack_into("!H", w.buf, len_pos, len(w.buf) - start)


def build_response(txid: int, qname: str, qtype: str, answers: list[RR],
                   rcode: int = 0, compress: bool = True) -> bytes:
    w = Writer(compress)
    flags = make_flags(qr=1, aa=1, rd=1, ra=1, rcode=rcode)
    w.buf += struct.pack("!HHHHHH", txid, flags, 1, len(answers), 0, 0)
    w.name(qname)
    w.buf += struct.pack("!HH", TYPES[qtype], IN)
    for rr in answers:
        write_rr(w, rr)
    return bytes(w.buf)


answers = [RR("www.example.com", "CNAME", 300, "web.example.com"),
           RR("web.example.com", "A", 300, "192.0.2.10"),
           RR("web.example.com", "A", 300, "192.0.2.11")]
packed = build_response(0x1A2B, "www.example.com", "A", answers)
plain = build_response(0x1A2B, "www.example.com", "A", answers, compress=False)
print(f"response with compression: {len(packed)} bytes; without: {len(plain)} bytes")
hexdump(packed)
print("Look for 'c0 0c': a pointer. Top two bits 11 mean 'pointer', the other 14 bits")
print("are an offset from the start of the message. 0x0c = 12 = right after the header,")
print("i.e. the question name 'www.example.com' is reused instead of repeated.")
assert b"\xc0\x0c" in packed and len(packed) < len(plain)

# ===== SECTION 5: PARSING (INCLUDING COMPRESSION) =====
print("\n===== SECTION 5: PARSING (INCLUDING COMPRESSION) =====")


def read_name(msg: bytes, pos: int) -> tuple[str, int]:
    """Return (name, position after the name in the ORIGINAL stream)."""
    labels: list[str] = []
    end = -1
    jumps = 0
    while True:
        if pos >= len(msg):
            raise ValueError("name runs past end of message")
        length = msg[pos]
        if length & 0xC0 == 0xC0:                      # compression pointer
            if pos + 1 >= len(msg):
                raise ValueError("truncated pointer")
            if end < 0:
                end = pos + 2
            pos = ((length & 0x3F) << 8) | msg[pos + 1]
            jumps += 1
            if jumps > 20:
                raise ValueError("too many compression jumps (pointer loop?)")
            continue
        if length == 0:
            return ".".join(labels), (end if end >= 0 else pos + 1)
        labels.append(msg[pos + 1:pos + 1 + length].decode("ascii"))
        pos += 1 + length


def parse_message(msg: bytes) -> dict:
    txid, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", msg[:12])
    pos = 12
    questions = []
    for _ in range(qd):
        qname, pos = read_name(msg, pos)
        qtype, qclass = struct.unpack("!HH", msg[pos:pos + 4])
        pos += 4
        questions.append((qname, TYPE_NAMES.get(qtype, qtype), qclass))
    records = []
    for _ in range(an + ns + ar):
        name, pos = read_name(msg, pos)
        rtype, rclass, ttl, rdlen = struct.unpack("!HHIH", msg[pos:pos + 10])
        pos += 10
        rd_end = pos + rdlen
        t = TYPE_NAMES.get(rtype, rtype)
        if t == "A":
            data = str(ipaddress.IPv4Address(msg[pos:rd_end]))
        elif t == "AAAA":
            data = str(ipaddress.IPv6Address(msg[pos:rd_end]))
        elif t in ("NS", "CNAME", "PTR"):
            data, _ = read_name(msg, pos)
        elif t == "MX":
            data = (struct.unpack("!H", msg[pos:pos + 2])[0], read_name(msg, pos + 2)[0])
        elif t == "TXT":
            data, p = [], pos
            while p < rd_end:
                data.append(msg[p + 1:p + 1 + msg[p]].decode())
                p += 1 + msg[p]
        elif t == "SOA":
            mname, p = read_name(msg, pos)
            rname, p = read_name(msg, p)
            data = (mname, rname, *struct.unpack("!IIIII", msg[p:p + 20]))
        else:
            data = msg[pos:rd_end]
        records.append(RR(name, t, ttl, data))
        pos = rd_end
    return {"id": txid, "flags": decode_flags(flags), "questions": questions,
            "records": records}


parsed = parse_message(packed)
print("ID:", hex(parsed["id"]), "flags:", parsed["flags"])
print("question:", parsed["questions"])
for rr in parsed["records"]:
    print(f"  {rr.name:<18}{rr.ttl:>5} IN {rr.rtype:<6}{rr.data}")
assert parsed["records"] == answers
assert parse_message(plain)["records"] == answers
print("check: OK (compressed and uncompressed messages parse to identical records)")

print("\nAll record types round-trip through the wire format:")
zoo = [RR("example.com", "NS", 86400, "ns1.example.com"),
       RR("example.com", "MX", 3600, (10, "mail.example.com")),
       RR("example.com", "TXT", 300, ["v=spf1 -all", "hello"]),
       RR("example.com", "SOA", 3600, ("ns1.example.com", "admin.example.com",
                                       2024010101, 7200, 900, 1209600, 300)),
       RR("10.2.0.192.in-addr.arpa", "PTR", 300, "www.example.com"),
       RR("www.example.com", "AAAA", 300, "2001:db8::10")]
msg = build_response(7, "example.com", "NS", zoo)
back = parse_message(msg)["records"]
for rr in back:
    print(f"  {rr.rtype:<6}{rr.data}")
assert back == zoo
print(f"check: OK ({len(zoo)} records, {len(msg)} bytes)")

# ===== SECTION 6: TRAP - A COMPRESSION POINTER LOOP =====
print("\n===== SECTION 6: TRAP - A COMPRESSION POINTER LOOP =====")
evil = bytearray(struct.pack("!HHHHHH", 1, 0x8180, 1, 0, 0, 0))
evil += b"\xc0\x0c" + struct.pack("!HH", 1, 1)  # question name = pointer to itself (offset 12)
print("malformed packet: the name at offset 12 is a pointer to offset 12.")
print("A naive parser follows it forever; ours counts jumps and refuses.")
try:
    parse_message(bytes(evil))
except ValueError as err:
    print("rejected:", err)
print("Real DNS software treats packets from the network as hostile input: bound every loop.")

# ===== SECTION 7: ITERATIVE RESOLUTION OVER A FAKE HIERARCHY =====
print("\n===== SECTION 7: ITERATIVE RESOLUTION OVER A FAKE HIERARCHY =====")
# Each "server" is a dict keyed by its fake IP; nothing touches the network.
ROOT, COM, AUTH = "198.51.100.1", "198.51.100.2", "203.0.113.53"
SERVERS = {
    ROOT: {"role": "root", "delegations": {"com": COM}},
    COM: {"role": "com TLD", "delegations": {"example.com": AUTH}},
    AUTH: {"role": "example.com authoritative",
           "records": {("www.example.com", "A"): ("192.0.2.10", 300),
                       ("mail.example.com", "A"): ("192.0.2.25", 300),
                       ("web.example.com", "CNAME"): ("www.example.com", 300)}},
}


def server_answer(ip: str, qname: str, qtype: str):
    """What one server says: ('answer',..), ('referral', ip, zone) or ('nxdomain',)."""
    srv = SERVERS[ip]
    if "records" in srv:
        if (qname, "CNAME") in srv["records"] and qtype != "CNAME":
            return ("cname", srv["records"][(qname, "CNAME")])
        hit = srv["records"].get((qname, qtype))
        return ("answer", hit) if hit else ("nxdomain",)
    for zone, nxt in srv["delegations"].items():
        if qname == zone or qname.endswith("." + zone):
            return ("referral", nxt, zone)
    return ("nxdomain",)


class Resolver:
    def __init__(self) -> None:
        self.now = 0
        self.answers: dict[tuple[str, str], tuple[str, int]] = {}
        self.delegations: dict[str, tuple[str, int]] = {"": (ROOT, 10 ** 9)}
        self.queries = 0

    def best_start(self, qname: str) -> str:
        best, best_len = ROOT, -1
        for zone, (ip, exp) in self.delegations.items():
            if exp > self.now and len(zone) > best_len and (zone == "" or qname.endswith(zone)):
                best, best_len = ip, len(zone)
        return best

    def resolve(self, qname: str, qtype: str = "A", depth: int = 0) -> str:
        key = (qname, qtype)
        if key in self.answers and self.answers[key][1] > self.now:
            print(f"    cache HIT  {qname} {qtype} -> {self.answers[key][0]}")
            return self.answers[key][0]
        ip = self.best_start(qname)
        while True:
            self.queries += 1
            reply = server_answer(ip, qname, qtype)
            print(f"    ask {ip:<14} ({SERVERS[ip]['role']}): {reply[0]}"
                  + (f" -> {reply[1]}" if reply[0] != "nxdomain" else ""))
            if reply[0] == "referral":
                self.delegations[reply[2]] = (reply[1], self.now + 172800)
                ip = reply[1]
            elif reply[0] == "cname" and depth < 5:
                target, ttl = reply[1]
                self.answers[(qname, "CNAME")] = (target, self.now + ttl)
                return self.resolve(target, qtype, depth + 1)
            elif reply[0] == "answer":
                value, ttl = reply[1]
                self.answers[key] = (value, self.now + ttl)
                return value
            else:
                return "NXDOMAIN"


r = Resolver()
print("1) cold cache: www.example.com A (iterative: resolver walks root -> TLD -> auth)")
before = r.queries
print("   result:", r.resolve("www.example.com"), "| server queries:", r.queries - before)
print("2) same question again at t=10s")
r.now = 10
before = r.queries
print("   result:", r.resolve("www.example.com"), "| server queries:", r.queries - before)
print("3) t=400s: answer TTL (300) expired, delegations (172800) still cached")
r.now = 400
before = r.queries
print("   result:", r.resolve("www.example.com"), "| server queries:", r.queries - before)
print("4) alias: web.example.com A (CNAME is followed)")
before = r.queries
print("   result:", r.resolve("web.example.com"), "| server queries:", r.queries - before)
print("5) a name that does not exist")
before = r.queries
print("   result:", r.resolve("nope.example.com"), "| server queries:", r.queries - before)
assert r.answers[("www.example.com", "A")][0] == "192.0.2.10"
print("Recursive vs iterative: YOUR PC sends 1 recursive query to the resolver and gets")
print("1 final answer; the resolver sends the 3 iterative queries above on your behalf.")
