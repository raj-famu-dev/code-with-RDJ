# `_1_NetworkTypesAndUses.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A computer network is a set of independent devices (hosts) connected by links so they can exchange data and share resources. Networks are classified by size (PAN, LAN, MAN, WAN), by who may use them (Internet, intranet, extranet), by how the machines relate (client-server or peer-to-peer) and by how many receivers a message has (unicast, broadcast, multicast, anycast).

**Goals of networking.** Resource sharing (printers, files, a database server), reliability (data replicated on several machines), cost saving (one big server instead of a big computer per user), scalability (add machines gradually), communication medium (email, video calls, messaging) and remote access.

**Applications.** Web browsing, email, file transfer, video streaming, online banking, e-commerce, IoT, cloud computing and, for you, serving machine-learning models over HTTP.

**Classification by scale.**

| Type | Full name | Typical reach | Example | Notes |
|------|-----------|---------------|---------|-------|
| PAN | Personal Area Network | about 1-10 m | Bluetooth headset, phone tethering | one person's devices |
| LAN | Local Area Network | up to a few km | home Wi-Fi, office, lab | privately owned, high speed, Ethernet/Wi-Fi |
| MAN | Metropolitan Area Network | a city, tens of km | cable TV network, city-wide fibre ring | e.g. DQDB, FDDI in old textbooks |
| WAN | Wide Area Network | country/world | the Internet, bank branch links | uses leased lines, telecom carriers, routers |

The reaches are rules of thumb, not a standard; exams expect the ordering PAN < LAN < MAN < WAN.

**Internet, intranet, extranet.** The *Internet* (capital I) is the global public network of networks running TCP/IP. An *intranet* is a private network of one organisation that uses Internet technology (web servers, email) but is only open to its own staff. An *extranet* is an intranet extended to selected outsiders such as suppliers or customers, usually behind a login or VPN. The label depends on who has access, not on the wires. An *internetwork* (lowercase *internet*) is any set of networks joined by routers.

**Client-server vs peer-to-peer.**

| Point | Client-server | Peer-to-peer (P2P) |
|-------|---------------|--------------------|
| Roles | fixed: server provides, client requests | every node is both client and server |
| Control | centralised, easy to secure, back up, administer | decentralised, hard to control |
| Failure | server is a single point of failure | no single point of failure |
| Scaling | server load grows with the number of clients | capacity grows as peers join |
| Cost | server hardware is expensive | cheap, no dedicated server |
| Examples | web, email, banking | BitTorrent, small office file sharing |

Kurose-Ross give the time to distribute a file of F bits to N peers: client-server `D_cs = max(N*F/u_s, F/d_min)`, peer-to-peer `D_p2p = max(F/u_s, F/d_min, N*F/(u_s + sum(u_i)))`, where `u_s` is the server upload rate, `u_i` each peer's upload rate and `d_min` the slowest download rate.

**Transmission (casting) modes.**

| Mode | Receivers | Example |
|------|-----------|---------|
| Unicast | exactly one | a normal TCP connection, a web request |
| Broadcast | every host on the network/segment | ARP request, DHCP discover (Ethernet destination `ff:ff:ff:ff:ff:ff`) |
| Multicast | a chosen group that joined | IPTV, routing protocol hellos, IPv4 range 224.0.0.0/4 |
| Anycast | one member of a group, the nearest | root DNS servers, CDN front doors, IPv6 anycast |

Do not confuse the last two: multicast reaches *all* group members, anycast reaches *one*. IPv6 dropped broadcast and uses multicast instead.

**Typical exam questions.** Differentiate LAN/MAN/WAN; differentiate intranet and extranet; compare client-server with P2P; list network goals/applications; define unicast, multicast, broadcast.

## Full Line-by-Line Breakdown

### SECTION 1: PAN / LAN / MAN / WAN
`SCALES` stores the rule-of-thumb reach of each class. `classify()` walks the list from smallest to largest and returns the first class that covers the distance, falling back to WAN. The four test distances land in four different classes and the `assert` confirms it.

```text
===== SECTION 1: PAN / LAN / MAN / WAN =====
type    reach (m)  example
PAN            10  Bluetooth earbuds, phone <-> smartwatch (about 10 m)
LAN         1,000  home Wi-Fi, one office floor or campus lab (up to ~1 km)
MAN        50,000  cable-TV/fibre ring across a city (up to ~50 km)
WAN    10,000,000  the Internet, a bank's links between countries
classify(         1 m) -> PAN  (laptop to mouse)
classify(       120 m) -> LAN  (lab of 40 PCs)
classify(    12,000 m) -> MAN  (two campuses in one city)
classify(11,000,000 m) -> WAN  (Florida to Tokyo)
check: OK
```

### SECTION 2: INTERNET vs INTRANET vs EXTRANET
`access_kind()` is deliberately not about technology: the same web server is Internet, intranet or extranet depending only on who is allowed in. The trap line reminds you of the capital-I distinction that exams love.

```text
===== SECTION 2: INTERNET vs INTRANET vs EXTRANET =====
public website               -> Internet (anyone)
HR payroll portal            -> Intranet (organisation's own staff only)
supplier order portal        -> Extranet (staff + approved outside partners)
random visitor to payroll    -> No access
Trap: 'internet' (lowercase) = any interconnected networks; 'Internet' = the one global TCP/IP network.
```

### SECTION 3: CLIENT-SERVER vs PEER-TO-PEER
First a real client-server exchange on loopback: the server binds `127.0.0.1` port 0 (the OS picks a free port), a thread accepts one connection, the client sends `GET page` and receives a reply; sockets have timeouts and the thread is joined. Then the file-distribution formulas are evaluated for a 15 GB file (120 billion bits), a 30 Mbps server and 2 Mbps peers. With 1000 peers client-server needs 1111 hours but P2P stays at the 16.7 hour floor set by the slowest download (`F/d_min`), because every new peer also uploads.

```text
===== SECTION 3: CLIENT-SERVER vs PEER-TO-PEER =====
loopback exchange: SERVER REPLY to 'GET page'
 peers N   client-server (h)    peer-to-peer (h)
      10                16.7                16.7
     100               111.1                16.7
    1000              1111.1                16.7
Client-server time grows linearly with N; P2P stays near the F/d_min floor because peers add upload capacity.
check: OK
```

### SECTION 4: UNICAST / BROADCAST / MULTICAST / ANYCAST
Six nodes sit at different hop distances from the sender. Each function returns the *set of receivers* so the difference is visible as a count: 1, 6, the group size 3, and 1 again for anycast, which picks the member with the fewest hops (`min` with a tie-break on name).

```text
===== SECTION 4: UNICAST / BROADCAST / MULTICAST / ANYCAST =====
unicast to D (1-to-1)                        -> receivers=['D'] (1 of 6)
broadcast (1-to-all)                         -> receivers=['A', 'B', 'C', 'D', 'E', 'F'] (6 of 6)
multicast video-group (1-to-many members)    -> receivers=['B', 'D', 'F'] (3 of 6)
anycast dns-anycast (1-to-nearest-one)       -> receivers=['C'] (1 of 6)
Trap: anycast looks like multicast (a group address) but delivers to ONE member only.
check: OK
```

### SECTION 5: WORKED EXAMPLE
See the next heading; the code does the same arithmetic.

```text
===== SECTION 5: WORKED EXAMPLE =====
total bits the server must upload = 50 x 48,000,000,000 = 2,400,000,000,000
time = 2,400,000,000,000 / 100,000,000 = 24,000 s = 400 min = 6.67 h
check: OK
```

## Worked Example
**Problem.** A server uploads at 100 Mbps and must send a 6 GB file to 50 clients using client-server. How long does it take if client download rates are not a bottleneck?

1. File size in bits = 6 x 8 x 10^9 = 48 x 10^9 bits.
2. The server must upload one full copy per client: 50 x 48 x 10^9 = 2.4 x 10^12 bits.
3. Time = bits / rate = 2.4 x 10^12 / 10^8 = 24,000 s.
4. 24,000 / 3600 = 6.67 hours.

The code prints exactly this (24,000 s, 400 min, 6.67 h). Under P2P the same job would drop sharply as peers share the upload load.

## Key Rules / Gotchas Recap
- PAN < LAN < MAN < WAN by reach; the boundaries are conventions, not law.
- Internet (capital I) is one specific network; internet is any network of networks.
- Intranet = staff only; extranet = staff plus chosen outsiders; the technology is the same.
- Client-server has a single point of failure; P2P does not but is harder to secure.
- Multicast reaches every group member; anycast reaches only the nearest one.
- Broadcast stays inside one broadcast domain; routers do not forward it. IPv6 has no broadcast.
- Network speeds use decimal prefixes: 1 Mbps = 1,000,000 bits per second.

## Why This Matters
Choosing client-server versus P2P versus anycast is exactly the architecture decision behind serving a model API, distributing large model weights or running a DNS/CDN layer. Knowing who may reach a service (Internet, intranet, extranet) is also the first question in any security review.
