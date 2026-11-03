# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Network layer services (datagram vs virtual circuit, forwarding vs routing)
and IPv4 addressing: dotted decimal, classful A-E, network/host id, special
addresses, and a classifier cross-checked against the ipaddress module."""
import ipaddress


# ===== SECTION 1: DATAGRAM VS VIRTUAL-CIRCUIT SERVICE =====
print("===== SECTION 1: DATAGRAM VS VIRTUAL-CIRCUIT SERVICE =====")

# A tiny 3-router line: A -> R1 -> R2 -> B.  Each router has a table.
# Datagram: table maps destination address -> next hop (looked up per packet).
datagram_tables = {
    "R1": {"B": "R2", "A": "A"},
    "R2": {"B": "B", "A": "R1"},
}
# Virtual circuit: table maps (in-VC id) -> (next hop, out-VC id), set up once.
vc_tables = {
    "R1": {("A", 5): ("R2", 9)},
    "R2": {("R1", 9): ("B", 2)},
}


def send_datagram(dest: str) -> list[str]:
    path, node = ["A", "R1"], "R1"
    while node != dest:
        node = datagram_tables[node][dest]
        path.append(node)
    return path


def send_vc() -> list[str]:
    path, node, prev, vc = ["A"], "R1", "A", 5
    path.append(node)
    while node in vc_tables:
        nxt, new_vc = vc_tables[node][(prev, vc)]
        print(f"  at {node}: in-VC {vc} -> out-VC {new_vc}, next {nxt}")
        prev, node, vc = node, nxt, new_vc
        path.append(node)
    return path


print("Datagram path of 2 packets (each carries full dest address):",
      send_datagram("B"), send_datagram("B"))
print("Virtual-circuit path (packets carry only a short VC id):")
print("  ", send_vc())
print("Forwarding = per-packet table lookup inside one router (data plane).")
print("Routing    = algorithm that FILLS the tables (control plane).")


# ===== SECTION 2: IPV4 DOTTED DECIMAL <-> 32-BIT =====
print("\n===== SECTION 2: DOTTED DECIMAL <-> 32-BIT =====")


def to_int(addr: str) -> int:
    parts = [int(p) for p in addr.split(".")]
    assert len(parts) == 4 and all(0 <= p <= 255 for p in parts), addr
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]


def to_dotted(n: int) -> str:
    return ".".join(str((n >> s) & 0xFF) for s in (24, 16, 8, 0))


a = "192.168.10.77"
n = to_int(a)
bits = f"{n:032b}"
print("address :", a)
print("binary  :", ".".join(bits[i:i + 8] for i in range(0, 32, 8)))
print("integer :", n, "hex:", hex(n))
print("back    :", to_dotted(n))
assert n == int(ipaddress.IPv4Address(a))
print("check: OK")


# ===== SECTION 3: CLASSFUL ADDRESSING =====
print("\n===== SECTION 3: CLASSFUL ADDRESSING (A-E) =====")
# (class, first-octet range, leading bits, default mask, net bits)
CLASSES = [
    ("A", 0, 127, "0", "255.0.0.0", 8),
    ("B", 128, 191, "10", "255.255.0.0", 16),
    ("C", 192, 223, "110", "255.255.255.0", 24),
    ("D", 224, 239, "1110", "(none, multicast)", None),
    ("E", 240, 255, "1111", "(none, reserved)", None),
]
print(f"{'cls':3} {'first octet':11} {'lead bits':9} {'default mask':18} nets / hosts per net")
for c, lo, hi, lead, mask, nb in CLASSES:
    if nb:
        extra = f"{2 ** (nb - len(lead)):>9} / {2 ** (32 - nb) - 2}"
    else:
        extra = "-"
    print(f"{c:3} {lo:>3}-{hi:<7} {lead:9} {mask:18} {extra}")
print("Note: class A is 0-127 by bit pattern, but 0/8 and 127/8 are special,")
print("so usable class A nets = 2^7 - 2 = 126 in the classic exam answer.")


def addr_class(addr: str) -> str:
    first = int(addr.split(".")[0])
    for c, lo, hi, *_ in CLASSES:
        if lo <= first <= hi:
            return c
    raise ValueError(addr)


def split_net_host(addr: str) -> tuple[str, str]:
    c = addr_class(addr)
    nb = {"A": 8, "B": 16, "C": 24}.get(c)
    if nb is None:
        return ("n/a", "n/a")
    v = to_int(addr)
    mask = (0xFFFFFFFF << (32 - nb)) & 0xFFFFFFFF
    return to_dotted(v & mask), to_dotted(v & ~mask & 0xFFFFFFFF)


for ad in ["10.4.5.6", "172.16.9.1", "192.168.10.77", "224.0.0.5", "250.1.1.1"]:
    net, host = split_net_host(ad)
    print(f"{ad:15} class {addr_class(ad)}  network id {net:12} host id {host}")


# ===== SECTION 4: SPECIAL ADDRESSES + CLASSIFIER =====
print("\n===== SECTION 4: SPECIAL ADDRESSES + CLASSIFIER =====")


def classify(addr: str) -> str:
    o = [int(p) for p in addr.split(".")]
    if addr == "255.255.255.255":
        return "limited broadcast"
    if o[0] == 0:
        return "this network / unspecified (0/8)"
    if o[0] == 127:
        return "loopback (127/8)"
    if o[0] == 10 or (o[0] == 172 and 16 <= o[1] <= 31) or (o[0] == 192 and o[1] == 168):
        return "private (RFC 1918)"
    if o[0] == 169 and o[1] == 254:
        return "APIPA / link-local (169.254/16)"
    if 224 <= o[0] <= 239:
        return "multicast (class D)"
    if o[0] >= 240:
        return "reserved (class E)"
    return "public unicast"


def lib_classify(addr: str) -> str:
    ip = ipaddress.IPv4Address(addr)
    if ip == ipaddress.IPv4Address("255.255.255.255"):
        return "limited broadcast"
    if ip.is_unspecified or addr.startswith("0."):
        return "this network / unspecified (0/8)"
    if ip.is_loopback:
        return "loopback (127/8)"
    if ip in ipaddress.ip_network("10.0.0.0/8") or ip in ipaddress.ip_network("172.16.0.0/12") \
            or ip in ipaddress.ip_network("192.168.0.0/16"):
        return "private (RFC 1918)"
    if ip.is_link_local:
        return "APIPA / link-local (169.254/16)"
    if ip.is_multicast:
        return "multicast (class D)"
    if ip.is_reserved:
        return "reserved (class E)"
    return "public unicast"


tests = ["127.0.0.1", "10.1.2.3", "172.16.0.9", "172.32.0.9", "192.168.1.1",
         "169.254.7.7", "255.255.255.255", "224.0.0.9", "8.8.8.8", "0.0.0.0",
         "250.0.0.1", "11.0.0.1"]
for t in tests:
    mine, lib = classify(t), lib_classify(t)
    assert mine == lib, (t, mine, lib)
    print(f"{t:16} -> {mine}")
print("check: OK (own classifier agrees with the ipaddress module on all)")
print("TRAP: 172.32.0.9 looks private but RFC1918 stops at 172.31.255.255.")


# ===== SECTION 5: BROADCAST ADDRESSES =====
print("\n===== SECTION 5: LIMITED VS DIRECTED BROADCAST =====")
net = ipaddress.ip_network("192.168.10.0/24")
print("Directed broadcast for", net, "=", net.broadcast_address,
      "(host bits all 1; reaches every host on THAT network, can be routed)")
print("Limited broadcast = 255.255.255.255 (this network only, routers never forward)")
print("Network address   =", net.network_address, "(host bits all 0, names the network, not a host)")
print("Usable hosts      =", net.num_addresses - 2, "= 2^8 - 2")
