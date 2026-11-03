# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Stop-and-Wait ARQ: timeout, lost frame, lost ACK, premature timeout, 1-bit
sequence numbers, efficiency 1/(1+2a), and a seeded event-driven simulator.
Implements the 'flow control and error control: Stop-and-Wait' part of the
Data Link chapter."""
import heapq
import random
from dataclasses import dataclass, field


# ===== SECTION 1: EVENT-DRIVEN SIMULATOR =====
print("===== SECTION 1: SIMULATOR DESIGN =====")
print("Times in ms. Tt = frame transmit time, Tp = one-way propagation delay.")
print("Events: DATA arrives, ACK arrives, TIMEOUT fires. ACK transmit time ignored.")


@dataclass
class Result:
    delivered: list[int] = field(default_factory=list)  # frame ids handed up
    data_sent: int = 0
    finish: float = 0.0
    log: list[str] = field(default_factory=list)


def simulate(n_frames: int, tt: float, tp: float, timeout: float,
             lose_data: set[int] | None = None, lose_ack: set[int] | None = None,
             use_seq: bool = True, loss_prob: float = 0.0, seed: int = 0,
             verbose: bool = False) -> Result:
    """lose_data/lose_ack hold 1-based indexes of transmissions to drop."""
    rng = random.Random(seed)
    lose_data, lose_ack = lose_data or set(), lose_ack or set()
    res = Result()
    q: list[tuple[float, int, str, int]] = []  # (time, tiebreak, kind, value)
    tb = 0
    now = 0.0
    seq, frame_id = 0, 0  # sender state
    expected = 0  # receiver state
    ack_count = 0
    timer_gen = 0

    def push(t: float, kind: str, val: int) -> None:
        nonlocal tb
        tb += 1
        heapq.heappush(q, (t, tb, kind, val))

    def say(msg: str) -> None:
        line = f"t={now:7.2f}  {msg}"
        res.log.append(line)
        if verbose:
            print("  " + line)

    def send() -> None:
        nonlocal timer_gen
        res.data_sent += 1
        timer_gen += 1
        drop = res.data_sent in lose_data or rng.random() < loss_prob
        tag = f"frame#{frame_id} seq={seq if use_seq else '-'} (tx {res.data_sent})"
        say(f"SEND  {tag}" + ("  -- LOST in channel" if drop else ""))
        if not drop:
            push(now + tt + tp, "data", frame_id * 2 + seq)
        push(now + timeout, "timeout", timer_gen)

    send()
    while q:
        now, _, kind, val = heapq.heappop(q)
        if kind == "data":
            fid, s = divmod(val, 2)
            if (not use_seq) or s == expected:
                res.delivered.append(fid)
                say(f"RECV  frame#{fid} delivered to network layer")
                expected ^= 1
            else:
                say(f"RECV  frame#{fid} seq={s} DUPLICATE discarded, re-ACK")
            ack_count += 1
            drop = ack_count in lose_ack or rng.random() < loss_prob
            say(f"ACK   sent for seq={s}" + ("  -- LOST in channel" if drop else ""))
            if not drop:
                push(now + tp, "ack", s)
        elif kind == "ack":
            if (not use_seq) or val == seq:
                say("ACK   arrives, sender moves on")
                frame_id += 1
                seq ^= 1
                if frame_id == n_frames:
                    res.finish = now
                    break
                send()
            else:
                say(f"ACK   seq={val} is stale, ignored")
        elif kind == "timeout" and val == timer_gen:
            say("TIMEOUT -> retransmit")
            send()
    return res


# ===== SECTION 2: NO LOSS BASELINE =====
print("\n===== SECTION 2: NO LOSS BASELINE =====")
r = simulate(3, tt=1.0, tp=4.0, timeout=12.0, verbose=True)
print("delivered:", r.delivered, "| data transmissions:", r.data_sent, "| finish:", r.finish)

# ===== SECTION 3: LOST FRAME, LOST ACK =====
print("\n===== SECTION 3: LOST FRAME =====")
r = simulate(2, 1.0, 4.0, 12.0, lose_data={1}, verbose=True)
print("delivered:", r.delivered, "| transmissions:", r.data_sent)
print("\n===== SECTION 3b: LOST ACK (the dangerous one) =====")
r = simulate(2, 1.0, 4.0, 12.0, lose_ack={1}, verbose=True)
print("delivered:", r.delivered, "| transmissions:", r.data_sent)
print("The receiver got frame#0 twice, but seq numbers let it discard the copy.")
r_no = simulate(2, 1.0, 4.0, 12.0, lose_ack={1}, use_seq=False)
print("TRAP same run WITHOUT sequence numbers -> delivered:", r_no.delivered,
      "(frame#0 delivered twice = duplicate data)")
assert r.delivered == [0, 1] and r_no.delivered == [0, 0, 1]

# ===== SECTION 4: PREMATURE TIMEOUT =====
print("\n===== SECTION 4: PREMATURE TIMEOUT =====")
print("RTT = Tt + 2*Tp = 9. Timeout 6 < RTT fires before the ACK can arrive.")
r = simulate(2, 1.0, 4.0, 6.0, verbose=True)
print("delivered:", r.delivered, "| transmissions:", r.data_sent, "(wasted retransmissions)")
print("Rule: timeout must exceed RTT (Tt + 2*Tp + receiver processing).")

# ===== SECTION 5: EFFICIENCY 1/(1+2a) =====
print("\n===== SECTION 5: EFFICIENCY =====")
print("U = Tt / (Tt + 2*Tp) = 1 / (1 + 2a), a = Tp/Tt")
print("Exam: B = 1 Mbps, frame = 1000 bits, distance 200 km, v = 2e5 km/s")
B, L, d, v = 1e6, 1000, 200.0, 2e5
Tt, Tp = L / B * 1000, d / v * 1000  # ms
a = Tp / Tt
U = 1 / (1 + 2 * a)
print(f"Tt = {Tt} ms, Tp = {Tp} ms, a = {a}, U = 1/(1+{2 * a}) = {U:.4f} = {U * 100:.2f}%")
print(f"throughput = U * B = {U * B / 1000:.1f} kbps")
sim = simulate(50, tt=Tt, tp=Tp, timeout=3 * (Tt + 2 * Tp))
meas = 50 * Tt / sim.finish
print(f"simulated 50 frames, no loss: finish {sim.finish:.1f} ms, utilization {meas:.4f}")
assert abs(meas - U) < 1e-9
print("formula matches simulation: check: OK")
print("\n a      U")
for aa in [0.01, 0.1, 1, 10, 100]:
    print(f"{aa:>6} {1 / (1 + 2 * aa):.4f}")

# ===== SECTION 6: LOSSY CHANNEL (seeded measurement) =====
print("\n===== SECTION 6: LOSSY CHANNEL (seeded measurement) =====")
p = 0.2
n = 400
res = simulate(n, 1.0, 4.0, 12.0, loss_prob=p, seed=42)
print(f"loss prob {p} each way, {n} frames, seed 42")
print("delivered in order, no duplicates:", res.delivered == list(range(n)))
print(f"transmissions per frame measured: {res.data_sent / n:.3f}")
print(f"expected 1/(1-p)^2 = {1 / (1 - p) ** 2:.3f}  (frame AND ACK must both survive)")
