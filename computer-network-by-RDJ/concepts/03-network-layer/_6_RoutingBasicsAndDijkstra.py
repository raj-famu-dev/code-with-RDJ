# Tags: #Python #ComputerNetworks #NetworkLayer #RoutingBasicsDijkstra | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Routing basics (static vs dynamic, adaptive vs non-adaptive), flooding with a
hop counter, and Dijkstra's shortest-path algorithm with a step table and
path reconstruction, cross-checked against a brute-force search."""
import heapq
import itertools

INF = float("inf")
GRAPH = {   # undirected weighted graph (link costs)
    "A": {"B": 2, "C": 5, "D": 1},
    "B": {"A": 2, "C": 3, "D": 2},
    "C": {"A": 5, "B": 3, "D": 3, "E": 1, "F": 5},
    "D": {"A": 1, "B": 2, "C": 3, "E": 1},
    "E": {"C": 1, "D": 1, "F": 2},
    "F": {"C": 5, "E": 2},
}


# ===== SECTION 1: CLASSIFICATION =====
print("===== SECTION 1: CLASSIFICATION OF ROUTING =====")
print("Static (non-adaptive): table set by hand, ignores traffic/topology changes")
print("Dynamic (adaptive)   : protocol updates table when topology/traffic changes")
print("Centralised vs distributed: one route-control centre vs every router computes")
print("Flat vs hierarchical : all routers equal vs regions/areas/AS")
print("Static pros: no protocol overhead, predictable, secure. Cons: no fault tolerance, hard to scale.")
print("Dynamic pros: self-healing, scales. Cons: CPU/bandwidth for updates, convergence time.")
print("Optimality principle: if R is on the best path from I to J, the best path from R to J")
print("follows the same route -> best routes to one destination form a sink TREE.")


# ===== SECTION 2: FLOODING =====
print("\n===== SECTION 2: FLOODING =====")


def flood(src: str, hops: int) -> tuple[int, dict[str, int]]:
    """Every router forwards a packet on all links except the one it arrived on,
    until the hop counter is 0.  Returns (total transmissions, copies per node)."""
    copies = {n: 0 for n in GRAPH}
    sent = 0
    frontier = [(src, None, hops)]
    while frontier:
        nxt = []
        for node, came_from, left in frontier:
            copies[node] += 1
            if left == 0:
                continue
            for nb in GRAPH[node]:
                if nb != came_from:
                    sent += 1
                    nxt.append((nb, node, left - 1))
        frontier = nxt
    return sent, copies


for hops in (1, 2, 3, 4):
    sent, copies = flood("A", hops)
    print(f"hop limit {hops}: {sent:>4} transmissions; copies at F = {copies['F']}")
print("Without a hop counter or sequence-number duplicate check flooding never stops (loops).")
print("Flooding always finds the shortest path (one copy takes it) and is very robust,")
print("but wastes bandwidth; used for link-state advertisements and in military nets.")


# ===== SECTION 3: DIJKSTRA STEP TABLE =====
print("\n===== SECTION 3: DIJKSTRA WITH STEP TABLE =====")


def dijkstra(g: dict, src: str, verbose: bool = False):
    dist = {n: INF for n in g}
    prev: dict[str, str | None] = {n: None for n in g}
    dist[src] = 0
    done: list[str] = []
    if verbose:
        order = sorted(g)
        print("step  picked  " + "  ".join(f"{n:>6}" for n in order))
    step = 0
    while len(done) < len(g):
        u = min((n for n in g if n not in done), key=lambda n: (dist[n], n))
        if dist[u] == INF:
            break
        done.append(u)
        for v, w in g[u].items():
            if v not in done and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
        if verbose:
            cells = []
            for n in order:
                if n in done:
                    cells.append(f"{'*' + str(dist[n]):>6}")
                elif dist[n] == INF:
                    cells.append(f"{'inf':>6}")
                else:
                    cells.append(f"{str(dist[n]) + ',' + str(prev[n]):>6}")
            print(f"{step:>4}  {u:>6}  " + "  ".join(cells))
        step += 1
    return dist, prev


dist, prev = dijkstra(GRAPH, "A", verbose=True)
print("(* = permanent/final distance; 'd,p' = tentative distance and predecessor)")
print("final distances from A:", dist)


# ===== SECTION 4: PATH RECONSTRUCTION AND CHECK =====
print("\n===== SECTION 4: PATH RECONSTRUCTION + CHECK =====")


def path_to(prev: dict, dst: str) -> list[str]:
    p = []
    while dst is not None:
        p.append(dst)
        dst = prev[dst]
    return p[::-1]


for d in "BCDEF":
    print(f"A -> {d}: cost {dist[d]}, path {' -> '.join(path_to(prev, d))}")


def brute(g, s, t):
    best = INF
    others = [n for n in g if n not in (s, t)]
    for r in range(len(others) + 1):
        for mid in itertools.permutations(others, r):
            seq = (s, *mid, t)
            if all(b in g[a] for a, b in zip(seq, seq[1:])):
                best = min(best, sum(g[a][b] for a, b in zip(seq, seq[1:])))
    return best


for t in "BCDEF":
    assert brute(GRAPH, "A", t) == dist[t]


def dijkstra_heap(g, s):
    d = {n: INF for n in g}
    d[s] = 0
    h = [(0, s)]
    while h:
        du, u = heapq.heappop(h)
        if du > d[u]:
            continue
        for v, w in g[u].items():
            if du + w < d[v]:
                d[v] = du + w
                heapq.heappush(h, (d[v], v))
    return d


assert dijkstra_heap(GRAPH, "A") == dist
print("check: OK (matches brute force over all simple paths and a heapq version)")

print("\nForwarding table of router A (destination -> next hop):")
for d in "BCDEF":
    p = path_to(prev, d)
    print(f"  {d} -> via {p[1]}")


# ===== SECTION 5: TRAP - NEGATIVE WEIGHTS AND LINK FAILURE =====
print("\n===== SECTION 5: TRAPS =====")
neg = {"A": {"B": 4, "C": 2}, "B": {"A": 4, "C": -3}, "C": {"A": 2, "B": -3}}
dn, _ = dijkstra(neg, "A")
print("Graph with a negative edge B-C = -3 (undirected, so a negative cycle exists).")
print("Dijkstra reports A->B =", dn["B"], "(the true answer is -infinity: loop B-C forever).")
print("Dijkstra needs non-negative weights; use Bellman-Ford (next topics) otherwise.")
g2 = {k: dict(v) for k, v in GRAPH.items()}
del g2["D"]["E"], g2["E"]["D"]
d2, p2 = dijkstra(g2, "A")
print(f"After link D-E fails, A->E becomes cost {d2['E']} via {' -> '.join(path_to(p2, 'E'))} (was {dist['E']}).")
print("Dynamic routing re-runs the algorithm after a topology change; static routing would not.")
