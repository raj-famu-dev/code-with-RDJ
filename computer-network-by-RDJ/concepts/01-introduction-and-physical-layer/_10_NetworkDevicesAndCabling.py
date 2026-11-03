# Tags: #Python #ComputerNetworks #PhysicalLayer #NetworkDevicesCabling | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Network devices and cabling: repeater, hub, bridge, switch, router, gateway, NIC,
modem and access point; collision vs broadcast domains counted from a topology; a
hub-vs-switch forwarding simulation with MAC learning; straight-through vs crossover
cables checked pin by pin. Implements the 'network devices' syllabus topic."""
from dataclasses import dataclass, field

# ===== SECTION 1: DEVICE SUMMARY =====
print("===== SECTION 1: DEVICE SUMMARY =====")
devices = [
    ("Repeater", "1 Physical", "regenerates/amplifies the signal to extend distance", "joins", "joins"),
    ("Hub", "1 Physical", "multiport repeater; sends every bit out of all other ports", "joins", "joins"),
    ("Bridge", "2 Data link", "joins 2 LAN segments; learns MACs and filters", "separates", "joins"),
    ("Switch", "2 Data link", "multiport bridge; per-port forwarding by MAC table", "separates (per port)", "joins (unless VLANs)"),
    ("Router", "3 Network", "forwards packets between networks using IP", "separates", "separates"),
    ("Gateway", "up to 7", "protocol converter between different architectures", "separates", "separates"),
    ("NIC", "1-2", "adapter with a MAC address that connects a host to the medium", "-", "-"),
    ("Modem", "1 Physical", "modulates/demodulates between digital data and an analog line", "-", "-"),
    ("Access point", "1-2", "bridges wireless clients (Wi-Fi) onto a wired LAN", "joins (shared air)", "joins"),
]
print(f"{'device':<14}{'layer':<13}{'collision dom.':<22}{'broadcast dom.':<22}job")
for name, layer, job, coll, bcast in devices:
    print(f"{name:<14}{layer:<13}{coll:<22}{bcast:<22}{job}")
print("Rule: hubs/repeaters EXTEND a collision domain; switches/bridges SPLIT collision domains; only routers split broadcast domains.")


# ===== SECTION 2: COUNTING COLLISION AND BROADCAST DOMAINS =====
print("\n===== SECTION 2: COUNTING COLLISION AND BROADCAST DOMAINS =====")
SHARED = {"host", "hub", "repeater", "ap"}        # share one medium with neighbours
SWITCHING = {"switch", "bridge", "router"}         # every port isolates its own segment


@dataclass
class Net:
    kinds: dict[str, str] = field(default_factory=dict)
    links: list[tuple[str, str]] = field(default_factory=list)

    def add(self, name: str, kind: str) -> None:
        self.kinds[name] = kind

    def link(self, a: str, b: str) -> None:
        self.links.append((a, b))

    def _components(self, members: set[str], via: list[tuple[str, str]]) -> int:
        parent = {m: m for m in members}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b in via:
            if a in members and b in members:
                parent[find(a)] = find(b)
        return len({find(m) for m in members})

    def collision_domains(self) -> int:
        shared = {n for n, k in self.kinds.items() if k in SHARED}
        comps = self._components(shared, self.links)
        switch_to_switch = sum(1 for a, b in self.links
                               if self.kinds[a] in SWITCHING and self.kinds[b] in SWITCHING)
        return comps + switch_to_switch

    def broadcast_domains(self) -> int:
        non_router = {n for n, k in self.kinds.items() if k != "router"}
        comps = self._components(non_router, self.links)
        router_to_router = sum(1 for a, b in self.links
                               if self.kinds[a] == "router" and self.kinds[b] == "router")
        return comps + router_to_router


def build(spec: list[tuple[str, str]], links: list[tuple[str, str]]) -> Net:
    n = Net()
    for name, kind in spec:
        n.add(name, kind)
    for a, b in links:
        n.link(a, b)
    return n


# A: one hub, 4 hosts
a = build([("H", "hub")] + [(f"h{i}", "host") for i in range(1, 5)], [("H", f"h{i}") for i in range(1, 5)])
# B: one switch, 4 hosts
b = build([("S", "switch")] + [(f"h{i}", "host") for i in range(1, 5)], [("S", f"h{i}") for i in range(1, 5)])
# C: router joining two switches, 3 hosts each
c = build([("R", "router"), ("S1", "switch"), ("S2", "switch")] + [(f"a{i}", "host") for i in range(3)] + [(f"b{i}", "host") for i in range(3)],
          [("R", "S1"), ("R", "S2")] + [("S1", f"a{i}") for i in range(3)] + [("S2", f"b{i}") for i in range(3)])
# D: hub with 3 hosts -> switch (+2 hosts) -> router -> 1 host
d = build([("H", "hub"), ("S", "switch"), ("R", "router")] + [(f"x{i}", "host") for i in range(3)] + [("y1", "host"), ("y2", "host"), ("z", "host")],
          [("H", f"x{i}") for i in range(3)] + [("S", "H"), ("S", "y1"), ("S", "y2"), ("S", "R"), ("R", "z")])
print(f"{'topology':<46}{'collision':>10}{'broadcast':>10}")
cases = [("A: 1 hub + 4 hosts", a, 1, 1), ("B: 1 switch + 4 hosts", b, 4, 1),
         ("C: router + 2 switches x 3 hosts", c, 8, 2),
         ("D: hub(3)->switch(+2)->router->1 host", d, 5, 2)]
for label, net, exp_c, exp_b in cases:
    cd, bd = net.collision_domains(), net.broadcast_domains()
    assert (cd, bd) == (exp_c, exp_b), (label, cd, bd)
    print(f"{label:<46}{cd:>10}{bd:>10}")
print("Hand check C: 6 host-switch links + 2 router-switch links = 8 collision domains; router splits 2 broadcast domains.")
print("Trap: a switch splits collision domains but NOT broadcast domains; an ARP request still floods every port of every switch.")
print("check: OK")


# ===== SECTION 3: HUB vs SWITCH FORWARDING =====
print("\n===== SECTION 3: HUB vs SWITCH FORWARDING =====")
PORTS = {"A": 1, "B": 2, "C": 3, "D": 4}       # host -> port number
FRAMES = [("A", "B"), ("B", "A"), ("A", "C"), ("C", "A"), ("A", "B"), ("B", "C"),
          ("C", "B"), ("A", "D"), ("D", "A"), ("A", "broadcast")]


def hub_forward(src: str, dst: str, in_port: int) -> list[int]:
    return [p for p in PORTS.values() if p != in_port]


class Switch:
    def __init__(self) -> None:
        self.table: dict[str, int] = {}

    def forward(self, src: str, dst: str, in_port: int) -> list[int]:
        self.table[src] = in_port                       # LEARN: source MAC seen on in_port
        if dst in self.table and self.table[dst] != in_port:
            return [self.table[dst]]                    # FORWARD: known destination, one port
        if dst in self.table:
            return []                                   # FILTER: destination on the same port as source
        return [p for p in PORTS.values() if p != in_port]   # FLOOD: unknown or broadcast


sw = Switch()
hub_copies = sw_copies = 0
print(f"{'frame':<24}{'hub sends to ports':<22}{'switch sends to ports':<24}switch table after")
for src, dst in FRAMES:
    p = PORTS[src]
    h = hub_forward(src, dst, p)
    s = sw.forward(src, dst, p)
    hub_copies += len(h)
    sw_copies += len(s)
    print(f"{src + ' -> ' + dst:<24}{str(h):<22}{str(s):<24}{dict(sw.table)}")
print(f"total frame copies sent: hub = {hub_copies}, switch = {sw_copies}")
print("Unknown destinations flood (A->B, A->C, A->D the first time); once a MAC is learned, frames go out ONE port. Broadcasts always flood.")
assert hub_copies == 30 and sw_copies == 3 + 1 + 3 + 1 + 1 + 1 + 1 + 3 + 1 + 3
assert sw.table == {"A": 1, "B": 2, "C": 3, "D": 4}

# Trap: stale MAC table entry after a host moves to another port.
print("\nTrap: host B is unplugged and moved from port 2 to a spare port 5 (nothing is sent yet).")
stale = sw.forward("A", "B", 1)
print(f"  A -> B goes to ports {stale}: the stale entry still says port 2, so B (now on port 5) never receives it.")
print("  Fix: B transmits once (the switch relearns port 5) or the entry ages out (typical default is a few minutes).")
sw.forward("B", "A", 5)
print(f"  after B transmits on port 5: A -> B goes to ports {sw.forward('A', 'B', 1)}")
assert sw.forward("A", "B", 1) == [5] and stale == [2]
print("check: OK")


# ===== SECTION 4: STRAIGHT-THROUGH vs CROSSOVER CABLES =====
print("\n===== SECTION 4: STRAIGHT-THROUGH vs CROSSOVER CABLES =====")
T568B = ["white/orange", "orange", "white/green", "blue", "white/blue", "green", "white/brown", "brown"]
T568A = ["white/green", "green", "white/orange", "blue", "white/blue", "orange", "white/brown", "brown"]
print("pin   T568A         T568B")
for i in range(8):
    print(f" {i + 1}    {T568A[i]:<14}{T568B[i]}")


def cable_map(end1: list[str], end2: list[str]) -> dict[int, int]:
    """Which pin on the far end does each near-end pin reach (matching wire colours)."""
    return {i + 1: end2.index(colour) + 1 for i, colour in enumerate(end1)}


straight = cable_map(T568B, T568B)
cross = cable_map(T568A, T568B)
print("straight-through (B on both ends):", straight)
print("crossover (A on one end, B on the other): pins that change =", {k: v for k, v in cross.items() if k != v})
assert {k: v for k, v in cross.items() if k != v} == {1: 3, 2: 6, 3: 1, 6: 2}

# 10/100BASE-T: MDI devices (PC NIC, router port) transmit on pins 1,2 and receive on 3,6; MDI-X (hub, switch) the opposite.
TX = {"MDI": {1, 2}, "MDI-X": {3, 6}}
RX = {"MDI": {3, 6}, "MDI-X": {1, 2}}
KIND = {"PC": "MDI", "router": "MDI", "switch": "MDI-X", "hub": "MDI-X"}


def link_works(dev1: str, dev2: str, cable: dict[int, int]) -> bool:
    """Every transmit pin of end 1 must arrive on a receive pin of end 2 (and vice versa)."""
    inverse = {v: k for k, v in cable.items()}
    fwd = all(cable[p] in RX[KIND[dev2]] for p in TX[KIND[dev1]])
    back = all(inverse[p] in RX[KIND[dev1]] for p in TX[KIND[dev2]])
    return fwd and back


print(f"\n{'link':<20}{'straight-through':<20}{'crossover':<12}rule")
pairs = [("PC", "switch"), ("PC", "hub"), ("router", "switch"), ("PC", "PC"), ("PC", "router"), ("switch", "switch"), ("hub", "switch")]
for x, y in pairs:
    s_ok, c_ok = link_works(x, y, straight), link_works(x, y, cross)
    rule = "unlike devices -> straight" if KIND[x] != KIND[y] else "like devices -> crossover"
    print(f"{x + ' - ' + y:<20}{'works' if s_ok else 'NO LINK':<20}{'works' if c_ok else 'NO LINK':<12}{rule}")
    assert (s_ok, c_ok) == ((True, False) if KIND[x] != KIND[y] else (False, True))
print("Modern NICs and switch ports use Auto-MDI/MDI-X and fix the mismatch themselves; Gigabit uses all 4 pairs,")
print("so a real gigabit crossover also swaps pairs 4-5 with 7-8. Memory trick: like-to-like needs a cross.")
print("check: OK")


# ===== SECTION 5: WORKED EXAMPLE =====
print("\n===== SECTION 5: WORKED EXAMPLE =====")
print("Problem: a switch with 8 PCs, joined by a router to a second switch with 5 PCs. Count the domains.")
w = build([("R", "router"), ("S1", "switch"), ("S2", "switch")] + [(f"p{i}", "host") for i in range(8)] + [(f"q{i}", "host") for i in range(5)],
          [("R", "S1"), ("R", "S2")] + [("S1", f"p{i}") for i in range(8)] + [("S2", f"q{i}") for i in range(5)])
print(f"collision domains = {w.collision_domains()} (8 + 5 host links + 2 router links = 15)")
print(f"broadcast domains = {w.broadcast_domains()} (one per router interface side)")
assert (w.collision_domains(), w.broadcast_domains()) == (15, 2)
print("check: OK")
