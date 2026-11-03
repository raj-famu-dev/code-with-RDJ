# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Fixed-length subnetting: subnet mask, borrowing host bits, number of subnets
(2^n) and hosts (2^h - 2), a full subnet table, and the classic traps."""
import ipaddress
from dataclasses import dataclass


def to_int(a: str) -> int:
    p = [int(x) for x in a.split(".")]
    return (p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]


def to_dotted(n: int) -> str:
    return ".".join(str((n >> s) & 255) for s in (24, 16, 8, 0))


def mask_from_prefix(p: int) -> int:
    return (0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF


# ===== SECTION 1: MASK, PREFIX AND BORROWED BITS =====
print("===== SECTION 1: MASK, PREFIX AND BORROWED BITS =====")
net, default_prefix = "192.168.10.0", 24     # class C
needed_subnets = 6
n = (needed_subnets - 1).bit_length()          # smallest n with 2^n >= 6
new_prefix = default_prefix + n
host_bits = 32 - new_prefix
print(f"Class C network {net}/{default_prefix}; need {needed_subnets} subnets")
print(f"borrow n = {n} bits  (2^{n} = {2 ** n} >= {needed_subnets})")
print(f"new prefix /{new_prefix}, mask {to_dotted(mask_from_prefix(new_prefix))}")
print("mask bits:", ".".join(f"{(mask_from_prefix(new_prefix) >> s) & 255:08b}" for s in (24, 16, 8, 0)))
print(f"host bits left h = {host_bits}; hosts per subnet = 2^{host_bits} - 2 = {2 ** host_bits - 2}")
print(f"block size (increment in last octet) = 2^{host_bits} = {2 ** host_bits}")


# ===== SECTION 2: SUBNET TABLE =====
print("\n===== SECTION 2: SUBNET TABLE =====")


@dataclass
class Subnet:
    network: int
    prefix: int

    @property
    def broadcast(self) -> int:
        return self.network | (~mask_from_prefix(self.prefix) & 0xFFFFFFFF)

    @property
    def first(self) -> int:
        return self.network + 1

    @property
    def last(self) -> int:
        return self.broadcast - 1


def split(network: str, prefix: int, new_prefix: int) -> list[Subnet]:
    size = 1 << (32 - new_prefix)
    base = to_int(network)
    return [Subnet(base + i * size, new_prefix) for i in range(1 << (new_prefix - prefix))]


subs = split(net, default_prefix, new_prefix)
print(f"{'#':>2} {'network':15} {'first host':15} {'last host':15} {'broadcast':15}")
for i, s in enumerate(subs):
    print(f"{i:>2} {to_dotted(s.network):15} {to_dotted(s.first):15} {to_dotted(s.last):15} {to_dotted(s.broadcast):15}")

lib = list(ipaddress.ip_network(f"{net}/{default_prefix}").subnets(new_prefix=new_prefix))
for s, l in zip(subs, lib):
    assert to_dotted(s.network) == str(l.network_address)
    assert to_dotted(s.broadcast) == str(l.broadcast_address)
    hosts = list(l.hosts())
    assert to_dotted(s.first) == str(hosts[0]) and to_dotted(s.last) == str(hosts[-1])
print("check: OK (all", len(subs), "rows match the ipaddress module)")
print(f"Requested 6 subnets but got {len(subs)}: 2 are spare.")


# ===== SECTION 3: ANALYSE ANY HOST ADDRESS =====
print("\n===== SECTION 3: WHICH SUBNET IS THIS HOST IN? =====")
host, pfx = "192.168.10.77", new_prefix
m = mask_from_prefix(pfx)
h = to_int(host)
print(f"host {host}/{pfx}  mask {to_dotted(m)}")
print(f"host bits : {h:032b}")
print(f"mask bits : {m:032b}")
print(f"AND (net) : {h & m:032b} = {to_dotted(h & m)}")
sn = Subnet(h & m, pfx)
print("broadcast :", to_dotted(sn.broadcast), " usable range:", to_dotted(sn.first), "-", to_dotted(sn.last))
iface = ipaddress.ip_interface(f"{host}/{pfx}")
assert to_dotted(h & m) == str(iface.network.network_address)
print("check: OK")


# ===== SECTION 4: TRAP - OFF-BY-TWO HOST COUNT =====
print("\n===== SECTION 4: TRAP - OFF-BY-TWO HOST COUNT =====")
for hb in (2, 3, 4, 8):
    print(f"h={hb}: wrong 2^h = {2 ** hb:>3}   right 2^h - 2 = {2 ** hb - 2:>3}")
print("A /30 has 4 addresses but only 2 usable hosts: ideal for a point-to-point link.")
print("A /31 (RFC 3021) is special: both addresses usable on point-to-point links.")
l31 = ipaddress.ip_network("10.0.0.0/31")
print("ipaddress hosts() of 10.0.0.0/31:", [str(x) for x in l31.hosts()])
print("A /32 is a single host route.")


# ===== SECTION 5: TRAP - SUBNET ZERO / ALL-ONES SUBNET =====
print("\n===== SECTION 5: TRAP - SUBNET-ZERO AND ALL-ONES SUBNET =====")
print("Old classful rule (RFC 950): the first (subnet-zero) and last (all-ones)")
print("subnets were NOT allowed, so usable subnets = 2^n - 2.")
for nb in (2, 3):
    print(f"  n={nb}: old rule {2 ** nb - 2} subnets, modern rule (CIDR era) {2 ** nb} subnets")
print("Modern practice (CIDR era) allows subnet zero and the all-ones subnet.")
print(f"Under the OLD rule our 6-subnet need would force n = 3 with only {2 ** 3 - 2} usable subnets: just enough.")
print("Under the OLD rule 4 subnets would need n = 3 (not 2), because 2^2 - 2 = 2 < 4.")
print("Exam tip: read the question - if it says 'subnet zero is not used', subtract 2.")
