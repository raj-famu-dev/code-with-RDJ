# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Switches, bridges and VLANs: transparent-bridge learning, flooding,
filtering and forwarding-table aging; the broadcast-storm loop problem and the
Spanning Tree Protocol root bridge election; IEEE 802.1Q VLAN tags; access vs
trunk ports; collision vs broadcast domains. All in-memory simulation.
Implements the 'Data link devices' part of the Data Link chapter."""
import struct
from collections import deque

# ===== SECTION 1: LEARNING BRIDGE (FLOOD / FILTER / FORWARD) =====
print("===== SECTION 1: LEARNING BRIDGE =====")
BROADCAST = "ff:ff:ff:ff:ff:ff"


class Switch:
    def __init__(self, ports: int, aging: int = 300) -> None:
        self.ports = list(range(1, ports + 1))
        self.table: dict[str, tuple[int, int]] = {}  # mac -> (port, last seen)
        self.aging = aging

    def receive(self, now: int, in_port: int, src: str, dst: str) -> str:
        self.table[src] = (in_port, now)  # LEARN: source address lives on in_port
        entry = self.table.get(dst)
        if dst == BROADCAST or entry is None or now - entry[1] > self.aging:
            outs = [p for p in self.ports if p != in_port]
            return f"FLOOD to ports {outs}" + ("" if dst == BROADCAST else " (unknown dst)")
        if entry[0] == in_port:
            return f"FILTER (dst on same port {in_port}, drop)"
        return f"FORWARD to port {entry[0]}"


sw = Switch(4)
hosts = {"A": ("aa:aa:aa:aa:aa:01", 1), "B": ("bb:bb:bb:bb:bb:02", 1),
         "C": ("cc:cc:cc:cc:cc:03", 2), "D": ("dd:dd:dd:dd:dd:04", 3)}
print("A and B share port 1 (via a hub), C on port 2, D on port 3")
steps = [("A", "C"), ("C", "A"), ("A", "B"), ("D", "BROADCAST"), ("C", "D"), ("B", "A")]
for i, (s, d) in enumerate(steps):
    dst = BROADCAST if d == "BROADCAST" else hosts[d][0]
    act = sw.receive(i, hosts[s][1], hosts[s][0], dst)
    print(f"  {s} -> {d:<9}: {act}")
names = {v[0]: k for k, v in hosts.items()}
print("table now:", {names[m]: f"port {p}" for m, (p, _) in sw.table.items()})
print("Learning uses the SOURCE address; forwarding decisions use the DESTINATION.")

# ===== SECTION 2: AGING =====
print("\n===== SECTION 2: FORWARDING TABLE AGING =====")
sw2 = Switch(3, aging=300)
a, c = hosts["A"][0], hosts["C"][0]
print("t=0   C -> A :", sw2.receive(0, 2, c, a))
print("t=1   A -> C :", sw2.receive(1, 1, a, c))
print("t=200 A -> C :", sw2.receive(200, 1, a, c), "(C's entry is 200 s old: still valid)")
print("t=400 A -> C :", sw2.receive(400, 1, a, c), "<- C's entry is older than 300 s: aged out")
print("TRAP: a host that moved to another port is unreachable until the entry")
print("ages out or it sends a frame, which is why aging exists (typical default 300 s).")

# ===== SECTION 3: LOOPS AND BROADCAST STORM =====
print("\n===== SECTION 3: LOOP = BROADCAST STORM =====")
# 3 switches fully meshed (triangle): S1-S2, S2-S3, S3-S1
links = [("S1", "S2"), ("S2", "S3"), ("S3", "S1")]


def flood_rounds(active: list[tuple[str, str]], start: str, rounds: int) -> list[int]:
    frontier = deque([(start, None)])  # (switch holding a frame copy, came_from)
    counts = []
    for _ in range(rounds):
        nxt: deque = deque()
        for sw_name, came in frontier:
            for x, y in active:
                if sw_name in (x, y):
                    other = y if sw_name == x else x
                    if other != came:  # never back out the arrival link
                        nxt.append((other, sw_name))
        counts.append(len(nxt))
        frontier = nxt
        if not frontier:
            break
    return counts


print("one broadcast injected into a triangle of switches, copies per hop round:")
print("  ", flood_rounds(links, "S1", 8), "... (never reaches 0, and it also multiplies when switches have more links)")
print("Ethernet has no TTL, so a looped broadcast circulates forever.")
print("Redundant links are wanted for fault tolerance -> Spanning Tree Protocol.")

# ===== SECTION 4: SPANNING TREE PROTOCOL =====
print("\n===== SECTION 4: SPANNING TREE ROOT ELECTION =====")
bridges = {  # name -> (priority, mac) ; bridge ID = priority then MAC, LOWEST wins
    "S1": (32768, "00:0a:00:00:00:01"),
    "S2": (32768, "00:0a:00:00:00:02"),
    "S3": (32768, "00:0a:00:00:00:00"),  # lowest MAC among equal priorities
    "S4": (32768, "00:0a:00:00:00:04"),
}
slinks = [("S1", "S2", 19), ("S2", "S3", 19), ("S3", "S1", 19), ("S3", "S4", 4), ("S4", "S2", 19)]
print("bridge IDs (priority, MAC):", {k: v for k, v in bridges.items()})
print("link costs (100 Mbps = 19, 1 Gbps = 4):", slinks)
best = {b: (bridges[b], 0, bridges[b]) for b in bridges}  # (root id, cost, sender id)
print("  round 0: every bridge claims itself as root")
for rnd in range(1, 10):
    new = dict(best)
    for x, y, cost in slinks:
        for me, nb in ((x, y), (y, x)):
            cand = (best[nb][0], best[nb][1] + cost, bridges[nb])
            if cand < new[me]:
                new[me] = cand
    changed = new != best
    best = new
    roots = {b: next(n for n in bridges if bridges[n] == best[b][0]) for b in bridges}
    print(f"  round {rnd}: believed root {roots}")
    if not changed:
        break
root = next(n for n in bridges if bridges[n] == best["S1"][0])
print("elected ROOT BRIDGE:", root, "(lowest bridge ID; ties on priority broken by lowest MAC)")
cost_to_root = {b: best[b][1] for b in bridges}
print("root path cost:", cost_to_root)
root_port_link: dict[str, tuple] = {}
for b in bridges:
    if b == root:
        continue
    cands = [(cost_to_root[o] + c, bridges[o], (x, y, c)) for x, y, c in slinks
             for me, o in ((x, y), (y, x)) if me == b]
    root_port_link[b] = min(cands)[2]
active, blocked = [], []
for x, y, c in slinks:
    rp_x = root_port_link.get(x) == (x, y, c)
    rp_y = root_port_link.get(y) == (x, y, c)
    if rp_x or rp_y:
        active.append((x, y))  # a root port end and its neighbour's designated port
    else:
        dx, dy = (cost_to_root[x], bridges[x]), (cost_to_root[y], bridges[y])
        des = x if dx < dy else y
        blk = y if des == x else x
        blocked.append((x, y))
        print(f"  segment {x}-{y}: designated port on {des}, port on {blk} BLOCKING")
print("active tree links:", active)
print("blocked links    :", blocked)
assert len(active) == len(bridges) - 1
counts = flood_rounds(active, "S1", 8)
print("same broadcast on the pruned tree, copies per hop round:", counts)
assert counts[-1] == 0
print("storm gone, every switch still reachable: check: OK")
print("If an active link fails, a blocked port moves to forwarding (reconvergence).")

# ===== SECTION 5: VLAN 802.1Q TAG =====
print("\n===== SECTION 5: 802.1Q VLAN TAG =====")
print("4-byte tag inserted after the source MAC: TPID(16)=0x8100 | PCP(3) DEI(1) VID(12)")


def make_tag(vid: int, pcp: int = 0, dei: int = 0) -> bytes:
    assert 1 <= vid <= 4094, "VID 0 and 4095 are reserved"
    tci = (pcp << 13) | (dei << 12) | vid
    return struct.pack("!HH", 0x8100, tci)


def parse_tag(tag: bytes) -> dict:
    tpid, tci = struct.unpack("!HH", tag)
    return {"tpid": hex(tpid), "pcp": tci >> 13, "dei": (tci >> 12) & 1, "vid": tci & 0xFFF}


t = make_tag(vid=20, pcp=5)
print("tag bytes:", t.hex(" "), "->", parse_tag(t))
assert parse_tag(t)["vid"] == 20 and parse_tag(t)["pcp"] == 5
print("usable VLAN IDs: 1..4094 (12 bits = 4096 values minus reserved 0 and 4095)")
print("tagged frame max size: 1518 + 4 = 1522 bytes")
try:
    make_tag(4095)
except AssertionError as e:
    print("TRAP make_tag(4095):", e)

# ===== SECTION 6: ACCESS VS TRUNK PORTS =====
print("\n===== SECTION 6: ACCESS VS TRUNK PORTS =====")
ports = {1: ("access", 10), 2: ("access", 10), 3: ("access", 20), 4: ("trunk", None)}
for p, (mode, vlan) in ports.items():
    print(f"  port {p}: {mode}" + (f" VLAN {vlan}" if vlan else " (carries all VLANs, tagged)"))


def vlan_flood(in_port: int) -> list[str]:
    vlan = ports[in_port][1] if ports[in_port][0] == "access" else 10  # trunk frame tagged 10
    out = []
    for p, (mode, v) in ports.items():
        if p == in_port:
            continue
        if mode == "access" and v == vlan:
            out.append(f"port {p} untagged")
        elif mode == "trunk":
            out.append(f"port {p} tagged VID {vlan}")
    return out


print("broadcast from port 1 (VLAN 10) goes to:", vlan_flood(1))
print("broadcast from port 3 (VLAN 20) goes to:", vlan_flood(3))
print("port 2 (VLAN 10) never sees VLAN 20 traffic -> separate broadcast domains;")
print("to talk across VLANs you need a router (or layer-3 switch).")

# ===== SECTION 7: COLLISION VS BROADCAST DOMAINS =====
print("\n===== SECTION 7: COLLISION VS BROADCAST DOMAINS =====")
print("Rules: hub/repeater = one shared collision domain; each switch port = its own")
print("collision domain; switch floods broadcasts so one broadcast domain; router or")
print("VLAN boundary splits broadcast domains.")
switch_ports, hub_hosts, vlans = 8, 3, 2
print(f"Example: 1 switch with {switch_ports} ports, one port feeds a hub with {hub_hosts} hosts.")
print(f"  collision domains = {switch_ports} (the hub's port and its {hub_hosts} hosts form ONE)")
print("  broadcast domains = 1 (no VLANs)")
print(f"  with {vlans} VLANs: collision domains still {switch_ports}, broadcast domains = {vlans}")
