# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""VLSM allocation (largest first), CIDR notation, route aggregation
(supernetting) and longest-prefix-match lookup, cross-checked with ipaddress."""
import ipaddress
from ipaddress import IPv4Address, IPv4Network


def to_int(a: str) -> int:
    p = [int(x) for x in a.split(".")]
    return (p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]


def to_dotted(n: int) -> str:
    return ".".join(str((n >> s) & 255) for s in (24, 16, 8, 0))


# ===== SECTION 1: CIDR NOTATION =====
print("===== SECTION 1: CIDR NOTATION =====")
for cidr in ["200.10.20.0/22", "10.1.2.3/8", "172.16.5.130/26"]:
    ip, p = cidr.split("/")
    p = int(p)
    mask = (0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF
    net = to_int(ip) & mask
    size = 1 << (32 - p)
    print(f"{cidr:17} mask {to_dotted(mask):15} network {to_dotted(net):13} addresses {size:>6} last {to_dotted(net + size - 1)}")
    lib = ipaddress.ip_interface(cidr).network
    assert str(lib.network_address) == to_dotted(net) and lib.num_addresses == size
print("check: OK")
print("CIDR drops class boundaries: prefix length can be any of /0../32.")


# ===== SECTION 2: VLSM ALLOCATION (LARGEST FIRST) =====
print("\n===== SECTION 2: VLSM ALLOCATION (LARGEST FIRST) =====")


def prefix_for_hosts(hosts: int) -> int:
    need = hosts + 2                         # network + broadcast
    return 32 - (need - 1).bit_length()


def vlsm(block: str, reqs: dict[str, int]) -> list[tuple[str, int, int]]:
    """Return [(name, network_int, prefix)]; raises if the block is too small."""
    base = to_int(block.split("/")[0])
    limit = base + (1 << (32 - int(block.split("/")[1])))
    cur, out = base, []
    for name, h in sorted(reqs.items(), key=lambda kv: -kv[1]):   # largest first
        p = prefix_for_hosts(h)
        size = 1 << (32 - p)
        assert cur % size == 0, "misaligned"   # largest-first keeps alignment
        if cur + size > limit:
            raise ValueError(f"no room for {name}")
        out.append((name, cur, p))
        cur += size
    return out


block = "192.168.1.0/24"
reqs = {"LAN-A": 100, "LAN-B": 50, "LAN-C": 25, "LAN-D": 10, "Link-1": 2, "Link-2": 2}
alloc = vlsm(block, reqs)
print(f"Block {block}; requirements (hosts): {reqs}")
print(f"{'name':7} {'need':>4} {'subnet':18} {'mask':15} {'range':31} bcast")
used = 0
for name, net, p in alloc:
    size = 1 << (32 - p)
    used += size
    print(f"{name:7} {reqs[name]:>4} {to_dotted(net) + '/' + str(p):18} {to_dotted((0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF):15} "
          f"{to_dotted(net + 1) + ' - ' + to_dotted(net + size - 2):31} {to_dotted(net + size - 1)}")
print(f"Addresses used {used} of 256 -> {256 - used} left for growth.")


# ===== SECTION 3: CHECKER VS ipaddress =====
print("\n===== SECTION 3: CHECKER (NO OVERLAP, FITS, CAPACITY) =====")
nets = [IPv4Network(f"{to_dotted(n)}/{p}") for _, n, p in alloc]
parent = IPv4Network(block)
for (name, _, _), nw in zip(alloc, nets):
    assert nw.subnet_of(parent), name
    assert nw.num_addresses - 2 >= reqs[name], name
for i in range(len(nets)):
    for j in range(i + 1, len(nets)):
        assert not nets[i].overlaps(nets[j]), (nets[i], nets[j])
print("every subnet is inside the parent, big enough, and none overlap")
print("check: OK")
print("TRAP: allocating SMALLEST first breaks alignment.")
try:
    cur = to_int("192.168.1.0")
    for name, h in sorted(reqs.items(), key=lambda kv: kv[1]):      # smallest first
        size = 1 << (32 - prefix_for_hosts(h))
        if cur % size:
            raise AssertionError(f"{name} (/{prefix_for_hosts(h)}) would start at {to_dotted(cur)} - not a multiple of {size}")
        cur += size
except AssertionError as e:
    print("  smallest-first fails:", e)
print("  Fix: sort descending, so each block starts on its own size boundary.")


# ===== SECTION 4: SUPERNETTING / ROUTE AGGREGATION =====
print("\n===== SECTION 4: SUPERNETTING / ROUTE AGGREGATION =====")
routes = ["200.10.0.0/24", "200.10.1.0/24", "200.10.2.0/24", "200.10.3.0/24"]
ints = [to_int(r.split("/")[0]) for r in routes]
first = ints[0]
# common prefix: highest bit where any differ
diff = 0
for v in ints:
    diff |= v ^ first
pfx = 32 - diff.bit_length()
print("routes:", routes)
for r, v in zip(routes, ints):
    print(f"  {to_dotted(v):11} {v:032b}")
print(f"common leading bits = {pfx} -> summary {to_dotted(first & ((0xFFFFFFFF << (32 - pfx)) & 0xFFFFFFFF))}/{pfx}")
lib_sum = list(ipaddress.collapse_addresses(IPv4Network(r) for r in routes))
print("ipaddress.collapse_addresses ->", [str(x) for x in lib_sum])
assert [str(x) for x in lib_sum] == [f"{to_dotted(first)}/{pfx}"]
print("check: OK")
bad = ["200.10.1.0/24", "200.10.2.0/24"]
print("TRAP: 200.10.1.0/24 + 200.10.2.0/24 cannot merge:",
      [str(x) for x in ipaddress.collapse_addresses(IPv4Network(r) for r in bad)],
      "(not aligned on a /23 boundary: .1 and .2 straddle .0-.1 / .2-.3)")
print("Rule: N blocks aggregate only if N is a power of 2, contiguous, and first block aligned.")


# ===== SECTION 5: LONGEST PREFIX MATCH =====
print("\n===== SECTION 5: LONGEST PREFIX MATCH =====")
table = [
    ("0.0.0.0/0", "default via ISP"),
    ("200.10.0.0/16", "if0"),
    ("200.10.1.0/24", "if1"),
    ("200.10.1.128/25", "if2"),
    ("10.0.0.0/8", "if3"),
]


def lookup(dst: str) -> tuple[str, str]:
    d = to_int(dst)
    best = None
    for cidr, hop in table:
        ip, p = cidr.split("/")
        p = int(p)
        mask = (0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF if p else 0
        if d & mask == to_int(ip) & mask and (best is None or p > best[0]):
            best = (p, cidr, hop)
    return best[1], best[2]


def lookup_lib(dst: str) -> str:
    a = IPv4Address(dst)
    m = [(IPv4Network(c), h) for c, h in table if a in IPv4Network(c)]
    return max(m, key=lambda x: x[0].prefixlen)[0].with_prefixlen


for dst in ["200.10.1.200", "200.10.1.5", "200.10.9.9", "10.9.9.9", "8.8.8.8"]:
    c, h = lookup(dst)
    assert c == lookup_lib(dst)
    print(f"{dst:13} matches {c:16} -> {h}")
print("check: OK")
print("200.10.1.200 matches /0, /16, /24 and /25; the /25 (longest) wins.")
