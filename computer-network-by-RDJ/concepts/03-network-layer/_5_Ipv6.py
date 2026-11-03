# Tags: #Python #ComputerNetworks #NetworkLayer #Ipv6 | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""IPv6: 128-bit addresses, compression rules, address types, the fixed 40-byte
header (build/parse with struct), extension headers, transition mechanisms and
a comparison with IPv4. Cross-checked with the ipaddress module."""
import ipaddress
import struct


# ===== SECTION 1: ADDRESS COMPRESSION =====
print("===== SECTION 1: ADDRESS COMPRESSION =====")


def compress(full: str) -> str:
    """Own implementation of the two rules: drop leading zeros, then
    replace the LONGEST run of >=2 all-zero groups with '::' (first if tie)."""
    groups = [g.lstrip("0") or "0" for g in full.split(":")]
    best_start, best_len, i = -1, 0, 0
    while i < 8:
        if groups[i] == "0":
            j = i
            while j < 8 and groups[j] == "0":
                j += 1
            if j - i > best_len:
                best_start, best_len = i, j - i
            i = j
        else:
            i += 1
    if best_len >= 2:
        left = ":".join(groups[:best_start])
        right = ":".join(groups[best_start + best_len:])
        return f"{left}::{right}"
    return ":".join(groups)


def expand(short: str) -> str:
    if "::" in short:
        l, r = short.split("::")
        lg = l.split(":") if l else []
        rg = r.split(":") if r else []
        groups = lg + ["0"] * (8 - len(lg) - len(rg)) + rg
    else:
        groups = short.split(":")
    return ":".join(g.zfill(4) for g in groups)


tests = [
    "2001:0db8:0000:0000:0000:ff00:0042:8329",
    "fe80:0000:0000:0000:0202:b3ff:fe1e:8329",
    "0000:0000:0000:0000:0000:0000:0000:0001",
    "0000:0000:0000:0000:0000:0000:0000:0000",
    "2001:0db8:0000:0001:0000:0000:0000:0001",     # two runs: longest wins
    "2001:0db8:0000:0001:0001:0001:0001:0001",     # single zero group: no '::'
]
for t in tests:
    c = compress(t)
    lib = str(ipaddress.IPv6Address(t))
    assert c == lib, (c, lib)
    assert expand(c) == t
    print(f"{t}\n   -> {c}")
print("check: OK (compress == ipaddress, expand(compress(x)) == x)")
print("TRAP: '::' may appear only ONCE (else ambiguous); 2001:db8::1::1 is invalid:")
try:
    ipaddress.IPv6Address("2001:db8::1::1")
except ipaddress.AddressValueError as e:
    print("  ipaddress rejects it:", str(e)[:50] + "...")
print("TRAP: a single all-zero group is NOT replaced by '::' (RFC 5952 says so).")


# ===== SECTION 2: ADDRESS TYPES =====
print("\n===== SECTION 2: ADDRESS TYPES =====")
samples = ["::1", "::", "fe80::1", "fd12:3456:789a::1", "2001:db8::1", "2607:f8b0::1",
           "ff02::1", "ff02::2", "ff05::1:3", "::ffff:192.0.2.1"]


def kind(a: str) -> str:
    ip = ipaddress.IPv6Address(a)
    v = int(ip)
    if v == 1:
        return "loopback (::1)"
    if v == 0:
        return "unspecified (::)"
    if v >> 120 == 0xFF:
        scope = (v >> 112) & 0xF
        names = {1: "interface-local", 2: "link-local", 5: "site-local", 14: "global"}
        return f"multicast ff00::/8, scope {names.get(scope, scope)}"
    if v >> 118 == 0b1111111010:
        return "link-local unicast fe80::/10"
    if v >> 121 == 0b1111110:
        return "unique local fc00::/7 (private-like)"
    if ip.ipv4_mapped:
        return f"IPv4-mapped ::ffff:0:0/96 ({ip.ipv4_mapped})"
    if v >> 125 == 0b001:
        return "global unicast 2000::/3"
    return "other"


for s in samples:
    print(f"{s:20} {kind(s)}")
a = ipaddress.IPv6Address("fe80::1")
assert a.is_link_local and ipaddress.IPv6Address("ff02::1").is_multicast
assert ipaddress.IPv6Address("fd12:3456:789a::1").is_private
print("check: OK (properties agree with ipaddress)")
print("Anycast has no prefix of its own: the same unicast address is configured on several")
print("nodes and the packet goes to the NEAREST one. There is NO broadcast in IPv6; ff02::1")
print("(all nodes on link) replaces it.")
print("A link-local address fe80::/10 exists on every IPv6 interface and is never routed.")


# ===== SECTION 3: THE 40-BYTE HEADER =====
print("\n===== SECTION 3: THE 40-BYTE HEADER =====")
FIELDS = [("Version", 4), ("Traffic Class", 8), ("Flow Label", 20), ("Payload Length", 16),
          ("Next Header", 8), ("Hop Limit", 8), ("Source Address", 128), ("Destination Address", 128)]
print("field                bits")
for n, b in FIELDS:
    print(f"{n:20} {b:>4}")
print(f"total = {sum(b for _, b in FIELDS)} bits = {sum(b for _, b in FIELDS) // 8} bytes (always fixed)")


def build_v6(tc: int, flow: int, payload_len: int, nxt: int, hop: int, src: str, dst: str) -> bytes:
    first = (6 << 28) | (tc << 20) | flow
    return (struct.pack("!IHBB", first, payload_len, nxt, hop)
            + ipaddress.IPv6Address(src).packed + ipaddress.IPv6Address(dst).packed)


def parse_v6(b: bytes) -> dict:
    first, plen, nxt, hop = struct.unpack("!IHBB", b[:8])
    return {"version": first >> 28, "traffic_class": (first >> 20) & 0xFF,
            "flow_label": first & 0xFFFFF, "payload_len": plen, "next_header": nxt,
            "hop_limit": hop, "src": str(ipaddress.IPv6Address(b[8:24])),
            "dst": str(ipaddress.IPv6Address(b[24:40]))}


hdr = build_v6(0, 0x12345, 32, 17, 64, "2001:db8::1", "2001:db8:0:1::2")
print("bytes:", len(hdr), "->", hdr[:8].hex(" "), "...")
p = parse_v6(hdr)
print("parsed:", p)
assert len(hdr) == 40 and p["version"] == 6 and p["src"] == "2001:db8::1" and p["flow_label"] == 0x12345
print("check: OK")
print("No header checksum, no IHL (fixed size), no fragmentation fields in the base header.")


# ===== SECTION 4: EXTENSION HEADERS AND FRAGMENTATION =====
print("\n===== SECTION 4: EXTENSION HEADERS =====")
NH = {0: "Hop-by-Hop Options", 6: "TCP", 17: "UDP", 43: "Routing", 44: "Fragment",
      50: "ESP", 51: "AH", 58: "ICMPv6", 60: "Destination Options"}
chain = [44, 6]       # base header's Next Header = 44 (Fragment ext hdr), whose NH = 6 (TCP)
print("base header Next Header chain: base ->", " -> ".join(NH[c] for c in chain))
print("Each extension header starts with its own 'Next Header' byte, forming a linked list.")
print("Routers (except Hop-by-Hop) do not look inside; only the endpoints process them.")
print("Fragmentation in IPv6 is done ONLY by the source host (Fragment header, next-header 44).")
print("Routers NEVER fragment: if a packet is too big they drop it and send ICMPv6 'Packet Too Big'.")
print("Minimum link MTU for IPv6 is 1280 bytes; hosts use Path MTU Discovery to learn the path MTU.")
frag_ext = struct.pack("!BBHI", 6, 0, (0 << 3) | 1, 0xABCDEF01)    # NH=TCP, offset 0, M=1
print("Fragment extension header is 8 bytes:", frag_ext.hex(" "))
assert len(frag_ext) == 8


# ===== SECTION 5: TRANSITION AND COMPARISON =====
print("\n===== SECTION 5: TRANSITION AND COMPARISON =====")
print("Dual stack : host/router runs IPv4 AND IPv6 side by side (most common approach).")
print("Tunneling  : IPv6 packet is carried as payload inside an IPv4 packet (protocol 41) across an IPv4-only part.")
print("Translation: a gateway converts IPv6 <-> IPv4 headers (e.g. NAT64 with DNS64).")
inner = build_v6(0, 0, 20, 6, 64, "2001:db8::1", "2001:db8::2")
outer = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(inner), 1, 0, 64, 41, 0,
                    ipaddress.IPv4Address("192.0.2.1").packed, ipaddress.IPv4Address("198.51.100.1").packed)
pkt = outer + inner
print(f"tunnel packet: outer IPv4 20 B (protocol 41) + inner IPv6 {len(inner)} B = {len(pkt)} B")
assert pkt[9] == 41 and parse_v6(pkt[20:])["dst"] == "2001:db8::2"
print("check: OK")
rows = [("Address size", "32 bits", "128 bits"), ("Address count", f"2^32 = {2**32:,}", "2^128 = " + f"{2**128:.3e}"),
        ("Header size", "20-60 B variable", "40 B fixed"), ("Header checksum", "yes", "no"),
        ("Fragmentation", "routers and source", "source only"), ("Broadcast", "yes", "no (multicast)"),
        ("Address config", "manual / DHCP", "SLAAC / DHCPv6"), ("Options", "in header", "extension headers"),
        ("Address notation", "dotted decimal", "colon hex"), ("ARP", "ARP", "Neighbor Discovery (ICMPv6)"),
        ("IPsec", "optional", "supported in the design (not forced on)"), ("TTL / hop", "TTL", "Hop Limit")]
print(f"{'feature':16} {'IPv4':20} IPv6")
for r in rows:
    print(f"{r[0]:16} {r[1]:20} {r[2]}")
