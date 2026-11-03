# `_10_NetworkDevicesAndCabling.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Network devices are the boxes that connect hosts and networks; each works at a particular OSI layer and so decides how far a signal, a frame or a broadcast travels. Knowing which device splits a *collision domain* and which splits a *broadcast domain* is one of the most common exam questions in networking, along with which cable (straight-through or crossover) joins which devices.

**Devices.**

| Device | Layer | What it does | Collision domains | Broadcast domains |
|--------|-------|--------------|-------------------|-------------------|
| Repeater | 1 | regenerates a weakened signal bit by bit to extend a segment; no filtering | extends | extends |
| Hub | 1 | multiport repeater; every bit arriving on a port is sent out of all other ports; half duplex, shared bandwidth | one domain for all ports | one |
| Bridge | 2 | connects two LAN segments, learns which MAC addresses are on each side, forwards only when needed, can join different LAN types | one per port (segment) | one |
| Switch | 2 | multiport bridge with hardware forwarding; MAC address table; supports full duplex and VLANs | one per port | one (per VLAN) |
| Router | 3 | forwards packets between different networks using IP addresses and a routing table; decrements TTL; blocks broadcasts | one per interface | one per interface |
| Gateway | up to 7 | converts between protocols or architectures (e.g. a mail gateway, VoIP gateway); in everyday use "default gateway" means the router's address | separates | separates |
| NIC | 1-2 | the adapter with the host's MAC address; frames, medium access | - | - |
| Modem | 1 | modulator-demodulator: converts digital data to analog (and back) for telephone, cable or DSL lines | - | - |
| Access point | 1-2 | connects Wi-Fi clients to the wired LAN; wireless clients share the air (half duplex, CSMA/CA) | shared air | joins |

**Collision domain** = set of devices whose frames can collide because they share a medium (hubs, repeaters, shared Wi-Fi channel). **Broadcast domain** = set of devices that receive a Layer-2 broadcast (destination `ff:ff:ff:ff:ff:ff`) sent by any one of them. Rules: hub or repeater ports share one collision domain; every switch or bridge port is its own collision domain; routers separate broadcast domains; switches do not (unless VLANs are configured, in which case each VLAN is a separate broadcast domain).

**Switch operation.** A switch builds a MAC address table by *learning*: it records the source MAC of every frame against the port it arrived on. For each frame it then *forwards* (destination known, other port), *filters* (destination on the same port), or *floods* (destination unknown or broadcast: all ports but the incoming one). Entries *age out* after a timeout. Cut-through switches start forwarding after reading the destination address; store-and-forward switches receive the whole frame and check the FCS first.

**Cabling.** Twisted-pair Ethernet cables use RJ45 connectors with two wiring standards for the colour order, T568A and T568B. A *straight-through* cable has the same standard on both ends and connects *unlike* devices (PC to switch, PC to hub, router to switch). A *crossover* cable has T568A on one end and T568B on the other, which swaps pins 1,2 with 3,6, and connects *like* devices (PC to PC, switch to switch, hub to switch, PC to router). For 10/100BASE-T a PC or router (MDI) transmits on pins 1 and 2 and receives on pins 3 and 6; a hub or switch (MDI-X) does the reverse. Modern ports detect and fix the mismatch themselves (auto-MDI/MDI-X), and Gigabit Ethernet uses all four pairs. A *rollover* (console) cable is a different thing, used for device configuration.

**Typical exam questions.** Which device works at which layer; count collision and broadcast domains in a diagram; hub vs switch; bridge vs switch; router vs switch; which cable joins which devices; how a switch learns.

## Full Line-by-Line Breakdown

### SECTION 1: DEVICE SUMMARY
A table of the nine devices with layer and effect on the two kinds of domain, plus the one-line rule to memorise.

```text
===== SECTION 1: DEVICE SUMMARY =====
device        layer        collision dom.        broadcast dom.        job
Repeater      1 Physical   joins                 joins                 regenerates/amplifies the signal to extend distance
Hub           1 Physical   joins                 joins                 multiport repeater; sends every bit out of all other ports
Bridge        2 Data link  separates             joins                 joins 2 LAN segments; learns MACs and filters
Switch        2 Data link  separates (per port)  joins (unless VLANs)  multiport bridge; per-port forwarding by MAC table
Router        3 Network    separates             separates             forwards packets between networks using IP
Gateway       up to 7      separates             separates             protocol converter between different architectures
NIC           1-2          -                     -                     adapter with a MAC address that connects a host to the medium
Modem         1 Physical   -                     -                     modulates/demodulates between digital data and an analog line
Access point  1-2          joins (shared air)    joins                 bridges wireless clients (Wi-Fi) onto a wired LAN
Rule: hubs/repeaters EXTEND a collision domain; switches/bridges SPLIT collision domains; only routers split broadcast domains.
```

### SECTION 2: COUNTING COLLISION AND BROADCAST DOMAINS
`Net` stores devices with a kind and a list of links. Collision domains: devices of a shared-medium kind (host, hub, repeater, access point) joined by links form one domain (found with union-find); every link that touches only switching devices (switch/bridge/router on both ends) is a domain by itself; and a host connected to a switch port is its own shared component, hence one domain per switch port. Broadcast domains: remove routers and count the connected groups (plus router-to-router links). Four topologies are counted and asserted: 1 hub = 1 and 1; 1 switch with 4 hosts = 4 and 1; router + two switches = 8 and 2; and a mixed hub/switch/router network = 5 and 2.

```text
===== SECTION 2: COUNTING COLLISION AND BROADCAST DOMAINS =====
topology                                       collision broadcast
A: 1 hub + 4 hosts                                     1         1
B: 1 switch + 4 hosts                                  4         1
C: router + 2 switches x 3 hosts                       8         2
D: hub(3)->switch(+2)->router->1 host                  5         2
Hand check C: 6 host-switch links + 2 router-switch links = 8 collision domains; router splits 2 broadcast domains.
Trap: a switch splits collision domains but NOT broadcast domains; an ARP request still floods every port of every switch.
check: OK
```

### SECTION 3: HUB vs SWITCH FORWARDING
Four hosts on ports 1 to 4 send ten frames. The hub copies every frame to all three other ports (30 copies). The switch learns the source MAC of each frame, sends frames to unknown destinations and the broadcast out of all other ports (flood) and later sends known destinations out of a single port: 18 copies in total, and the hosts that are not involved no longer see the traffic. The trap moves host B to another port; until B transmits again the stale table entry sends A's frames to the old port.

```text
===== SECTION 3: HUB vs SWITCH FORWARDING =====
frame                   hub sends to ports    switch sends to ports   switch table after
A -> B                  [2, 3, 4]             [2, 3, 4]               {'A': 1}
B -> A                  [1, 3, 4]             [1]                     {'A': 1, 'B': 2}
A -> C                  [2, 3, 4]             [2, 3, 4]               {'A': 1, 'B': 2}
C -> A                  [1, 2, 4]             [1]                     {'A': 1, 'B': 2, 'C': 3}
A -> B                  [2, 3, 4]             [2]                     {'A': 1, 'B': 2, 'C': 3}
B -> C                  [1, 3, 4]             [3]                     {'A': 1, 'B': 2, 'C': 3}
C -> B                  [1, 2, 4]             [2]                     {'A': 1, 'B': 2, 'C': 3}
A -> D                  [2, 3, 4]             [2, 3, 4]               {'A': 1, 'B': 2, 'C': 3}
D -> A                  [1, 2, 3]             [1]                     {'A': 1, 'B': 2, 'C': 3, 'D': 4}
A -> broadcast          [2, 3, 4]             [2, 3, 4]               {'A': 1, 'B': 2, 'C': 3, 'D': 4}
total frame copies sent: hub = 30, switch = 18
Unknown destinations flood (A->B, A->C, A->D the first time); once a MAC is learned, frames go out ONE port. Broadcasts always flood.

Trap: host B is unplugged and moved from port 2 to a spare port 5 (nothing is sent yet).
  A -> B goes to ports [2]: the stale entry still says port 2, so B (now on port 5) never receives it.
  Fix: B transmits once (the switch relearns port 5) or the entry ages out (typical default is a few minutes).
  after B transmits on port 5: A -> B goes to ports [5]
check: OK
```

### SECTION 4: STRAIGHT-THROUGH vs CROSSOVER CABLES
The T568A and T568B colour orders are lists of 8 wire colours. `cable_map()` matches colours between the two ends to see which pin each wire reaches: B to B is straight; A to B swaps 1 with 3 and 2 with 6. `link_works()` then checks that every transmit pin of one end lands on a receive pin of the other end. The table confirms the rule: unlike devices need a straight-through cable, like devices need a crossover.

```text
===== SECTION 4: STRAIGHT-THROUGH vs CROSSOVER CABLES =====
pin   T568A         T568B
 1    white/green   white/orange
 2    green         orange
 3    white/orange  white/green
 4    blue          blue
 5    white/blue    white/blue
 6    orange        green
 7    white/brown   white/brown
 8    brown         brown
straight-through (B on both ends): {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
crossover (A on one end, B on the other): pins that change = {1: 3, 2: 6, 3: 1, 6: 2}

link                straight-through    crossover   rule
PC - switch         works               NO LINK     unlike devices -> straight
PC - hub            works               NO LINK     unlike devices -> straight
router - switch     works               NO LINK     unlike devices -> straight
PC - PC             NO LINK             works       like devices -> crossover
PC - router         NO LINK             works       like devices -> crossover
switch - switch     NO LINK             works       like devices -> crossover
hub - switch        NO LINK             works       like devices -> crossover
Modern NICs and switch ports use Auto-MDI/MDI-X and fix the mismatch themselves; Gigabit uses all 4 pairs,
so a real gigabit crossover also swaps pairs 4-5 with 7-8. Memory trick: like-to-like needs a cross.
check: OK
```

### SECTION 5: WORKED EXAMPLE
Counts the domains of the exam network below.

```text
===== SECTION 5: WORKED EXAMPLE =====
Problem: a switch with 8 PCs, joined by a router to a second switch with 5 PCs. Count the domains.
collision domains = 15 (8 + 5 host links + 2 router links = 15)
broadcast domains = 2 (one per router interface side)
check: OK
```

## Worked Example
**Problem.** A switch connects 8 PCs, a router connects that switch to a second switch which has 5 PCs. How many collision and broadcast domains are there?

1. Each of the 13 PCs has its own switch port: 13 collision domains.
2. Each of the two links from the router to a switch is also its own collision domain: 2 more.
3. Total collision domains = 15.
4. The router has two interfaces, one on each side; each side is one broadcast domain: 2 broadcast domains.

The code reports 15 and 2. If the two switches were replaced by hubs there would be only 2 collision domains (each hub, with its PCs and its router link, is one big shared domain), which is why hubs are obsolete.

## Key Rules / Gotchas Recap
- Hub and repeater: Layer 1, one shared collision domain.
- Bridge and switch: Layer 2, one collision domain per port, but one broadcast domain (per VLAN).
- Router: Layer 3, splits both collision and broadcast domains.
- A switch learns from the SOURCE address and forwards by the DESTINATION address; unknown and broadcast are flooded.
- Stale MAC table entries after a move cause black holes until relearned or aged out.
- Unlike devices use straight-through; like devices use crossover (auto-MDI/MDIX makes this moot on modern gear).
- "Gateway" is used loosely; the default gateway on a PC is simply the router's address.

## Why This Matters
Switch behaviour is the root of real attacks and faults (MAC flooding, ARP spoofing, broadcast storms) that you will study in the security module, and domain boundaries decide how you segment networks, VLANs and cloud subnets. Being able to read a topology and say where traffic goes is core troubleshooting skill.
