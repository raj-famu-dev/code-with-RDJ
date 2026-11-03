# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP congestion control: cwnd, ssthresh, slow start, congestion avoidance (AIMD),
Tahoe vs Reno vs NewReno, fast recovery, a per-RTT cwnd simulation with text table and
ASCII plot, the throughput formulas, and AIMD fairness. Pure simulation, units = MSS."""
import math

# ===== SECTION 1: THE RULES =====
print("===== SECTION 1: THE RULES (cwnd IN UNITS OF MSS, ONE STEP = ONE RTT) =====")
print("""cwnd       congestion window: how much the sender may have in flight (limit = min(cwnd, rwnd))
ssthresh   slow-start threshold: where growth switches from exponential to linear
slow start          cwnd < ssthresh : +1 MSS per ACK  => cwnd DOUBLES every RTT
congestion avoidance cwnd >= ssthresh: +1/cwnd per ACK => cwnd grows by ~1 MSS per RTT (additive increase)
loss by 3 dup ACKs  (mild: network still delivering)  ssthresh = max(cwnd/2, 2)
loss by timeout     (severe: nothing getting through) ssthresh = max(cwnd/2, 2), cwnd = 1
Tahoe : any loss -> cwnd = 1, slow start again
Reno  : 3 dup ACKs -> fast retransmit + fast recovery: cwnd = ssthresh, stay in congestion avoidance
        timeout    -> cwnd = 1 (same as Tahoe)
NewReno: Reno, but stays in fast recovery until ALL segments lost from that window are repaired
AIMD  : Additive Increase (+1 MSS/RTT), Multiplicative Decrease (x 1/2 on loss)""")
print("slow start by hand (initial cwnd 1, ssthresh 16): ", end="")
cw, trace = 1, []
while cw < 16:
    trace.append(cw)
    cw = min(cw * 2, 16)
trace.append(cw)
print(" -> ".join(map(str, trace)), "(then +1 per RTT)")
assert trace == [1, 2, 4, 8, 16]
print("check: 1, 2, 4, 8, 16 doubles each RTT: OK")


# ===== SECTION 2: SIMULATION WITH ONE LOSS EVENT =====
print("\n===== SECTION 2: SIMULATION: ONE TRIPLE-DUPLICATE-ACK LOSS =====")


def simulate(variant: str, rounds: int, events: dict[int, tuple[str, int]],
             ssthresh0: int = 16) -> list[tuple[int, int, str]]:
    """Return [(cwnd, ssthresh, phase)] per round (round 1 first).
    events[r] = ("dup", n_lost) or ("timeout", 1): loss detected at the END of round r.
    Simplified per-RTT model (a documented simplification, not a packet-level TCP)."""
    cwnd, ssthresh, hold = 1, ssthresh0, 0
    out: list[tuple[int, int, str]] = []
    for r in range(1, rounds + 1):
        phase = "slow start" if cwnd < ssthresh else "cong. avoid"
        if hold:
            phase = "fast recovery"
        out.append((cwnd, ssthresh, phase))
        if r in events:
            kind, lost = events[r]
            ssthresh = max(cwnd // 2, 2)
            if kind == "timeout" or variant == "tahoe":
                cwnd, hold = 1, 0
            elif variant == "reno":
                # best case: each extra loss in the window triggers another halving (Reno leaves
                # recovery on the first partial ACK). It may also time out instead.
                cwnd = max(cwnd // (2 ** lost), 2)
                ssthresh = cwnd
                hold = 0
            else:  # newreno: one halving, then ONE extra RTT of recovery per additional loss
                cwnd, hold = ssthresh, lost - 1
        elif hold:
            hold -= 1  # still repairing holes, no growth
        elif cwnd < ssthresh:
            cwnd = min(cwnd * 2, ssthresh)
        else:
            cwnd += 1
    return out


R = 20
events1 = {9: ("dup", 1)}
runs = {v: simulate(v, R, events1) for v in ("tahoe", "reno", "newreno")}
print("initial ssthresh = 16; a triple-duplicate-ACK loss is detected at the end of round 9")
print(f"{'rnd':>3} | {'Tahoe':>5} {'ssth':>4} | {'Reno':>5} {'ssth':>4} | {'NewReno':>7} {'ssth':>4} | phase (Reno)")
for i in range(R):
    t, rn, nr = runs["tahoe"][i], runs["reno"][i], runs["newreno"][i]
    mark = "  <-- loss detected" if (i + 1) in events1 else ""
    print(f"{i + 1:>3} | {t[0]:>5} {t[1]:>4} | {rn[0]:>5} {rn[1]:>4} | {nr[0]:>7} {nr[1]:>4} | {rn[2]}{mark}")
assert runs["tahoe"][9][0] == 1 and runs["reno"][9][0] == 10
print("check: at loss cwnd was 20 -> ssthresh = 10. Tahoe restarts at 1; Reno/NewReno continue at 10: OK")
print("Reno gets back to the pre-loss rate far sooner: that is the point of fast recovery.")
print("(real Reno briefly inflates cwnd to ssthresh+3 during recovery and deflates afterwards;")
print(" the per-RTT table shows the value after recovery.)")


# ===== SECTION 3: TIMEOUT AND MULTIPLE LOSSES =====
print("\n===== SECTION 3: TIMEOUT, AND TWO LOSSES IN ONE WINDOW =====")
events2 = {9: ("timeout", 1)}
tt = {v: simulate(v, 14, events2) for v in ("tahoe", "reno", "newreno")}
same = tt["tahoe"] == tt["reno"] == tt["newreno"]
print("timeout at the end of round 9: cwnd path of all variants identical:", same)
print("  cwnd rounds 8..14:", [c for c, _, _ in tt["tahoe"][7:]], "(restart at 1 with ssthresh 10)")
assert same
events3 = {9: ("dup", 2)}
mm = {v: simulate(v, 16, events3) for v in ("tahoe", "reno", "newreno")}
print("\ntwo segments lost from the SAME window (cwnd 20), 3 dup ACKs received, rounds 9..16:")
for v in ("tahoe", "reno", "newreno"):
    print(f"  {v:<8} cwnd: {[c for c, _, _ in mm[v][8:]]}")
print("  Tahoe  : collapses to 1 either way.")
print("  Reno   : leaves recovery after the first partial ACK; best case it halves again (20 -> 5),")
print("           and often has to wait for a timeout instead (model shows the best case).")
print("  NewReno: partial ACKs keep it in recovery; it repairs one hole per RTT and halves ONCE (20 -> 10).")
print("  (a simplified model of well-known behaviour; real stacks also use SACK to repair faster)")


# ===== SECTION 4: ASCII PLOT =====
print("\n===== SECTION 4: ASCII PLOT OF cwnd (one # = 1 MSS) =====")
print("rnd  Tahoe                      Reno / NewReno")
for i in range(R):
    tc = runs["tahoe"][i][0]
    rc = runs["reno"][i][0]
    print(f"{i + 1:>3}  {'#' * tc:<24} |{'#' * rc}")
print("Tahoe's sawtooth drops to the floor; Reno's drops by half. Both climb linearly (AIMD).")


# ===== SECTION 5: THROUGHPUT =====
print("\n===== SECTION 5: THROUGHPUT FORMULAS =====")
print("window/RTT rule:     throughput = window / RTT (bytes per second)")
mss, rtt = 1460, 0.100
for w in (10, 44, 100):
    print(f"  cwnd {w:>3} MSS, RTT 100 ms: {w * mss * 8 / rtt / 1e6:7.3f} Mbit/s")
print("AIMD sawtooth: cwnd oscillates between W/2 and W, so average window = 3/4 W,")
print("  average throughput ~ 0.75 x W x MSS / RTT.")
link_bps, rtt, mss = 10_000_000, 0.100, 1500
bdp_bytes = link_bps * rtt / 8
w_max = bdp_bytes / mss
print(f"example: link 10 Mbit/s, RTT 100 ms, MSS {mss}: BDP = {bdp_bytes:.0f} bytes = {w_max:.1f} MSS")
print(f"  if loss happens when cwnd reaches the BDP: average = 0.75 x {link_bps / 1e6:.0f} = {0.75 * link_bps / 1e6:.2f} Mbit/s")
W = 80
cyc = []
for _ in range(50):
    for c in range(W // 2, W + 1):
        cyc.append(c)
avg = sum(cyc) / len(cyc)
print(f"sawtooth check: W = {W}, simulated mean cwnd = {avg:.2f} vs 0.75 W = {0.75 * W:.2f}")
assert abs(avg - 0.75 * W) < 1
print("check: mean of a W/2..W sawtooth is about 3/4 W: OK")
p = 1e-4
mathis = 1.22 * 1460 / (0.100 * math.sqrt(p))
print(f"Mathis formula: throughput ~ 1.22 x MSS / (RTT x sqrt(p)); MSS 1460, RTT 100 ms, loss p = {p}:")
print(f"  = {mathis:,.0f} bytes/s = {mathis * 8 / 1e6:.1f} Mbit/s   (an approximation for Reno-like AIMD)")
print("  consequences: halve the RTT -> double the rate; quadruple the loss -> halve the rate.")
print("Linux today uses CUBIC by default; BBR is a different, model-based approach (not simulated).")


# ===== SECTION 6: FAIRNESS =====
print("\n===== SECTION 6: WHY AIMD IS FAIR (TWO FLOWS, ONE LINK) =====")


def share(policy: str, x: float, y: float, cap: float = 100.0, steps: int = 400) -> tuple[float, float]:
    for _ in range(steps):
        if x + y > cap:  # congestion: both flows see a loss
            if policy == "AIMD":
                x, y = x / 2, y / 2
            else:  # AIAD: subtract a constant
                x, y = max(x - 1, 1), max(y - 1, 1)
        else:
            x, y = x + 1, y + 1  # additive increase for both
    return x, y


for policy in ("AIAD", "AIMD"):
    x, y = share(policy, 70.0, 10.0)
    print(f"{policy}: start (70, 10), gap 60 -> after 400 RTTs: ({x:.1f}, {y:.1f}), gap {abs(x - y):.1f}")
a, b = share("AIMD", 70.0, 10.0)
assert abs(a - b) < 1 and abs(share("AIAD", 70.0, 10.0)[0] - share("AIAD", 70.0, 10.0)[1]) > 50
print("check: AIMD closes the gap (each halving halves it, each increase leaves it unchanged);")
print("       AIAD keeps the gap forever: OK")
print("Caveat: AIMD is fair only between flows with SIMILAR RTTs; short-RTT flows grow faster.")
