# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""IP multicast (class D, IGMP group membership, flooding vs reverse path
forwarding with pruning) and Mobile IP (home agent, foreign agent, care-of
address, tunnelling), all simulated in memory."""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field

# ===== SECTION 1: CLASS D AND GROUP ADDRESSES =====
print("===== SECTION 1: CLASS D AND GROUP ADDRESSES =====")
grp = ipaddress.ip_network("224.0.0.0/4")
print(f"multicast block {grp}: {grp.network_address} - {grp.broadcast_address} (leading bits 1110, 2^28 groups)")
for a, what in [("224.0.0.1", "all hosts on this subnet"), ("224.0.0.2", "all routers on this subnet"),
                ("224.0.0.5", "OSPF routers"), ("224.0.0.9", "RIPv2 routers"),
                ("224.0.0.22", "IGMPv3 reports"), ("239.1.2.3", "administratively scoped (private use)"),
                ("192.0.2.1", "unicast, not multicast")]:
    ip = ipaddress.IPv4Address(a)
    print(f"  {a:12} is_multicast={ip.is_multicast!s:5} {what}")
assert ipaddress.IPv4Address("239.1.2.3").is_multicast and not ipaddress.IPv4Address("192.0.2.1").is_multicast
print("A group address is only ever a DESTINATION (never a source). 224.0.0.0/24 is link-local: routers never forward it.")


def group_to_mac(ip: str) -> str:
    low23 = int(ipaddress.IPv4Address(ip)) & 0x7FFFFF
    mac = (0x01005E << 24) | low23
    return ":".join(f"{(mac >> s) & 255:02x}" for s in range(40, -8, -8))


for g in ["224.0.0.1", "239.1.2.3", "224.129.2.3"]:
    print(f"  Ethernet multicast MAC for {g:12} = {group_to_mac(g)}")
assert group_to_mac("224.1.2.3") == group_to_mac("225.1.2.3")
print("TRAP: only 23 of the 28 group bits fit in the MAC, so 32 groups share one MAC:")
print(f"  224.1.2.3 -> {group_to_mac('224.1.2.3')}   225.1.2.3 -> {group_to_mac('225.1.2.3')} (same). The IP layer must filter.")


# ===== SECTION 2: IGMP MEMBERSHIP =====
print("\n===== SECTION 2: IGMP MEMBERSHIP =====")


@dataclass
class IgmpRouter:
    """Router interface state: group -> set of hosts that reported membership."""
    members: dict[str, set[str]] = field(default_factory=dict)

    def report(self, host: str, group: str) -> None:
        self.members.setdefault(group, set()).add(host)

    def leave(self, host: str, group: str) -> None:
        self.members.get(group, set()).discard(host)
        if group in self.members and not self.members[group]:
            # IGMPv2: router sends a group-specific query before removing; here no one answers
            del self.members[group]

    def query(self, answers: dict[str, list[str]]) -> None:
        """General query to 224.0.0.1; hosts reply per group (report suppression: one per group)."""
        self.members = {}
        for host, groups in answers.items():
            for g in groups:
                self.members.setdefault(g, set()).add(host)

    def forward_group(self, group: str) -> bool:
        return bool(self.members.get(group))


r = IgmpRouter()
r.report("hostA", "239.1.1.1")
r.report("hostB", "239.1.1.1")
r.report("hostC", "239.2.2.2")
print("after reports   :", {g: sorted(h) for g, h in sorted(r.members.items())})
r.leave("hostA", "239.1.1.1")
print("hostA leaves    :", {g: sorted(h) for g, h in sorted(r.members.items())}, "(group still has hostB: keep forwarding)")
r.leave("hostC", "239.2.2.2")
print("hostC leaves    :", {g: sorted(h) for g, h in sorted(r.members.items())}, "(no members: stop forwarding 239.2.2.2)")
assert r.forward_group("239.1.1.1") and not r.forward_group("239.2.2.2")
print("check: OK")
r.query({"hostB": ["239.1.1.1"], "hostD": ["239.3.3.3"]})
print("periodic General Query: only hosts that still answer are remembered ->", {g: sorted(h) for g, h in sorted(r.members.items())})
print("IGMP (IP protocol 2): hosts <-> LOCAL router. Router sends periodic General Queries to 224.0.0.1;")
print("hosts answer with Membership Reports. v2 adds explicit Leave and group-specific query; v3 adds source filtering.")
print("IGMP only tells the last-hop router who is listening; routers use PIM/DVMRP to build the delivery tree.")
print("ICMP vs IGMP: ICMP reports errors/queries about unicast delivery (any host to any host);")
print("  IGMP manages multicast group membership (host to its directly connected router only).")


# ===== SECTION 3: FLOODING VS RPF =====
print("\n===== SECTION 3: MULTICAST TREE - FLOOD VS RPF =====")
LINKS = [("R1", "R2"), ("R1", "R3"), ("R2", "R3"), ("R2", "R4"), ("R3", "R4"), ("R3", "R5"), ("R4", "R5")]
ADJ: dict[str, list[str]] = {}
for a, b in LINKS:
    ADJ.setdefault(a, []).append(b)
    ADJ.setdefault(b, []).append(a)
print("links:", LINKS, "source attached to R1; receivers behind R4 only")


def naive_flood(ttl: int) -> int:
    sent, frontier = 0, [("R1", None, ttl)]
    while frontier:
        nxt = []
        for node, came, left in frontier:
            if left == 0:
                continue
            for nb in ADJ[node]:
                if nb != came:
                    sent += 1
                    nxt.append((nb, node, left - 1))
        frontier = nxt
    return sent


def shortest_parent() -> dict[str, str]:
    """Unicast next hop from each router back toward the source R1 (BFS)."""
    parent, queue = {"R1": ""}, ["R1"]
    for u in queue:
        for v in sorted(ADJ[u]):
            if v not in parent:
                parent[v] = u
                queue.append(v)
    return parent


def rpf_flood() -> tuple[int, int, list[tuple[str, str]]]:
    """Forward only if the packet arrived from the neighbour we would use to reach the source."""
    toward = shortest_parent()
    sent = dropped = 0
    delivered: list[tuple[str, str]] = []
    queue = [("R1", None)]
    seen_accept = set()
    for node, came in queue:
        if came is not None and toward[node] != came:
            dropped += 1                      # failed RPF check
            continue
        if node in seen_accept:
            continue
        seen_accept.add(node)
        for nb in sorted(ADJ[node]):
            if nb != came:
                sent += 1
                delivered.append((node, nb))
                queue.append((nb, node))
    return sent, dropped, delivered


print(f"naive flooding with TTL 4: {naive_flood(4)} transmissions (loops multiply copies)")
s, d, edges = rpf_flood()
print(f"RPF flooding: {s} transmissions, {d} copies dropped by the RPF check (arrived on the wrong interface)")
print("shortest-path tree toward source R1:", {k: v for k, v in shortest_parent().items() if v})
receivers = {"R4"}
toward = shortest_parent()
needed: set[str] = set()
for rcv in receivers:
    n = rcv
    while n != "R1":
        needed.add(n)
        n = toward[n]
print(f"after PRUNING branches with no receivers, routers on the tree: R1 + {sorted(needed)}")
pruned = [n for n in ADJ if n not in needed and n != "R1"]
print("pruned routers (no receivers downstream):", pruned if pruned else "none (every router leads to a receiver)")
assert s < naive_flood(4)
print("check: OK (RPF sends each copy over a loop-free tree: fewer transmissions than naive flooding)")
print("Flood-and-prune (DVMRP, PIM dense mode): flood with RPF, then prune; good for dense groups.")
print("Shared tree (PIM sparse mode, core-based): receivers explicitly JOIN toward a rendezvous point; good for sparse groups.")


# ===== SECTION 4: MOBILE IP TUNNEL SIMULATION =====
print("\n===== SECTION 4: MOBILE IP (HOME AGENT / FOREIGN AGENT / CARE-OF ADDRESS) =====")


@dataclass
class Pkt:
    src: str
    dst: str
    payload: object
    proto: int = 17

    def __str__(self) -> str:
        return f"[{self.src} -> {self.dst}]"


class HomeAgent:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.bindings: dict[str, str] = {}       # home address -> care-of address

    def register(self, home: str, coa: str) -> None:
        self.bindings[home] = coa

    def intercept(self, p: Pkt) -> Pkt:
        coa = self.bindings.get(p.dst)
        if coa is None:
            return p                              # mobile is at home: deliver normally
        return Pkt(self.ip, coa, p, proto=4)      # IP-in-IP tunnel (protocol 4)


class ForeignAgent:
    def __init__(self, coa: str) -> None:
        self.coa = coa

    def decapsulate(self, p: Pkt) -> Pkt:
        assert p.proto == 4 and p.dst == self.coa
        return p.payload


HOME = "10.1.0.77"        # mobile node's permanent home address (home network 10.1.0.0/16)
HA, FA_COA = "10.1.0.1", "172.20.5.1"
ha, fa = HomeAgent(HA), ForeignAgent(FA_COA)
print("1. Agent discovery: FA advertises (ICMP router advertisement extension), mobile learns care-of address", FA_COA)
print("2. Registration: mobile -> FA -> HA 'home", HOME, "is now reachable via", FA_COA + "'")
ha.register(HOME, FA_COA)
print("   HA binding table:", ha.bindings)
orig = Pkt("203.0.113.8", HOME, "hello mobile")
print("3. Correspondent sends to the HOME address:", orig)
tunnel = ha.intercept(orig)
print("4. HA intercepts and tunnels (outer protocol 4):", tunnel, "carrying", tunnel.payload)
inner = fa.decapsulate(tunnel)
print("5. FA decapsulates and hands to the mobile:", inner, inner.payload)
assert inner == orig
reply = Pkt(HOME, "203.0.113.8", "hi back")
print("6. Mobile replies DIRECTLY to the correspondent (no tunnel):", reply)
print("   Path in: CN -> HA -> FA -> MN, path back: MN -> CN  = triangle routing (inefficient).")
print("   Fix (route optimisation): CN learns the care-of address and sends straight to it.")
ha.bindings.clear()
print("7. Mobile returns home and deregisters -> HA delivers normally:", ha.intercept(orig))
print("check: OK")
print("TRAP: the CORRESPONDENT never knows the mobile moved; the home address stays constant so TCP connections survive.")
print("Two kinds of care-of address: FA care-of (shared by many mobiles, FA decapsulates) and")
print("co-located care-of (mobile gets its own temporary address, decapsulates itself).")
print("Registration has a lifetime and must be renewed; registration messages use UDP port 434.")


# ===== SECTION 5: SUMMARY =====
print("\n===== SECTION 5: COMPARISON TABLE =====")
rows = [("Delivery", "1 to 1", "1 to many (group)", "1 to all"),
        ("Address", "unicast IP", "class D 224.0.0.0/4", "255.255.255.255 / directed"),
        ("Copies on a link", "1 per receiver", "1 (shared tree)", "1 per network")]
print(f"{'':17} {'unicast':16} {'multicast':30} broadcast")
for row in rows:
    print(f"{row[0]:17} {row[1]:16} {row[2]:30} {row[3]}")
print("Multicast saves sender bandwidth: 1 stream to 1000 receivers instead of 1000 unicast streams;")
print(f"  e.g. a 2 Mbit/s video to 1000 viewers: unicast {2 * 1000} Mbit/s from the source, multicast 2 Mbit/s.")
