# `_5_StopAndWait.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Stop-and-Wait is the simplest ARQ (Automatic Repeat reQuest) protocol: the sender transmits one frame, starts a timer and waits for an acknowledgement (ACK) before sending the next. If the timer expires first, it retransmits. It provides both flow control (the receiver is never flooded) and error control (lost or damaged frames are repeated), at the price of poor efficiency on long or fast links.

**Why it needs a timer and sequence numbers.** Three things can go wrong. (1) The data frame is lost or corrupted: no ACK comes back, the sender times out and resends; harmless. (2) The ACK is lost: the sender times out and resends a frame the receiver already has; without sequence numbers the receiver would accept it as new data (a duplicate). (3) The timeout is too short (premature timeout): the sender resends while the original ACK is still in flight, causing duplicates and stale ACKs. A sequence number in each frame lets the receiver discard duplicates; a one-bit number (0 and 1, alternating) is enough in Stop-and-Wait because only one frame is outstanding. The ACK carries the number of the frame it confirms (or the next expected frame) so the sender can ignore stale ACKs.

**Timeout rule.** The timeout must exceed the round-trip time: RTT = Tt + 2*Tp (plus receiver processing time and the ACK transmission time, which is usually ignored in exam questions).

**Efficiency (utilisation).** In each cycle the sender is busy for Tt (transmit time = L/B) but the cycle lasts Tt + 2*Tp.
U = Tt / (Tt + 2Tp) = 1 / (1 + 2a), where a = Tp / Tt.
Throughput = U * B. Efficiency falls as a grows: on a long fat link the sender mostly waits. Window size 1 is the reason; sliding window protocols (next two files) fix it.

With frame loss probability p each way, a transmission cycle succeeds only if the frame and its ACK both arrive, so the average number of transmissions per frame is about 1/(1-p)^2 when losses are independent and ACKs also suffer the same loss rate.

| Event | What the sender sees | What happens |
|---|---|---|
| Data frame lost | no ACK, timer expires | retransmit; receiver gets it once |
| ACK lost | no ACK, timer expires | retransmit; receiver discards duplicate by sequence number, re-ACKs |
| Timeout too short | ACK arrives after the retransmission | duplicate sent; stale ACK ignored thanks to sequence numbers |

Advantages: trivial, little buffer. Disadvantages: low efficiency when a is large, only one frame in flight.

## Full Line-by-Line Breakdown

### SECTION 1: SIMULATOR DESIGN
The simulator is event driven with a priority queue (`heapq`). Events are DATA arriving at the receiver, ACK arriving at the sender, and a TIMEOUT. The sender state is the current frame id and sequence bit; the receiver state is the expected sequence bit. Losses are scripted by transmission number (for example, drop the 1st data transmission) or random with a seeded generator. Timers carry a generation number so that a stale timer for an already acknowledged frame is ignored.

Output from a real run:

```text
===== SECTION 1: SIMULATOR DESIGN =====
Times in ms. Tt = frame transmit time, Tp = one-way propagation delay.
Events: DATA arrives, ACK arrives, TIMEOUT fires. ACK transmit time ignored.
```

### SECTION 2: NO LOSS BASELINE
Baseline with no loss: Tt = 1, Tp = 4, so a frame sent at 0 arrives at 5, the ACK arrives at 9 and the next frame leaves at 9. Each frame takes a full RTT of 9 ms.

Output from a real run:

```text
===== SECTION 2: NO LOSS BASELINE =====
  t=   0.00  SEND  frame#0 seq=0 (tx 1)
  t=   5.00  RECV  frame#0 delivered to network layer
  t=   5.00  ACK   sent for seq=0
  t=   9.00  ACK   arrives, sender moves on
  t=   9.00  SEND  frame#1 seq=1 (tx 2)
  t=  14.00  RECV  frame#1 delivered to network layer
  t=  14.00  ACK   sent for seq=1
  t=  18.00  ACK   arrives, sender moves on
  t=  18.00  SEND  frame#2 seq=0 (tx 3)
  t=  23.00  RECV  frame#2 delivered to network layer
  t=  23.00  ACK   sent for seq=0
  t=  27.00  ACK   arrives, sender moves on
delivered: [0, 1, 2] | data transmissions: 3 | finish: 27.0
```

### SECTION 3: LOST FRAME
The first transmission of frame 0 is lost. Nothing arrives, the timer fires at t = 12 and the frame is resent; it is delivered at t = 17. Three transmissions are used for two frames.

Output from a real run:

```text
===== SECTION 3: LOST FRAME =====
  t=   0.00  SEND  frame#0 seq=0 (tx 1)  -- LOST in channel
  t=  12.00  TIMEOUT -> retransmit
  t=  12.00  SEND  frame#0 seq=0 (tx 2)
  t=  17.00  RECV  frame#0 delivered to network layer
  t=  17.00  ACK   sent for seq=0
  t=  21.00  ACK   arrives, sender moves on
  t=  21.00  SEND  frame#1 seq=1 (tx 3)
  t=  26.00  RECV  frame#1 delivered to network layer
  t=  26.00  ACK   sent for seq=1
  t=  30.00  ACK   arrives, sender moves on
delivered: [0, 1] | transmissions: 3
```

### SECTION 3b: LOST ACK (the dangerous one)
The ACK is lost (the dangerous case). The receiver already delivered frame 0 at t = 5. After the timeout the sender resends it; the receiver sees sequence 0 again while it expects 1, so it discards the duplicate and re-sends the ACK. The trap run repeats the same loss without sequence numbers: frame 0 is delivered twice.

Output from a real run:

```text
===== SECTION 3b: LOST ACK (the dangerous one) =====
  t=   0.00  SEND  frame#0 seq=0 (tx 1)
  t=   5.00  RECV  frame#0 delivered to network layer
  t=   5.00  ACK   sent for seq=0  -- LOST in channel
  t=  12.00  TIMEOUT -> retransmit
  t=  12.00  SEND  frame#0 seq=0 (tx 2)
  t=  17.00  RECV  frame#0 seq=0 DUPLICATE discarded, re-ACK
  t=  17.00  ACK   sent for seq=0
  t=  21.00  ACK   arrives, sender moves on
  t=  21.00  SEND  frame#1 seq=1 (tx 3)
  t=  26.00  RECV  frame#1 delivered to network layer
  t=  26.00  ACK   sent for seq=1
  t=  30.00  ACK   arrives, sender moves on
delivered: [0, 1] | transmissions: 3
The receiver got frame#0 twice, but seq numbers let it discard the copy.
TRAP same run WITHOUT sequence numbers -> delivered: [0, 0, 1] (frame#0 delivered twice = duplicate data)
```

### SECTION 4: PREMATURE TIMEOUT
Timeout 6 is shorter than the RTT 9. The sender resends frame 0 at t = 6; the original ACK then arrives at t = 9 and moves the sender on; the duplicate is discarded by the receiver; its ACK arrives later and is ignored as stale. Output shows 4 transmissions for 2 frames: correct delivery but wasted bandwidth.

Output from a real run:

```text
===== SECTION 4: PREMATURE TIMEOUT =====
RTT = Tt + 2*Tp = 9. Timeout 6 < RTT fires before the ACK can arrive.
  t=   0.00  SEND  frame#0 seq=0 (tx 1)
  t=   5.00  RECV  frame#0 delivered to network layer
  t=   5.00  ACK   sent for seq=0
  t=   6.00  TIMEOUT -> retransmit
  t=   6.00  SEND  frame#0 seq=0 (tx 2)
  t=   9.00  ACK   arrives, sender moves on
  t=   9.00  SEND  frame#1 seq=1 (tx 3)
  t=  11.00  RECV  frame#0 seq=0 DUPLICATE discarded, re-ACK
  t=  11.00  ACK   sent for seq=0
  t=  14.00  RECV  frame#1 delivered to network layer
  t=  14.00  ACK   sent for seq=1
  t=  15.00  TIMEOUT -> retransmit
  t=  15.00  SEND  frame#1 seq=1 (tx 4)
  t=  15.00  ACK   seq=0 is stale, ignored
  t=  18.00  ACK   arrives, sender moves on
delivered: [0, 1] | transmissions: 4 (wasted retransmissions)
Rule: timeout must exceed RTT (Tt + 2*Tp + receiver processing).
```

### SECTION 5: EFFICIENCY
Exam values: 1 Mbps link, 1000-bit frames, 200 km at 2e5 km/s gives Tt = 1 ms and Tp = 1 ms, so a = 1 and U = 1/3. The simulator, run with no loss for 50 frames, gives exactly the same utilisation, which confirms the formula. The small table shows how quickly efficiency falls as a grows.

Output from a real run:

```text
===== SECTION 5: EFFICIENCY =====
U = Tt / (Tt + 2*Tp) = 1 / (1 + 2a), a = Tp/Tt
Exam: B = 1 Mbps, frame = 1000 bits, distance 200 km, v = 2e5 km/s
Tt = 1.0 ms, Tp = 1.0 ms, a = 1.0, U = 1/(1+2.0) = 0.3333 = 33.33%
throughput = U * B = 333.3 kbps
simulated 50 frames, no loss: finish 150.0 ms, utilization 0.3333
formula matches simulation: check: OK

 a      U
  0.01 0.9804
   0.1 0.8333
     1 0.3333
    10 0.0476
   100 0.0050
```

### SECTION 6: LOSSY CHANNEL (seeded measurement)
With 20 percent independent loss each way and 400 frames (seed 42) all frames are still delivered in order without duplicates. The measured transmissions per frame (1.515) are close to, but not exactly, the simple estimate 1/(1-p)^2 = 1.562; it is one seeded sample, not a proof.

Output from a real run:

```text
===== SECTION 6: LOSSY CHANNEL (seeded measurement) =====
loss prob 0.2 each way, 400 frames, seed 42
delivered in order, no duplicates: True
transmissions per frame measured: 1.515
expected 1/(1-p)^2 = 1.562  (frame AND ACK must both survive)
```

## Worked Example
**Problem.** A 2 Mbps link carries 1000-bit frames over 400 km (propagation 2e5 km/s). Find the Stop-and-Wait utilisation.

**Solution.** Tt = 1000 / 2e6 = 0.5 ms. Tp = 400 / 2e5 = 2 ms. a = Tp/Tt = 4. U = 1/(1+2*4) = 1/9 = 11.1 percent, throughput about 222 kbps. (The program's own example, with a = 1, gives 1/3 = 33.33 percent and 333.3 kbps, and the simulation matches.)

## Key Rules / Gotchas Recap
- Efficiency U = 1/(1+2a), a = Tp/Tt.
- Timeout must exceed RTT = Tt + 2Tp (+ processing).
- A lost ACK causes a duplicate; sequence numbers (0/1) let the receiver discard it.
- Receiver re-ACKs duplicates so the sender can move on.
- Stale ACKs are ignored by comparing the ACK number with the current sequence bit.
- Stop-and-Wait is sliding window with window size 1.
- Loss rates measured by the simulator are seeded samples, not guarantees.

## Why This Matters
Every reliable transport and link protocol builds on this idea: timers, acknowledgements, retransmissions and duplicate suppression. Understanding why a lost ACK is worse than a lost frame is the basis for idempotent request design in networked services.
