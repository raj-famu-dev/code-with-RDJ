# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Go-Back-N ARQ: sender window 2^m - 1, receiver window 1, cumulative ACKs,
retransmitting the whole outstanding window after a timeout, the throughput
formula N/(1+2a), and the window-size trap with m-bit sequence numbers.
Implements the sliding-window 'Go-Back-N' part of the Data Link chapter."""
from dataclasses import dataclass, field


# ===== SECTION 1: WINDOWS AND SEQUENCE NUMBERS =====
print("===== SECTION 1: WINDOWS AND SEQUENCE NUMBERS =====")
print(f"{'m bits':>7} {'seq space':>10} {'GBN max sender window':>22}")
for m in [1, 2, 3, 4]:
    print(f"{m:>7} {2 ** m:>10} {2 ** m - 1:>22}")
print("Receiver window is 1: it accepts only the next in-order frame.")


# ===== SECTION 2: SIMULATOR =====
@dataclass
class GbnResult:
    delivered: list[int] = field(default_factory=list)
    transmissions: list[int] = field(default_factory=list)  # seq of every send
    log: list[str] = field(default_factory=list)
    finish: int = 0


def gbn(total: int, window: int, tt: int, tp: int, timeout: int,
        lose_first_tx: set[int] | None = None, verbose: bool = False,
        max_ticks: int = 2000) -> GbnResult:
    """Tick-based simulation. One frame may start per tick (tt = 1 tick).
    Data arrives tt+tp after it is sent; an ACK arrives tp later.
    lose_first_tx: sequence numbers whose FIRST transmission is lost."""
    lose = set(lose_first_tx or ())
    res = GbnResult()
    base = nxt = expected = 0
    timer_start: int | None = None
    data_q: list[tuple[int, int]] = []  # (arrival tick, seq)
    ack_q: list[tuple[int, int]] = []  # (arrival tick, cumulative ack number)

    def say(t: int, msg: str) -> None:
        res.log.append(f"t={t:3d}  {msg}")
        if verbose:
            print(f"  t={t:3d}  {msg}")

    for t in range(max_ticks):
        for item in sorted(x for x in ack_q if x[0] == t):  # ACKs reaching sender
            ack_q.remove(item)
            k = item[1]
            if k + 1 > base:
                say(t, f"sender gets ACK {k}: cumulative, window slides base {base}->{k + 1}")
                base = k + 1
                timer_start = t if base < nxt else None
            else:
                say(t, f"sender gets ACK {k}: duplicate, ignored")
        for item in sorted(x for x in data_q if x[0] == t):  # data reaching receiver
            data_q.remove(item)
            s = item[1]
            if s == expected:
                res.delivered.append(s)
                say(t, f"receiver gets {s}: in order, delivered, ACK {s}")
                ack_q.append((t + tp, s))
                expected += 1
            else:
                say(t, f"receiver gets {s}: expected {expected}, DISCARDED")
                if expected > 0:
                    ack_q.append((t + tp, expected - 1))
        if base == total:
            res.finish = t
            return res
        if timer_start is not None and t - timer_start >= timeout:
            say(t, f"TIMEOUT for frame {base}: go back, resend {base}..{nxt - 1}")
            nxt = base
            timer_start = None
        if nxt < total and nxt < base + window:
            lost = nxt in lose and nxt not in {s for s in res.transmissions}
            if lost:
                lose.discard(nxt)
            res.transmissions.append(nxt)
            say(t, f"sender sends {nxt}" + ("  -- LOST" if lost else ""))
            if not lost:
                data_q.append((t + tt + tp, nxt))
            if timer_start is None:
                timer_start = t
            nxt += 1
    raise RuntimeError("did not finish")


print("\n===== SECTION 2: SIMULATION WITH ONE LOST FRAME =====")
print("total=8 frames, window N=4, tt=1, tp=2, timeout=7 ticks, frame 2 lost once")
r = gbn(8, 4, 1, 2, 7, lose_first_tx={2}, verbose=True)
print("delivered in order:", r.delivered)
print("transmissions     :", r.transmissions)
extra = len(r.transmissions) - 8
print(f"extra transmissions caused by one loss: {extra} (the whole window is resent)")
assert r.delivered == list(range(8))

print("\n===== SECTION 3: NO LOSS VS LOSS =====")
clean = gbn(8, 4, 1, 2, 7)
print(f"no loss : {len(clean.transmissions)} transmissions, finished tick {clean.finish}")
print(f"one loss: {len(r.transmissions)} transmissions, finished tick {r.finish}")
print("Compare Selective Repeat (file 7): only frame 2 would be resent.")

# ===== SECTION 4: THROUGHPUT FORMULA =====
print("\n===== SECTION 4: THROUGHPUT FORMULA =====")
print("U = min(1, N / (1 + 2a)), a = Tp / Tt")
Tt, Tp = 1, 2
a = Tp / Tt
print(f"Exam: Tt = 1 ms, Tp = 2 ms -> a = {a}, 1+2a = {1 + 2 * a:.0f}")
print(f"{'N':>3} {'formula U':>10} {'simulated U':>12}")
for N in [1, 2, 3, 4, 5, 6]:
    formula = min(1.0, N / (1 + 2 * a))
    res = gbn(200, N, 1, 2, 7 + N)
    sim = 200 / (res.finish + 1)
    print(f"{N:>3} {formula:>10.3f} {sim:>12.3f}")
print("N = 1 is Stop-and-Wait (U = 1/(1+2a) = 0.2). N = 1+2a = 5 fills the pipe.")
print("Ideal window for full utilisation = 1 + 2a frames, needing sequence space > that.")

# ===== SECTION 5: TRAP - WINDOW = 2^m =====
print("\n===== SECTION 5: TRAP - WINDOW SIZE 2^m BREAKS GO-BACK-N =====")


def gbn_ambiguity(m: int, window: int) -> list[int]:
    """Sender sends `window` frames, every ACK is lost, sender times out and
    resends from seq 0 (mod 2^m). Receiver only knows sequence numbers mod 2^m."""
    space = 2 ** m
    expected = 0
    accepted = []
    for s in range(window):  # first copy, all arrive
        assert s % space == expected % space
        accepted.append(s)
        expected += 1
    # retransmission of the first frame: seq number 0 again
    if 0 == expected % space:
        accepted.append(0)  # receiver thinks it is the NEXT new frame
    return accepted


m = 2
print(f"m = {m}, sequence space 0..{2 ** m - 1}")
ok = gbn_ambiguity(m, 2 ** m - 1)
bad = gbn_ambiguity(m, 2 ** m)
print(f"N = {2 ** m - 1}: receiver expects seq {(2 ** m - 1) % 2 ** m}, retransmitted seq 0 "
      f"is {'taken as new' if len(ok) > 3 else 'rejected (correct)'}")
print(f"N = {2 ** m}: all {2 ** m} frames arrived, receiver expects seq 0 again; "
      f"retransmitted old frame 0 is {'ACCEPTED AS NEW DATA (bug)' if len(bad) > 4 else 'rejected'}")
assert len(ok) == 3 and len(bad) == 5
print("check: OK  -> sender window must be at most 2^m - 1 for Go-Back-N")
