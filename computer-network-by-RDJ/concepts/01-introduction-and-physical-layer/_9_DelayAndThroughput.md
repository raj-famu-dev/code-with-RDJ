# `_9_DelayAndThroughput.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Network performance is described mainly by delay (how long a bit or packet takes), throughput (how many bits per second actually arrive) and the relationship between them. Delay on one hop is the sum of processing, queuing, transmission and propagation delay; the bandwidth-delay product tells you how much data must be in flight to fill a link.

**The four delays.**
- *Processing delay:* examining the header, checking errors, choosing the output link; microseconds or less.
- *Queuing delay:* waiting in the output buffer; zero on an idle link and growing without bound as load approaches capacity.
- *Transmission delay* `= L / R`: time to push all L bits of a packet onto a link of rate R bps. Depends on packet size and *bandwidth*.
- *Propagation delay* `= d / s`: time for a signal to cross distance d at speed s (about 2 x 10^8 m/s in copper or fibre, up to 3 x 10^8 m/s in free space). Depends on distance, not on rate.

Total nodal delay `= d_proc + d_queue + d_trans + d_prop`.

**RTT** (round-trip time) is the time for a packet to reach the destination and its reply to return; with negligible transmission and queuing it is `2 x d_prop`. Tools such as `ping` measure it.

**Bandwidth-delay product (BDP)** `= bandwidth x RTT` (bits). It is the volume of data "in the pipe" at once. For full utilisation the sender window must be at least BDP. A "long fat network" (high bandwidth and high RTT) has a large BDP.

**Throughput vs bandwidth.** Bandwidth (link rate) is the capacity; throughput is the achieved rate, always at most the slowest link on the path (the bottleneck), further reduced by protocol overhead, losses, window limits and competing traffic. *Goodput* counts only useful application bytes.

**Utilisation.** Fraction of time a resource is busy. For stop-and-wait: `U = t_frame / (t_frame + RTT)` (ignoring ACK size); a sliding window of N frames gives `U = min(1, N x t_frame / (t_frame + RTT))`, so the window needed to fill the link is about `1 + RTT / t_frame`.

**Queuing theory (M/M/1 model).** With traffic intensity `rho = (arrival rate x average packet size) / link rate`, the mean time waiting in the queue is `rho / (1 - rho) x service_time`. It is a model (Poisson arrivals, exponential service) but captures the key lesson: delay climbs sharply as rho approaches 1.

**Jitter** is the variation of delay between packets, for example the mean absolute difference between consecutive delays, or the standard deviation. Real-time voice and video need low jitter; receivers use a playout buffer.

**Typical exam questions.** Compute transmission and propagation delay for a given packet, rate and distance; total delay over several hops; RTT; BDP and required window; link utilisation of stop-and-wait; throughput over several links.

## Full Line-by-Line Breakdown

### SECTION 1: THE FOUR DELAYS ON ONE HOP
`d_trans` and `d_prop` implement the two formulas. A 1500-byte packet (12,000 bits) on a 100 Mbps link needs 120 microseconds to transmit, while the signal needs 10 milliseconds to cross 2000 km at 2 x 10^8 m/s, so propagation dominates by a factor of about 80. Processing (20 microseconds) and queuing (150 microseconds) are assumed inputs, labelled as such, not measurements. The trap shows doubling the data rate only affects transmission, and doubling the distance only propagation.

```text
===== SECTION 1: THE FOUR DELAYS ON ONE HOP =====
packet = 12,000 bits, link = 100 Mbps, distance = 2,000 km, signal speed = 2.0e+08 m/s
  processing   (assumed) =      20.0 us
  queuing      (assumed) =     150.0 us
  transmission = L/R     =     120.0 us
  propagation  = d/s     =   10000.0 us
  total nodal + link delay = 10.2900 ms
Trap: doubling the data rate to 200 Mbps changes transmission to 60 us but propagation stays 10000 us.
      A longer cable changes propagation, not transmission: 4000 km -> 20 ms.
Also: 100 Mbps means 100,000,000 bits per second (decimal), and 1500 BYTES = 12,000 BITS.
```

### SECTION 2: RTT AND BANDWIDTH-DELAY PRODUCT
RTT = 2 x 10 ms = 20 ms. BDP at 100 Mbps is 2,000,000 bits (0.25 MB) and at 1 Gbps ten times more (2.5 MB). A geostationary satellite sits about 35,786 km above the equator, so ground to satellite to ground is about 71,572 km, roughly 239 ms one way at 3 x 10^8 m/s: physics alone gives a round trip near half a second.

```text
===== SECTION 2: RTT AND BANDWIDTH-DELAY PRODUCT =====
RTT (propagation only) = 2 x 10 ms = 20 ms
BDP at 100 Mbps = 100,000,000 bps x 0.020 s = 2,000,000 bits = 0.25 MB (bits 'in flight')
BDP at 1 Gbps   = 1,000,000,000 bps x 0.020 s = 20,000,000 bits = 2.50 MB (bits 'in flight')
BDP = the data needed in flight to keep the pipe full; a sender window smaller than the BDP leaves the link idle.
Geostationary satellite hop (ground -> satellite -> ground, straight overhead, c = 3e8 m/s): 239 ms one way, RTT about 477 ms (physics only; real links add more).
```

### SECTION 3: THROUGHPUT VS BANDWIDTH AND UTILISATION
The path has links of 100 Mbps, 10 Gbps and 20 Mbps, so throughput cannot exceed 20 Mbps, the bottleneck. The stop-and-wait example shows how awful a 100 Mbps link is when each 12,000-bit frame must wait a 10 ms round trip for its acknowledgement: 120 microseconds of sending per 10.12 ms cycle, 1.19% utilisation, 1.19 Mbps. The window that would fill the link is about 84 frames.

```text
===== SECTION 3: THROUGHPUT VS BANDWIDTH AND UTILISATION =====
Path link rates (bps): {'access link': '100 Mbps', 'ISP core': '10000 Mbps', 'server link': '20 Mbps'}
End-to-end throughput <= bottleneck = server link = 20 Mbps (bandwidth is capacity, throughput is what you actually get)
Stop-and-wait: frame time = 120 us, RTT = 10 ms -> utilisation = 120 / 10120 = 1.19%
Effective throughput = 1.19 Mbps on a 100 Mbps link!
A sliding window of about 84 frames would keep the link full (window ~ 1 + RTT/frame_time).
check: OK
```

### SECTION 4: QUEUING DELAY (SIMULATION vs M/M/1)
`simulate()` runs a single FIFO link with seeded random Poisson arrivals and exponential service times: each packet starts when it arrives or when the server frees up, whichever is later, and its wait is the difference. 200,000 packets are simulated per load level and compared with `mm1_wait()`. At rho = 0.1 the wait is about 13 microseconds; at 0.9 it is about 1.08 ms, 80 times larger. The simulated and formula values agree to within a few percent, and the code asserts within 15%.

```text
===== SECTION 4: QUEUING DELAY (SIMULATION vs M/M/1) =====
mean service time = 120 us; queuing delay vs traffic intensity rho (load / capacity):
  rho  formula (us)  simulated (us)
  0.1          13.3            13.3
  0.5         120.0           119.1
  0.8         480.0           485.5
  0.9        1080.0          1077.9
Queuing delay explodes as rho -> 1; if rho > 1 the queue grows without bound and packets are dropped.
Rule of thumb for design: keep utilisation well below 1.
check: OK (simulated average within 15% of the formula)
```

### SECTION 5: JITTER
Twelve seeded one-way delays are generated as 20 ms plus random queuing. Mean, standard deviation and the mean absolute difference between consecutive packets are printed. A steady link of 30 ms has a higher mean than this sample but zero jitter, which is the point of the trap: average delay and jitter are different quantities.

```text
===== SECTION 5: JITTER =====
one-way delays (ms): [21.1, 23.1, 21.8, 23.7, 23.9, 20.3, 20.1, 27.3, 21.2, 21.1, 41.7, 22.5]
mean delay = 24.0 ms, standard deviation = 5.7 ms
jitter (mean absolute difference between consecutive packets) = 5.7 ms
Jitter = variation in delay. Voice/video need low jitter: a playout (de-jitter) buffer trades a little extra fixed delay for smoothness.
Trap: low AVERAGE delay does not mean low jitter; two links can have the same mean and very different jitter.
steady link: mean 30.0 ms, jitter 0.0 ms
```

### SECTION 6: WORKED EXAMPLE
Two exam-style calculations; solved by hand below.

```text
===== SECTION 6: WORKED EXAMPLE =====
per link: 24,000/10,000,000 = 2.4 ms transmission + 2.5 ms propagation = 4.9 ms
two store-and-forward links: 2 x 4.9 = 9.8 ms
(b) 1 Gbps, RTT 100 ms: BDP = 12,500,000 bytes (12.5 MB); a 65,536-byte window gives 5.24 Mbps = 0.52% of the link
check: OK
```

## Worked Example
**Problem (a).** A 3000-byte packet is sent over two store-and-forward links in series, each 10 Mbps and 500 km long (signal speed 2 x 10^8 m/s). Ignore queuing and processing. Find the total delay.

1. L = 3000 x 8 = 24,000 bits. Transmission per link = 24,000 / 10^7 = 2.4 ms.
2. Propagation per link = 500,000 / (2 x 10^8) = 2.5 ms.
3. Per link = 4.9 ms. Store-and-forward repeats this on each link: 2 x 4.9 = 9.8 ms.

**Problem (b).** A 1 Gbps path has a 100 ms RTT. What is the BDP, and what throughput does a 64 KB (65,536-byte) window give?

1. BDP = 10^9 x 0.1 = 10^8 bits = 12,500,000 bytes = 12.5 MB.
2. Throughput = window / RTT = 65,536 x 8 / 0.1 = 5.24 Mbps, which is 0.52% of the link.

The code prints 9.8 ms, 12.5 MB and 5.24 Mbps.

## Key Rules / Gotchas Recap
- Transmission delay depends on size and rate; propagation delay depends on distance and speed. Raising bandwidth never reduces propagation delay.
- Convert bytes to bits (x 8) and use decimal prefixes for rates (1 Mbps = 10^6 bps).
- Store-and-forward repeats transmission delay on every hop.
- RTT = 2 x propagation (plus processing, queuing, transmission of the reply).
- Window < BDP means an under-used link; window-limited throughput = window / RTT.
- Throughput is limited by the slowest link on the path.
- Queuing delay is non-linear: it explodes as utilisation nears 100%.
- Low mean delay does not imply low jitter.

## Why This Matters
These formulas explain why a fast link feels slow (high RTT, small windows), why model-serving latency has a floor set by distance, and how to size buffers and TCP windows. Queuing behaviour is why tail latency spikes under load.
