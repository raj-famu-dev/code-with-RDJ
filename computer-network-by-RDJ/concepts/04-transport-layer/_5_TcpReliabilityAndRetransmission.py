# Tags: #Python #ComputerNetworks #TransportLayer #TcpReliabilityRetransmission | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP reliability: cumulative ACKs, duplicate ACKs and fast retransmit after 3,
timeout retransmission, Jacobson/Karels RTT estimation (SRTT, RTTVAR, RTO) worked
numerically, Karn's algorithm, and a seeded-loss simulator. Pure simulation."""
import random

# ===== SECTION 1: RTT ESTIMATION (JACOBSON / KARELS, RFC 6298) =====
print("===== SECTION 1: RTT ESTIMATION (JACOBSON / KARELS, RFC 6298) =====")
ALPHA, BETA, K = 1 / 8, 1 / 4, 4


class RttEstimator:
    def __init__(self, min_rto: float | None = None) -> None:
        self.srtt: float | None = None
        self.rttvar = 0.0
        self.rto = 1000.0  # RFC 6298 initial RTO is 1 second (in ms here)
        self.min_rto = min_rto

    def sample(self, r: float) -> float:
        if self.srtt is None:  # first measurement
            self.srtt = r
            self.rttvar = r / 2
        else:
            # RTTVAR uses the OLD srtt, so update it first
            self.rttvar = (1 - BETA) * self.rttvar + BETA * abs(self.srtt - r)
            self.srtt = (1 - ALPHA) * self.srtt + ALPHA * r
        self.rto = self.srtt + K * self.rttvar
        if self.min_rto is not None:
            self.rto = max(self.rto, self.min_rto)
        return self.rto


samples = [100, 120, 90, 300, 110, 100]
est = RttEstimator()
print("formulas: RTTVAR = 3/4 RTTVAR + 1/4 |SRTT - R| ; SRTT = 7/8 SRTT + 1/8 R ; RTO = SRTT + 4 RTTVAR")
print("first sample: SRTT = R, RTTVAR = R/2")
print(f"{'sample R':>8} {'SRTT':>8} {'RTTVAR':>8} {'RTO':>8}   (all milliseconds)")
for r in samples:
    est.sample(r)
    print(f"{r:>8} {est.srtt:>8.3f} {est.rttvar:>8.3f} {est.rto:>8.3f}")
# hand-computed textbook values for the first two rows
e2 = RttEstimator()
e2.sample(100)
assert (e2.srtt, e2.rttvar, e2.rto) == (100, 50, 300)
e2.sample(120)
assert (e2.srtt, e2.rttvar, e2.rto) == (102.5, 42.5, 272.5)
print("check: R=100 -> (100, 50, 300) and R=120 -> (102.5, 42.5, 272.5) match hand calculation: OK")
print("The spike R=300 raised RTTVAR a lot, so RTO jumped (a safety margin), then decays.")
floored = RttEstimator(min_rto=1000)
for r in samples:
    floored.sample(r)
print(f"RFC 6298 also says RTO should be at least 1 s: final RTO = {floored.rto:.0f} ms vs raw {est.rto:.1f} ms")

print("\nolder textbook formula (EWMA only, no variance), alpha = 0.9:")
srtt = float(samples[0])
for r in samples[1:]:
    srtt = 0.9 * srtt + 0.1 * r
print(f"  SRTT after the same samples = {srtt:.3f} ms; RTO = 2 x SRTT = {2 * srtt:.3f} ms")
print("  trap: 2 x SRTT ignores jitter; a 300 ms spike is far above it. Jacobson/Karels fixes that.")


# ===== SECTION 2: KARN'S ALGORITHM AND BACKOFF =====
print("\n===== SECTION 2: KARN'S ALGORITHM AND EXPONENTIAL BACKOFF =====")
print("Problem: segment sent at t=0, timeout, resent at t=300, ACK arrives at t=400.")
print("Is that ACK for the first copy (RTT 400) or the resend (RTT 100)? Nobody can tell.")
base = RttEstimator()
base.sample(100)
base.sample(100)
good_rto = base.rto
wrong = RttEstimator()
wrong.srtt, wrong.rttvar = base.srtt, base.rttvar
wrong.sample(400)  # naive: assume it matched the first send
wrong2 = RttEstimator()
wrong2.srtt, wrong2.rttvar = base.srtt, base.rttvar
wrong2.sample(100)  # naive: assume it matched the resend
print(f"RTO before: {good_rto:.1f} ms; if we guess 400: {wrong.rto:.1f} ms; if we guess 100: {wrong2.rto:.1f} ms")
print("Both guesses can be wrong and poison the estimator.")
print("Karn's rule: NEVER take an RTT sample from a retransmitted segment.")
print("Plus: after each timeout double the RTO (exponential backoff) until a fresh sample arrives.")
rto = 300.0
for attempt in range(1, 6):
    print(f"  timeout #{attempt}: wait {rto:.0f} ms, then retransmit and set RTO = {rto * 2:.0f} ms")
    rto *= 2
print("Backoff keeps TCP from hammering a congested network; it is a form of congestion control.")


# ===== SECTION 3: CUMULATIVE ACKS, DUP ACKS, FAST RETRANSMIT =====
print("\n===== SECTION 3: SIMULATOR WITH LOSS (FAST RETRANSMIT vs TIMEOUT) =====")
DELAY = 5      # one-way delay in ticks
RTO = 40       # fixed retransmission timeout in ticks (> one RTT plus window drain)
DUP_THRESHOLD = 3


def simulate(total: int, window: int, loss_prob: float = 0.0, seed: int = 0,
             force_lose: set[tuple[int, int]] | None = None, verbose: bool = True) -> dict[str, int]:
    """Segments numbered 1..total. ACK n means 'I have everything below n; send n next'.
    force_lose is a set of (segment, transmission_number) pairs that are dropped."""
    rng = random.Random(seed)
    force_lose = force_lose or set()
    events: dict[int, list[tuple[str, int]]] = {}
    tx_count: dict[int, int] = {}
    stats = {"sent": 0, "fast": 0, "timeout": 0, "dupacks": 0, "ticks": 0}

    def log(t: int, msg: str) -> None:
        if verbose:
            print(f"  t={t:<3} {msg}")

    def transmit(t: int, seg: int, why: str) -> None:
        tx_count[seg] = tx_count.get(seg, 0) + 1
        stats["sent"] += 1
        lost = (seg, tx_count[seg]) in force_lose or rng.random() < loss_prob
        log(t, f"SEND seg {seg}{'' if why == 'new' else ' (' + why + ')'}{'   <-- LOST' if lost else ''}")
        if not lost:
            events.setdefault(t + DELAY, []).append(("data", seg))

    base, nxt = 1, 1  # base = oldest unacked, nxt = next new segment
    expected, buffered = 1, set()  # receiver state
    dup, timer_start = 0, None
    for t in range(0, 2000):
        for kind, val in events.pop(t, []):
            if kind == "data":  # receiver side
                if val == expected:
                    expected += 1
                    while expected in buffered:
                        buffered.discard(expected)
                        expected += 1
                elif val > expected:
                    buffered.add(val)
                log(t, f"  receiver got seg {val} -> ACK {expected}")
                if rng.random() >= loss_prob:  # the ACK itself can be lost too
                    events.setdefault(t + DELAY, []).append(("ack", expected))
                else:
                    log(t, "  (that ACK was lost; a later cumulative ACK will cover it)")
            else:  # sender gets an ACK
                if val > base:
                    base, dup = val, 0
                    timer_start = t if base < nxt else None
                    log(t, f"  sender got ACK {val} (new): base -> {base}")
                elif val == base and base < nxt:
                    dup += 1
                    stats["dupacks"] += 1
                    log(t, f"  sender got ACK {val} (DUPLICATE #{dup})")
                    if dup == DUP_THRESHOLD:
                        stats["fast"] += 1
                        transmit(t, base, "FAST RETRANSMIT after 3 dup ACKs")
        if base > total:
            stats["ticks"] = t
            break
        if timer_start is not None and t - timer_start >= RTO and base < nxt:
            stats["timeout"] += 1
            transmit(t, base, "TIMEOUT RETRANSMIT")
            timer_start, dup = t, 0
        if nxt <= total and nxt - base < window:
            transmit(t, nxt, "new")
            if timer_start is None:
                timer_start = t
            nxt += 1
    return stats


print("scenario A: 10 segments, window 6, segment 3 lost on its first transmission")
sa = simulate(10, 6, force_lose={(3, 1)})
print("  result:", sa)
assert sa["fast"] == 1 and sa["timeout"] == 0
print("check: loss repaired by FAST RETRANSMIT (no timeout needed): OK")
print("  a duplicate ACK is a hint: 'something after the gap arrived'. 3 of them = probably loss, not reorder.")

print("\nscenario B: 4 segments, window 6, segment 3 lost (too few segments after it for 3 dup ACKs)")
sb = simulate(4, 6, force_lose={(3, 1)})
print("  result:", sb)
assert sb["timeout"] == 1 and sb["fast"] == 0
print("check: only 1 segment follows the gap -> 1 dup ACK -> must wait for the TIMEOUT: OK")

print("\nscenario C: 60 segments, window 8, 10% random loss of data AND acks, seed 1 (no log)")
sc = simulate(60, 8, loss_prob=0.10, seed=1, verbose=False)
print("  result:", sc)
retrans = sc["fast"] + sc["timeout"]
print(f"  60 needed, {sc['sent']} transmissions: {sc['sent'] - 60} extra = {retrans} loss-triggered "
      f"resends ({sc['fast']} fast, {sc['timeout']} timeout)")
print("  every run with seed 1 prints the same numbers; a different seed gives different ones.")
print("  note: the simulator ends when everything is acknowledged, so all 60 were delivered in order.")
