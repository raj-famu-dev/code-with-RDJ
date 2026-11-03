# Tags: #Python #ComputerNetworks #DataLinkLayer #HdlcPppArp | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""HDLC, PPP and ARP: HDLC frame with bit stuffing and a 16-bit FCS, PPP framing
(byte stuffing), phases, PAP vs CHAP, and ARP request/reply packed with struct
plus an in-memory ARP cache with timeout. RARP, proxy ARP and gratuitous ARP
are shown as variations. Implements the 'Data link protocols' and ARP parts of
the Data Link chapter. In-memory only; no real network traffic."""
import hashlib
import struct

# ===== SECTION 1: HDLC FRAME =====
print("===== SECTION 1: HDLC FRAME =====")
print("| Flag 01111110 | Address 8 | Control 8 | Information | FCS 16 | Flag 01111110 |")
print("Control field (bits in transmission order, bit 1 first):")
print("  I-frame (data)        : 0 | N(S) 3 | P/F 1 | N(R) 3")
print("  S-frame (supervisory) : 1 0 | type 2 (RR, RNR, REJ, SREJ) | P/F | N(R) 3")
print("  U-frame (unnumbered)  : 1 1 | type 2 | P/F | type 3 (SABM, UA, DISC...)")


def i_control(ns: int, nr: int, pf: int = 0) -> str:
    return "0" + format(ns, "03b")[::-1] + str(pf) + format(nr, "03b")[::-1]


def frame_kind(ctrl: str) -> str:
    return "I" if ctrl[0] == "0" else ("S" if ctrl[1] == "0" else "U")


ctrl = i_control(ns=2, nr=5, pf=1)
print(f"I-frame N(S)=2 N(R)=5 P/F=1 -> control bits {ctrl}, kind {frame_kind(ctrl)}")
print("3-bit sequence numbers -> window up to 7 (modulo 8), 7 bits is the extended mode.")

# ===== SECTION 2: HDLC BUILD, STUFF, VERIFY =====
print("\n===== SECTION 2: HDLC BUILD, BIT STUFFING, FCS =====")


def crc16_x25(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8408 if crc & 1 else crc >> 1
    return crc ^ 0xFFFF


assert crc16_x25(b"123456789") == 0x906E
print("CRC-16/X.25 (the HDLC FCS) of '123456789' = 906e: check: OK")


def to_bits(data: bytes) -> str:  # HDLC sends each byte least significant bit first
    return "".join(format(b, "08b")[::-1] for b in data)


def from_bits(bits: str) -> bytes:
    return bytes(int(bits[i:i + 8][::-1], 2) for i in range(0, len(bits), 8))


def stuff(bits: str) -> str:
    out, ones = [], 0
    for b in bits:
        out.append(b)
        ones = ones + 1 if b == "1" else 0
        if ones == 5:
            out.append("0")
            ones = 0
    return "".join(out)


def unstuff(bits: str) -> str:
    out, ones, i = [], 0, 0
    while i < len(bits):
        out.append(bits[i])
        ones = ones + 1 if bits[i] == "1" else 0
        if ones == 5:
            i += 1
            ones = 0
        i += 1
    return "".join(out)


FLAG = "01111110"
address = 0xFF  # all-stations address
control = int(ctrl[::-1], 2)  # bit 1 (first sent) is the least significant bit
info = b"\x7e\xff\x3f"  # data deliberately full of 1s and containing the flag byte
body = bytes([address, control]) + info
fcs = crc16_x25(body)
body += struct.pack("<H", fcs)
wire = FLAG + stuff(to_bits(body)) + FLAG
print("address 0xff, control", f"0x{control:02x}", "info", info.hex(" "), "FCS", f"{fcs:04x}")
print("raw bits    :", to_bits(body))
print("stuffed bits:", stuff(to_bits(body)))
print("flag only at the two ends?", wire.count(FLAG) == 2)
inner = unstuff(wire[8:-8])
got = from_bits(inner)
ok = crc16_x25(got[:-2]) == struct.unpack("<H", got[-2:])[0]
print("receiver: unstuffed", got.hex(" "), "FCS ok =", ok)
assert got == body and ok and wire.count(FLAG) == 2
print("HDLC round-trip: check: OK")

# ===== SECTION 3: PPP FRAME AND BYTE STUFFING =====
print("\n===== SECTION 3: PPP FRAME =====")
print("| Flag 7E | Address FF | Control 03 | Protocol 2 | Payload | FCS 2 | Flag 7E |")
PROTO = {0x0021: "IPv4", 0xC021: "LCP", 0x8021: "IPCP", 0xC023: "PAP", 0xC223: "CHAP"}
for k, v in PROTO.items():
    print(f"  protocol 0x{k:04x} = {v}")
ESC, FL = 0x7D, 0x7E


def ppp_stuff(data: bytes) -> bytes:
    out = bytearray()
    for b in data:
        if b in (FL, ESC):
            out += bytes([ESC, b ^ 0x20])  # PPP escapes with XOR 0x20
        else:
            out.append(b)
    return bytes(out)


def ppp_unstuff(data: bytes) -> bytes:
    out, i = bytearray(), 0
    while i < len(data):
        if data[i] == ESC:
            i += 1
            out.append(data[i] ^ 0x20)
        else:
            out.append(data[i])
        i += 1
    return bytes(out)


def ppp_frame(proto: int, payload: bytes) -> bytes:
    core = b"\xff\x03" + struct.pack("!H", proto) + payload
    core += struct.pack("<H", crc16_x25(core))
    return bytes([FL]) + ppp_stuff(core) + bytes([FL])


pf = ppp_frame(0x0021, b"data~with}specials")
print("PPP frame:", pf.hex(" "))
print("0x7e inside payload became 7d 5e, 0x7d became 7d 5d (byte stuffing, unlike HDLC bit stuffing)")
core = ppp_unstuff(pf[1:-1])
assert core[:2] == b"\xff\x03" and crc16_x25(core[:-2]) == struct.unpack("<H", core[-2:])[0]
print("parsed protocol:", PROTO[struct.unpack("!H", core[2:4])[0]], "payload:", core[4:-2])
print("check: OK")

# ===== SECTION 4: PPP PHASES, LCP, NCP, PAP, CHAP =====
print("\n===== SECTION 4: PPP PHASES =====")
phases = [
    ("Link Dead", "no carrier / physical layer down"),
    ("Link Establishment", "LCP: Configure-Request/Ack negotiate MRU, auth method, magic number"),
    ("Authentication", "optional: PAP or CHAP"),
    ("Network-Layer", "NCP (IPCP for IPv4): negotiate IP address"),
    ("Link Open", "IP datagrams flow"),
    ("Link Termination", "LCP Terminate-Request, then carrier drop"),
]
for i, (n, d) in enumerate(phases):
    print(f"  {i + 1}. {n:<20} {d}")
print("\nPAP: peer sends name+password in CLEARTEXT, once, in one message.")
secret, challenge, ident = b"s3cret", b"\x10\x20\x30\x40", 7
print("CHAP: authenticator sends a random challenge; peer replies MD5(id + secret + challenge)")
resp = hashlib.md5(bytes([ident]) + secret + challenge).hexdigest()
print("  response sent on the wire:", resp, "(the secret itself never travels)")
good = hashlib.md5(bytes([ident]) + secret + challenge).hexdigest() == resp
bad = hashlib.md5(bytes([ident]) + b"guess" + challenge).hexdigest() == resp
print("  authenticator verifies with its own copy of the secret:", good, "| wrong secret:", bad)
print("  CHAP can re-challenge during the session. MD5 is dated; modern links use EAP/TLS.")
print("PAP vs CHAP: PAP simple, replayable, cleartext; CHAP 3-way, challenge/response.")

# ===== SECTION 5: ARP PACKET =====
print("\n===== SECTION 5: ARP REQUEST/REPLY FORMAT =====")
print("28 bytes for IPv4 over Ethernet, carried in an Ethernet frame with type 0x0806:")
print("  HTYPE 2 (1=Ethernet) | PTYPE 2 (0x0800) | HLEN 1 (6) | PLEN 1 (4) | OPER 2")
print("  SHA 6 (sender MAC) | SPA 4 (sender IP) | THA 6 (target MAC) | TPA 4 (target IP)")
ARP_FMT = "!HHBBH6s4s6s4s"
assert struct.calcsize(ARP_FMT) == 28


def mac(s: str) -> bytes:
    return bytes(int(x, 16) for x in s.split("."))


def ip(s: str) -> bytes:
    return bytes(int(x) for x in s.split("."))


def ip_s(b: bytes) -> str:
    return ".".join(map(str, b))


def mac_s(b: bytes) -> str:
    return ".".join(f"{x:02x}" for x in b)


def arp_pkt(op: int, sha: str, spa: str, tha: str, tpa: str) -> bytes:
    return struct.pack(ARP_FMT, 1, 0x0800, 6, 4, op, mac(sha), ip(spa), mac(tha), ip(tpa))


def arp_parse(p: bytes) -> dict:
    h, pt, hl, pl, op, sha, spa, tha, tpa = struct.unpack(ARP_FMT, p)
    return {"op": {1: "request", 2: "reply", 3: "RARP request", 4: "RARP reply"}[op],
            "sha": mac_s(sha), "spa": ip_s(spa), "tha": mac_s(tha), "tpa": ip_s(tpa)}


req = arp_pkt(1, "02.00.00.00.00.01", "192.168.1.10", "00.00.00.00.00.00", "192.168.1.20")
print("request:", req.hex(" "))
print("parsed :", arp_parse(req), "(THA all zeros = unknown; sent to ff.ff.ff.ff.ff.ff)")
rep = arp_pkt(2, "02.00.00.00.00.02", "192.168.1.20", "02.00.00.00.00.01", "192.168.1.10")
print("reply  :", arp_parse(rep), "(unicast back to the asker)")
assert len(req) == 28

# ===== SECTION 6: IN-MEMORY ARP CACHE WITH TIMEOUT =====
print("\n===== SECTION 6: ARP CACHE WITH TIMEOUT =====")


class Host:
    def __init__(self, name: str, mac_addr: str, ip_addr: str, ttl: int = 60) -> None:
        self.name, self.mac, self.ip, self.ttl = name, mac_addr, ip_addr, ttl
        self.cache: dict[str, tuple[str, int]] = {}  # ip -> (mac, learned_at)
        self.arp_requests_sent = 0

    def lookup(self, now: int, target_ip: str, lan: list["Host"]) -> str:
        entry = self.cache.get(target_ip)
        if entry and now - entry[1] < self.ttl:
            return f"cache HIT {target_ip} -> {entry[0]}"
        reason = "expired" if entry else "miss"
        self.arp_requests_sent += 1
        pkt = arp_pkt(1, self.mac, self.ip, "00.00.00.00.00.00", target_ip)
        for h in lan:  # broadcast: every host on the LAN sees it
            if h is not self and h.on_arp(now, pkt):
                reply = arp_pkt(2, h.mac, h.ip, self.mac, self.ip)
                info = arp_parse(reply)
                self.cache[info["spa"]] = (info["sha"], now)
                return f"cache {reason} -> BROADCAST request, reply from {h.name}: {info['sha']}"
        return f"cache {reason} -> BROADCAST request, no reply (host down)"

    def on_arp(self, now: int, pkt: bytes) -> bool:
        p = arp_parse(pkt)
        if p["tpa"] != self.ip:
            return False  # not for me: ignore
        self.cache[p["spa"]] = (p["sha"], now)  # learn the asker for free
        return True


A = Host("A", "02.00.00.00.00.01", "192.168.1.10", ttl=60)
B = Host("B", "02.00.00.00.00.02", "192.168.1.20")
C = Host("C", "02.00.00.00.00.03", "192.168.1.30")
lan = [A, B, C]
print("A (TTL 60 s) wants to reach 192.168.1.20 at several times:")
for t in [0, 10, 59, 60, 200]:
    print(f"  t={t:>3}: {A.lookup(t, '192.168.1.20', lan)}")
print("A sent", A.arp_requests_sent, "requests for 5 lookups")
print("B learned A from the request:", B.cache)
print("lookup of 192.168.1.99 :", A.lookup(300, "192.168.1.99", lan))
assert A.arp_requests_sent == 4
print("TRAP: ARP only works inside one LAN; for off-subnet hosts ask for the ROUTER's MAC.")
print("ARP has no authentication; defences include static entries and switch-level ARP inspection.")

# ===== SECTION 7: RARP, PROXY ARP, GRATUITOUS ARP =====
print("\n===== SECTION 7: RARP, PROXY ARP, GRATUITOUS ARP =====")
rarp = arp_pkt(3, "02.00.00.00.00.09", "0.0.0.0", "02.00.00.00.00.09", "0.0.0.0")
print("RARP: reverse lookup MAC -> IP, opcode 3/4:", arp_parse(rarp)["op"],
      "(obsolete: replaced by BOOTP and DHCP)")
print("Proxy ARP: a router answers an ARP request for a host behind it using ITS OWN MAC,")
print("  so hosts think the remote host is on-link; the router then forwards.")
grat = arp_pkt(1, "02.00.00.00.00.01", "192.168.1.10", "00.00.00.00.00.00", "192.168.1.10")
p = arp_parse(grat)
print("Gratuitous ARP:", p)
print("  sender IP == target IP:", p["spa"] == p["tpa"], "-> announces 'I am here' / refreshes")
print("  neighbours' caches, and a reply would mean a duplicate IP address on the LAN.")


def on_gratuitous(host: Host, now: int, pkt: bytes) -> None:
    """Hosts that already cache the sender refresh the entry; others ignore it."""
    q = arp_parse(pkt)
    if q["spa"] in host.cache:
        host.cache[q["spa"]] = (q["sha"], now)


B.cache["192.168.1.10"] = ("02.00.00.00.00.ff", 0)  # stale: A's network card was replaced
print("B's stale entry for A      :", B.cache["192.168.1.10"])
on_gratuitous(B, 5, grat)
on_gratuitous(C, 5, grat)  # C never talked to A: nothing cached, nothing learned
print("after the announcement B   :", B.cache["192.168.1.10"])
print("C (had no entry) cache     :", C.cache)
assert B.cache["192.168.1.10"][0] == "02.00.00.00.00.01" and not C.cache
