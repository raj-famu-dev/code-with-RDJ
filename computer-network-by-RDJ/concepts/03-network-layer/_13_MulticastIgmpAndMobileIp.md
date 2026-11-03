# `_13_MulticastIgmpAndMobileIp.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
IP multicast sends one packet to a group of interested receivers, with routers copying it only where the delivery tree branches, using class D addresses (224.0.0.0/4) and IGMP so hosts can tell their local router which groups they want. Mobile IP lets a device keep its permanent home address while it roams to other networks, by having a home agent forward its traffic through a tunnel to a temporary care-of address. Both extend plain unicast IP to cases it cannot handle efficiently (one-to-many) or at all (a host that moves).

### Part A: Multicast
**Addressing.** Class D: first bits `1110`, range 224.0.0.0 to 239.255.255.255 (224.0.0.0/4), about 2^28 groups. A group address can only be a destination. Well-known groups: 224.0.0.1 all hosts on the subnet, 224.0.0.2 all routers, 224.0.0.5/6 OSPF, 224.0.0.9 RIPv2; 224.0.0.0/24 is link-local (never forwarded by routers); 239.0.0.0/8 is administratively scoped (private use).

**Ethernet mapping.** IPv4 multicast maps to MAC `01:00:5e` + the low 23 bits of the group address. Five bits are lost, so 32 groups share a MAC, and the IP layer must filter.

**IGMP (Internet Group Management Protocol).** Runs between hosts and their directly connected router, carried directly in IP (protocol number 2). The router periodically sends a General Membership Query to 224.0.0.1; hosts answer with Membership Reports for each group they have joined (a host that hears another report for its group may suppress its own). IGMPv1 had no leave (membership just timed out), IGMPv2 added Leave Group and group-specific queries for fast leave, IGMPv3 adds source filtering. IGMP tells the last-hop router which groups have members on a link; it does not build the tree between routers (DVMRP, PIM do).

**ICMP vs IGMP.**

| | ICMP | IGMP |
|---|---|---|
| Purpose | error reporting and diagnostics (ping, unreachable, TTL exceeded) | group membership management for multicast |
| Between | any host/router and any other | host and its directly attached router |
| IP protocol number | 1 | 2 |

**Multicast routing: from flooding to trees.**
- Naive flooding duplicates packets endlessly in a network with loops.
- Reverse Path Forwarding (RPF): a router accepts a packet only if it arrived on the interface it would itself use to send unicast packets to the source; it then forwards to all other interfaces; otherwise it drops it. This yields a loop-free tree rooted at the source, without storing per-packet state.
- Flood and prune (DVMRP, PIM dense mode): flood using RPF, then routers with no group members downstream send Prune messages back up. Good when most subnets have receivers.
- Shared tree (PIM sparse mode, CBT): receivers explicitly send Join messages toward a rendezvous point or core; good for sparse groups across a wide area.

Advantages: sender bandwidth and router load do not grow with receivers. Used for IPTV, software distribution, financial feeds and routing protocol hellos. Limits: best-effort UDP-style delivery, difficult to deploy across the Internet.

### Part B: Mobile IP
**Problem.** An IP address is both identity and location. If a laptop moves to another network its address no longer matches the subnet, yet its TCP connections should survive.

**Entities.** Mobile node (MN) with a permanent home address on its home network; Home Agent (HA), a router on the home network that tracks the MN; Foreign Agent (FA), a router on the visited network; care-of address (CoA), the temporary address where the MN can currently be reached (the FA's address, or a co-located address the MN acquired itself); Correspondent node (CN), the peer.

**Operation.**
1. Agent discovery: HA/FA broadcast agent advertisements (an extension of ICMP router discovery); MN works out whether it is at home or away and learns a CoA.
2. Registration: MN (via the FA) registers the CoA with its HA, creating a binding with a lifetime (UDP port 434).
3. Packets for the home address reach the home network; the HA intercepts them and tunnels them (IP-in-IP encapsulation, protocol 4) to the CoA.
4. The FA (or the MN itself for a co-located CoA) decapsulates and delivers to the MN.
5. The MN replies directly to the CN with its home address as source (triangle routing): inbound goes CN -> HA -> FA -> MN, outbound MN -> CN. Route optimisation lets the CN learn the CoA and tunnel directly.
6. On returning home the MN deregisters.

Typical exam questions: "Explain Mobile IP with a diagram", "Define home agent, foreign agent, care-of address", "What is triangle routing?", "IGMP vs ICMP", "How does RPF work?".

## Full Line-by-Line Breakdown

### SECTION 1: CLASS D AND GROUP ADDRESSES
The `ipaddress` module confirms the block is 224.0.0.0/4 and tells multicast addresses from unicast. `group_to_mac` keeps the low 23 bits and prefixes `01:00:5e`. The trap: 224.1.2.3 and 225.1.2.3 (and 224.129.2.3 vs 239.1.2.3) produce the same MAC, because five group bits are dropped.

Output from a real run:

```text
===== SECTION 1: CLASS D AND GROUP ADDRESSES =====
multicast block 224.0.0.0/4: 224.0.0.0 - 239.255.255.255 (leading bits 1110, 2^28 groups)
  224.0.0.1    is_multicast=True  all hosts on this subnet
  224.0.0.2    is_multicast=True  all routers on this subnet
  224.0.0.5    is_multicast=True  OSPF routers
  224.0.0.9    is_multicast=True  RIPv2 routers
  224.0.0.22   is_multicast=True  IGMPv3 reports
  239.1.2.3    is_multicast=True  administratively scoped (private use)
  192.0.2.1    is_multicast=False unicast, not multicast
A group address is only ever a DESTINATION (never a source). 224.0.0.0/24 is link-local: routers never forward it.
  Ethernet multicast MAC for 224.0.0.1    = 01:00:5e:00:00:01
  Ethernet multicast MAC for 239.1.2.3    = 01:00:5e:01:02:03
  Ethernet multicast MAC for 224.129.2.3  = 01:00:5e:01:02:03
TRAP: only 23 of the 28 group bits fit in the MAC, so 32 groups share one MAC:
  224.1.2.3 -> 01:00:5e:01:02:03   225.1.2.3 -> 01:00:5e:01:02:03 (same). The IP layer must filter.
```

### SECTION 2: IGMP MEMBERSHIP
`IgmpRouter` stores group -> set of hosts. Reports add hosts; `leave` removes them and deletes a group when empty, at which point forwarding for it stops. A final General Query rebuilds the table from whoever still answers. The text compares IGMP and ICMP.

Output from a real run:

```text
===== SECTION 2: IGMP MEMBERSHIP =====
after reports   : {'239.1.1.1': ['hostA', 'hostB'], '239.2.2.2': ['hostC']}
hostA leaves    : {'239.1.1.1': ['hostB'], '239.2.2.2': ['hostC']} (group still has hostB: keep forwarding)
hostC leaves    : {'239.1.1.1': ['hostB']} (no members: stop forwarding 239.2.2.2)
check: OK
periodic General Query: only hosts that still answer are remembered -> {'239.1.1.1': ['hostB'], '239.3.3.3': ['hostD']}
IGMP (IP protocol 2): hosts <-> LOCAL router. Router sends periodic General Queries to 224.0.0.1;
hosts answer with Membership Reports. v2 adds explicit Leave and group-specific query; v3 adds source filtering.
IGMP only tells the last-hop router who is listening; routers use PIM/DVMRP to build the delivery tree.
ICMP vs IGMP: ICMP reports errors/queries about unicast delivery (any host to any host);
  IGMP manages multicast group membership (host to its directly connected router only).
```

### SECTION 3: MULTICAST TREE - FLOOD VS RPF
Five routers with loops. Naive flooding with TTL 4 costs 33 transmissions. RPF uses the BFS parent toward the source as the "interface toward the source": a copy is forwarded only if it came from that parent, so only 10 transmissions are made and 6 of them are dropped on receipt by the RPF check; the accepted copies form the tree R1-R2, R1-R3, R2-R4, R3-R5. Pruning then removes branches with no receivers: with receivers only behind R4, R3 and R5 are pruned.

Output from a real run:

```text
===== SECTION 3: MULTICAST TREE - FLOOD VS RPF =====
links: [('R1', 'R2'), ('R1', 'R3'), ('R2', 'R3'), ('R2', 'R4'), ('R3', 'R4'), ('R3', 'R5'), ('R4', 'R5')] source attached to R1; receivers behind R4 only
naive flooding with TTL 4: 33 transmissions (loops multiply copies)
RPF flooding: 10 transmissions, 6 copies dropped by the RPF check (arrived on the wrong interface)
shortest-path tree toward source R1: {'R2': 'R1', 'R3': 'R1', 'R4': 'R2', 'R5': 'R3'}
after PRUNING branches with no receivers, routers on the tree: R1 + ['R2', 'R4']
pruned routers (no receivers downstream): ['R3', 'R5']
check: OK (RPF sends each copy over a loop-free tree: fewer transmissions than naive flooding)
Flood-and-prune (DVMRP, PIM dense mode): flood with RPF, then prune; good for dense groups.
Shared tree (PIM sparse mode, core-based): receivers explicitly JOIN toward a rendezvous point; good for sparse groups.
```

### SECTION 4: MOBILE IP (HOME AGENT / FOREIGN AGENT / CARE-OF ADDRESS)
`HomeAgent` keeps a binding table (home address -> care-of address) and wraps intercepted packets in an outer packet with protocol 4 addressed to the CoA; `ForeignAgent` unwraps it. The numbered steps print the full life cycle: discovery, registration, correspondent sends to the home address, tunnelling, decapsulation, direct reply (triangle routing), and deregistration after returning home, when the HA delivers normally again.

Output from a real run:

```text
===== SECTION 4: MOBILE IP (HOME AGENT / FOREIGN AGENT / CARE-OF ADDRESS) =====
1. Agent discovery: FA advertises (ICMP router advertisement extension), mobile learns care-of address 172.20.5.1
2. Registration: mobile -> FA -> HA 'home 10.1.0.77 is now reachable via 172.20.5.1'
   HA binding table: {'10.1.0.77': '172.20.5.1'}
3. Correspondent sends to the HOME address: [203.0.113.8 -> 10.1.0.77]
4. HA intercepts and tunnels (outer protocol 4): [10.1.0.1 -> 172.20.5.1] carrying [203.0.113.8 -> 10.1.0.77]
5. FA decapsulates and hands to the mobile: [203.0.113.8 -> 10.1.0.77] hello mobile
6. Mobile replies DIRECTLY to the correspondent (no tunnel): [10.1.0.77 -> 203.0.113.8]
   Path in: CN -> HA -> FA -> MN, path back: MN -> CN  = triangle routing (inefficient).
   Fix (route optimisation): CN learns the care-of address and sends straight to it.
7. Mobile returns home and deregisters -> HA delivers normally: [203.0.113.8 -> 10.1.0.77]
check: OK
TRAP: the CORRESPONDENT never knows the mobile moved; the home address stays constant so TCP connections survive.
Two kinds of care-of address: FA care-of (shared by many mobiles, FA decapsulates) and
co-located care-of (mobile gets its own temporary address, decapsulates itself).
Registration has a lifetime and must be renewed; registration messages use UDP port 434.
```

### SECTION 5: COMPARISON TABLE
Unicast vs multicast vs broadcast, and the bandwidth saving for a 2 Mbit/s stream to 1000 viewers (2000 Mbit/s from the source with unicast versus 2 Mbit/s with multicast). The numbers are simple arithmetic on assumed inputs, not measurements.

Output from a real run:

```text
===== SECTION 5: COMPARISON TABLE =====
                  unicast          multicast                      broadcast
Delivery          1 to 1           1 to many (group)              1 to all
Address           unicast IP       class D 224.0.0.0/4            255.255.255.255 / directed
Copies on a link  1 per receiver   1 (shared tree)                1 per network
Multicast saves sender bandwidth: 1 stream to 1000 receivers instead of 1000 unicast streams;
  e.g. a 2 Mbit/s video to 1000 viewers: unicast 2000 Mbit/s from the source, multicast 2 Mbit/s.
```

## Worked Example
**Q:** Mobile node with home address 10.1.0.77 (home agent 10.1.0.1) is visiting a network whose foreign agent has care-of address 172.20.5.1. A correspondent 203.0.113.8 sends it a packet. Describe the packets.

1. Correspondent sends `203.0.113.8 -> 10.1.0.77`. It routes to the home network.
2. HA (10.1.0.1) has a binding 10.1.0.77 -> 172.20.5.1, intercepts the packet and encapsulates it: outer `10.1.0.1 -> 172.20.5.1`, protocol 4, inner packet unchanged.
3. FA at 172.20.5.1 strips the outer header and delivers the inner packet to the mobile.
4. Mobile replies with source = its home address: `10.1.0.77 -> 203.0.113.8`, sent directly (no tunnel). Inbound and outbound paths differ: triangle routing.

The script prints exactly these packet headers.

## Key Rules / Gotchas Recap
- Class D = 224.0.0.0/4 (1110...), only as a destination; 224.0.0.x is link-local.
- MAC = 01:00:5e + low 23 bits; 32 groups per MAC, filter in IP.
- IGMP: host to local router, IP protocol 2; v2 adds leave, v3 source filtering. ICMP is protocol 1 and is for errors/diagnostics.
- RPF: accept only on the interface toward the source, forward on all others; prune where no receivers.
- Dense mode floods and prunes; sparse mode joins toward a rendezvous point.
- Mobile IP: home address is permanent; the care-of address is temporary; HA tunnels with IP-in-IP (protocol 4).
- Triangle routing: in via HA, out directly; fixed by route optimisation.
- The correspondent does not need to know the host moved.

## Why This Matters
Multicast and group-membership ideas underlie service discovery (mDNS, SSDP), IPTV, market-data feeds and even cluster heartbeat protocols, and are a recurring source of unexpected traffic on corporate networks. Mobile IP's identity-versus-location split is the same idea modern mobile networks, VPNs and roaming connections rely on.
