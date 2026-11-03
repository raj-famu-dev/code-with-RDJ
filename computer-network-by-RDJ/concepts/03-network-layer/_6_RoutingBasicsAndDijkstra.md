# `_6_RoutingBasicsAndDijkstra.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Routing is the process of choosing the path a packet takes from source to destination through a network of routers; the routing algorithm fills each router's forwarding table. Dijkstra's algorithm is the standard way to compute the least-cost path from one node to all others when link costs are known, and it is the engine inside link-state protocols such as OSPF.

**Classification of routing algorithms.**

| | Non-adaptive (static) | Adaptive (dynamic) |
|---|---|---|
| Decision | routes fixed in advance, by hand | recomputed as topology/traffic changes |
| Overhead | none | update messages, CPU |
| Fault tolerance | none | self-healing |
| Examples | static routes, default route | RIP, OSPF, BGP |

Other axes: centralised vs distributed, global (full topology: link state) vs decentralised (neighbour information only: distance vector), flat vs hierarchical.

**Optimality principle.** If router R lies on the best path from I to J, the best path from R to J lies on the same route. Consequence: the best routes to one destination form a tree (sink tree) rooted at that destination.

**Flooding.** Each router sends every incoming packet out on all links except the one it came in on. Needs a damping method: a hop counter (decrement at each router, discard at 0), or sequence numbers so each router forwards a given packet only once. Pros: simple, extremely robust, always uses the shortest path as one of its copies, needs no topology knowledge. Cons: huge duplicate traffic. Uses: link-state advertisement distribution, broadcast, military networks.

**Dijkstra's algorithm.**
1. Set dist(source) = 0 and all others infinity; no node permanent.
2. Pick the non-permanent node u with the smallest tentative distance and make it permanent.
3. For every neighbour v of u: if dist(u) + cost(u,v) < dist(v), update dist(v) and set predecessor(v) = u (relaxation).
4. Repeat until all nodes are permanent.
5. Path to any node: follow predecessors backwards from the destination, then reverse.
Complexity O(V^2) with an array, O((V+E) log V) with a binary heap. It requires non-negative edge costs.

Typical exam question: "Apply Dijkstra from node A on this graph, show each step, give the shortest path to F and the routing table of A."

## Full Line-by-Line Breakdown

### SECTION 1: CLASSIFICATION OF ROUTING
Plain-text summary of static vs dynamic, with the pros and cons and the optimality principle. No computation, but these are common theory questions.

Output from a real run:

```text
===== SECTION 1: CLASSIFICATION OF ROUTING =====
Static (non-adaptive): table set by hand, ignores traffic/topology changes
Dynamic (adaptive)   : protocol updates table when topology/traffic changes
Centralised vs distributed: one route-control centre vs every router computes
Flat vs hierarchical : all routers equal vs regions/areas/AS
Static pros: no protocol overhead, predictable, secure. Cons: no fault tolerance, hard to scale.
Dynamic pros: self-healing, scales. Cons: CPU/bandwidth for updates, convergence time.
Optimality principle: if R is on the best path from I to J, the best path from R to J
follows the same route -> best routes to one destination form a sink TREE.
```

### SECTION 2: FLOODING
`flood` simulates a hop-limited flood on the 6-router graph from A. A node forwards a copy on every link except the one it arrived on, until the hop counter reaches 0. The numbers (3, 12, 35, 86 transmissions) show how quickly duplicates multiply; F first receives a copy at hop limit 2 (the path A-D-E-F is only 3 hops but A-C-F is 2 hops), and then receives more and more copies. This is exactly why real flooding needs sequence numbers to suppress duplicates.

Output from a real run:

```text
===== SECTION 2: FLOODING =====
hop limit 1:    3 transmissions; copies at F = 0
hop limit 2:   12 transmissions; copies at F = 1
hop limit 3:   35 transmissions; copies at F = 5
hop limit 4:   86 transmissions; copies at F = 12
Without a hop counter or sequence-number duplicate check flooding never stops (loops).
Flooding always finds the shortest path (one copy takes it) and is very robust,
but wastes bandwidth; used for link-state advertisements and in military nets.
```

### SECTION 3: DIJKSTRA WITH STEP TABLE
The graph has links A-B 2, A-C 5, A-D 1, B-C 3, B-D 2, C-D 3, C-E 1, C-F 5, D-E 1, E-F 2. `dijkstra(..., verbose=True)` prints the classic exam table: one row per step, the node made permanent, and for every node either `*dist` (permanent) or `dist,predecessor` (tentative). Row 1 picks D (distance 1) and improves C from 5 to 4 and E from inf to 2; row 3 picks E and improves C again to 3 and F to 4. The last row gives the final distances.

Output from a real run:

```text
===== SECTION 3: DIJKSTRA WITH STEP TABLE =====
step  picked       A       B       C       D       E       F
   0       A      *0     2,A     5,A     1,A     inf     inf
   1       D      *0     2,A     4,D      *1     2,D     inf
   2       B      *0      *2     4,D      *1     2,D     inf
   3       E      *0      *2     3,E      *1      *2     4,E
   4       C      *0      *2      *3      *1      *2     4,E
   5       F      *0      *2      *3      *1      *2      *4
(* = permanent/final distance; 'd,p' = tentative distance and predecessor)
final distances from A: {'A': 0, 'B': 2, 'C': 3, 'D': 1, 'E': 2, 'F': 4}
```

### SECTION 4: PATH RECONSTRUCTION + CHECK
`path_to` walks the predecessor chain backwards and reverses it. Example: C has predecessor E, E has D, D has A, giving A -> D -> E -> C with cost 3 (cheaper than the direct link of cost 5). The results are validated by brute-force enumeration of every simple path and by an independent heap-based implementation. The forwarding table of A only needs the first hop of each path.

Output from a real run:

```text
===== SECTION 4: PATH RECONSTRUCTION + CHECK =====
A -> B: cost 2, path A -> B
A -> C: cost 3, path A -> D -> E -> C
A -> D: cost 1, path A -> D
A -> E: cost 2, path A -> D -> E
A -> F: cost 4, path A -> D -> E -> F
check: OK (matches brute force over all simple paths and a heapq version)

Forwarding table of router A (destination -> next hop):
  B -> via B
  C -> via D
  D -> via D
  E -> via D
  F -> via D
```

### SECTION 5: TRAPS
Negative weights: with an undirected negative edge the graph has a negative cycle, so Dijkstra's answer is meaningless (the real distance is unbounded). Use Bellman-Ford (next topic) if costs can be negative. Link failure: removing D-E forces A -> E to cost 5 via C, showing why dynamic routing must re-run the algorithm after a topology change.

Output from a real run:

```text
===== SECTION 5: TRAPS =====
Graph with a negative edge B-C = -3 (undirected, so a negative cycle exists).
Dijkstra reports A->B = -1 (the true answer is -infinity: loop B-C forever).
Dijkstra needs non-negative weights; use Bellman-Ford (next topics) otherwise.
After link D-E fails, A->E becomes cost 5 via A -> D -> C -> E (was 2).
Dynamic routing re-runs the algorithm after a topology change; static routing would not.
```

## Worked Example
**Q:** From the graph above find the shortest path and cost from A to F.

1. Start: A=0, B=2, C=5, D=1, others infinity. Smallest unfixed = D (1). Fix D.
2. From D: C = min(5, 1+3) = 4 (pred D), E = 1+1 = 2 (pred D).
3. Next smallest: B (2) and E (2) tie; take B. B improves nothing (C via B = 5 > 4).
4. Fix E (2): C = min(4, 2+1) = 3 (pred E), F = 2+2 = 4 (pred E).
5. Fix C (3): F via C = 8 > 4, no change. Fix F (4).
6. F <- E <- D <- A, so the path is A -> D -> E -> F with cost 4.

The code prints cost 4 and the same path.

## Key Rules / Gotchas Recap
- Dijkstra is greedy: the smallest tentative distance is final; this only holds with non-negative weights.
- Always record the predecessor when you relax; the path is rebuilt backwards.
- The routing table stores the first hop only, not the whole path.
- Ties can be broken any way; different valid paths may have equal cost.
- Flooding needs a hop counter or sequence numbers, otherwise it never ends.
- Static routes do not react to failures; dynamic routing does.

## Why This Matters
Shortest-path search is the same algorithm behind OSPF inside every enterprise and ISP network, and it is the base for graph algorithms used in maps, dependency resolution and knowledge-graph tooling. Writing it with a step table is also the fastest way to debug why traffic takes a path you did not expect.
