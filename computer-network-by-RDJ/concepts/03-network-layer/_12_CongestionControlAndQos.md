# `_12_CongestionControlAndQos.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Congestion happens when more packets are offered to a router or link than it can forward, so queues grow, delay rises and packets are dropped; congestion control is the set of techniques that prevent or relieve this, and Quality of Service (QoS) makes sure important traffic gets the bandwidth, delay and loss it needs. They exist because retransmitting dropped packets adds more load and can drive a network into congestion collapse, where throughput falls even as offered load rises.

**Causes.** Bursty traffic; slow links or processors; too little buffer memory; many input lines feeding one output line; retransmissions after loss.

**Flow control vs congestion control.** Flow control is a point-to-point matter (sender must not overrun the receiver). Congestion control is a global matter (all senders together must not overrun the network).

**Open loop vs closed loop.**

| | Open loop | Closed loop |
|---|---|---|
| Idea | prevent congestion by design, no feedback | detect congestion, feed back, adjust |
| Techniques | admission control, traffic shaping (leaky bucket, token bucket), policing, scheduling | choke packets, backpressure, load shedding, explicit congestion notification, TCP window adjustment |

**Leaky bucket.** Arriving packets are put in a finite queue (the bucket with a hole) that is drained at a constant rate. Output is smooth no matter how bursty the input; a full bucket discards new arrivals. Rate of output is fixed.

**Token bucket.** Tokens are generated at a constant rate up to a bucket size. To be sent, a packet (or byte) must take a token. If the bucket is full of saved tokens an idle source can later send a burst up to the bucket size, then falls back to the token rate. Burst length: S = C / (M - rho) where C = bucket size, M = maximum output rate, rho = token rate. Example: C = 250 KB, M = 25 MB/s, rho = 2 MB/s gives S = 250 / 23 = about 10.87 ms.

| | Leaky bucket | Token bucket |
|---|---|---|
| Output | constant rate | allows bursts up to bucket size |
| Idle periods | credit lost | credit saved as tokens |
| Overflow | packets discarded | packets wait (shaping) or are dropped (policing) |

**Traffic shaping vs policing.** Shaping buffers and delays excess traffic so it conforms (done on the sending side; adds delay). Policing checks traffic against the contract and drops or re-marks the excess (done at the network edge; no buffering).

**Closed-loop techniques.**
- Choke packet: a router measures utilisation (for example u = a x u + (1 - a) x f); above a threshold it sends a choke packet to the source, which reduces its rate. Hop-by-hop choke packets relieve each router along the path (backpressure).
- Load shedding: when routers are flooded they discard packets. Policy "wine" (old packets are worth more than new: file transfer) vs "milk" (new is better than old: real-time media). Random Early Detection (RED) drops packets randomly before the queue is full so TCP senders slow down early.
- Explicit Congestion Notification (ECN) marks packets instead of dropping them.

**QoS techniques.** Overprovisioning; buffering; shaping; resource reservation and admission control; packet scheduling (FIFO, priority queuing, weighted fair queuing). Architectures: Integrated Services (IntServ, per-flow reservation using RSVP) and Differentiated Services (DiffServ, packets marked with a class in the DSCP field of the IP header, treated per hop). QoS parameters: bandwidth, delay, jitter, loss.

Typical exam questions: "Explain leaky bucket with an example", "Compare leaky and token bucket", "Open loop vs closed loop", "What is a choke packet?", "Traffic shaping vs policing".

## Full Line-by-Line Breakdown

### SECTION 1: CAUSES AND TAXONOMY
Prints the causes and the open/closed-loop table, then runs a tiny queue model: service rate 3 packets/tick, a 5-packet buffer, arrivals `[0, 2, 8, 3, 1]`. At t=2, 8 packets arrive: only 5 fit, 3 are dropped, 3 are served, and 2 remain. Congestion is a buffer overflow in a few lines.

Output from a real run:

```text
===== SECTION 1: CAUSES AND TAXONOMY =====
Congestion: too many packets arrive for a router/link to handle, queues fill, delay rises, packets are dropped.
Causes: bursty traffic, slow links or slow router CPUs, limited buffer memory, many inputs
  for one output, and retransmissions of dropped packets (which add MORE load: a vicious circle).
Congestion collapse: offered load rises but useful throughput FALLS.
Flow control = sender vs receiver speed (end to end). Congestion control = whole network.
Open loop    prevent: good design, no feedback    admission control, traffic shaping (leaky/token bucket), policing, scheduling
Closed loop  react: monitor, feed back, adjust    choke packets, backpressure, load shedding, explicit congestion notification, TCP window

Queue model: service rate 3 packets/tick, buffer 5, arrivals [0, 2, 8, 3, 1]
  t=0: arrive 0, dropped 0, served 0, queued after 0
  t=1: arrive 2, dropped 0, served 2, queued after 0
  t=2: arrive 8, dropped 3, served 3, queued after 2
  t=3: arrive 3, dropped 0, served 3, queued after 2
  t=4: arrive 1, dropped 0, served 3, queued after 0
```

### SECTION 2: LEAKY BUCKET (SEEDED STREAM)
A seeded RNG (seed 42) generates the arrivals, so the stream is identical on every run. `leaky_bucket` adds arrivals to the level, discards what exceeds the capacity (6), then lets out `rate` (2) packets. The output column is never above 2 (smoothing); the 9 dropped packets are the price of bursts larger than the bucket. The conservation check proves every arrival is accounted for as sent, dropped or still in the bucket.

Output from a real run:

```text
===== SECTION 2: LEAKY BUCKET (SEEDED STREAM) =====
arrivals per tick: [6, 0, 0, 6, 1, 0, 0, 0, 6, 0, 6, 6, 5, 0] -> total 36
leaky bucket capacity 6 packets, output rate 2 packets/tick
tick arrive  sent dropped in bucket
   0      6     2       0         4
   1      0     2       0         2
   2      0     2       0         0
   3      6     2       0         4
   4      1     2       0         3
   5      0     2       0         1
   6      0     1       0         0
   7      0     0       0         0
   8      6     2       0         4
   9      0     2       0         2
  10      6     2       2         4
  11      6     2       4         4
  12      5     2       3         4
  13      0     2       0         2
output never exceeds 2 per tick (max 2): bursts are SMOOTHED to a constant rate
conservation check: arrivals 36 = sent 25 + dropped 9 + left 2: OK
```

### SECTION 3: TOKEN BUCKET (SAME STREAM)
`token_bucket` adds `rate` tokens per tick (up to `bucket`), each packet consumes one. Starting full, the first burst of 6 sends 4 immediately (the bucket size), then the rest at 2 per tick as tokens refill. At ticks 6-7 the source is idle (tick 5 only drains the leftover backlog), so tokens accumulate back up to 4, and at tick 8 another burst of 4 is allowed. This is the difference from the leaky bucket, whose output would have stayed at a constant rate. The formula for burst length is evaluated with the textbook numbers (10.87 ms).

Output from a real run:

```text
===== SECTION 3: TOKEN BUCKET (SAME STREAM) =====
token bucket size 4, token rate 2/tick, starts full, packets WAIT when no token (shaping)
tick arrive  sent tokens left
   0      6     4           0
   1      0     2           0
   2      0     0           2
   3      6     4           0
   4      1     2           0
   5      0     1           1
   6      0     0           3
   7      0     0           4
   8      6     4           0
   9      0     2           0
  10      6     2           0
  11      6     2           0
  12      5     2           0
  13      0     2           0
max burst sent = 4 (bucket size allows up to 4 at once, then falls back to rate 2)
Difference: leaky bucket output is ALWAYS constant rate; token bucket allows bursts
up to the bucket size after idle periods, saving up 'credit'.
TRAP: tokens are a CREDIT, not a queue: a full bucket holds tokens, not packets.
Burst length S = C / (M - rho): C=250 KB bucket, M=25 MB/s max rate, rho=2 MB/s token rate -> S = 10.87 ms
```

### SECTION 4: SHAPING VS POLICING
The same token-bucket contract is applied two ways. Shaping lets excess packets wait for tokens (27 sent, 9 still queued at the end, none lost). Policing has no queue: any packet without a token is dropped (21 sent, 15 dropped). The assertion checks that sent plus dropped equals all arrivals under policing.

Output from a real run:

```text
===== SECTION 4: SHAPING VS POLICING =====
same stream, same bucket(4)/rate(2):  shaping  sent 27, dropped 0 (rest still waiting: 9)
                                      policing sent 21, dropped 15
Shaping  = DELAY excess traffic (buffer) to conform to the contract; adds latency, used on the SENDER side.
Policing = DROP (or re-mark) excess traffic; no buffering, used at the NETWORK EDGE to enforce an SLA.
check: OK
```

### SECTION 5: CHOKE PACKETS, LOAD SHEDDING, QoS
A seeded busy/idle line makes utilisation u smoothed with weight 0.5: it stays 0 at first, rises as the line stays busy, and crosses the 0.8 threshold at tick 5, after which every tick generates a choke packet to the source. The rest is the theory summary (wine vs milk, RED, IntServ vs DiffServ) and a small FIFO vs priority queuing demonstration: voice packets jump ahead of data.

Output from a real run:

```text
===== SECTION 5: CHOKE PACKETS, LOAD SHEDDING, QoS =====
choke packets: utilisation u = 0.5*u + 0.5*f (f = line busy now?), threshold 0.8
  t= 0 f=0 u=0.00 
  t= 1 f=0 u=0.00 
  t= 2 f=0 u=0.00 
  t= 3 f=1 u=0.50 
  t= 4 f=1 u=0.75 
  t= 5 f=1 u=0.88 CHOKE sent to source
  t= 6 f=1 u=0.94 CHOKE sent to source
  t= 7 f=1 u=0.97 CHOKE sent to source
  t= 8 f=1 u=0.98 CHOKE sent to source
  t= 9 f=1 u=0.99 CHOKE sent to source
  t=10 f=1 u=1.00 CHOKE sent to source
6 chokes at ticks [5, 6, 7, 8, 9, 10]; a source that receives one should cut its rate (e.g. halve it)
Choke packet: router tells the SOURCE directly. Hop-by-hop choke / backpressure: relieves each hop on the way.
Load shedding: when the router is drowning it simply drops packets, chosen by policy:
  WINE (old is better: file transfer, keep old packets) vs MILK (new is better: real-time media, drop old).
  Random Early Detection (RED) drops randomly BEFORE the queue is full to signal TCP early.

QoS techniques: overprovisioning; buffering; traffic shaping (leaky/token bucket); resource reservation;
  admission control; packet scheduling (FIFO, priority queuing, weighted fair queuing).
  Integrated Services (IntServ) = per-flow reservation (RSVP).  Differentiated Services (DiffServ) = marks
  packets with a class (DSCP in the IP header) and routers give classes different treatment per hop.
QoS parameters: bandwidth, delay, jitter, loss.
FIFO order        : ['data1', 'voice2', 'data3', 'voice4', 'data5']
Priority (voice 1st): ['voice2', 'voice4', 'data1', 'data3', 'data5']
```

## Worked Example
**Q:** A leaky bucket has capacity 6 packets and leaks 2 packets per tick. 6 packets arrive at tick 0, none at ticks 1-2, and 6 more at tick 3. What is sent at each tick and is anything lost?

1. Tick 0: 6 arrive (fits exactly), 2 leave, 4 remain.
2. Tick 1: nothing arrives, 2 leave, 2 remain.
3. Tick 2: 2 leave, 0 remain.
4. Tick 3: 6 arrive, 2 leave, 4 remain. Nothing is lost because the bucket never exceeded 6.

The script's table starts with exactly this behaviour (sent 2, 2, 2, 2) and shows losses only later when 6 + 6 + 5 packets arrive in consecutive ticks.

## Key Rules / Gotchas Recap
- Open loop = prevent (shape, admit); closed loop = feedback (choke, backpressure, shed).
- Leaky bucket: constant output, no bursts, overflow discarded.
- Token bucket: saves credit; bursts up to bucket size; output rate is the limit only in the long run.
- Tokens are credits, not packets; the token bucket's packet queue is separate.
- Shaping delays; policing drops.
- Burst length S = C / (M - rho).
- Retransmission after loss makes congestion worse; hence congestion control matters.
- IntServ reserves per flow; DiffServ marks classes.

## Why This Matters
Rate limiters (API gateways, LLM request throttling, cloud egress limits) are token buckets, so this exact code pattern protects AI services from overload and abuse. Understanding queues, drops and shaping also explains why latency spikes under load and how DDoS mitigation is built.
