# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Link-state routing: every router floods an LSA (with sequence number),
builds an identical link-state database (LSDB), and runs SPF (Dijkstra) on it.
Includes duplicate suppression, a link failure re-run, OSPF DR/BDR election and
a link-state vs distance-vector comparison."""
from __future__ import annotations

import heapq
from dataclasses import dataclass

INF = float("inf")
TOPOLOGY = {   # undirected link costs
    ("A", "B"): 2, ("A", "C"): 5, ("A", "D"): 1, ("B", "C"): 3, ("B", "D"): 2,
    ("C", "D"): 3, ("C", "E"): 1, ("D", "E"): 1, ("E", "F"): 2, ("C", "F"): 5,
}


@dataclass(frozen=True)
class Lsa:
    origin: str
    seq: int
    links: tuple[tuple[str, int], ...]      # (neighbour, cost)


class Router:
    def __init__(self, name: str) -> None:
        self.name = name
        self.lsdb: dict[str, Lsa] = {}

    def spf(self) -> tuple[dict[str, float], dict[str, str | None]]:
        graph = {o: dict(l.links) for o, l in self.lsdb.items()}
        dist = {n: INF for n in graph}
        first: dict[str, str | None] = {n: None for n in graph}
        dist[self.name] = 0
        heap = [(0, self.name, None)]
        done = set()
        while heap:
            d, u, fh = heapq.heappop(heap)
            if u in done:
                continue
            done.add(u)
            first[u] = fh
            for v, w in graph[u].items():
                if v in graph and d + w < dist[v]:     # v must have advertised itself
                    dist[v] = d + w
                    heapq.heappush(heap, (d + w, v, v if u == self.name else fh))
        return dist, first


class Domain:
    def __init__(self, links: dict[tuple[str, str], int]) -> None:
        self.links = dict(links)
        self.routers = {n: Router(n) for pair in links for n in pair}
        self.seq = {n: 0 for n in self.routers}
        self.messages = 0

    def neighbours(self, r: str) -> dict[str, int]:
        out = {}
        for (a, b), c in self.links.items():
            if a == r:
                out[b] = c
            elif b == r:
                out[a] = c
        return out

    def originate(self, r: str) -> Lsa:
        self.seq[r] += 1
        return Lsa(r, self.seq[r], tuple(sorted(self.neighbours(r).items())))

    def flood(self, lsa: Lsa, start: str, suppress: bool = True, ttl: int = 12, log: bool = False) -> int:
        """Deliver lsa starting at router `start`; returns messages sent."""
        sent = 0
        queue = [(start, None, ttl)]
        while queue:
            nxt = []
            for node, came, left in queue:
                r = self.routers[node]
                have = r.lsdb.get(lsa.origin)
                if suppress and have is not None and have.seq >= lsa.seq:
                    continue            # duplicate / old: do not forward
                r.lsdb[lsa.origin] = lsa
                if left == 0:
                    continue
                for nb in self.neighbours(node):
                    if nb != came:
                        sent += 1
                        nxt.append((nb, node, left - 1))
            queue = nxt
        self.messages += sent
        return sent


# ===== SECTION 1: LSA FLOODING =====
print("===== SECTION 1: LSA FLOODING =====")
dom = Domain(TOPOLOGY)
total = 0
for name in sorted(dom.routers):
    lsa = dom.originate(name)
    n = dom.flood(lsa, name)
    total += n
    print(f"router {name} originates LSA seq {lsa.seq} links={dict(lsa.links)} -> {n} messages")
print(f"total flooding messages: {total} for {len(dom.routers)} LSAs on {len(TOPOLOGY)} links")
print("Rule: install an LSA only if its sequence number is NEWER than the stored one,")
print("then forward it on every link except the one it came in on.")


# ===== SECTION 2: IDENTICAL LSDB AND SPF AT EACH ROUTER =====
print("\n===== SECTION 2: IDENTICAL LSDB + SPF PER ROUTER =====")
dbs = [{o: (l.seq, l.links) for o, l in r.lsdb.items()} for r in dom.routers.values()]
assert all(d == dbs[0] for d in dbs)
print("all", len(dbs), "routers hold the same LSDB with", len(dbs[0]), "LSAs: check OK")
print("LSDB (as a topology table):")
for o, (seq, links) in sorted(dbs[0].items()):
    print(f"  {o}: " + ", ".join(f"{n}={c}" for n, c in links))
print()
tables = {}
for name in sorted(dom.routers):
    dist, first = dom.routers[name].spf()
    tables[name] = (dist, first)
    cells = "  ".join(f"{d}:{int(dist[d])}via {first[d] or '-'}" for d in sorted(dist) if d != name)
    print(f"SPF at {name}: {cells}")


def reference(src: str, links: dict) -> dict[str, float]:
    """Bellman-Ford as an independent check."""
    nodes = {n for p in links for n in p}
    d = {n: INF for n in nodes}
    d[src] = 0
    for _ in nodes:
        for (a, b), c in links.items():
            if d[a] + c < d[b]:
                d[b] = d[a] + c
            if d[b] + c < d[a]:
                d[a] = d[b] + c
    return d


for name, (dist, _) in tables.items():
    assert dist == reference(name, TOPOLOGY)
print("check: OK (SPF distances at every router equal an independent Bellman-Ford)")


# ===== SECTION 3: TRAP - NO SEQUENCE NUMBER =====
print("\n===== SECTION 3: TRAP - FLOODING WITHOUT SEQUENCE NUMBERS =====")
d2 = Domain(TOPOLOGY)
lsa = d2.originate("A")
with_check = d2.flood(lsa, "A", suppress=True)
d3 = Domain(TOPOLOGY)
lsa3 = d3.originate("A")
without = d3.flood(lsa3, "A", suppress=False, ttl=6)
print(f"one LSA from A, with sequence check   : {with_check} messages")
print(f"one LSA from A, no check, hop limit 6 : {without} messages (duplicates multiply; without ANY limit it never ends)")
print("Stale LSA: an old copy (seq 1) arriving after seq 2 must be ignored:")
lsa_v2 = d2.originate("A")                     # seq 2
d2.flood(lsa_v2, "A")
stale_msgs = d2.flood(lsa, "A")                # the old seq-1 LSA arrives again
print(f"  every router now holds seq {d2.routers['F'].lsdb['A'].seq}; replaying seq 1 sends {stale_msgs} messages and changes nothing")
assert stale_msgs == 0 and d2.routers["F"].lsdb["A"].seq == 2


# ===== SECTION 4: LINK FAILURE =====
print("\n===== SECTION 4: LINK FAILURE (C-E DOWN) =====")
del dom.links[("C", "E")]
total = 0
for end in ("C", "E"):
    lsa = dom.originate(end)               # seq increments to 2
    total += dom.flood(lsa, end)
print(f"C and E re-originate LSAs (seq 2) -> {total} messages; every router re-runs SPF")
for name in ("A", "F"):
    dist, first = dom.routers[name].spf()
    print(f"SPF at {name}: " + "  ".join(f"{d}:{int(dist[d])}via {first[d] or '-'}" for d in sorted(dist) if d != name))
dist, first = dom.routers["A"].spf()
assert dist == reference("A", {k: v for k, v in TOPOLOGY.items() if k != ("C", "E")})
print("check: OK")
fd, ff = dom.routers["F"].spf()
print(f"F's cost to C changed {int(tables['F'][0]['C'])} -> {int(fd['C'])} (was via {tables['F'][1]['C']}, now via {ff['C']}): the direct F-C link is now best")
print("Only 2 LSAs were flooded: every router recomputes locally. No count-to-infinity.")


# ===== SECTION 5: OSPF OVERVIEW + COMPARISON =====
print("\n===== SECTION 5: OSPF OVERVIEW + COMPARISON =====")
print("OSPF: IP protocol number 89, link-state IGP. Cost = reference bandwidth / interface bandwidth.")
print("Areas: big AS split into areas; Area 0 is the backbone; every other area connects to it.")
print("  Area Border Routers (ABR) summarise routes between areas -> smaller LSDB, less flooding.")
print("Multi-access LAN: routers elect a Designated Router (DR) and Backup (BDR); all routers")
print("  exchange LSAs only with DR/BDR instead of a full mesh (n(n-1)/2 adjacencies).")
cands = {"R1": (1, "1.1.1.1"), "R2": (1, "2.2.2.2"), "R3": (100, "3.3.3.3"), "R4": (0, "4.4.4.4")}


def key(item):
    name, (prio, rid) = item
    return (prio, tuple(int(x) for x in rid.split(".")))


eligible = [(n, v) for n, v in cands.items() if v[0] > 0]      # priority 0 = never DR
ranked = sorted(eligible, key=key, reverse=True)
print("candidates (priority, router-id):", cands)
print(f"election: highest priority wins, ties broken by highest router ID -> DR={ranked[0][0]}, BDR={ranked[1][0]}")
print("R4 has priority 0: it can never become DR or BDR.")
n_rt = len(cands)
print(f"adjacencies for {n_rt} routers: full mesh {n_rt * (n_rt - 1) // 2}; with DR/BDR 2*(n-2)+1 = {2 * (n_rt - 2) + 1}")
rows = [("Topology knowledge", "neighbours' vectors only", "whole map (LSDB)"),
        ("Algorithm", "Bellman-Ford", "Dijkstra (SPF)"),
        ("Sends", "whole table, to neighbours", "own link states, to everyone (flood)"),
        ("Convergence", "slow, count-to-infinity", "fast, loop-free"),
        ("CPU / memory", "low", "higher"),
        ("Bandwidth", "periodic full tables", "small event-driven LSAs"),
        ("Scalability", "small networks (RIP max 15 hops)", "large, with areas"),
        ("Example", "RIP", "OSPF, IS-IS")]
print(f"{'':20} {'Distance vector':30} Link state")
for a, b, c in rows:
    print(f"{a:20} {b:30} {c}")
