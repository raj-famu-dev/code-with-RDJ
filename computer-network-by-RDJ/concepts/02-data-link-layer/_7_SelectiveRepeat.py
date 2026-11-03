# Tags: #Python #ComputerNetworks #DataLinkLayer #SelectiveRepeat | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Selective Repeat ARQ: sender and receiver windows of 2^(m-1), receiver
buffering, individual ACKs and per-frame timers, a demonstrated failure when
the window is too large, a comparison of the three ARQ protocols, plus
pipelining and piggybacking. Implements the 'Selective Repeat' part of the
Data Link chapter."""
from dataclasses import dataclass, field


# ===== SECTION 1: WINDOW RULE =====
print("===== SECTION 1: WINDOW RULE =====")
print(f"{'m bits':>7} {'seq space':>10} {'SR max window (2^(m-1))':>25}")
for m in [2, 3, 4]:
    print(f"{m:>7} {2 ** m:>10} {2 ** (m - 1):>25}")
print("Both sender AND receiver have a window of this size.")


# ===== SECTION 2: SIMULATOR =====
@dataclass
class SrResult:
    delivered: list[int] = field(default_factory=list)
    transmissions: list[int] = field(default_factory=list)
    finish: int = 0


def sr(total: int, window: int, tt: int, tp: int, timeout: int,
       lose_first_tx: set[int] | None = None, verbose: bool = False) -> SrResult:
    lose = set(lose_first_tx or ())
    res = SrResult()
    base = nxt = rcv_base = 0
    acked: set[int] = set()
    buffered: set[int] = set()
    sent_at: dict[int, int] = {}
    data_q: list[tuple[int, int]] = []
    ack_q: list[tuple[int, int]] = []

    def say(t: int, msg: str) -> None:
        if verbose:
            print(f"  t={t:3d}  {msg}")

    def transmit(t: int, s: int, why: str) -> None:
        lost = s in lose and s not in res.transmissions
        res.transmissions.append(s)
        sent_at[s] = t
        say(t, f"sender {why} {s}" + ("  -- LOST" if lost else ""))
        if not lost:
            data_q.append((t + tt + tp, s))

    for t in range(2000):
        for item in sorted(x for x in ack_q if x[0] == t):
            ack_q.remove(item)
            acked.add(item[1])
            say(t, f"sender gets ACK {item[1]} (individual)")
            while base in acked:
                base += 1
        for item in sorted(x for x in data_q if x[0] == t):
            data_q.remove(item)
            s = item[1]
            if rcv_base <= s < rcv_base + window:
                if s == rcv_base:
                    say(t, f"receiver gets {s}: in order")
                else:
                    say(t, f"receiver gets {s}: out of order, BUFFERED (waiting for {rcv_base})")
                buffered.add(s)
                while rcv_base in buffered:
                    buffered.discard(rcv_base)
                    res.delivered.append(rcv_base)
                    rcv_base += 1
                    say(t, f"   deliver {rcv_base - 1} to network layer")
            else:
                say(t, f"receiver gets {s}: old duplicate, re-ACK")
            ack_q.append((t + tp, s))
        if base == total:
            res.finish = t
            return res
        resent = False
        for s in range(base, nxt):  # per-frame timers
            if s not in acked and t - sent_at[s] >= timeout and not resent:
                transmit(t, s, "TIMEOUT, resends only")
                resent = True
        if not resent and nxt < total and nxt < base + window:
            transmit(t, nxt, "sends")
            nxt += 1
    raise RuntimeError("did not finish")


print("\n===== SECTION 2: SIMULATION WITH ONE LOST FRAME =====")
print("total=8, window N=4, tt=1, tp=2, timeout=7, frame 2 lost once")
r = sr(8, 4, 1, 2, 7, lose_first_tx={2}, verbose=True)
print("delivered in order:", r.delivered)
print("transmissions     :", r.transmissions)
print("extra transmissions:", len(r.transmissions) - 8, "(only frame 2 resent)")
assert r.delivered == list(range(8)) and len(r.transmissions) == 9

# ===== SECTION 3: WHY WINDOW <= HALF THE SEQUENCE SPACE =====
print("\n===== SECTION 3: DEMONSTRATED FAILURE WITH A TOO-LARGE WINDOW =====")


def ambiguous(m: int, n: int) -> bool:
    """Sender sends n frames 0..n-1, all arrive, all ACKs are lost, so the sender
    retransmits frame 0. Receiver window has slid to rcv_base = n (mod 2^m).
    Return True if the OLD frame 0 falls inside the new receive window and so
    is wrongly accepted as new data."""
    space = 2 ** m
    new_window = {(n + i) % space for i in range(n)}
    return 0 in new_window


m = 3
print(f"m = {m}, sequence numbers 0..{2 ** m - 1}")
print(f"{'window':>7} {'new rx window':>20} {'old 0 accepted as new?':>24}")
for n in range(1, 2 ** m):
    win = [(n + i) % 2 ** m for i in range(n)]
    bad = ambiguous(m, n)
    print(f"{n:>7} {str(win):>20} {'YES (BUG)' if bad else 'no':>24}")
for n in range(1, 2 ** m):
    assert ambiguous(m, n) == (n > 2 ** (m - 1))
print("check: OK -> failure appears exactly when N > 2^(m-1) = 4")
print("Concrete case m=2, N=3: old 0 lands in new window [3,0,1] and is delivered"
      " as frame 4: DUPLICATE/WRONG data.")

# ===== SECTION 4: COMPARISON OF THE THREE ARQ PROTOCOLS =====
print("\n===== SECTION 4: COMPARISON TABLE =====")
rows = [
    ("Feature", "Stop-and-Wait", "Go-Back-N", "Selective Repeat"),
    ("Sender window", "1", "2^m - 1", "2^(m-1)"),
    ("Receiver window", "1", "1", "2^(m-1)"),
    ("Min seq bits", "1", "m", "m"),
    ("Receiver buffer", "no", "no", "yes"),
    ("ACK type", "per frame", "cumulative", "individual"),
    ("On loss resend", "that frame", "whole window", "that frame only"),
    ("Efficiency", "1/(1+2a)", "N/(1+2a)", "N/(1+2a)"),
    ("Complexity", "lowest", "medium", "highest"),
]
for row in rows:
    print(f"{row[0]:<17}{row[1]:<15}{row[2]:<14}{row[3]}")

# ===== SECTION 5: PIPELINING AND PIGGYBACKING =====
print("\n===== SECTION 5: PIPELINING AND PIGGYBACKING =====")
print("Pipelining = sending several frames before the first ACK returns.")
print("Stop-and-Wait sends 1 frame per RTT; with window N it sends N per RTT")
print("(see the U table in file 6). Piggybacking = carry the ACK inside the")
print("reverse-direction DATA frame instead of a separate ACK frame.")


@dataclass
class Frame:
    seq: int
    ack: int | None  # None = no ACK field in use
    payload: str


def count_frames(n_each: int, piggyback: bool) -> int:
    """Idealised two-way transfer: A and B each send n_each data frames."""
    data = 2 * n_each
    if piggyback:
        return data  # every ACK rides on a data frame going the other way
    return data + data  # one separate ACK frame per data frame


print("A and B each send 10 data frames (idealised, no loss, traffic in step):")
print("  separate ACK frames :", count_frames(10, False), "frames on the wire")
print("  piggybacked ACKs    :", count_frames(10, True), "frames on the wire")
f = Frame(seq=3, ack=5, payload="hello")
print("example piggybacked frame:", f, "-> carries data 3 AND ACK for B's frame 5")
print("Trap: if B has nothing to send, the ACK waits. Real protocols start an")
print("ACK timer and send a bare ACK if no data appears in time.")
