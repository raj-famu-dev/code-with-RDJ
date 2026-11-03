# `_3_SwitchingTechniques.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Switching is how a network moves data from a source to a destination through intermediate nodes instead of wiring every pair of hosts together. There are three classic techniques: circuit switching (reserve a path first), message switching (store and forward whole messages) and packet switching (store and forward small packets). The Internet uses packet switching.

**Circuit switching.** Three phases: (1) circuit establishment (signalling reserves a dedicated path or channel on every link), (2) data transfer over the reserved path with no waiting at switches, (3) circuit teardown. Resources are dedicated for the whole call, even during silence, so utilisation is low for bursty data. Delay: `set-up + L/R + total propagation`. Used in the telephone network. Implemented with space-division switches (crossbars) or time-division switches.

**Message switching.** No path is reserved. A whole message is passed from node to node, stored fully at each node, then forwarded (store-and-forward). It needs big buffers (often disk), gives long delays and cannot support interactive traffic well, but allows speed/format conversion and avoids set-up. Delay over k links of rate R: `k*(L/R) + k*propagation` (ignoring queuing).

**Packet switching.** The message is cut into packets (header + payload). Each switch stores a packet, then forwards it; because packets are small, the second packet can start crossing link 1 while the first crosses link 2 (pipelining). With P packets, k links, packet time `t = (payload+header)/R`: delay = `(k + P - 1) * t + k * propagation`. Packet size is a trade-off: very small packets waste bits in headers, very large ones lose pipelining. Statistical multiplexing lets many users share links, which is why packet switching suits bursty traffic; the price is queuing delay and possible loss when queues overflow.

Two packet-switching modes:

| Point | Datagram network | Virtual-circuit network |
|-------|------------------|-------------------------|
| Set-up | none | yes, a virtual path is set up first |
| Header carries | full destination address | short VC identifier (VCI) |
| Routing decision | per packet, from a forwarding table | once at set-up; later by VCI table lookup |
| Order | packets may arrive out of order | arrive in order on the same path |
| Failure | packets simply take another route | circuit must be re-established |
| State in switches | none per connection | per-connection table entry |
| Examples | IP | X.25, Frame Relay, ATM, MPLS-style labels |

A virtual circuit is "virtual" because it is a logical path over shared links; no bandwidth is dedicated, unlike a real circuit.

**Comparison summary.**

| | Circuit | Message | Packet |
|---|---------|---------|--------|
| Set-up | needed | not needed | not needed (datagram) / needed (VC) |
| Dedicated path | yes | no | no |
| Unit forwarded | continuous stream | whole message | packet |
| Efficiency for bursty data | poor | medium | high |
| Delay variation | none after set-up | high | varies with queues |

**Typical exam questions.** Compute total delay for a message across k hops under each technique; compare datagram with virtual circuit; explain why packets can arrive out of order.

## Full Line-by-Line Breakdown

### SECTION 1: THE WORKED SCENARIO
Defines the numbers used everywhere: an 800,000-bit message, 1 Mbps on every link, 4 links (source, three switches, destination), 2 ms propagation per link, packets of 8,000 payload bits plus a 400-bit header, and an assumed 50 ms circuit set-up. The set-up time is an assumption chosen for this exercise; real set-up times differ.

```text
===== SECTION 1: THE WORKED SCENARIO =====
message = 800,000 bits, link rate = 1,000,000 bps, links = 4 (3 switches)
propagation per link = 2 ms; packet = 8,000 payload + 400 header bits
circuit set-up (assumed) = 50 ms
```

### SECTION 2: DELAY OF EACH TECHNIQUE
Three small functions implement the formulas. Circuit: the stream crosses the reserved path as one pipe so only one `L/R` appears. Message: the full 0.8 s transmission is repeated on all 4 links (3.208 s). Packet: 100 packets; the last packet leaves the source after 99 packet-times and then needs 4 packet-times to cross the links, hence `(4+100-1) x 0.0084`. The trap shows what happens if you forget the 400-bit headers: you under-estimate by about 41 ms. The `assert` pins the ordering and the exact values.

```text
===== SECTION 2: DELAY OF EACH TECHNIQUE =====
circuit : 0.050 + 0.800 + 0.008 = 0.858 s
message : 4 x 0.800 + 0.008 = 3.208 s
packet  : P=100 packets, (4+100-1) x 0.0084 + 0.008 = 0.873 s
Ranking (fastest first): [('circuit', 0.858), ('packet', 0.873), ('message', 3.208)]
Packet switching beats message switching because packets pipeline across links;
circuit switching is slightly faster HERE (only because the assumed set-up is a small 50 ms), but it
reserves the line even when idle and its set-up cost does not shrink for short messages.
check: OK
Trap: forgetting headers gives 0.832 s, but the real packet delay is 0.873 s (4.8% overhead bits).
```

### SECTION 3: PACKET SIZE TRADE-OFF
Re-evaluates the packet formula for payloads from 400 to 800,000 bits. The delay falls as pipelining improves, bottoms out near 8,000-bit payloads in this table, and rises again as packets get large. The last row, one 800,000-bit packet, behaves like message switching (plus one header).

```text
===== SECTION 3: PACKET SIZE TRADE-OFF =====
 payload bits  packets  delay (s)
          400    2,000      1.610
        1,000      800      1.132
        4,000      200      0.901
        8,000      100      0.873
       40,000       20      0.937
      200,000        4      1.411
      800,000        1      3.210
Tiny packets: header overhead dominates. Huge packets: no pipelining (a single 800,000-bit packet = message switching).
Best delay in this table: 0.873 s
```

### SECTION 4: DATAGRAM vs VIRTUAL CIRCUIT
Two paths exist, 20 ms and 35 ms. The datagram sender picks a path per packet using a seeded random generator, so packets overtake each other and the arrival order is scrambled (sequence 2 arrives before 1). The virtual-circuit sender fixes one path, so order is kept. The last line shows a VC table entry: a switch receiving VCI 5 on port1 sends it out of port3 relabelled with VCI 9 (VCIs have only local meaning on each link).

```text
===== SECTION 4: DATAGRAM vs VIRTUAL CIRCUIT =====
datagram         paths=['u', 'l', 'u', 'l', 'l', 'l', 'u', 'l'] arrival order=[0, 2, 1, 6, 3, 4, 5, 7] in order=False
virtual circuit  paths=['u', 'u', 'u', 'u', 'u', 'u', 'u', 'u'] arrival order=[0, 1, 2, 3, 4, 5, 6, 7] in order=True
Datagram: no set-up, per-packet routing, packets may arrive out of order (TCP/IP fixes this above IP).
Virtual circuit: set-up phase, a short VC identifier in each header, in order, state kept in every switch.
VC switch table maps (in-port, in-VCI) -> (out-port, out-VCI): {('port1', 5): ('port3', 9)}
```

### SECTION 5: COMPARISON AND WORKED EXAMPLE
Prints the comparison table and the answers used in the worked example.

```text
===== SECTION 5: COMPARISON AND WORKED EXAMPLE =====
                        circuit             message                   packet
set-up                  yes (before data)   no                        no
resources               dedicated           per hop, on demand        shared, on demand
store-and-forward unit  none                entire message            small packet
delay problem           set-up delay        big buffers, long delay   queuing, reorder, loss
typical use             old telephone       telegram, e-mail relays   Internet
Worked example answer: message switching over 4 links = 3.208 s; packet switching = 0.873 s
check: OK
```

## Worked Example
**Problem.** A message of 800,000 bits crosses 4 links, each 1 Mbps with 2 ms propagation. Find the delay with message switching and with packet switching using 8,000-bit payloads plus 400-bit headers.

1. Message switching: transmission per link = 800,000 / 1,000,000 = 0.8 s. Four links: 3.2 s. Propagation: 4 x 2 ms = 8 ms. Total = 3.208 s.
2. Packet switching: P = 800,000 / 8,000 = 100 packets. Packet time = 8,400 / 1,000,000 = 8.4 ms.
3. Total packet-times = k + P - 1 = 4 + 100 - 1 = 103. 103 x 8.4 ms = 865.2 ms.
4. Add propagation 8 ms: 0.8732 s.

Packet switching is about 3.7 times faster than message switching here (3.208 / 0.8732). The code confirms both numbers.

## Key Rules / Gotchas Recap
- Packet delay = (k + P - 1) x packet time + propagation; do not multiply P by k.
- Message switching repeats the whole transmission time on every link.
- Include header bits in the packet time; leaving them out under-estimates delay.
- Packet size is a trade-off: too small wastes header bits, too big loses pipelining.
- Datagram: no set-up, may reorder. Virtual circuit: set-up, fixed path, in order, VCI swapped hop by hop.
- A virtual circuit does not reserve bandwidth; a physical circuit does.
- Circuit-switching delay depends on the assumed set-up time; state your assumption.

## Why This Matters
Every packet you see in a debugger or capture is the result of these choices. Understanding per-packet overhead and reordering explains throughput numbers, why TCP needs sequence numbers, and why MPLS-style label switching exists.
