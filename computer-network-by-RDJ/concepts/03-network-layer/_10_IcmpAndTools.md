# `_10_IcmpAndTools.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
ICMP (Internet Control Message Protocol, RFC 792) is the network layer's error-reporting and diagnostic protocol: routers and hosts use it to tell a sender that a packet could not be delivered, that its TTL expired, or to answer a "are you there?" query. IP itself is best-effort and silent about failures, so ICMP is the feedback channel; `ping` and `traceroute` are built on it.

**Where it lives.** An ICMP message is carried inside an IP datagram (IP protocol number 1) but is considered part of the network layer, not a transport protocol; it has no ports.

**Message format.**

| Byte offset | Field | Size |
|---|---|---|
| 0 | Type | 1 byte |
| 1 | Code | 1 byte (sub-type) |
| 2 | Checksum | 2 bytes, Internet checksum over the whole ICMP message |
| 4 | Rest of header | 4 bytes; for echo: 2-byte identifier + 2-byte sequence number |
| 8 | Data | echo: arbitrary payload; errors: original IP header + first 8 bytes of the original data |

**Common types and codes.**

| Type | Code | Meaning |
|---|---|---|
| 8 / 0 | 0 | Echo Request / Echo Reply (ping) |
| 3 | 0 / 1 / 3 / 4 | Destination Unreachable: network / host / port / fragmentation needed with DF set |
| 11 | 0 / 1 | Time Exceeded: TTL expired in transit / fragment reassembly timeout |
| 5 | 0-3 | Redirect: a better first-hop router exists on the same network |
| 12 | 0 | Parameter Problem |

(Source Quench, type 4, was an old congestion hint and is deprecated.)

**Rules.** No ICMP error is generated about an ICMP error message, about multicast/broadcast destinations, or for non-first fragments; this prevents error storms. ICMP does not make IP reliable; it only reports.

**ping.** Sends Echo Requests with an identifier and sequence number; the target returns an Echo Reply with the same identifier, sequence and data. The sender measures round-trip time (RTT) and counts losses. Real ping needs a raw socket or special privilege, so this lesson only builds and parses the messages and simulates the path.

**traceroute.** Sends probes with TTL = 1, 2, 3, ... Each router that decrements the TTL to 0 drops the probe and sends back ICMP Time Exceeded, revealing its address and giving a per-hop RTT. When the probe finally reaches the destination, the destination answers (Port Unreachable for UDP probes aimed at a closed port, Echo Reply for ICMP probes), ending the trace. Limitations: routers may rate-limit or filter ICMP (shown as `* * *`), and different probes can take different paths.

**Checksum.** 16-bit one's complement of the one's complement sum of all 16-bit words of the message (checksum field zero while computing). If the length is odd, a zero byte is appended for the calculation only.

Typical exam questions: "Which ICMP message does traceroute rely on?", "Give the format of an ICMP message", "What does Destination Unreachable (type 3) code 4 mean?", "How does ping work?".

## Full Line-by-Line Breakdown

### SECTION 1: ICMP TYPES AND CODES
A lookup table of the commonly examined (type, code) pairs, printed sorted. The footnote says ICMP is carried in IP protocol 1 and that errors are never reported about ICMP errors.

Output from a real run:

```text
===== SECTION 1: ICMP TYPES AND CODES =====
type code  meaning
   0    0  Echo Reply (ping answer)
   3    0  Destination Unreachable: network unreachable
   3    1  Destination Unreachable: host unreachable
   3    3  Destination Unreachable: port unreachable
   3    4  Destination Unreachable: fragmentation needed and DF set
   5    1  Redirect: for the host (use a better first hop)
   8    0  Echo Request (ping)
  11    0  Time Exceeded: TTL expired in transit
  11    1  Time Exceeded: fragment reassembly time exceeded
  12    0  Parameter Problem: pointer indicates the error
ICMP rides inside IP (protocol number 1). It REPORTS problems and answers queries;
it does not make IP reliable, and no ICMP error is sent about an ICMP error.
```

### SECTION 2: PACK / UNPACK WITH CHECKSUM
`pack_icmp` builds `!BBHI` (type, code, checksum, rest of header), computes the checksum over header+payload with the checksum field zero, and writes it in. `unpack_icmp` returns the fields and a `valid` flag that is true when checksumming the whole message gives 0. The echo request starts `08 00` (type 8, code 0), then the checksum, identifier `12 34`, sequence `00 01`, then the data `abcdefgh`. Corrupting a data byte makes verification fail; an odd-length payload still verifies because the pad byte is only used in the sum. The reply has type 0, so its checksum differs from the request's.

Output from a real run:

```text
===== SECTION 2: PACK / UNPACK WITH CHECKSUM =====
echo request bytes: 08 00 54 35 12 34 00 01 61 62 63 64 65 66 67 68
type=8 code=0 checksum=0x5435 id=0x1234 seq=1 data=b'abcdefgh' valid=True
check: OK
after corrupting one data byte: valid = False (receiver silently discards)
odd-length payload (3 bytes) still verifies: True (zero pad is used only in the sum)
echo reply : type 0 same id/seq/data, checksum 0x5c35 (differs because type changed)
Error messages (types 3, 5, 11, 12) carry the offending IP header + first 8 bytes of its data,
so the sender can tell which packet/port caused it.
```

### SECTION 3: IN-MEMORY ROUTER CHAIN
Defines the simulated path: 4 routers plus the target, each link with a fixed base delay. `send(ttl, rng)` walks the chain: each router decrements TTL; if it reaches 0 the router answers Time Exceeded; at the last hop the target replies (Echo Reply for ping, Port Unreachable for UDP traceroute). Time is base delay plus a small seeded jitter, doubled for the round trip. These numbers are simulation outputs, not real measurements, and nothing here touches the network.

Output from a real run:

```text
===== SECTION 3: IN-MEMORY ROUTER CHAIN =====
simulated path: gw(192.168.1.1) -> isp1(10.20.0.1) -> core(10.30.0.1) -> edge(10.40.0.1) -> target(198.51.100.7)
Delays below are SIMULATED numbers from a seeded RNG, not measurements of anything real.
```

### SECTION 4: PING SIMULATION (RTT TABLE)
Five echo requests are packed, verified and "sent". The table shows the reply source, TTL (64 minus the 4 router decrements = 60 on the way back) and simulated RTT, followed by the min/avg/max summary line like real ping.

Output from a real run:

```text
===== SECTION 4: PING SIMULATION (RTT TABLE) =====
PING 198.51.100.7 (simulated), 8 data bytes
  seq=1 reply from 198.51.100.7: Echo Reply, ttl=60, time=63.0 ms (simulated)
  seq=2 reply from 198.51.100.7: Echo Reply, ttl=60, time=62.6 ms (simulated)
  seq=3 reply from 198.51.100.7: Echo Reply, ttl=60, time=63.3 ms (simulated)
  seq=4 reply from 198.51.100.7: Echo Reply, ttl=60, time=63.5 ms (simulated)
  seq=5 reply from 198.51.100.7: Echo Reply, ttl=60, time=62.5 ms (simulated)
summary: 5 sent, 5 received, 0% loss, rtt min/avg/max = 62.5/63.0/63.5 ms (simulated)
Reply TTL = 64 - 4 routers' decrements = 60: the TTL in a reply hints at the hop count.
check: OK
```

### SECTION 5: TRACEROUTE SIMULATION (TTL = 1, 2, 3 ...)
For TTL 1 to 5, three probes each. Hops 1 to 4 answer Time Exceeded from their own address; at TTL 5 the target answers Port Unreachable and the loop stops. RTTs grow with hop distance. The assertion checks the destination appears at TTL equal to the number of devices on the path. The trap line shows a probe with TTL 2 being killed by the second router.

Output from a real run:

```text
===== SECTION 5: TRACEROUTE SIMULATION (TTL = 1, 2, 3 ...) =====
traceroute to 198.51.100.7 (simulated), max 10 hops, 3 probes each
  1  192.168.1.1     2.0 ms  1.8 ms  2.4 ms   <- Time Exceeded
  2  10.20.0.1       12.3 ms  12.1 ms  12.3 ms   <- Time Exceeded
  3  10.30.0.1       36.3 ms  37.3 ms  37.8 ms   <- Time Exceeded
  4  10.40.0.1       54.0 ms  53.3 ms  53.9 ms   <- Time Exceeded
  5  198.51.100.7    61.6 ms  62.3 ms  62.6 ms   <- Port Unreachable
check: OK (destination reached at TTL 5 = number of devices on the path)
How it works: probe with TTL 1 dies at router 1, which returns ICMP Time Exceeded (11,0)
revealing its address; TTL 2 dies at router 2; ... until the destination answers
(Port Unreachable for UDP probes to a closed high port, or Echo Reply for ICMP probes).
Caveat: many routers rate-limit or drop ICMP, giving '* * *' lines; paths may also change between probes.
TRAP: a router that decrements TTL to 0 must drop the packet, never forward it:
  probe with TTL 2 -> Time Exceeded from 10.20.0.1
```

## Worked Example
**Q:** Why does traceroute to a host 5 hops away print five lines, and what ICMP messages does it see?

1. Probe 1 has TTL 1. Router 1 decrements it to 0, drops the packet and returns ICMP Time Exceeded (type 11, code 0) from its own IP. Line 1 is that router.
2. Probe 2 has TTL 2: router 1 forwards (TTL 1), router 2 decrements to 0 and returns Time Exceeded. Line 2.
3. Same for TTL 3 and 4.
4. Probe 5 reaches the destination with TTL left; a UDP probe to an unused port produces ICMP Destination Unreachable, code 3 (port unreachable). Receiving it tells traceroute it has arrived: line 5.

The simulation prints precisely four Time Exceeded lines followed by one Port Unreachable line.

## Key Rules / Gotchas Recap
- ICMP is carried in IP (protocol 1), has no ports, and reports; it does not repair.
- Echo Request is type 8, Echo Reply is type 0; Time Exceeded is 11; Destination Unreachable is 3.
- Checksum covers the whole ICMP message (header and data); odd length is padded in the sum only.
- Error messages quote the original IP header + 8 bytes of data.
- Traceroute relies on TTL expiry (type 11) from routers and a different reply from the destination.
- Silence (`* * *`) does not prove a hop is down; many devices filter or rate-limit ICMP.
- Simulated RTTs here are made-up, seeded numbers, never evidence about a real network.

## Why This Matters
ICMP is the first tool when debugging connectivity and Path MTU problems (blocking all ICMP breaks Path MTU Discovery), and security teams monitor it for reconnaissance and tunnelling. Being able to craft and parse these bytes yourself is what makes writing network tools and reading packet captures possible.
