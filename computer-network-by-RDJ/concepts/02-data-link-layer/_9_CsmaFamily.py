# Tags: #Python #ComputerNetworks #DataLinkLayer #CsmaFamily | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""CSMA family: 1-persistent, non-persistent and p-persistent CSMA, CSMA/CD with
binary exponential backoff and the minimum frame size 2*Tp*B, CSMA/CA and the
RTS/CTS idea for the hidden terminal. Implements the Medium Access Control
(CSMA) part of the Data Link chapter."""
import random

# ===== SECTION 1: PERSISTENCE STRATEGIES =====
print("===== SECTION 1: PERSISTENCE STRATEGIES =====")
print(f"{'method':<16}{'channel busy':<28}{'channel idle'}")
print(f"{'1-persistent':<16}{'keep listening':<28}{'send with probability 1'}")
print(f"{'non-persistent':<16}{'wait random time, re-sense':<28}{'send immediately'}")
print(f"{'p-persistent':<16}{'wait until idle':<28}{'send with prob p, else next slot'}")
print()
print("Setup: n stations all have a frame ready while the channel is busy.")
print("When it turns idle, what is P(exactly one station starts in that slot)?")
rng = random.Random(5)
trials = 20000
print(f"{'n':>3} {'1-persistent':>13} {'p=0.1 sim':>10} {'p=0.1 formula':>14}")
for n in [2, 3, 5, 10]:
    p = 0.1
    ok = sum(sum(rng.random() < p for _ in range(n)) == 1 for _ in range(trials))
    formula = n * p * (1 - p) ** (n - 1)
    print(f"{n:>3} {0.0:>13.1f} {ok / trials:>10.4f} {formula:>14.4f}")
print("1-persistent: all n start together -> certain collision for n >= 2 (column 0.0).")
print("p-persistent trades idle slots for fewer collisions; best p is about 1/n.")
print("(sim column = seeded measurement with seed 5)")

# ===== SECTION 2: CSMA/CD MINIMUM FRAME SIZE =====
print("\n===== SECTION 2: CSMA/CD MINIMUM FRAME SIZE =====")
print("Sender must still be transmitting when the collision signal returns:")
print("   Tt >= 2 * Tp   =>   L_min = 2 * Tp * B")


def min_frame_bits(distance_m: float, bandwidth_bps: float, v: float = 2e8) -> float:
    tp = distance_m / v
    return 2 * tp * bandwidth_bps


cases = [
    ("10 Mbps, Tp = 25.6 us", 25.6e-6 * 2e8, 10e6),
    ("10 Mbps, 2500 m (v = 2e8)", 2500, 10e6),
    ("100 Mbps, 200 m", 200, 100e6),
    ("1 Gbps, 200 m", 200, 1e9),
]
for label, dist, bw in cases:
    bits = min_frame_bits(dist, bw)
    print(f"{label:<28} L_min = {bits:>8.0f} bits = {bits / 8:>7.1f} bytes")
assert round(min_frame_bits(25.6e-6 * 2e8, 10e6)) == 512
print("Classic 10 Mbps Ethernet: slot time 51.2 us x 10 Mbps = 512 bits = 64 bytes: check: OK")
print("Exam: min frame = 1000 bits at 10 Mbps, v = 2e8 -> max distance:")
d_max = 1000 / 10e6 / 2 * 2e8
print(f"   d = (L / B) / 2 * v = {d_max:.0f} m")

print("\nTRAP: frame shorter than 2*Tp -> collision NOT noticed")
B, Tp = 10e6, 25.6e-6
for L in [256, 512, 1024]:
    Tt = L / B
    seen = Tt >= 2 * Tp
    print(f"  L = {L:>4} bits, Tt = {Tt * 1e6:5.1f} us, 2Tp = {2 * Tp * 1e6:.1f} us ->"
          f" {'collision detected' if seen else 'sender finished first: loss goes UNDETECTED'}")

# ===== SECTION 3: BINARY EXPONENTIAL BACKOFF =====
print("\n===== SECTION 3: BINARY EXPONENTIAL BACKOFF =====")
print("After the n-th collision wait K slots, K uniform in 0..2^min(n,10)-1; give up after 16 tries.")
for n in [1, 2, 3, 4, 10, 11]:
    print(f"  collision {n:>2}: K in 0..{2 ** min(n, 10) - 1}")


def contend(rng: random.Random, verbose: bool = False) -> int:
    """Two stations collide on try 1 and back off until they pick different K.
    Returns number of collisions before one succeeds (give up at 16)."""
    collisions = 1
    while collisions < 16:
        k1 = rng.randrange(2 ** min(collisions, 10))
        k2 = rng.randrange(2 ** min(collisions, 10))
        if verbose:
            print(f"  after collision {collisions}: A waits {k1}, B waits {k2} slots"
                  + (" -> collide again" if k1 == k2 else f" -> {'A' if k1 < k2 else 'B'} goes first"))
        if k1 != k2:
            return collisions
        collisions += 1
    return 16


rng = random.Random(3)
print("trace of one contention (seed 3):")
contend(rng, verbose=True)
rng = random.Random(99)
runs = [contend(rng) for _ in range(20000)]
print(f"mean collisions before success over 20000 runs: {sum(runs) / len(runs):.3f} (seeded measurement)")
print("theory: after collision n the two pick equal K with probability 1/2^n")
print(f"fraction needing 2+ collisions: {sum(r >= 2 for r in runs) / len(runs):.3f} (theory 0.5)")

# ===== SECTION 4: CSMA/CA =====
print("\n===== SECTION 4: CSMA/CA (Wi-Fi style backoff) =====")
print("Wireless cannot listen while sending, so it AVOIDS collisions:")
print("wait DIFS idle, count down a random backoff only while the channel is idle,")
print("freeze the counter when someone else transmits, receiver replies ACK after SIFS.")
rng = random.Random(8)
CW = 15
back = {"A": rng.randint(0, CW), "B": rng.randint(0, CW), "C": rng.randint(0, CW)}
print("initial backoff slots (CW=15, seed 8):", back)
clock = 0
order = []
while back:
    winner = min(back, key=lambda s: back[s])
    wait = back[winner]
    clock += wait
    order.append(winner)
    del back[winner]
    for s in back:
        back[s] -= wait  # counters froze at remaining value after the winner sent
    print(f"  after {wait} idle slots {winner} transmits; others freeze at {dict(back)}")
print("transmission order:", order, "(ties would collide, then CW doubles)")

# ===== SECTION 5: HIDDEN TERMINAL AND RTS/CTS =====
print("\n===== SECTION 5: HIDDEN TERMINAL AND RTS/CTS =====")
pos = {"A": 0, "B": 100, "C": 200}  # metres on a line
RANGE = 120


def hears(x: str, y: str) -> bool:
    return abs(pos[x] - pos[y]) <= RANGE


for x in "ABC":
    print(f"  {x} hears: {[y for y in 'ABC' if y != x and hears(x, y)]}")
print("A and C both want to send to B. A cannot hear C:", not hears("A", "C"))
print("TRAP: carrier sensing says 'idle' at both, both send, frames collide AT B.")
print("RTS/CTS fix: A sends RTS (short); B answers CTS which C DOES hear.")
cts_heard = [y for y in "ABC" if y != "B" and hears("B", y)]
print("CTS from B reaches:", cts_heard, "-> C sets its NAV (network allocation vector)")
print("and stays silent for the duration, so A's data frame is safe.")
print("Cost: RTS+CTS overhead, so used only above a frame-size threshold.")
