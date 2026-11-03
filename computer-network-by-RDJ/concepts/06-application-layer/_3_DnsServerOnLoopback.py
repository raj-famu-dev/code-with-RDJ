# Tags: #Python #ComputerNetworks #ApplicationLayer #DnsServerLoopback | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches a tiny authoritative DNS server over UDP on 127.0.0.1 (port 0), a
hand-built client, TTL caching, the transaction-ID trap, truncation (TC bit) and
conceptual DNS security (spoofing, cache poisoning, DNSSEC, DoH/DoT).
Syllabus idea: DNS in practice. Loopback only; the zone data is fake (RFC 5737).
"""
import ipaddress
import socket
import struct
import threading

HOST = "127.0.0.1"
ZONE = {  # (lowercase name, type) -> (list of IPv4 strings, ttl)
    ("www.example.test", 1): (["192.0.2.10", "192.0.2.11"], 60),
    ("mail.example.test", 1): (["192.0.2.25"], 300),
}
KNOWN_NAMES = {name for name, _ in ZONE}

# ===== SECTION 1: WHAT THE SERVER MUST DO =====
print("===== SECTION 1: WHAT THE SERVER MUST DO =====")
print("1. receive a UDP datagram, 2. parse header + question, 3. look up the zone,")
print("4. build a reply with the SAME transaction ID and question,")
print("5. RCODE 0 + answers, or RCODE 3 (NXDOMAIN) if the name does not exist,")
print("   or RCODE 0 + zero answers (NODATA) if the name exists but not that type.")
print("Zone (fake):", {f"{n} A": v for (n, _), v in ZONE.items()})


# ===== SECTION 2: THE PACKET LOGIC (NO SOCKETS YET) =====
print("\n===== SECTION 2: THE PACKET LOGIC (NO SOCKETS YET) =====")


def encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        out += bytes([len(label)]) + label.encode("ascii")
    return out + b"\x00"


def decode_name(msg: bytes, pos: int) -> tuple[str, int]:
    labels = []
    while msg[pos] != 0:
        n = msg[pos]
        if n & 0xC0:
            raise ValueError("compression not expected in a query")
        labels.append(msg[pos + 1:pos + 1 + n].decode("ascii"))
        pos += 1 + n
    return ".".join(labels), pos + 1


def make_query(txid: int, name: str, qtype: int = 1) -> bytes:
    return struct.pack("!HHHHHH", txid, 0x0100, 1, 0, 0, 0) + encode_name(name) \
        + struct.pack("!HH", qtype, 1)


def build_reply(query: bytes, max_udp: int = 512) -> bytes:
    txid, flags, qd, *_ = struct.unpack("!HHHHHH", query[:12])
    if qd != 1:
        return struct.pack("!HHHHHH", txid, 0x8001, 0, 0, 0, 0)       # FORMERR
    qname, pos = decode_name(query, 12)
    qtype, qclass = struct.unpack("!HH", query[pos:pos + 4])
    question = query[12:pos + 4]
    key = (qname.lower(), qtype)
    rd = flags & 0x0100
    if key in ZONE:
        addrs, ttl = ZONE[key]
        body = b"".join(b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, ttl, 4)
                        + ipaddress.IPv4Address(a).packed for a in addrs)
        rcode, count = 0, len(addrs)
    elif qname.lower() in KNOWN_NAMES:
        body, rcode, count = b"", 0, 0                                 # NODATA
    else:
        body, rcode, count = b"", 3, 0                                 # NXDOMAIN
    header = struct.pack("!HHHHHH", txid, 0x8400 | rd | 0x80 | rcode, 1, count, 0, 0)
    reply = header + question + body
    if len(reply) > max_udp:                                           # truncation
        reply = struct.pack("!HHHHHH", txid, 0x8600 | rd | 0x80, 1, 0, 0, 0) + question
    return reply


def parse_reply(data: bytes) -> dict:
    txid, flags, qd, an, *_ = struct.unpack("!HHHHHH", data[:12])
    _, pos = decode_name(data, 12)
    pos += 4
    ips, ttl = [], None
    for _ in range(an):
        pos += 2                                  # owner name is a 2-byte pointer here
        _, _, ttl, rdlen = struct.unpack("!HHIH", data[pos:pos + 10])
        pos += 10
        ips.append(str(ipaddress.IPv4Address(data[pos:pos + rdlen])))
        pos += rdlen
    return {"id": txid, "rcode": flags & 0xF, "aa": (flags >> 10) & 1,
            "tc": (flags >> 9) & 1, "ips": ips, "ttl": ttl}


for name, qt in (("www.example.test", 1), ("WWW.Example.TEST", 1),
                 ("nothere.example.test", 1), ("www.example.test", 28)):
    r = parse_reply(build_reply(make_query(0x0042, name, qt)))
    print(f"  {name:<22} type={qt:<3} -> rcode={r['rcode']} aa={r['aa']} ips={r['ips']} ttl={r['ttl']}")
assert parse_reply(build_reply(make_query(1, "www.example.test")))["ips"] == ["192.0.2.10", "192.0.2.11"]
print("check: OK (case-insensitive match, NXDOMAIN=3, NODATA=0 with no answers)")

# ===== SECTION 3: SERVER ON A UDP SOCKET + HAND-BUILT CLIENT =====
print("\n===== SECTION 3: SERVER ON A UDP SOCKET + HAND-BUILT CLIENT =====")


class DnsServer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST, 0))
        self.sock.settimeout(0.2)
        self.port: int = self.sock.getsockname()[1]
        self.queries = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run)

    def run(self) -> None:
        while not self.stop.is_set():
            try:
                data, addr = self.sock.recvfrom(512)
            except socket.timeout:
                continue
            self.queries += 1
            try:
                self.sock.sendto(build_reply(data), addr)
            except (ValueError, struct.error, IndexError):
                pass                              # malformed query: drop silently

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.stop.set()
        self.thread.join(timeout=5)
        self.sock.close()


def lookup(port: int, name: str, txid: int, qtype: int = 1) -> dict:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        s.sendto(make_query(txid, name, qtype), (HOST, port))
        data, _ = s.recvfrom(4096)
    return parse_reply(data)


server = DnsServer()
server.start()
try:
    print("server listening on UDP", HOST, "port", "<chosen by OS, port 0>")
    for i, name in enumerate(["www.example.test", "mail.example.test", "ghost.example.test"], 1):
        r = lookup(server.port, name, 0x1000 + i)
        status = "NXDOMAIN" if r["rcode"] == 3 else "OK"
        print(f"  {name:<22} id={r['id']:#06x} {status:<9} ips={r['ips']} ttl={r['ttl']}")
    print("server saw", server.queries, "queries")

    # ===== SECTION 4: CACHING WITH TTL =====
    print("\n===== SECTION 4: CACHING WITH TTL =====")

    class CachingClient:
        def __init__(self, port: int) -> None:
            self.port = port
            self.now = 0                                  # simulated clock (seconds)
            self.cache: dict[str, tuple[list[str], int]] = {}
            self.next_id = 0x2000

        def resolve(self, name: str) -> tuple[list[str], str]:
            hit = self.cache.get(name)
            if hit and hit[1] > self.now:
                return hit[0], f"cache (expires t={hit[1]}s)"
            self.next_id += 1
            r = lookup(self.port, name, self.next_id)
            if r["ips"]:
                self.cache[name] = (r["ips"], self.now + r["ttl"])
            return r["ips"], "server"

    cc = CachingClient(server.port)
    start = server.queries
    for t in (0, 30, 59, 60, 61):
        cc.now = t
        ips, src = cc.resolve("www.example.test")
        print(f"  t={t:>2}s  www.example.test -> {ips} from {src}")
    print("server queries used:", server.queries - start, "(TTL=60: t=0 and t=60 missed, the other three hit the cache)")
    assert server.queries - start == 2
    print("check: OK (5 lookups, only 2 reached the server)")

    # ===== SECTION 5: TRAP - TRANSACTION ID MISMATCH =====
    print("\n===== SECTION 5: TRAP - TRANSACTION ID MISMATCH =====")
    print("UDP has no connection: ANY datagram that reaches the client's port looks like")
    print("a reply. Only the 16-bit ID (and source port/address) tell it apart.")

    def run_with_forger(strict: bool) -> str:
        """A fake 'server' socket sends a forged reply (wrong ID) BEFORE the real one."""
        fake = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fake.bind((HOST, 0))
        fake.settimeout(2)
        cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cli.settimeout(2)
        try:
            txid = 0x7777
            cli.sendto(make_query(txid, "www.example.test"), fake.getsockname())
            query, caddr = fake.recvfrom(512)
            forged = bytearray(build_reply(query))
            struct.pack_into("!H", forged, 0, 0x1234)                 # wrong ID
            forged[-4:] = ipaddress.IPv4Address("203.0.113.66").packed  # bogus IP
            fake.sendto(bytes(forged), caddr)                         # arrives first
            fake.sendto(build_reply(query), caddr)                    # the genuine one
            while True:
                data, _ = cli.recvfrom(4096)
                r = parse_reply(data)
                if strict and r["id"] != txid:
                    continue                                          # ignore, keep waiting
                return f"id={r['id']:#06x} ips={r['ips']}"
        finally:
            fake.close()
            cli.close()

    print("naive client (accepts first datagram):", run_with_forger(strict=False))
    print("strict client (checks ID matches)    :", run_with_forger(strict=True))
    print("Even the ID is weak: 1 in 65536 per forged packet if the attacker can guess the")
    print("source port. Fix: random ID AND random source port, plus checking the question.")

    # ===== SECTION 6: TRUNCATION (TC BIT) =====
    print("\n===== SECTION 6: TRUNCATION (TC BIT) =====")
    big = {"big.example.test": ([f"198.51.100.{i}" for i in range(1, 41)], 60)}
    ZONE[("big.example.test", 1)] = big["big.example.test"]
    KNOWN_NAMES.add("big.example.test")
    raw = build_reply(make_query(9, "big.example.test"), max_udp=65535)
    print(f"40 A records need {len(raw)} bytes; classic DNS-over-UDP limit is 512 bytes")
    r = lookup(server.port, "big.example.test", 0x3001)
    print(f"over UDP the server answers tc={r['tc']}, answers kept={len(r['ips'])}")
    print("TC=1 tells the client: 'incomplete, retry this query over TCP port 53'.")
    print("(EDNS0 lets clients advertise larger UDP sizes; TCP stays the fallback.)")
    assert r["tc"] == 1 and len(raw) > 512
    print("check: OK")
finally:
    server.close()
print("server thread stopped:", not server.thread.is_alive())

# ===== SECTION 7: DNS SECURITY NOTES (CONCEPTUAL) =====
print("\n===== SECTION 7: DNS SECURITY NOTES (CONCEPTUAL) =====")
print("Spoofing / cache poisoning: an attacker tries to get a resolver to cache a")
print("false answer by winning a race with the real reply. Success needs matching:")
print("  the ID (16 bits) and, if randomised, the source port (up to 16 bits more).")
print(f"  ID only          : 1 in {2 ** 16:,} per forged packet")
print(f"  ID + random port : 1 in {2 ** 32:,} (upper bound; real port ranges are smaller)")
print("A poisoned cache then sends EVERY user of that resolver to the wrong address")
print("until the TTL expires. Defences: random ID + port, 0x20 case randomisation,")
print("validating that the answer matches the question, and DNSSEC.")
print("DNSSEC (RFC 4033-4035): zones SIGN their records (RRSIG), publish keys (DNSKEY)")
print("and a chain of trust (DS records) up to the root. Proves AUTHENTICITY and")
print("INTEGRITY; it does NOT hide which names you look up.")
print("DNS over TLS (port 853) and DNS over HTTPS (RFC 8484, port 443) ENCRYPT the")
print("client-to-resolver hop for privacy; they do not authenticate the zone data.")
