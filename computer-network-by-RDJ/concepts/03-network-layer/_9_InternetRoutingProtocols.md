# `_9_InternetRoutingProtocols.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The Internet is a network of networks called autonomous systems (AS); inside an AS the owner runs an Interior Gateway Protocol (IGP) such as RIP or OSPF to find the best paths, and between ASes the Internet runs the Exterior Gateway Protocol BGP, which chooses routes by policy and business relationships rather than only by shortest distance. Splitting routing this way makes the Internet scale and lets every organisation control its own internal routing.

**Autonomous system.** A collection of IP networks and routers under one administrative authority presenting a common routing policy to the Internet. Each has an AS number (ASN). Examples of ASN ranges: 64512 to 65534 are private; 64496 to 64511 are reserved for documentation (RFC 5398), which is why the simulation uses 64501-64505.

**IGP vs EGP.**

| | IGP (interior) | EGP (exterior) |
|---|---|---|
| Scope | inside one AS | between ASes |
| Goal | best path, fast convergence | policy, stability, scalability |
| Examples | RIP, OSPF, IS-IS, EIGRP | BGP |

**RIP (Routing Information Protocol).**
- Distance vector, metric = hop count. 16 means unreachable, so the maximum usable distance is 15 hops (a limit on network size).
- Updates every 30 seconds; a route not refreshed within 180 seconds is invalid, advertised with metric 16 and removed after a 120-second garbage-collection time (RFC 2453 defaults; implementations also expose hold-down and flush timers, so check vendor docs).
- RIPv1 (classful, broadcast), RIPv2 (carries subnet masks, multicasts to 224.0.0.9, supports authentication), RIPng for IPv6. Runs over UDP port 520.
- Uses split horizon, poison reverse and triggered updates to limit count-to-infinity.

**OSPF.** Link state, over IP protocol 89, cost = reference bandwidth / interface bandwidth, areas with Area 0 as backbone. (See topic 8.)

**BGP (Border Gateway Protocol, BGP-4, RFC 4271).**
- Path-vector: each route announcement carries the list of ASes it has crossed (AS_PATH). A router prepends its own ASN when advertising to an external peer, and rejects any route whose AS_PATH already contains its own ASN. That kills routing loops without count-to-infinity.
- Runs over TCP port 179 between configured peers. eBGP between ASes, iBGP between routers of the same AS.
- Policy-based. Typical attributes: LOCAL_PREF (higher is preferred, the main tool to express "use this provider"), AS_PATH length (shorter preferred), ORIGIN, MED, and so on. A simplified decision order: highest local preference, then shortest AS path, then other tie-breakers. Real implementations have a longer, vendor-defined list.
- Carries prefixes in CIDR form and supports aggregation.
- Weaknesses: it trusts what peers announce (route leaks and prefix hijacks happen); mitigations include prefix filters and RPKI origin validation.

**Administrative distance.** When one prefix is learned from several sources, the router first prefers the source with the lowest administrative distance (AD), and only compares metrics among routes from the same protocol. Common Cisco IOS defaults: connected 0, static 1, eBGP 20, OSPF 110, RIP 120, iBGP 200. Other vendors use different values.

Typical exam questions: "Differentiate IGP and EGP", "Why is RIP limited to 15 hops?", "Explain BGP path vector and how loops are avoided", "Why does the AS-path with fewer hops sometimes lose?".

## Full Line-by-Line Breakdown

### SECTION 1: AUTONOMOUS SYSTEMS, IGP VS EGP
Text and a table of RIP/OSPF/BGP with type, algorithm, metric and transport. The key line is IGP = inside one AS (best path); EGP = between ASes (policy first).

Output from a real run:

```text
===== SECTION 1: AUTONOMOUS SYSTEMS, IGP VS EGP =====
Autonomous System (AS): a set of networks under ONE administrative control with a
  common routing policy, identified by an AS number (ASN). 64512-65534 are reserved for
  private use; 32-bit ASNs also exist. 64496-64511 are reserved for documentation (RFC 5398).
protocol  type  algorithm        metric                       transport
RIP       IGP   distance vector  hop count                    UDP 520
OSPF      IGP   link state       cost (bandwidth based)       IP protocol 89
BGP       EGP   path vector      AS path + policy attributes  TCP 179
IGP = routes INSIDE one AS (best path, fast).  EGP = routes BETWEEN ASes (policy first).
BGP run between ASes is eBGP; run between routers of the same AS is iBGP.
```

### SECTION 2: RIP (HOP LIMIT 15, TIMERS)
States the timers and versions, then simulates 17 routers in a chain with synchronous updates; R1's directly connected net has metric 1 and each router adds 1 to its neighbour's offer, capped at 16. The converged list is 1..15, 16, 16: the 16th router cannot reach the network at all. The assertion confirms the cap.

Output from a real run:

```text
===== SECTION 2: RIP (HOP LIMIT 15, TIMERS) =====
RIP metric = hop count; 16 means unreachable, so the network diameter is limited to 15 hops.
Timers (RFC 2453 defaults): update every 30 s, route times out after 180 s of silence,
then it is advertised as 16 for a 120 s garbage-collection period before removal.
RIPv1: classful, broadcast. RIPv2: sends the mask, multicasts to 224.0.0.9.
RIP propagates one hop per update; simulate a chain R1-R2-...-R17 with synchronous updates:
converged metrics for routers 1..17: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 16]
R15 reaches the net with metric 15; R16 and R17 get 16 = unreachable.
check: OK (the 16th router in a chain cannot be reached: hop limit 15)
```

### SECTION 3: OSPF COST
Computes cost = reference / bandwidth (minimum 1) for three link speeds, with a 100 Mbit/s reference. The trap: 100 Mbit/s and 1 Gbit/s both get cost 1, so OSPF would treat them as equal. The fix is to set a larger reference bandwidth consistently on every router. A second mini-example shows OSPF adding costs along a path and choosing the cheapest total, not the fewest hops (path B has 3 hops but cost 3; path A has 2 hops and cost 11).

Output from a real run:

```text
===== SECTION 3: OSPF COST =====
cost = reference bandwidth / interface bandwidth (reference here 100 Mbit/s, minimum 1)
  10 Mbit/s   -> cost 10
  100 Mbit/s  -> cost 1
  1 Gbit/s    -> cost 1
TRAP: with this reference, 100 Mbit/s and 1 Gbit/s links both get cost 1 -> OSPF cannot
tell them apart; raise the reference bandwidth consistently on ALL routers.
path A cost 11 (10M+100M links) vs path B cost 3 (three 100M links): OSPF picks B (lowest total cost)
```

### SECTION 4: BGP PATH-VECTOR SIMULATION
Six AS peerings, five ASes; AS 64505 originates the documentation prefix 203.0.113.0/24. In each round every AS reads its peers' best routes, prepends the peer's ASN to the path, rejects routes containing its own ASN (loop prevention) and keeps the better route by (local preference, shorter path). With no policy 64501 chooses `[64503, 64505]`. After setting local-pref 200 for neighbour 64502 on AS 64501, it chooses the longer `[64502, 64504, 64505]`: policy beats path length. The final lines show the own-ASN rejection rule.

Output from a real run:

```text
===== SECTION 4: BGP PATH-VECTOR SIMULATION =====
(ASNs 64501-64505 are documentation ASNs, not real networks)
Peering: 64501-64502, 64501-64503, 64502-64504, 64503-64504, 64504-64505, 64503-64505
AS 64505 originates 203.0.113.0/24. Best path chosen by each AS (shortest AS path, no policy):
  (converged in 3 rounds; 6 advertisements rejected by loop prevention)
  AS64501: path [64503, 64505] via 64503
  AS64502: path [64504, 64505] via 64504
  AS64503: path [64505] via 64505
  AS64504: path [64505] via 64505
  AS64505: path (origin) via None
check: OK (64501 learns [64503, 64505]: 2 AS hops via 64503, shorter than via 64502)

Same network, but AS 64501 has a policy: prefer routes from 64502 (e.g. cheaper transit), local-pref 200:
  AS64501 now uses path [64502, 64504, 64505] although it is longer: policy beats path length.
check: OK
Loop prevention: a router that sees its OWN ASN in an AS path rejects the route:
  AS64501 receives path [64502, 64501, 64505] -> rejected (contains own ASN)
This is why BGP (path vector) has no count-to-infinity: the whole path is carried.
```

### SECTION 5: ADMINISTRATIVE DISTANCE (CISCO DEFAULTS)
Lists the common default ADs (labelled vendor specific) and shows that when both RIP (metric 2) and OSPF (cost 30) know a prefix, OSPF is installed, because 110 beats 120; the metrics are not even compared.

Output from a real run:

```text
===== SECTION 5: ADMINISTRATIVE DISTANCE (CISCO DEFAULTS) =====
Administrative distance = trustworthiness of the SOURCE of a route (lower wins).
Values below are Cisco IOS defaults; other vendors use different numbers.
  Directly connected     0
  Static route           1
  eBGP                  20
  OSPF                 110
  RIP                  120
  iBGP                 200
Same prefix learned by RIP (metric 2) and OSPF (cost 30): installed from OSPF;
AD decides BETWEEN protocols; metric only decides WITHIN one protocol.
```

## Worked Example
**Q:** AS 64501 can reach prefix P through AS 64502 (path 64502 64504 64505) or AS 64503 (path 64503 64505). Which does BGP choose by default, and what must the operator do to prefer the first?

1. With default local preference (100 for both), the decision falls to AS-path length: 2 beats 3, so AS 64503 is chosen.
2. To prefer AS 64502 the operator raises LOCAL_PREF for routes learned from 64502 (e.g. 200). LOCAL_PREF is evaluated before path length, so now 64502 wins.
3. If a route arrived with 64501 already in its path it would be rejected as a loop.

The simulation prints exactly these two outcomes.

## Key Rules / Gotchas Recap
- IGP inside an AS (RIP, OSPF), EGP between ASes (BGP).
- RIP: hop count, 16 = infinity, maximum 15 hops, 30-second updates, UDP 520.
- OSPF cost = reference bandwidth / bandwidth; keep the reference consistent and large enough for fast links.
- BGP: path vector, TCP 179, policy first, shortest AS path second (simplified).
- A BGP router rejects any path containing its own ASN.
- Administrative distance picks between protocols; metric picks within a protocol; AD values are vendor specific.
- BGP trusts announcements, so filtering and origin validation matter.

## Why This Matters
Large outages and traffic hijacks (a wrong BGP announcement) are caused by exactly these policy and trust rules, and cloud/CDN engineers tune BGP to steer traffic. Understanding AS paths also helps interpret traceroute output and threat intelligence about which network an address belongs to.
