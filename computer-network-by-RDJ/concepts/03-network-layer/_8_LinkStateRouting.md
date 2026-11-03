# `_8_LinkStateRouting.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
In link-state routing every router learns the entire network map: each one floods a small advertisement describing its own links to all other routers, so all routers end up holding the same database, and each then runs Dijkstra's shortest-path-first (SPF) algorithm on it independently. It converges faster and without count-to-infinity, at the price of more memory, CPU and flooding; OSPF and IS-IS work this way.

**The five steps of link state:**
1. Discover neighbours (Hello packets) and learn the cost of each link.
2. Build a link-state advertisement (LSA / LSP): who I am, a sequence number, and my list of (neighbour, cost).
3. Flood the LSA to every router.
4. Every router stores all LSAs in its link-state database (LSDB); all databases are identical.
5. Each router runs SPF with itself as root and fills its forwarding table (destination -> first hop).

**Reliable flooding.** The sequence number is the key: a router installs an LSA only if its sequence number is higher than what it stores, then forwards it on all links except the arrival link. Old or duplicate copies are dropped, so flooding terminates. (Real protocols also use an age field to expire stale LSAs.) Flooding is triggered by changes and also refreshed periodically.

**When a link fails:** the two routers on its ends originate new LSAs with a higher sequence number; they are flooded; every router updates its LSDB and re-runs SPF. No router relies on another router's computed result, so there is no rumour-spreading and no count-to-infinity.

**OSPF overview.**
- A link-state IGP carried directly over IP (protocol number 89). Link cost is based on interface bandwidth (reference bandwidth divided by the interface bandwidth).
- Areas: a large AS is divided into areas to limit flooding and LSDB size. Area 0 is the backbone and all other areas attach to it. Area Border Routers (ABRs) summarise routes between areas. Autonomous System Boundary Routers (ASBRs) inject external routes.
- Designated Router (DR) and Backup DR (BDR): on a multi-access network (e.g. Ethernet) routers form adjacencies only with the DR/BDR rather than with every neighbour, reducing a full mesh of n(n-1)/2 adjacencies to 2(n-2)+1. Election: highest router priority wins, ties broken by the highest router ID; priority 0 means never eligible.
- Supports VLSM/CIDR, authentication and equal-cost multipath.

**Distance vector vs link state.**

| | Distance vector (RIP) | Link state (OSPF) |
|---|---|---|
| Knowledge | neighbours' vectors only | whole topology |
| Algorithm | Bellman-Ford | Dijkstra |
| Messages | whole table to neighbours | own links, flooded to all |
| Convergence | slow; count-to-infinity | fast |
| Resources | low | more CPU and memory |
| Scale | small | large, using areas |

Typical exam questions: "Explain link-state routing", "Build the LSDB and the routing table for router X", "Compare with distance vector", "Role of DR/BDR and areas in OSPF".

## Full Line-by-Line Breakdown

### SECTION 1: LSA FLOODING
`Lsa` is an immutable record (origin, sequence number, list of links). `Domain.flood` implements reliable flooding: install only if newer, then forward on all links except the arrival link. Each of the six routers originates one LSA; each costs 15 transmissions on this 10-link graph (some are duplicates that the receiver drops), totalling 90 messages.

Output from a real run:

```text
===== SECTION 1: LSA FLOODING =====
router A originates LSA seq 1 links={'B': 2, 'C': 5, 'D': 1} -> 15 messages
router B originates LSA seq 1 links={'A': 2, 'C': 3, 'D': 2} -> 15 messages
router C originates LSA seq 1 links={'A': 5, 'B': 3, 'D': 3, 'E': 1, 'F': 5} -> 15 messages
router D originates LSA seq 1 links={'A': 1, 'B': 2, 'C': 3, 'E': 1} -> 15 messages
router E originates LSA seq 1 links={'C': 1, 'D': 1, 'F': 2} -> 15 messages
router F originates LSA seq 1 links={'C': 5, 'E': 2} -> 15 messages
total flooding messages: 90 for 6 LSAs on 10 links
Rule: install an LSA only if its sequence number is NEWER than the stored one,
then forward it on every link except the one it came in on.
```

### SECTION 2: IDENTICAL LSDB + SPF PER ROUTER
The assertion proves every router ends with an identical six-LSA database, which is printed as a topology table. `Router.spf` is Dijkstra on that database; it also records the first hop towards each destination (the forwarding-table entry). For router A: C costs 3 via D (A-D-E-C). Every router's distances are compared to an independent Bellman-Ford implementation, so a bug in either would show.

Output from a real run:

```text
===== SECTION 2: IDENTICAL LSDB + SPF PER ROUTER =====
all 6 routers hold the same LSDB with 6 LSAs: check OK
LSDB (as a topology table):
  A: B=2, C=5, D=1
  B: A=2, C=3, D=2
  C: A=5, B=3, D=3, E=1, F=5
  D: A=1, B=2, C=3, E=1
  E: C=1, D=1, F=2
  F: C=5, E=2

SPF at A: B:2via B  C:3via D  D:1via D  E:2via D  F:4via D
SPF at B: A:2via A  C:3via C  D:2via D  E:3via D  F:5via D
SPF at C: A:3via E  B:3via B  D:2via E  E:1via E  F:3via E
SPF at D: A:1via A  B:2via B  C:2via E  E:1via E  F:3via E
SPF at E: A:2via D  B:3via D  C:1via C  D:1via D  F:2via F
SPF at F: A:4via E  B:5via E  C:3via E  D:3via E  E:2via E
check: OK (SPF distances at every router equal an independent Bellman-Ford)
```

### SECTION 3: TRAP - FLOODING WITHOUT SEQUENCE NUMBERS
With the sequence check one LSA costs 15 messages. With the check turned off and only a hop limit of 6 it costs 538 messages, because every copy is re-forwarded. Without the hop limit it would never end. The second half shows the other role of sequence numbers: after seq 2 is installed, a delayed replay of seq 1 sends 0 messages and changes nothing.

Output from a real run:

```text
===== SECTION 3: TRAP - FLOODING WITHOUT SEQUENCE NUMBERS =====
one LSA from A, with sequence check   : 15 messages
one LSA from A, no check, hop limit 6 : 538 messages (duplicates multiply; without ANY limit it never ends)
Stale LSA: an old copy (seq 1) arriving after seq 2 must be ignored:
  every router now holds seq 2; replaying seq 1 sends 0 messages and changes nothing
```

### SECTION 4: LINK FAILURE (C-E DOWN)
The link C-E is removed. Only C and E originate new LSAs (seq 2) and flood them; every router re-runs SPF locally. A's cost to C rises from 3 to 4 (route A-D-C, since A-D-E-C is gone), and F, which previously used E to reach C, now sends C-bound traffic directly over the F-C link with cost 5 (the other path F-E-D-C costs 6). The result is validated by a reference Bellman-Ford on the reduced topology.

Output from a real run:

```text
===== SECTION 4: LINK FAILURE (C-E DOWN) =====
C and E re-originate LSAs (seq 2) -> 26 messages; every router re-runs SPF
SPF at A: B:2via B  C:4via D  D:1via D  E:2via D  F:4via D
SPF at F: A:4via E  B:5via E  C:5via C  D:3via E  E:2via E
check: OK
F's cost to C changed 3 -> 5 (was via E, now via C): the direct F-C link is now best
Only 2 LSAs were flooded: every router recomputes locally. No count-to-infinity.
```

### SECTION 5: OSPF OVERVIEW + COMPARISON
Prints the OSPF fact summary, runs a DR/BDR election (R3 wins with priority 100; R1 and R2 tie on priority so the higher router ID, R2, becomes BDR; R4 with priority 0 is excluded), counts adjacencies with and without a DR, and prints the comparison table.

Output from a real run:

```text
===== SECTION 5: OSPF OVERVIEW + COMPARISON =====
OSPF: IP protocol number 89, link-state IGP. Cost = reference bandwidth / interface bandwidth.
Areas: big AS split into areas; Area 0 is the backbone; every other area connects to it.
  Area Border Routers (ABR) summarise routes between areas -> smaller LSDB, less flooding.
Multi-access LAN: routers elect a Designated Router (DR) and Backup (BDR); all routers
  exchange LSAs only with DR/BDR instead of a full mesh (n(n-1)/2 adjacencies).
candidates (priority, router-id): {'R1': (1, '1.1.1.1'), 'R2': (1, '2.2.2.2'), 'R3': (100, '3.3.3.3'), 'R4': (0, '4.4.4.4')}
election: highest priority wins, ties broken by highest router ID -> DR=R3, BDR=R2
R4 has priority 0: it can never become DR or BDR.
adjacencies for 4 routers: full mesh 6; with DR/BDR 2*(n-2)+1 = 5
                     Distance vector                Link state
Topology knowledge   neighbours' vectors only       whole map (LSDB)
Algorithm            Bellman-Ford                   Dijkstra (SPF)
Sends                whole table, to neighbours     own link states, to everyone (flood)
Convergence          slow, count-to-infinity        fast, loop-free
CPU / memory         low                            higher
Bandwidth            periodic full tables           small event-driven LSAs
Scalability          small networks (RIP max 15 hops) large, with areas
Example              RIP                            OSPF, IS-IS
```

## Worked Example
**Q:** Four routers elect a DR/BDR on one LAN: R1 (priority 1, ID 1.1.1.1), R2 (1, 2.2.2.2), R3 (100, 3.3.3.3), R4 (0, 4.4.4.4). Who are DR and BDR?

1. R4 has priority 0, so it is ineligible.
2. R3 has the highest priority (100): DR.
3. R1 and R2 tie on priority 1; the higher router ID is 2.2.2.2, so R2 is BDR.
4. Adjacencies: full mesh would need 4 x 3 / 2 = 6; with DR/BDR it is 2 x (4 - 2) + 1 = 5.

The code prints DR=R3, BDR=R2 and 5 adjacencies. (In real OSPF an existing DR is not pre-empted by a later router with higher priority; the election is not pre-emptive.)

## Key Rules / Gotchas Recap
- LSA = origin + sequence number + (neighbour, cost) list; sequence number decides newer vs older.
- Flood on every link except the arrival link; drop duplicates and older copies.
- All routers hold the same LSDB; each runs SPF with itself as root.
- A failure triggers only two new LSAs; every router recomputes on its own.
- OSPF: protocol 89, Area 0 backbone, ABR summarises, DR/BDR on multi-access LANs.
- DR election: highest priority, then highest router ID; priority 0 is excluded.
- Link state costs more CPU, memory and flooding traffic than distance vector.

## Why This Matters
Link-state ideas (every node keeps the full graph, recomputes locally from flooded events) show up in service meshes, cluster membership and any system that must reconverge quickly after a failure. Knowing how OSPF fails (stale or inconsistent LSDBs, flooding storms) is basic network-operations and security knowledge.
