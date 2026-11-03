# `_2_MobileAndCellularNetworks.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A cellular network divides a region into cells, each served by a base station with a limited set of radio channels. Because radio signals fade with distance, the same frequencies can be reused in cells far enough apart, which multiplies the capacity of a scarce spectrum; as a user moves, the call is handed off from cell to cell without breaking.

**Cell clusters and frequency reuse.** Cells are drawn as hexagons because they tile a plane with no gaps while approximating a circular coverage area. A *cluster* of N cells uses all S available channels once, so each cell gets k = S/N channels. The cluster is then repeated across the area. For hexagons, N must equal i^2 + i*j + j^2 for non-negative integers i and j, which gives 1, 3, 4, 7, 9, 12, 13, 16, 19 ... (5, 6, 8 and 10 are not possible). The *frequency reuse factor* is 1/N. The distance between centres of the nearest co-channel cells is D = R * sqrt(3N), where R is the cell radius, so D/R = sqrt(3N). A small N gives more channels per cell (higher capacity) but co-channel cells are closer, so interference is higher. With six first-tier interferers and path-loss exponent n, a common approximation is SIR = (D/R)^n / 6. To grow capacity operators *split* cells into smaller ones, *sector* them with directional antennas, or lower power. Total capacity of a system with M clusters is C = M * S.

**Handoff (handover).** When a mobile moves, the signal from the serving base station falls and a neighbour's rises. The network switches the call when the neighbour is better. A *hard* handoff releases the old channel before acquiring the new one (break-before-make: GSM, LTE, 5G NR). A *soft* handoff keeps both links briefly (make-before-break: 3G CDMA). Switching the instant the neighbour is stronger causes *ping-pong* between two cells when the signal fluctuates; networks use a *hysteresis margin* (neighbour must beat the server by X dB) and a time-to-trigger.

**Generations.** The main technological shift per generation (dates approximate and vary by country):

| Gen | Era | Key technology | Main shift |
|---|---|---|---|
| 1G | 1980s | analog voice, FDMA (e.g. AMPS) | mobile voice |
| 2G | early 1990s | digital GSM (TDMA+FDMA), IS-95 (CDMA) | digital voice, SMS, encryption; GPRS/EDGE add packet data |
| 3G | early 2000s | UMTS/WCDMA, CDMA2000 | genuine mobile internet |
| 4G | around 2010 | LTE, OFDMA, all-IP core | pure packet network; voice over IP (VoLTE) |
| 5G | from about 2019 | NR, mmWave and mid-band, massive MIMO | service-based core, network slicing, low-latency modes |

**Core network roles.** GSM: mobile station, base transceiver station (BTS), base station controller (BSC), mobile switching centre (MSC), with the Home Location Register (HLR, permanent subscriber record and current location pointer) and Visitor Location Register (VLR, records of subscribers currently in the MSC's area). LTE's Evolved Packet Core: eNodeB radio node, MME (mobility management), HSS (subscriber database), Serving Gateway and PDN Gateway (user data to the internet). 5G core is service-based: gNB radio node, AMF (access and mobility), SMF (session management), UPF (user plane forwarding), UDM (subscriber data). When a phone moves to a new MSC area it performs a *location update*, which is how an incoming call finds it.

**Satellite networks.** A satellite's orbital period follows Kepler's third law, T = 2*pi*sqrt(a^3/mu). *GEO* satellites at about 35,786 km have a period of one sidereal day, so they hover over one point; they cover huge areas but a ground-satellite-ground hop has a minimum propagation delay of about 239 ms (round trip about 477 ms). *MEO* (roughly 2,000-35,000 km, e.g. navigation systems) and *LEO* (roughly 500-2,000 km) have much shorter delay; at 550 km the straight-up-and-down floor is under 4 ms one way. LEO satellites cross the sky in minutes, so a LEO network needs many satellites and constant handoff of ground stations between them.

**Mobile IP.** Module 03's IP addresses identify a *location*, so a host that moves would normally have to change address and drop its TCP connections. Mobile IP (RFC 5944 for IPv4) keeps a permanent *home address* on the *home network*. When away, the mobile node obtains a *care-of address* (CoA) from a foreign agent or via DHCP and registers the binding with its *home agent*. The home agent intercepts packets for the home address (proxy ARP) and *tunnels* them to the CoA using IP-in-IP encapsulation (RFC 2003). Replies can go directly to the correspondent (triangle routing).

Typical exam questions: compute cluster size, reuse distance and channels per cell; why hexagons; hard vs soft handoff; HLR vs VLR; roles of home and foreign agents; advantages of LEO over GEO.

## Full Line-by-Line Breakdown

### SECTION 1: CELLS, FREQUENCY REUSE AND THE REUSE FACTOR
`valid_cluster_sizes` enumerates i^2 + ij + j^2, so the code shows that 5, 6, 8 and 10 are *not* valid (the trap: students often pick N = 5 or 6). The table computes k = S/N channels per cell, reuse factor 1/N, D/R = sqrt(3N) and the first-tier SIR approximation 10 log10((D/R)^4 / 6) with path-loss exponent 4. The trade-off is visible: N = 3 gives 280 channels per cell but only 11.3 dB SIR; N = 12 gives 70 channels per cell and 23.3 dB. The numbers are the textbook idealisation; real networks add sectors, power control and other tricks.

```text
===== SECTION 1: CELLS, FREQUENCY REUSE AND THE REUSE FACTOR =====
Valid cluster sizes N = i^2+ij+j^2 up to 20: [1, 3, 4, 7, 9, 12, 13, 16, 19]
TRAP: N=5, 6, 8, 10 look plausible but are NOT valid for hexagonal cells. In the valid list? {5: False, 6: False, 8: False, 10: False}
Operator has S=840 channels; one cluster of N cells uses all S, so each cell gets k=S/N
  N   channels/cell k=S/N   reuse factor 1/N   D/R=sqrt(3N)   SIR(6 interferers, n=4)
  3          280            1/3                3.000        11.3 dB
  4          210            1/4                3.464        13.8 dB
  7          120            1/7                4.583        18.7 dB
 12           70            1/12               6.000        23.3 dB
Capacity trade-off: a smaller N gives every cell more channels (more capacity) but a smaller D/R,
so co-channel cells sit closer and the signal-to-interference ratio (SIR) falls.
System capacity for M=32 clusters is C = M*S = 26,880 channels; with smaller cells M grows.
Same 224 cells: N=7 -> 120 channels per cell, N=4 -> 210 per cell (x1.75 capacity per cell)
check: OK (D/R for N=7 is 4.583)
```

### SECTION 2: HANDOFF AND THE PING-PONG TRAP
A mobile drives from one base station (0 m) toward another (1000 m). The received power uses a log-distance path-loss model plus seeded random fading (4 dB standard deviation), identical for both runs so the comparison is fair. Handoff when the neighbour is merely stronger flips back and forth near the boundary. Requiring a 6 dB margin cuts the number of handoffs but does not remove all flipping; real systems also use a time-to-trigger. The `assert` checks only that hysteresis gave fewer handoffs and still at least one genuine crossing.

```text
===== SECTION 2: HANDOFF AND THE PING-PONG TRAP =====
Mobile drives 0 -> 1000 m past a cell edge at ~500 m, noisy signal (seeded).
Switch whenever the other cell is stronger (0 dB hysteresis): 9 handoffs: [(340.0, 'BS2'), (360.0, 'BS1'), (440.0, 'BS2'), (500.0, 'BS1'), (540.0, 'BS2'), (560.0, 'BS1'), (600.0, 'BS2'), (660.0, 'BS1'), (680.0, 'BS2')]
Switch only if stronger by 6 dB (hysteresis):                  3 handoffs: [(640.0, 'BS2'), (660.0, 'BS1'), (680.0, 'BS2')]
check: OK (hysteresis reduces the number of handoffs; a genuine crossing still hands off)
Hysteresis cuts the flip-flopping (9 -> 3 here) but does not remove it entirely; real systems add time-to-trigger too.
Hard handoff = break-before-make (GSM, LTE, NR). Soft handoff = make-before-break (3G CDMA).
```

### SECTION 3: GENERATIONS 1G - 5G
A table of the main idea of each generation. It deliberately omits speed numbers: peak rates are marketing ceilings and real rates differ by operator, band, load and location, and I have no measurement here to cite.

```text
===== SECTION 3: GENERATIONS 1G - 5G =====
Gen  Era (approx.)      Main technology                                 Main shift
1G   1980s            analog voice (e.g. AMPS), FDMA                  wireless voice at all
2G   early 1990s      digital voice, GSM = TDMA+FDMA; IS-95 = CDMA    digital + SMS + encryption (GPRS/EDGE add packet data)
3G   early 2000s      UMTS/WCDMA, CDMA2000                            real mobile packet data, internet access
4G   around 2010      LTE, OFDMA downlink, all-IP                     pure packet network, voice becomes VoLTE
5G   from about 2019  NR, wider bands incl. mmWave, massive MIMO      service-based core, slicing, ultra-low latency modes
Eras are approximate and differ by country/operator; speeds are NOT listed because real rates vary hugely.
```

### SECTION 4: CORE NETWORK ROLES AND A LOCATION UPDATE
The role table maps equivalent functions across GSM, LTE and 5G. The `Network` class then models a HLR that remembers one serving MSC per phone and a VLR per MSC. A location update moves the phone's record; `route_call` asks the HLR which MSC to page. The phone number is fictional (555-0100 style). The closing remark links the idea to Mobile IP: "home" record plus "visitor" record.

```text
===== SECTION 4: CORE NETWORK ROLES AND A LOCATION UPDATE =====
Role                GSM                 LTE (EPC)            5G
Radio node          BTS (+BSC)          eNodeB               gNB
Mobility/attach     MSC/VLR             MME                  AMF
Subscriber DB       HLR                 HSS                  UDM
Packet gateway      GGSN/SGSN (GPRS)    SGW + PGW            UPF (user plane) + SMF (sessions)
  location update: +1-555-0100 now at MSC-Tallahassee; HLR points to MSC-Tallahassee
  call for +1-555-0100: gateway asks HLR -> MSC-Tallahassee -> page via BTS in its area
  location update: +1-555-0100 now at MSC-Orlando; HLR points to MSC-Orlando (was MSC-Tallahassee)
  call for +1-555-0100: gateway asks HLR -> MSC-Orlando -> page via BTS in its area
The HLR/HSS is the 'home' record; the VLR/MME is the 'visitor' record. Same idea as Mobile IP's home/foreign agent.
```

### SECTION 5: SATELLITE AND LEO
Kepler's law with mu = 398,600.4418 km^3/s^2 and Earth radius 6,378.137 km gives the orbital period. GEO comes out at about 86,164 s (a sidereal day), which the `assert` verifies, and that is *why* GEO satellites appear fixed. Propagation delay is distance over the speed of light: 2 x 35,786 km / 299,792 km/s = 238.7 ms one-way ground-to-ground at best, 477.5 ms RTT. For a 550 km LEO example, 3.7 ms and 7.3 ms. These are physics floors, never promises of real latency.

```text
===== SECTION 5: SATELLITE AND LEO =====
GEO                              altitude  35786 km: orbital period   1436.1 min, min one-way hop  238.7 ms, min RTT  477.5 ms
LEO (550 km, example altitude)   altitude    550 km: orbital period     95.6 min, min one-way hop    3.7 ms, min RTT    7.3 ms
check: OK (GEO period 86164 s ~ one sidereal day 86164 s, so it hovers over one spot)
These are propagation FLOORS (straight up and down at the speed of light), real delay adds processing and queuing.
GEO: 3 satellites cover most of Earth but ~0.5 s RTT hurts TCP and voice. LEO: low latency, but each satellite
moves quickly across the sky, so many satellites are needed and ground stations hand off between them (like cells).
```

### SECTION 6: MOBILE IP (LINK TO MODULE 03)
Packets are dataclasses so you can see nesting. The home agent holds a binding from the home address to the care-of address. A packet addressed to the home address is wrapped in a new packet whose source is the home agent and destination is the CoA; the `proto` of the outer packet is "IP-in-IP". At the CoA the outer header is removed and the original packet is delivered. The `assert` shows the inner packet is unchanged, so the correspondent and the TCP connection never notice the move. Cost: 20 extra bytes per packet and the detour through the home agent.

```text
===== SECTION 6: MOBILE IP (LINK TO MODULE 03) =====
Mobile node's permanent home address 10.1.0.50; away on a foreign network with care-of address 172.16.9.77.
Registration: mobile -> home agent 10.1.0.1: 'binding 10.1.0.50 => 172.16.9.77' (RFC 5944 for IPv4)
1. Correspondent sends: IpPacket(src='203.0.113.5', dst='10.1.0.50', payload='GET /', proto='TCP')
2. Home agent intercepts (proxy ARP) and encapsulates: IpPacket(src='10.1.0.1', dst='172.16.9.77', payload=IpPacket(src='203.0.113.5', dst='10.1.0.50', payload='GET /', proto='TCP'), proto='IP-in-IP')
3. At the care-of address the tunnel end removes the outer header: IpPacket(src='203.0.113.5', dst='10.1.0.50', payload='GET /', proto='TCP')
check: OK (inner packet delivered unchanged; the correspondent never knew the mobile moved)
Reply path: mobile -> correspondent directly (triangle routing: in via home agent, out direct).
Overhead of IP-in-IP = one extra IPv4 header = 20 bytes per packet (RFC 2003).
```

## Worked Example
**Q.** An operator has 840 duplex channels and uses i = 2, j = 1. Find N, channels per cell, D/R and the approximate SIR (6 interferers, n = 4).

1. N = i^2 + ij + j^2 = 4 + 2 + 1 = 7
2. k = 840 / 7 = 120 channels per cell; reuse factor = 1/7
3. D/R = sqrt(3 x 7) = sqrt(21) = 4.583
4. SIR = (4.583)^4 / 6 = 441 / 6 = 73.5, or 10 log10(73.5) = 18.7 dB

The code prints exactly 120, 4.583 and 18.7 dB for N = 7.

## Key Rules / Gotchas Recap
- Valid hexagonal cluster sizes: i^2 + ij + j^2 (1, 3, 4, 7, 9, 12 ...). Not 5, 6, 8, 10.
- D/R = sqrt(3N). Smaller N = more channels per cell but worse interference.
- Hysteresis prevents ping-pong handoffs; hard = break-before-make, soft = make-before-break.
- HLR/HSS = home record; VLR/MME = visitor record.
- GEO delay floor about 239 ms one way ground-to-ground (477 ms RTT); LEO is far lower but needs many satellites.
- Mobile IP: home address stays fixed; care-of address changes; home agent tunnels (IP-in-IP).

## Why This Matters
Every phone, vehicle tracker and many IoT and edge-AI devices depend on cellular or satellite links, and their latency, handoff and NAT behaviour affect how you design retries and timeouts. The location-update and tunnel ideas reappear in cloud networking (overlays) and in VPNs.
