# Tags: #Python #ComputerNetworks #NetworkLayer #CongestionControlQos | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Congestion control and QoS: causes of congestion, open-loop vs closed-loop,
leaky bucket and token bucket implemented on a seeded packet stream, load
shedding, choke packets, shaping vs policing, and a QoS overview."""
from __future__ import annotations

import random
from collections import deque

# ===== SECTION 1: CAUSES AND TAXONOMY =====
print("===== SECTION 1: CAUSES AND TAXONOMY =====")
print("Congestion: too many packets arrive for a router/link to handle, queues fill, delay rises, packets are dropped.")
print("Causes: bursty traffic, slow links or slow router CPUs, limited buffer memory, many inputs")
print("  for one output, and retransmissions of dropped packets (which add MORE load: a vicious circle).")
print("Congestion collapse: offered load rises but useful throughput FALLS.")
print("Flow control = sender vs receiver speed (end to end). Congestion control = whole network.")
rows = [("Open loop", "prevent: good design, no feedback", "admission control, traffic shaping (leaky/token bucket), policing, scheduling"),
        ("Closed loop", "react: monitor, feed back, adjust", "choke packets, backpressure, load shedding, explicit congestion notification, TCP window")]
for r in rows:
    print(f"{r[0]:12} {r[1]:36} {r[2]}")
q = 5
arr = [0, 2, 8, 3, 1]
queue_len = 0
print("\nQueue model: service rate 3 packets/tick, buffer 5, arrivals", arr)
for t, a in enumerate(arr):
    queue_len += a
    dropped = max(0, queue_len - q)
    queue_len = min(queue_len, q)
    served = min(3, queue_len)
    queue_len -= served
    print(f"  t={t}: arrive {a}, dropped {dropped}, served {served}, queued after {queue_len}")


# ===== SECTION 2: LEAKY BUCKET =====
print("\n===== SECTION 2: LEAKY BUCKET (SEEDED STREAM) =====")
rng = random.Random(42)
STREAM = [rng.choice([0, 0, 1, 2, 5, 6]) for _ in range(14)]     # packets (unit size) arriving per tick
print("arrivals per tick:", STREAM, "-> total", sum(STREAM))


def leaky_bucket(stream: list[int], capacity: int, rate: int) -> tuple[list[int], list[int], list[int]]:
    """Packets enter a queue of `capacity`; exactly `rate` leave per tick. Overflow is discarded."""
    level, sent, dropped, levels = 0, [], [], []
    for a in stream:
        level += a
        d = max(0, level - capacity)
        level -= d
        out = min(rate, level)
        level -= out
        sent.append(out)
        dropped.append(d)
        levels.append(level)
    return sent, dropped, levels


sent, dropped, levels = leaky_bucket(STREAM, capacity=6, rate=2)
print("leaky bucket capacity 6 packets, output rate 2 packets/tick")
print(f"{'tick':>4} {'arrive':>6} {'sent':>5} {'dropped':>7} {'in bucket':>9}")
for t in range(len(STREAM)):
    print(f"{t:>4} {STREAM[t]:>6} {sent[t]:>5} {dropped[t]:>7} {levels[t]:>9}")
assert max(sent) <= 2
assert sum(STREAM) == sum(sent) + sum(dropped) + levels[-1]
print(f"output never exceeds 2 per tick (max {max(sent)}): bursts are SMOOTHED to a constant rate")
print(f"conservation check: arrivals {sum(STREAM)} = sent {sum(sent)} + dropped {sum(dropped)} + left {levels[-1]}: OK")


# ===== SECTION 3: TOKEN BUCKET =====
print("\n===== SECTION 3: TOKEN BUCKET (SAME STREAM) =====")


def token_bucket(stream: list[int], bucket: int, rate: int, shape: bool = True):
    """Tokens arrive at `rate`/tick up to `bucket`. A packet needs 1 token to go.
    shape=True: packets without a token WAIT in a queue (shaping).
    shape=False: packets without a token are DROPPED (policing)."""
    tokens, backlog = bucket, 0
    out, drops, toks = [], [], []
    for a in stream:
        tokens = min(bucket, tokens + rate)
        if shape:
            backlog += a
        else:
            backlog = a
        send = min(backlog, tokens)
        tokens -= send
        backlog -= send
        d = 0
        if not shape:
            d, backlog = backlog, 0
        out.append(send)
        drops.append(d)
        toks.append(tokens)
    return out, drops, toks


o, dr, tk = token_bucket(STREAM, bucket=4, rate=2, shape=True)
print("token bucket size 4, token rate 2/tick, starts full, packets WAIT when no token (shaping)")
print(f"{'tick':>4} {'arrive':>6} {'sent':>5} {'tokens left':>11}")
for t in range(len(STREAM)):
    print(f"{t:>4} {STREAM[t]:>6} {o[t]:>5} {tk[t]:>11}")
assert max(o) <= 4
print(f"max burst sent = {max(o)} (bucket size allows up to 4 at once, then falls back to rate 2)")
print("Difference: leaky bucket output is ALWAYS constant rate; token bucket allows bursts")
print("up to the bucket size after idle periods, saving up 'credit'.")
print("TRAP: tokens are a CREDIT, not a queue: a full bucket holds tokens, not packets.")
print("Burst length S = C / (M - rho): C=250 KB bucket, M=25 MB/s max rate, rho=2 MB/s token rate ->",
      f"S = {250e3 / (25e6 - 2e6) * 1000:.2f} ms")
assert abs(250e3 / (25e6 - 2e6) - 0.01087) < 1e-4


# ===== SECTION 4: SHAPING VS POLICING =====
print("\n===== SECTION 4: SHAPING VS POLICING =====")
o_s, d_s, _ = token_bucket(STREAM, 4, 2, shape=True)
o_p, d_p, _ = token_bucket(STREAM, 4, 2, shape=False)
print(f"same stream, same bucket(4)/rate(2):  shaping  sent {sum(o_s)}, dropped 0 (rest still waiting: {sum(STREAM) - sum(o_s)})")
print(f"                                      policing sent {sum(o_p)}, dropped {sum(d_p)}")
print("Shaping  = DELAY excess traffic (buffer) to conform to the contract; adds latency, used on the SENDER side.")
print("Policing = DROP (or re-mark) excess traffic; no buffering, used at the NETWORK EDGE to enforce an SLA.")
assert sum(o_p) + sum(d_p) == sum(STREAM)
print("check: OK")


# ===== SECTION 5: CHOKE PACKETS, LOAD SHEDDING, QOS =====
print("\n===== SECTION 5: CHOKE PACKETS, LOAD SHEDDING, QoS =====")
# Router estimates utilisation u = a*u + (1-a)*f (f = instant 0/1 busy). Above threshold -> choke packet.
a_coef, thresh = 0.5, 0.8
u = 0.0
rng = random.Random(5)
busy = [1 if rng.random() < p else 0 for p in [0.3] * 3 + [0.95] * 8]
print("choke packets: utilisation u = 0.5*u + 0.5*f (f = line busy now?), threshold 0.8")
chokes = []
for t, f in enumerate(busy):
    u = a_coef * u + (1 - a_coef) * f
    flag = "CHOKE sent to source" if u > thresh else ""
    if flag:
        chokes.append(t)
    print(f"  t={t:>2} f={f} u={u:.2f} {flag}")
print(f"{len(chokes)} chokes at ticks {chokes}; a source that receives one should cut its rate (e.g. halve it)")
print("Choke packet: router tells the SOURCE directly. Hop-by-hop choke / backpressure: relieves each hop on the way.")
print("Load shedding: when the router is drowning it simply drops packets, chosen by policy:")
print("  WINE (old is better: file transfer, keep old packets) vs MILK (new is better: real-time media, drop old).")
print("  Random Early Detection (RED) drops randomly BEFORE the queue is full to signal TCP early.")
print("\nQoS techniques: overprovisioning; buffering; traffic shaping (leaky/token bucket); resource reservation;")
print("  admission control; packet scheduling (FIFO, priority queuing, weighted fair queuing).")
print("  Integrated Services (IntServ) = per-flow reservation (RSVP).  Differentiated Services (DiffServ) = marks")
print("  packets with a class (DSCP in the IP header) and routers give classes different treatment per hop.")
print("QoS parameters: bandwidth, delay, jitter, loss.")
# priority vs FIFO demonstration
pkts = [("data", 1), ("voice", 2), ("data", 3), ("voice", 4), ("data", 5)]
fifo = [f"{n}{i}" for n, i in pkts]
prio = [f"{n}{i}" for n, i in sorted(pkts, key=lambda p: (p[0] != "voice", p[1]))]
print("FIFO order        :", fifo)
print("Priority (voice 1st):", prio)
