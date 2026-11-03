# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Network topologies: bus, star, ring, mesh, tree, hybrid. Builds each as a graph,
counts links and ports for n nodes, and simulates node/link failures with a
connectivity search. Implements the 'physical topology' part of the syllabus."""
from collections import deque
from itertools import combinations

Edge = tuple[str, str]


def nodes(n: int) -> list[str]:
    return [f"N{i}" for i in range(1, n + 1)]


# ===== SECTION 1: BUILD EACH TOPOLOGY AS A GRAPH =====
print("===== SECTION 1: BUILD EACH TOPOLOGY AS A GRAPH =====")


def star(n: int) -> list[Edge]:
    """n end nodes each cabled to one central hub/switch 'HUB'."""
    return [(x, "HUB") for x in nodes(n)]


def ring(n: int) -> list[Edge]:
    ns = nodes(n)
    return [(ns[i], ns[(i + 1) % n]) for i in range(n)]


def mesh(n: int) -> list[Edge]:
    return list(combinations(nodes(n), 2))


def bus(n: int) -> list[Edge]:
    """One backbone cable modelled as tap points T1..Tn in a line (n-1 backbone
    segments of ONE physical cable); each node has a drop line to its tap."""
    taps = [f"T{i}" for i in range(1, n + 1)]
    return [(taps[i], taps[i + 1]) for i in range(n - 1)] + list(zip(nodes(n), taps))


def tree(depth: int, fanout: int = 2) -> list[Edge]:
    """Complete tree: root R, every parent has `fanout` children."""
    edges: list[Edge] = []
    level = ["R"]
    for d in range(1, depth + 1):
        nxt = []
        for p in level:
            for k in range(fanout):
                c = f"{p}.{k}"
                edges.append((p, c))
                nxt.append(c)
        level = nxt
    return edges


def hybrid() -> list[Edge]:
    """Two stars whose hubs are joined by a trunk link (a star-of-stars hybrid)."""
    return [("A1", "H1"), ("A2", "H1"), ("A3", "H1"),
            ("B1", "H2"), ("B2", "H2"), ("B3", "H2"), ("H1", "H2")]


def vertices(edges: list[Edge]) -> set[str]:
    return {v for e in edges for v in e}


for name, edges in [("star n=5", star(5)), ("ring n=5", ring(5)), ("mesh n=5", mesh(5)),
                    ("bus n=5", bus(5)), ("tree depth=2", tree(2)), ("hybrid", hybrid())]:
    print(f"{name:<13} vertices={len(vertices(edges)):>2} graph edges={len(edges):>2}")
print("(bus: 5 edges are drop lines, 4 are pieces of the single backbone cable, so 9 edges = 1 physical backbone + 5 drops)")


# ===== SECTION 2: LINK / PORT COUNTS FOR n NODES =====
print("\n===== SECTION 2: LINK / PORT COUNTS FOR n NODES =====")
print(f"{'n':>3} {'star':>6} {'ring':>6} {'bus drops':>10} {'mesh n(n-1)/2':>14} {'ports/node (mesh)':>18}")
for n in (3, 4, 5, 6, 10, 20):
    mesh_links = n * (n - 1) // 2
    assert mesh_links == len(mesh(n))
    assert len(star(n)) == n and len(ring(n)) == n
    print(f"{n:>3} {n:>6} {n:>6} {n:>10} {mesh_links:>14} {n - 1:>18}")
print("Mesh needs n(n-1)/2 cables and n-1 NIC ports on EVERY node; that is why full mesh is rare.")
print("bus: 1 backbone cable + n drop lines (and 2 terminators); star: n cables + 1 hub port each.")
# Trap: n(n-1) counts each cable twice (once from each end).
wrong = 5 * 4
print(f"Trap: n(n-1) for n=5 gives {wrong} (counts each cable twice); correct is {wrong // 2}.")
assert wrong // 2 == len(mesh(5))
print("check: OK")


# ===== SECTION 3: FAILURE IMPACT =====
print("\n===== SECTION 3: FAILURE IMPACT =====")


def components(edges: list[Edge], dead_nodes: set[str] = frozenset(),
               dead_links: set[frozenset] = frozenset()) -> list[set[str]]:
    """Connected groups of surviving vertices (BFS)."""
    adj: dict[str, set[str]] = {}
    for a, b in edges:
        if a in dead_nodes or b in dead_nodes or frozenset((a, b)) in dead_links:
            continue
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    alive = vertices(edges) - dead_nodes
    seen: set[str] = set()
    groups = []
    for s in sorted(alive):
        if s in seen:
            continue
        comp, q = {s}, deque([s])
        seen.add(s)
        while q:
            u = q.popleft()
            for v in adj.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    comp.add(v)
                    q.append(v)
        groups.append(comp)
    return groups


def report(label: str, edges: list[Edge], **kw) -> None:
    comps = components(edges, **kw)
    sizes = sorted(len(c) for c in comps)
    verdict = "still connected" if len(comps) == 1 else f"SPLIT into {len(comps)} islands {sizes}"
    print(f"{label:<44} -> {verdict}")


report("star: hub dies", star(5), dead_nodes={"HUB"})
report("star: one leaf dies", star(5), dead_nodes={"N3"})
report("bus: backbone break between T2-T3", bus(5), dead_links={frozenset(("T2", "T3"))})
report("bus: one node (N3) dies", bus(5), dead_nodes={"N3"})
report("ring (bidirectional): one cable cut", ring(5), dead_links={frozenset(("N1", "N2"))})
report("ring: two cables cut", ring(5), dead_links={frozenset(("N1", "N2")), frozenset(("N3", "N4"))})
report("mesh n=5: 3 of the 4 cables at N1 cut", mesh(5), dead_links={frozenset(("N1", "N2")), frozenset(("N1", "N3")), frozenset(("N1", "N4"))})
report("tree: root dies (depth 2)", tree(2), dead_nodes={"R"})
report("hybrid: link H1-H2 cut", hybrid(), dead_links={frozenset(("H1", "H2"))})
print("Trap: a token ring that passes data one way only dies on ONE cut; a dual/bidirectional ring survives it.")


# ===== SECTION 4: COMPARISON TABLE =====
print("\n===== SECTION 4: COMPARISON TABLE =====")
rows = [
    ("bus", "cheap, little cable", "backbone fault kills all; collisions", "n drops + 1 backbone"),
    ("star", "easy to add/remove, 1 fault isolated", "hub is single point of failure", "n"),
    ("ring", "orderly access, no collisions", "one break stops a unidirectional ring", "n"),
    ("mesh", "most reliable, private links", "huge cabling and ports", "n(n-1)/2"),
    ("tree", "hierarchical, scalable", "root failure splits network", "n-1 (nodes)"),
    ("hybrid", "mix of strengths, flexible", "complex and costly", "depends"),
]
print(f"{'topology':<10}{'advantage':<38}{'disadvantage':<40}{'cables'}")
for r in rows:
    print(f"{r[0]:<10}{r[1]:<38}{r[2]:<40}{r[3]}")


# ===== SECTION 5: WORKED EXAMPLE =====
print("\n===== SECTION 5: WORKED EXAMPLE =====")
n = 8
print(f"A lab has n={n} computers. Fully meshed: cables = {n}*{n - 1}/2 = {n * (n - 1) // 2}; ports per PC = {n - 1}.")
print(f"Star: cables = {n}; ports per PC = 1; switch ports = {n}.")
print(f"Extra cables for mesh over star = {n * (n - 1) // 2 - n}.")
assert n * (n - 1) // 2 == 28 and 28 - 8 == 20
print("check: OK")
