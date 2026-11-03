# `_9_CsmaFamily.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
CSMA (Carrier Sense Multiple Access) improves on ALOHA by listening before talking: a station senses the channel and transmits only if it seems idle. Collisions can still happen because of propagation delay, so CSMA is extended with collision detection (CSMA/CD, wired Ethernet) or collision avoidance (CSMA/CA, Wi-Fi).

**Persistence strategies (what to do when the channel is busy).**

| Method | Busy channel | Idle channel | Trade-off |
|---|---|---|---|
| 1-persistent | keep sensing | send with probability 1 | lowest delay; certain collision if two stations wait |
| Non-persistent | wait a random time, sense again | send immediately | fewer collisions; longer delay, wasted idle time |
| p-persistent (slotted) | wait until idle | send with probability p, else defer one slot | tunable; best p is about 1/n for n waiting stations |

**CSMA/CD.** The station listens while transmitting. If it detects a collision it stops, sends a short jam signal so everybody notices, and backs off. For the sender to hear the collision, it must still be transmitting when the signal returns: Tt >= 2*Tp, i.e. minimum frame size L_min = 2 * Tp * B, where Tp is the one-way propagation delay between the two farthest stations and B the bandwidth. Classic 10 Mbps Ethernet: slot time 51.2 microseconds, 512 bits = 64 bytes. Exam rearrangements: maximum distance d = (L/B)/2 * v for a given minimum frame; or the minimum frame for a given distance.

**Binary exponential backoff (BEB).** After the n-th collision on a frame, wait K slot times with K chosen uniformly from 0 .. 2^min(n,10) - 1 (slot time 51.2 microseconds in 10 Mbps Ethernet); after 16 failed attempts give up and report an error. The range doubles each time so contention among more stations resolves automatically.

**CSMA/CA.** Radios cannot detect collisions while sending (the transmitter overwhelms the receiver) and the hidden terminal problem exists, so Wi-Fi avoids collisions. Rules: wait for the channel to be idle for DIFS, pick a random backoff counter from a contention window (CW), count down only while the channel is idle, freeze while someone transmits, send, and the receiver replies with an ACK after the shorter SIFS (no ACK means assume collision and double CW). **RTS/CTS:** the sender sends a short Request To Send; the receiver answers Clear To Send. Stations hearing the CTS set their network allocation vector (NAV) and keep quiet for the announced time, solving the hidden terminal (A and C both reach B but cannot hear each other). Cost: extra overhead, so it is used for long frames.

| | CSMA/CD | CSMA/CA |
|---|---|---|
| Medium | wired, half-duplex Ethernet | wireless |
| Collisions | detected, then backoff | avoided with backoff, ACK, optional RTS/CTS |
| Min frame rule | 2*Tp*B | none; ACK confirms |

## Full Line-by-Line Breakdown

### SECTION 1: PERSISTENCE STRATEGIES
The first block prints the three strategies. Then a seeded experiment: n stations all wait for the channel to free. 1-persistent stations all start together, so exactly-one-sender never happens for n >= 2 (column 0.0). For p-persistent with p = 0.1 the probability that exactly one starts is n*p*(1-p)^(n-1); the simulation (seed 5) lands close to the formula.

Output from a real run:

```text
===== SECTION 1: PERSISTENCE STRATEGIES =====
method          channel busy                channel idle
1-persistent    keep listening              send with probability 1
non-persistent  wait random time, re-sense  send immediately
p-persistent    wait until idle             send with prob p, else next slot

Setup: n stations all have a frame ready while the channel is busy.
When it turns idle, what is P(exactly one station starts in that slot)?
  n  1-persistent  p=0.1 sim  p=0.1 formula
  2           0.0     0.1757         0.1800
  3           0.0     0.2399         0.2430
  5           0.0     0.3292         0.3281
 10           0.0     0.3846         0.3874
1-persistent: all n start together -> certain collision for n >= 2 (column 0.0).
p-persistent trades idle slots for fewer collisions; best p is about 1/n.
(sim column = seeded measurement with seed 5)
```

### SECTION 2: CSMA/CD MINIMUM FRAME SIZE
`min_frame_bits` computes 2*Tp*B. Four cases: the classic 10 Mbps Ethernet (Tp = 25.6 microseconds gives 512 bits = 64 bytes, asserted); 10 Mbps over 2500 m gives 250 bits; 100 Mbps over 200 m gives 200 bits; 1 Gbps over 200 m gives 2000 bits (250 bytes). The exam rearrangement finds the maximum distance for a 1000-bit minimum frame. The trap compares frame transmit time with 2*Tp: a 256-bit frame at 10 Mbps finishes sending before the collision signal can return, so the loss goes undetected.

Output from a real run:

```text
===== SECTION 2: CSMA/CD MINIMUM FRAME SIZE =====
Sender must still be transmitting when the collision signal returns:
   Tt >= 2 * Tp   =>   L_min = 2 * Tp * B
10 Mbps, Tp = 25.6 us        L_min =      512 bits =    64.0 bytes
10 Mbps, 2500 m (v = 2e8)    L_min =      250 bits =    31.2 bytes
100 Mbps, 200 m              L_min =      200 bits =    25.0 bytes
1 Gbps, 200 m                L_min =     2000 bits =   250.0 bytes
Classic 10 Mbps Ethernet: slot time 51.2 us x 10 Mbps = 512 bits = 64 bytes: check: OK
Exam: min frame = 1000 bits at 10 Mbps, v = 2e8 -> max distance:
   d = (L / B) / 2 * v = 10000 m

TRAP: frame shorter than 2*Tp -> collision NOT noticed
  L =  256 bits, Tt =  25.6 us, 2Tp = 51.2 us -> sender finished first: loss goes UNDETECTED
  L =  512 bits, Tt =  51.2 us, 2Tp = 51.2 us -> collision detected
  L = 1024 bits, Tt = 102.4 us, 2Tp = 51.2 us -> collision detected
```

### SECTION 3: BINARY EXPONENTIAL BACKOFF
The table lists K ranges for collisions 1, 2, 3, 4, 10 and 11 (the range stops growing at 10). A traced contention (seed 3) shows two stations picking equal K (0 and 0), colliding again, then picking 2 and 3 so A goes first. Over 20000 seeded runs the fraction needing at least two collisions is 0.493, close to the theoretical 0.5 (after the first collision they pick the same K with probability 1/2).

Output from a real run:

```text
===== SECTION 3: BINARY EXPONENTIAL BACKOFF =====
After the n-th collision wait K slots, K uniform in 0..2^min(n,10)-1; give up after 16 tries.
  collision  1: K in 0..1
  collision  2: K in 0..3
  collision  3: K in 0..7
  collision  4: K in 0..15
  collision 10: K in 0..1023
  collision 11: K in 0..1023
trace of one contention (seed 3):
  after collision 1: A waits 0, B waits 0 slots -> collide again
  after collision 2: A waits 2, B waits 3 slots -> A goes first
mean collisions before success over 20000 runs: 1.632 (seeded measurement)
theory: after collision n the two pick equal K with probability 1/2^n
fraction needing 2+ collisions: 0.493 (theory 0.5)
```

### SECTION 4: CSMA/CA (Wi-Fi style backoff)
A seeded contention-window demo: three stations choose backoff counters from CW = 15 (A=7, B=11, C=12). The counters count down together while the channel is idle; A reaches 0 first and transmits; B and C freeze at 4 and 5; and so on. Ties would collide and double CW.

Output from a real run:

```text
===== SECTION 4: CSMA/CA (Wi-Fi style backoff) =====
Wireless cannot listen while sending, so it AVOIDS collisions:
wait DIFS idle, count down a random backoff only while the channel is idle,
freeze the counter when someone else transmits, receiver replies ACK after SIFS.
initial backoff slots (CW=15, seed 8): {'A': 7, 'B': 11, 'C': 12}
  after 7 idle slots A transmits; others freeze at {'B': 4, 'C': 5}
  after 4 idle slots B transmits; others freeze at {'C': 1}
  after 1 idle slots C transmits; others freeze at {}
transmission order: ['A', 'B', 'C'] (ties would collide, then CW doubles)
```

### SECTION 5: HIDDEN TERMINAL AND RTS/CTS
Three stations on a line, radio range 120 m, positions 0, 100 and 200 m. A and C both hear B but not each other, so carrier sensing fails (both think the channel is idle) and their frames collide at B. B's CTS reaches A and C, so C sets its NAV and stays silent.

Output from a real run:

```text
===== SECTION 5: HIDDEN TERMINAL AND RTS/CTS =====
  A hears: ['B']
  B hears: ['A', 'C']
  C hears: ['B']
A and C both want to send to B. A cannot hear C: True
TRAP: carrier sensing says 'idle' at both, both send, frames collide AT B.
RTS/CTS fix: A sends RTS (short); B answers CTS which C DOES hear.
CTS from B reaches: ['A', 'C'] -> C sets its NAV (network allocation vector)
and stays silent for the duration, so A's data frame is safe.
Cost: RTS+CTS overhead, so used only above a frame-size threshold.
```

## Worked Example
**Problem.** A CSMA/CD network runs at 1 Gbps and its two farthest stations are 200 m apart (signal speed 2e8 m/s). Find the minimum frame size.

**Solution.** Tp = 200 / 2e8 = 1 microsecond. L_min = 2 * Tp * B = 2 * 1e-6 * 1e9 = 2000 bits = 250 bytes. (This is why half-duplex Gigabit Ethernet needed carrier extension to a longer slot.) The program prints `2000 bits = 250.0 bytes`.

## Key Rules / Gotchas Recap
- 1-persistent collides surely when two stations wait; non-persistent is polite but wastes time; p-persistent is tunable.
- CSMA/CD: L_min = 2 * Tp * B; shorter frames hide collisions from the sender.
- BEB: after the n-th collision pick K in 0..2^min(n,10)-1; give up after 16 attempts.
- The jam signal makes sure all stations notice the collision.
- CSMA/CA needs ACKs because collisions cannot be detected; the counter freezes while the channel is busy.
- RTS/CTS addresses the hidden terminal, at the cost of overhead.
- Measured collision statistics here come from fixed seeds.

## Why This Matters
Exponential backoff with jitter is the standard retry pattern in distributed systems and API clients, taken straight from Ethernet. Wi-Fi contention explains why a crowded access point slows everyone down.
