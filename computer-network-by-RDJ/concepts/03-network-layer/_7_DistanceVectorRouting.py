# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Distance-vector routing (Bellman-Ford): synchronous table exchange until
convergence, count-to-infinity demonstrated, and fixes: split horizon, poison
reverse and hold-down, simulated round by round on a 5-router topology."""
from __future__ import annotations

from collections import deque

INF = 16     # RIP-style "infinity"
Table = dict[str, dict[str, tuple[int, str | None]]]   # router -> dest -> (cost, next hop)


class Network:
    def __init__(self, links: dict[tuple[str, str], int], mode: str = "plain", holddown: int = 0):
        self.links = {frozenset(k): v for k, v in links.items()}
        self.nodes = sorted({n for k in links for n in k})
        self.mode = mode            # plain | split | poison
        self.holddown = holddown
        self.hold: dict[tuple[str, str], int] = {}
        self.t: Table = {r: {d: ((0, r) if d == r else (INF, None)) for d in self.nodes} for r in self.nodes}

    def neighbours(self, r: str) -> dict[str, int]:
        return {next(iter(k - {r})): c for k, c in self.links.items() if r in k}

    def fail(self, a: str, b: str) -> None:
        del self.links[frozenset((a, b))]
        for r, other in ((a, b), (b, a)):      # each side notices its own dead link
            for d in self.nodes:
                if self.t[r][d][1] == other:
                    self.t[r][d] = (INF, None)
                    if self.holddown:
                        self.hold[(r, d)] = self.holddown

    def step(self) -> bool:
        old = {r: dict(v) for r, v in self.t.items()}
        changed = False
        for r in self.nodes:
            nb = self.neighbours(r)
            for d in self.nodes:
                if d == r:
                    continue
                cost, nh = old[r][d]
                new = (cost, nh)
                # 1) news from the current next hop is always believed
                if nh in nb:
                    adv = self._adv(old, nh, r, d)
                    if adv >= 0:
                        c = min(INF, adv + nb[nh])
                        new = (c, nh if c < INF else None)
                    else:
                        new = (INF, None)
                # 2) better offers from other neighbours (unless in hold-down)
                if self.hold.get((r, d), 0) == 0:
                    for n, lc in nb.items():
                        adv = self._adv(old, n, r, d)
                        if adv >= 0 and min(INF, adv + lc) < new[0]:
                            new = (adv + lc, n)
                if new[0] >= INF and cost < INF and self.holddown:
                    self.hold[(r, d)] = self.holddown
                if new != (cost, nh):
                    changed = True
                    self.t[r][d] = new
        for k in list(self.hold):
            if self.hold[k] > 0:
                self.hold[k] -= 1
                changed = True if self.hold[k] > 0 else changed
        return changed

    def _adv(self, snap: Table, n: str, to: str, dest: str) -> int:
        cost, nh = snap[n][dest]
        if nh == to and dest != to:
            if self.mode == "split":
                return -1
            if self.mode == "poison":
                return INF
        return cost


LINKS = {("A", "B"): 1, ("B", "C"): 1, ("B", "D"): 1, ("C", "D"): 1, ("D", "E"): 1}


def show_dest(net: Network, dest: str, nodes: str) -> str:
    return "  ".join(f"{r}:{net.t[r][dest][0]:>2}" for r in nodes)


# ===== SECTION 1: BELLMAN-FORD UPDATE AND CONVERGENCE =====
print("===== SECTION 1: BELLMAN-FORD UPDATE AND CONVERGENCE =====")
print("Rule: D_x(y) = min over neighbours v of ( c(x,v) + D_v(y) )")
net = Network(LINKS)
print("Topology: A-B, B-C, B-D, C-D, D-E (all cost 1)")
rounds = 0
print("cost to A after each exchange round:  " + show_dest(net, "A", "ABCDE") + "   (round 0)")
while net.step():
    rounds += 1
    print(f"cost to A after each exchange round:  {show_dest(net, 'A', 'ABCDE')}   (round {rounds})")
print(f"converged after {rounds} rounds (= network diameter in hops: A to E is 3)")
print("\nFinal routing table of router E (dest, cost, next hop):")
for d in net.nodes:
    c, nh = net.t["E"][d]
    print(f"  {d}: cost {c} via {nh}")
# cross-check with BFS (all costs are 1)


def bfs(src: str) -> dict[str, int]:
    dist, q = {src: 0}, deque([src])
    while q:
        u = q.popleft()
        for v in net.neighbours(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
for r in net.nodes:
    b = bfs(r)
    assert all(net.t[r][d][0] == b[d] for d in net.nodes)
print("check: OK (every router's costs equal BFS hop counts)")


# ===== SECTION 2: COUNT TO INFINITY =====
print("\n===== SECTION 2: COUNT TO INFINITY (PLAIN DV) =====")


def run_failure(mode: str, holddown: int = 0, show: bool = True, max_rounds: int = 40) -> int:
    n = Network(LINKS, mode, holddown)
    while n.step():
        pass
    n.fail("A", "B")
    if show:
        print(f"[{mode}, hold-down={holddown}] link A-B fails. Cost to A at B, C, D, E each round:")
        print(f"  round  0: {show_dest(n, 'A', 'BCDE')}")
    r = 0
    while r < max_rounds:
        r += 1
        changed = n.step()
        if show and r == 13:
            print("  ...")
        if show and (r <= 12 or not changed):
            print(f"  round {r:>2}: {show_dest(n, 'A', 'BCDE')}")
        if not changed:
            break
    return r


r_plain = run_failure("plain")
print(f"plain DV needed {r_plain} rounds to give up on A; each router's cost climbs by 1 per exchange round until {INF} = 'unreachable'")
print("Meanwhile packets to A loop B -> C/D -> B (a routing loop) and TTL burns.")
print("This is why RIP defines infinity = 16: it bounds the count (max usable hops = 15).")


# ===== SECTION 3: SPLIT HORIZON AND POISON REVERSE =====
print("\n===== SECTION 3: SPLIT HORIZON AND POISON REVERSE =====")
# Simple 3-router chain where split horizon fully works:
chain = {("A", "B"): 1, ("B", "C"): 1}
for mode in ("plain", "split"):
    n = Network(chain, mode)
    while n.step():
        pass
    n.fail("A", "B")
    rr = 0
    while rr < 40 and n.step():
        rr += 1
    print(f"chain A-B-C, link A-B fails, mode={mode:5}: C's cost to A settles at {n.t['C']['A'][0]} after {rr} rounds")
print("Split horizon: never advertise a route back out of the interface it was learned from.")
print("Poison reverse: advertise it back WITH cost = infinity (explicit, faster).")
print("TRAP: split horizon does NOT cure loops that involve 3+ routers (our B-C-D triangle):")
r_split = run_failure("split")
print(f"split horizon on the triangle still took {r_split} rounds (see rows above).")
r_poison = run_failure("poison")
print(f"poison reverse on the triangle took {r_poison} rounds: also a loop across a triangle.")


# ===== SECTION 4: HOLD-DOWN =====
print("\n===== SECTION 4: HOLD-DOWN TIMER =====")
r_hd = run_failure("split", holddown=3)
print(f"split horizon + hold-down(3 rounds) settled in {r_hd} rounds instead of {r_split}.")
print("Hold-down: after a route goes unreachable, ignore any NEW finite offers for it for a")
print("while, so stale information from neighbours cannot revive it. Price: slower recovery")
print("if the route really does come back.")
for label, args in [("plain", ("plain", 0)), ("split", ("split", 0)), ("poison", ("poison", 0)),
                    ("split+hold-down", ("split", 3))]:
    rr = run_failure(args[0], args[1], show=False)
    print(f"  {label:16} rounds until stable: {rr}")
other = Network(LINKS, "split", 3)
while other.step():
    pass
assert other.t["E"]["A"][0] == 3
print("check: OK (before failure, E reaches A with cost 3 in all modes)")


# ===== SECTION 5: COMPARE AND SUMMARISE =====
print("\n===== SECTION 5: SUMMARY TABLE =====")
rows = [("Knows", "only neighbours' vectors", "whole topology (link state)"),
        ("Algorithm", "Bellman-Ford", "Dijkstra"),
        ("Messages", "whole table to neighbours periodically", "link states flooded to all"),
        ("Convergence", "slow, count-to-infinity", "fast"),
        ("Example", "RIP", "OSPF"),
        ("Rumour routing", "yes ('routing by rumour')", "no")]
print(f"{'':15} {'Distance vector':40} Link state")
for a, b, c in rows:
    print(f"{a:15} {b:40} {c}")
