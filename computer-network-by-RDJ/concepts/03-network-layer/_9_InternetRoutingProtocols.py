# Tags: #Python #ComputerNetworks #NetworkLayer #InternetRoutingProtocols | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Internet routing: autonomous systems, IGP vs EGP, RIP (hop limit 15, timers),
OSPF cost, and BGP as a path-vector protocol with loop prevention and policy
(local preference), simulated on a small AS graph. In-memory only."""
from __future__ import annotations

from dataclasses import dataclass, field


# ===== SECTION 1: AUTONOMOUS SYSTEMS, IGP VS EGP =====
print("===== SECTION 1: AUTONOMOUS SYSTEMS, IGP VS EGP =====")
print("Autonomous System (AS): a set of networks under ONE administrative control with a")
print("  common routing policy, identified by an AS number (ASN). 64512-65534 are reserved for")
print("  private use; 32-bit ASNs also exist. 64496-64511 are reserved for documentation (RFC 5398).")
rows = [("RIP", "IGP", "distance vector", "hop count", "UDP 520"),
        ("OSPF", "IGP", "link state", "cost (bandwidth based)", "IP protocol 89"),
        ("BGP", "EGP", "path vector", "AS path + policy attributes", "TCP 179")]
print(f"{'protocol':9} {'type':5} {'algorithm':16} {'metric':28} transport")
for r in rows:
    print(f"{r[0]:9} {r[1]:5} {r[2]:16} {r[3]:28} {r[4]}")
print("IGP = routes INSIDE one AS (best path, fast).  EGP = routes BETWEEN ASes (policy first).")
print("BGP run between ASes is eBGP; run between routers of the same AS is iBGP.")


# ===== SECTION 2: RIP =====
print("\n===== SECTION 2: RIP (HOP LIMIT 15, TIMERS) =====")
RIP_INF = 16
print("RIP metric = hop count; 16 means unreachable, so the network diameter is limited to 15 hops.")
print("Timers (RFC 2453 defaults): update every 30 s, route times out after 180 s of silence,")
print("then it is advertised as 16 for a 120 s garbage-collection period before removal.")
print("RIPv1: classful, broadcast. RIPv2: sends the mask, multicasts to 224.0.0.9.")
print("RIP propagates one hop per update; simulate a chain R1-R2-...-R17 with synchronous updates:")
n_routers = 17
metric = {i: RIP_INF for i in range(1, n_routers + 1)}     # metric from router i to a net attached to R1
metric[1] = 1                                              # directly connected = 1 in RIP
for rnd in range(1, 20):
    new = dict(metric)
    for i in range(2, n_routers + 1):
        new[i] = min(RIP_INF, metric[i - 1] + 1)
    if new == metric:
        break
    metric = new
print("converged metrics for routers 1..17:", [metric[i] for i in range(1, n_routers + 1)])
print(f"R15 reaches the net with metric {metric[15]}; R16 and R17 get {metric[16]} = unreachable.")
assert metric[15] == 15 and metric[16] == 16 and metric[17] == 16
print("check: OK (the 16th router in a chain cannot be reached: hop limit 15)")


# ===== SECTION 3: OSPF COST =====
print("\n===== SECTION 3: OSPF COST =====")
REF = 100_000_000      # reference bandwidth in bit/s (a configurable value; 100 Mbit/s here)
links = {"10 Mbit/s": 10_000_000, "100 Mbit/s": 100_000_000, "1 Gbit/s": 1_000_000_000}
print(f"cost = reference bandwidth / interface bandwidth (reference here {REF // 10**6} Mbit/s, minimum 1)")
for name, bw in links.items():
    print(f"  {name:11} -> cost {max(1, REF // bw)}")
print("TRAP: with this reference, 100 Mbit/s and 1 Gbit/s links both get cost 1 -> OSPF cannot")
print("tell them apart; raise the reference bandwidth consistently on ALL routers.")
path_a = [10_000_000, 100_000_000]
path_b = [100_000_000, 100_000_000, 100_000_000]
ca, cb = sum(REF // b for b in path_a), sum(REF // b for b in path_b)
print(f"path A cost {ca} (10M+100M links) vs path B cost {cb} (three 100M links): OSPF picks {'B' if cb < ca else 'A'} (lowest total cost)")


# ===== SECTION 4: BGP PATH VECTOR AND POLICY =====
print("\n===== SECTION 4: BGP PATH-VECTOR SIMULATION =====")


@dataclass
class Route:
    prefix: str
    as_path: tuple[int, ...]
    local_pref: int = 100
    learned_from: int | None = None


@dataclass
class As:
    asn: int
    peers: list[int] = field(default_factory=list)
    pref: dict[int, int] = field(default_factory=dict)   # policy: local-pref per neighbour
    rib: dict[str, Route] = field(default_factory=dict)  # best route per prefix


def better(a: Route, b: Route) -> bool:
    """Decision (simplified): highest local-pref, then shortest AS path, then lowest neighbour ASN."""
    ka = (-a.local_pref, len(a.as_path), a.learned_from or 0)
    kb = (-b.local_pref, len(b.as_path), b.learned_from or 0)
    return ka < kb


def run_bgp(ases: dict[int, As], origin: int, prefix: str, verbose: bool = False) -> int:
    ases[origin].rib[prefix] = Route(prefix, (), 100, None)       # own network: empty path
    rounds, changed = 0, True
    rejected = 0
    while changed:
        changed, rounds = False, rounds + 1
        snapshot = {a: dict(x.rib) for a, x in ases.items()}
        for asn, node in ases.items():
            for peer in node.peers:
                for pfx, r in snapshot[peer].items():
                    adv_path = (peer,) + r.as_path           # peer prepends its own ASN when advertising
                    if asn in adv_path:
                        rejected += 1                        # loop prevention
                        continue
                    cand = Route(pfx, adv_path, node.pref.get(peer, 100), peer)
                    cur = node.rib.get(pfx)
                    if cur is None or better(cand, cur):
                        node.rib[pfx] = cand
                        changed = True
        if rounds > 20:
            break
    if verbose:
        print(f"  (converged in {rounds} rounds; {rejected} advertisements rejected by loop prevention)")
    return rejected


def build() -> dict[int, As]:
    peering = [(64501, 64502), (64501, 64503), (64502, 64504), (64503, 64504), (64504, 64505), (64503, 64505)]
    ases = {n: As(n) for n in range(64501, 64506)}
    for a, b in peering:
        ases[a].peers.append(b)
        ases[b].peers.append(a)
    return ases


PFX = "203.0.113.0/24"      # documentation prefix (RFC 5737)
print("(ASNs 64501-64505 are documentation ASNs, not real networks)")
print("Peering: 64501-64502, 64501-64503, 64502-64504, 64503-64504, 64504-64505, 64503-64505")
print(f"AS 64505 originates {PFX}. Best path chosen by each AS (shortest AS path, no policy):")
net = build()
run_bgp(net, 64505, PFX, verbose=True)
for asn in sorted(net):
    r = net[asn].rib[PFX]
    print(f"  AS{asn}: path {list(r.as_path) or '(origin)'} via {r.learned_from}")
assert net[64501].rib[PFX].as_path == (64503, 64505)
print("check: OK (64501 learns [64503, 64505]: 2 AS hops via 64503, shorter than via 64502)")

print("\nSame network, but AS 64501 has a policy: prefer routes from 64502 (e.g. cheaper transit), local-pref 200:")
net2 = build()
net2[64501].pref[64502] = 200
run_bgp(net2, 64505, PFX)
r = net2[64501].rib[PFX]
print(f"  AS64501 now uses path {list(r.as_path)} although it is longer: policy beats path length.")
assert r.as_path == (64502, 64504, 64505)
print("check: OK")
print("Loop prevention: a router that sees its OWN ASN in an AS path rejects the route:")
adv = (64502, 64501, 64505)
print(f"  AS64501 receives path {list(adv)} -> {'rejected (contains own ASN)' if 64501 in adv else 'accepted'}")
print("This is why BGP (path vector) has no count-to-infinity: the whole path is carried.")


# ===== SECTION 5: ADMINISTRATIVE DISTANCE =====
print("\n===== SECTION 5: ADMINISTRATIVE DISTANCE (CISCO DEFAULTS) =====")
AD = [("Directly connected", 0), ("Static route", 1), ("eBGP", 20), ("OSPF", 110), ("RIP", 120), ("iBGP", 200)]
print("Administrative distance = trustworthiness of the SOURCE of a route (lower wins).")
print("Values below are Cisco IOS defaults; other vendors use different numbers.")
for n, v in AD:
    print(f"  {n:20} {v:>3}")
cands = [("RIP", 120, 2), ("OSPF", 110, 30)]
winner = min(cands, key=lambda c: c[1])
print(f"Same prefix learned by RIP (metric 2) and OSPF (cost 30): installed from {winner[0]};")
print("AD decides BETWEEN protocols; metric only decides WITHIN one protocol.")
