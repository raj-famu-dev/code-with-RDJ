# `_7_DistanceVectorRouting.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
In distance-vector routing each router keeps a table of the best known distance to every destination and periodically sends that table (its "vector") to its direct neighbours; each router then recomputes its own table with the Bellman-Ford equation. It is simple and needs no global map, which is why RIP uses it, but it converges slowly and suffers from the count-to-infinity problem.

**Bellman-Ford update.** For router x and destination y:

`D_x(y) = min over neighbours v of [ c(x, v) + D_v(y) ]`

The neighbour v that gives the minimum becomes the next hop. Initially a router knows only itself (cost 0) and its direct links. After k rounds of exchange it knows the best routes using at most k hops, so the number of rounds to converge is about the network diameter.

**Algorithm steps (per router):**
1. Initialise: 0 to self, cost of direct links to neighbours, infinity to others.
2. Periodically (RIP: every 30 s) send the whole vector to each neighbour.
3. On receiving neighbour v's vector, for each destination compute c(x,v) + D_v(y); if smaller than the current entry, or if it comes from the current next hop (so news about it must be believed even when worse), update the table.
4. Repeat; stop when no table changes (converged).

**Properties.** Good news travels fast (a new, shorter route spreads one hop per round). Bad news travels slowly: this is the root of count-to-infinity.

**Count-to-infinity problem.** Suppose the link to A fails. B loses its route, but C and D still advertise "A is 2 hops away" (via B!). B believes it, sets A = 3 via C, then C sets A = 4 via B, and so on: the metric rises round by round and packets loop between routers until the metric reaches the protocol's "infinity" (RIP: 16).

**Fixes.**
- Define a small infinity (RIP: 16, so usable paths are at most 15 hops).
- Split horizon: do not advertise a route out of the interface from which it was learned. Cures two-router loops.
- Poison reverse: advertise that route back with infinity, an explicit statement "do not use me to reach A". Costs bigger updates.
- Hold-down timer: when a route is declared unreachable, ignore new finite offers for it for a period, so stale rumours cannot revive it. Price: slower recovery.
- Triggered updates: send an update immediately when a metric changes instead of waiting for the next period.
- Neither split horizon nor poison reverse stops loops that include three or more routers; that needs hold-down, triggered updates or a bounded infinity.

**Distance vector vs link state:** see the table in section 5 and the next topic.

Typical exam questions: "Show the tables of each router after each exchange", "Explain count-to-infinity with an example", "How does split horizon help?".

## Full Line-by-Line Breakdown

### SECTION 1: BELLMAN-FORD UPDATE AND CONVERGENCE
`Network` holds each router's table (destination -> (cost, next hop)). `step()` is one synchronous round: every router reads the neighbours' tables from the previous round and applies the Bellman-Ford rule. The topology is A-B, B-C, B-D, C-D, D-E (all cost 1). The printed column shows the cost to A growing outwards one hop per round: B knows after round 1, C and D after round 2, E after round 3. That is the convergence time, equal to the diameter. Finally the whole network is cross-checked against BFS hop counts (all costs are 1).

Output from a real run:

```text
===== SECTION 1: BELLMAN-FORD UPDATE AND CONVERGENCE =====
Rule: D_x(y) = min over neighbours v of ( c(x,v) + D_v(y) )
Topology: A-B, B-C, B-D, C-D, D-E (all cost 1)
cost to A after each exchange round:  A: 0  B:16  C:16  D:16  E:16   (round 0)
cost to A after each exchange round:  A: 0  B: 1  C:16  D:16  E:16   (round 1)
cost to A after each exchange round:  A: 0  B: 1  C: 2  D: 2  E:16   (round 2)
cost to A after each exchange round:  A: 0  B: 1  C: 2  D: 2  E: 3   (round 3)
converged after 3 rounds (= network diameter in hops: A to E is 3)

Final routing table of router E (dest, cost, next hop):
  A: cost 3 via D
  B: cost 2 via D
  C: cost 2 via D
  D: cost 1 via D
  E: cost 0 via E
check: OK (every router's costs equal BFS hop counts)
```

### SECTION 2: COUNT TO INFINITY (PLAIN DV)
After convergence the link A-B is removed. B detects its own dead link and sets A = infinity (16). But in the same round C and D, who still believe "A is 2 away via B", offer that to B. B accepts (3 via C), and then C and D must raise their own cost to 4 because their next hop B got worse, and so on. Every router's cost rises by 1 per round until it hits 16 (unreachable) after about 15 rounds. During all that time traffic for A loops. This is the trap: the algorithm eventually gives the right answer but very slowly.

Output from a real run:

```text
===== SECTION 2: COUNT TO INFINITY (PLAIN DV) =====
[plain, hold-down=0] link A-B fails. Cost to A at B, C, D, E each round:
  round  0: B:16  C: 2  D: 2  E: 3
  round  1: B: 3  C: 3  D: 3  E: 3
  round  2: B: 4  C: 4  D: 4  E: 4
  round  3: B: 5  C: 5  D: 5  E: 5
  round  4: B: 6  C: 6  D: 6  E: 6
  round  5: B: 7  C: 7  D: 7  E: 7
  round  6: B: 8  C: 8  D: 8  E: 8
  round  7: B: 9  C: 9  D: 9  E: 9
  round  8: B:10  C:10  D:10  E:10
  round  9: B:11  C:11  D:11  E:11
  round 10: B:12  C:12  D:12  E:12
  round 11: B:13  C:13  D:13  E:13
  round 12: B:14  C:14  D:14  E:14
  ...
  round 15: B:16  C:16  D:16  E:16
plain DV needed 15 rounds to give up on A; each router's cost climbs by 1 per exchange round until 16 = 'unreachable'
Meanwhile packets to A loop B -> C/D -> B (a routing loop) and TTL burns.
This is why RIP defines infinity = 16: it bounds the count (max usable hops = 15).
```

### SECTION 3: SPLIT HORIZON AND POISON REVERSE
On a simple chain A-B-C, plain DV takes 14 rounds to make C give up on A, while split horizon makes C learn the truth in 1 round, because C never advertises "A" back to B (C learned that route from B), so B never hears the stale rumour and only its own news (A = infinity) reaches C. The trap: on the triangle B-C-D, split horizon and poison reverse still count up, because the lie travels around a loop of three routers (B to C to D to B) and each hop is a "different" interface. The tables flap between finite values and 16 but still need about 15 rounds.

Output from a real run:

```text
===== SECTION 3: SPLIT HORIZON AND POISON REVERSE =====
chain A-B-C, link A-B fails, mode=plain: C's cost to A settles at 16 after 14 rounds
chain A-B-C, link A-B fails, mode=split: C's cost to A settles at 16 after 1 rounds
Split horizon: never advertise a route back out of the interface it was learned from.
Poison reverse: advertise it back WITH cost = infinity (explicit, faster).
TRAP: split horizon does NOT cure loops that involve 3+ routers (our B-C-D triangle):
[split, hold-down=0] link A-B fails. Cost to A at B, C, D, E each round:
  round  0: B:16  C: 2  D: 2  E: 3
  round  1: B:16  C: 3  D: 3  E: 3
  round  2: B: 4  C:16  D:16  E: 4
  round  3: B:16  C:16  D: 5  E:16
  round  4: B:16  C: 6  D:16  E: 6
  round  5: B: 7  C:16  D:16  E:16
  round  6: B:16  C:16  D: 8  E:16
  round  7: B:16  C: 9  D:16  E: 9
  round  8: B:10  C:16  D:16  E:16
  round  9: B:16  C:16  D:11  E:16
  round 10: B:16  C:12  D:16  E:12
  round 11: B:13  C:16  D:16  E:16
  round 12: B:16  C:16  D:14  E:16
  ...
  round 15: B:16  C:16  D:16  E:16
split horizon on the triangle still took 15 rounds (see rows above).
[poison, hold-down=0] link A-B fails. Cost to A at B, C, D, E each round:
  round  0: B:16  C: 2  D: 2  E: 3
  round  1: B:16  C: 3  D: 3  E: 3
  round  2: B: 4  C:16  D:16  E: 4
  round  3: B:16  C:16  D: 5  E:16
  round  4: B:16  C: 6  D:16  E: 6
  round  5: B: 7  C:16  D:16  E:16
  round  6: B:16  C:16  D: 8  E:16
  round  7: B:16  C: 9  D:16  E: 9
  round  8: B:10  C:16  D:16  E:16
  round  9: B:16  C:16  D:11  E:16
  round 10: B:16  C:12  D:16  E:12
  round 11: B:13  C:16  D:16  E:16
  round 12: B:16  C:16  D:14  E:16
  ...
  round 15: B:16  C:16  D:16  E:16
poison reverse on the triangle took 15 rounds: also a loop across a triangle.
```

### SECTION 4: HOLD-DOWN TIMER
With split horizon plus a 3-round hold-down, each router that hears "A unreachable" refuses finite offers for A during the hold period, so the rumour can never loop. The whole network settles in 5 rounds instead of 15. A comparison of all four modes follows. The last line asserts that, before any failure, E reaches A with cost 3 in every mode.

Output from a real run:

```text
===== SECTION 4: HOLD-DOWN TIMER =====
[split, hold-down=3] link A-B fails. Cost to A at B, C, D, E each round:
  round  0: B:16  C: 2  D: 2  E: 3
  round  1: B:16  C: 3  D: 3  E: 3
  round  2: B:16  C:16  D:16  E: 4
  round  3: B:16  C:16  D:16  E:16
  round  4: B:16  C:16  D:16  E:16
  round  5: B:16  C:16  D:16  E:16
split horizon + hold-down(3 rounds) settled in 5 rounds instead of 15.
Hold-down: after a route goes unreachable, ignore any NEW finite offers for it for a
while, so stale information from neighbours cannot revive it. Price: slower recovery
if the route really does come back.
  plain            rounds until stable: 15
  split            rounds until stable: 15
  poison           rounds until stable: 15
  split+hold-down  rounds until stable: 5
check: OK (before failure, E reaches A with cost 3 in all modes)
```

### SECTION 5: SUMMARY TABLE
A short Distance vector vs Link state table for revision.

Output from a real run:

```text
===== SECTION 5: SUMMARY TABLE =====
                Distance vector                          Link state
Knows           only neighbours' vectors                 whole topology (link state)
Algorithm       Bellman-Ford                             Dijkstra
Messages        whole table to neighbours periodically   link states flooded to all
Convergence     slow, count-to-infinity                  fast
Example         RIP                                      OSPF
Rumour routing  yes ('routing by rumour')                no
```

## Worked Example
**Q:** Routers A-B-C in a line, all links cost 1. Show what happens at C when A-B fails, with and without split horizon.

Without split horizon:
1. Before: B has A = 1, C has A = 2 (via B).
2. A-B fails. B sets A = infinity. C still advertises "A = 2" to B.
3. B updates: A = 2 + 1 = 3 via C. B advertises 3 to C. C updates (next hop is B): A = 4. And so on, rising by 2 every back-and-forth exchange until infinity (16).

With split horizon: C learned A from B, so C does not advertise A back to B. B has only its own news, A = infinity, which it tells C; C sets A = infinity immediately.

The script's chain demo shows 14 rounds (plain) vs 1 round (split horizon) for C to settle at 16.

## Key Rules / Gotchas Recap
- Update rule is c(x,v) + D_v(y); the next hop is the neighbour achieving the min.
- Always accept the next hop's news, even if worse; otherwise stale routes live forever.
- Convergence takes about diameter rounds for good news, but up to "infinity" rounds for bad news.
- RIP infinity = 16; maximum usable path 15 hops.
- Split horizon (omit) and poison reverse (advertise infinity) fix only two-node loops.
- Hold-down and triggered updates are needed for larger loops.
- Distance vector sends the whole table to neighbours only; link state floods link information to everyone.

## Why This Matters
BGP is a path-vector protocol that grew out of distance-vector ideas, so the count-to-infinity and loop-avoidance lessons carry straight into how the Internet's routing works and how route leaks spread. The same "believe your next hop, damp the rumour" reasoning is used in gossip and distributed-systems protocols.
