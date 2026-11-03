# `_11_SwitchesBridgesAndVlan.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A bridge or layer-2 switch connects LAN segments and forwards frames based on MAC addresses, learning where each address lives so it does not need configuring. Redundant links make it fault tolerant but create loops, which the Spanning Tree Protocol (STP) removes. VLANs split one physical switch into several logical LANs.

**Transparent (learning) bridge.** Keeps a forwarding table of MAC address, port and age. For every frame: (1) LEARN: record source MAC against the arrival port. (2) Look up the destination. If the destination is unknown or broadcast: FLOOD out all ports except the arrival port. If the destination is on the arrival port: FILTER (drop) because the receiver already saw it. Otherwise FORWARD only out the destination port. Entries age out (typically around 300 seconds, configurable) so stale addresses disappear and moved hosts relearn.

**Hub vs bridge vs switch vs router.** A hub repeats bits to all ports (one collision domain). A bridge/switch filters by MAC, giving each port its own collision domain. A router separates broadcast domains and forwards by IP.

**Loops and broadcast storms.** Ethernet frames have no TTL. If switches form a loop, a broadcast or unknown-destination frame circulates forever and copies multiply; the network collapses, and forwarding tables flap because the same source appears on different ports.

**Spanning Tree Protocol (IEEE 802.1D).** Switches exchange BPDUs and: (1) elect a ROOT BRIDGE: lowest bridge ID wins, where bridge ID = priority (default 32768) then MAC address, so equal priorities are broken by the lowest MAC; (2) each non-root bridge picks a ROOT PORT, the port with the lowest cost to the root (cost by bandwidth: 10 Mbps = 100, 100 Mbps = 19, 1 Gbps = 4 in the classic 802.1D scale; ties go to the lower sender bridge ID); (3) each segment gets one DESIGNATED PORT, on the bridge with the lowest cost to the root (ties: lower bridge ID); (4) all other ports go to BLOCKING. The result is a loop-free tree; if a link fails, a blocked port is unblocked.

**VLAN (IEEE 802.1Q).** A VLAN is a separate broadcast domain defined in software. 802.1Q inserts a 4-byte tag after the source MAC: TPID 16 bits = 0x8100, then PCP 3 bits (priority), DEI 1 bit (drop eligible), VID 12 bits (VLAN ID). Usable VIDs are 1 to 4094. The maximum tagged frame becomes 1522 bytes. An ACCESS port belongs to one VLAN and carries untagged frames to end hosts. A TRUNK port carries many VLANs between switches, with tags to tell them apart. Hosts in different VLANs need a router (or layer-3 switch) to communicate.

| Device | Collision domains | Broadcast domains |
|---|---|---|
| Hub (n ports) | 1 | 1 |
| Switch (n ports) | n (one per port) | 1 (without VLANs) |
| Switch with k VLANs | n | k |
| Router (n interfaces) | n | n |

## Full Line-by-Line Breakdown

### SECTION 1: LEARNING BRIDGE
`Switch.receive` implements learn then decide. In the trace A and B sit on port 1 (behind a hub), C on port 2, D on port 3. First A to C: C unknown, so FLOOD. C replying to A: A was learned, FORWARD to port 1. A to B: B is still unknown (B has never sent), FLOOD. D's broadcast always floods. C to D: forwarded to port 3. B to A: both are on port 1, so FILTER. The final table maps A and B to port 1, C to 2, D to 3.

Output from a real run:

```text
===== SECTION 1: LEARNING BRIDGE =====
A and B share port 1 (via a hub), C on port 2, D on port 3
  A -> C        : FLOOD to ports [2, 3, 4] (unknown dst)
  C -> A        : FORWARD to port 1
  A -> B        : FLOOD to ports [2, 3, 4] (unknown dst)
  D -> BROADCAST: FLOOD to ports [1, 2, 4]
  C -> D        : FORWARD to port 3
  B -> A        : FILTER (dst on same port 1, drop)
table now: {'A': 'port 1', 'C': 'port 2', 'D': 'port 3', 'B': 'port 1'}
Learning uses the SOURCE address; forwarding decisions use the DESTINATION.
```

### SECTION 2: FORWARDING TABLE AGING
Aging: a table with a 300 second limit. C is learned at t = 0. At t = 1 and t = 200 frames to C are forwarded. At t = 400 the entry is older than 300 s, so the switch floods again and relearns later. The trap explains why a host that moves ports needs entries to expire.

Output from a real run:

```text
===== SECTION 2: FORWARDING TABLE AGING =====
t=0   C -> A : FLOOD to ports [1, 3] (unknown dst)
t=1   A -> C : FORWARD to port 2
t=200 A -> C : FORWARD to port 2 (C's entry is 200 s old: still valid)
t=400 A -> C : FLOOD to ports [2, 3] (unknown dst) <- C's entry is older than 300 s: aged out
TRAP: a host that moved to another port is unreachable until the entry
ages out or it sends a frame, which is why aging exists (typical default 300 s).
```

### SECTION 3: LOOP = BROADCAST STORM
A triangle of three switches S1-S2-S3. The helper counts copies of one broadcast per hop round, never sending a copy back out the arrival link. The number stays at 2 forever; in real switches with more links it would grow, and there is no TTL to stop it.

Output from a real run:

```text
===== SECTION 3: LOOP = BROADCAST STORM =====
one broadcast injected into a triangle of switches, copies per hop round:
   [2, 2, 2, 2, 2, 2, 2, 2] ... (never reaches 0, and it also multiplies when switches have more links)
Ethernet has no TTL, so a looped broadcast circulates forever.
Redundant links are wanted for fault tolerance -> Spanning Tree Protocol.
```

### SECTION 4: SPANNING TREE ROOT ELECTION
The bridge IDs are priority 32768 for all, so the lowest MAC wins: S3 (...:00). Every bridge starts by claiming itself root; in the first exchange all learn the better claim. Root path costs are S1 19, S2 19, S4 4 (via the 1 Gbps S3-S4 link, cost 4). The code derives the root port of each bridge, then marks every segment that is not a root-port link: S1-S2 (designated on S1 by lower bridge ID, S2 blocks) and S4-S2 (designated on S4 with lower cost 4, S2 blocks). Three links remain, equal to the number of bridges minus one, a spanning tree. The same broadcast on the pruned tree dies out after reaching every switch.

Output from a real run:

```text
===== SECTION 4: SPANNING TREE ROOT ELECTION =====
bridge IDs (priority, MAC): {'S1': (32768, '00:0a:00:00:00:01'), 'S2': (32768, '00:0a:00:00:00:02'), 'S3': (32768, '00:0a:00:00:00:00'), 'S4': (32768, '00:0a:00:00:00:04')}
link costs (100 Mbps = 19, 1 Gbps = 4): [('S1', 'S2', 19), ('S2', 'S3', 19), ('S3', 'S1', 19), ('S3', 'S4', 4), ('S4', 'S2', 19)]
  round 0: every bridge claims itself as root
  round 1: believed root {'S1': 'S3', 'S2': 'S3', 'S3': 'S3', 'S4': 'S3'}
  round 2: believed root {'S1': 'S3', 'S2': 'S3', 'S3': 'S3', 'S4': 'S3'}
elected ROOT BRIDGE: S3 (lowest bridge ID; ties on priority broken by lowest MAC)
root path cost: {'S1': 19, 'S2': 19, 'S3': 0, 'S4': 4}
  segment S1-S2: designated port on S1, port on S2 BLOCKING
  segment S4-S2: designated port on S4, port on S2 BLOCKING
active tree links: [('S2', 'S3'), ('S3', 'S1'), ('S3', 'S4')]
blocked links    : [('S1', 'S2'), ('S4', 'S2')]
same broadcast on the pruned tree, copies per hop round: [1, 2, 0]
storm gone, every switch still reachable: check: OK
If an active link fails, a blocked port moves to forwarding (reconvergence).
```

### SECTION 5: 802.1Q VLAN TAG
`make_tag` packs TPID 0x8100 and a TCI made of PCP (3 bits), DEI (1) and VID (12) with `struct.pack("!HH")`. VLAN 20 priority 5 gives bytes `81 00 a0 14`. `parse_tag` reverses it. VID 4095 (and 0) is rejected by the assert as reserved.

Output from a real run:

```text
===== SECTION 5: 802.1Q VLAN TAG =====
4-byte tag inserted after the source MAC: TPID(16)=0x8100 | PCP(3) DEI(1) VID(12)
tag bytes: 81 00 a0 14 -> {'tpid': '0x8100', 'pcp': 5, 'dei': 0, 'vid': 20}
usable VLAN IDs: 1..4094 (12 bits = 4096 values minus reserved 0 and 4095)
tagged frame max size: 1518 + 4 = 1522 bytes
TRAP make_tag(4095): VID 0 and 4095 are reserved
```

### SECTION 6: ACCESS VS TRUNK PORTS
Port 1 and 2 are access ports in VLAN 10, port 3 is access in VLAN 20, port 4 is a trunk. A VLAN 10 broadcast from port 1 goes untagged to port 2 and tagged (VID 10) to the trunk; port 3 never sees it. A VLAN 20 broadcast reaches only the trunk, tagged 20.

Output from a real run:

```text
===== SECTION 6: ACCESS VS TRUNK PORTS =====
  port 1: access VLAN 10
  port 2: access VLAN 10
  port 3: access VLAN 20
  port 4: trunk (carries all VLANs, tagged)
broadcast from port 1 (VLAN 10) goes to: ['port 2 untagged', 'port 4 tagged VID 10']
broadcast from port 3 (VLAN 20) goes to: ['port 4 tagged VID 20']
port 2 (VLAN 10) never sees VLAN 20 traffic -> separate broadcast domains;
to talk across VLANs you need a router (or layer-3 switch).
```

### SECTION 7: COLLISION VS BROADCAST DOMAINS
Counting domains: one 8-port switch where one port feeds a hub of 3 hosts gives 8 collision domains (the hub plus its hosts count as one) and 1 broadcast domain; two VLANs make it 2 broadcast domains.

Output from a real run:

```text
===== SECTION 7: COLLISION VS BROADCAST DOMAINS =====
Rules: hub/repeater = one shared collision domain; each switch port = its own
collision domain; switch floods broadcasts so one broadcast domain; router or
VLAN boundary splits broadcast domains.
Example: 1 switch with 8 ports, one port feeds a hub with 3 hosts.
  collision domains = 8 (the hub's port and its 3 hosts form ONE)
  broadcast domains = 1 (no VLANs)
  with 2 VLANs: collision domains still 8, broadcast domains = 2
```

## Worked Example
**Problem.** Four bridges have equal priority; S3 has the lowest MAC. Link costs: S3-S1 19, S3-S2 19, S1-S2 19, S3-S4 4, S4-S2 19. Which bridge is root, and which ports block?

**Solution.** Equal priority, lowest MAC wins: S3 is the root. Root path costs: S1 = 19, S2 = 19 (direct to S3), S4 = 4. Segment S1-S2: both ends have cost 19, tie broken by lower bridge ID, so S1 is designated and S2's port on that segment blocks. Segment S4-S2: S4 has cost 4 versus 19, so S4 is designated and S2's port blocks. Active links: S3-S1, S3-S2, S3-S4. The program prints exactly this.

## Key Rules / Gotchas Recap
- Learn from the SOURCE address; decide using the DESTINATION address.
- Unknown or broadcast: flood to all other ports; same port: filter.
- Aging removes stale entries (typical default 300 s, configurable).
- Loops plus no TTL cause broadcast storms; STP blocks redundant ports.
- Root bridge = lowest priority, then lowest MAC (not highest).
- Root port = lowest cost to root; one designated port per segment; the rest block.
- 802.1Q tag = 4 bytes (TPID 0x8100, PCP 3, DEI 1, VID 12); usable VIDs 1-4094.
- Switch ports are separate collision domains; broadcast domains are split only by routers or VLANs.

## Why This Matters
Understanding learning, flooding and STP explains real outages such as broadcast storms and unexpected traffic floods, and VLAN tagging is the basis of network segmentation used in data centres and security design (isolating lab or untrusted traffic).
