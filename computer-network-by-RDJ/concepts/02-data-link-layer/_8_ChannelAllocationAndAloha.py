# Tags: #Python #ComputerNetworks #DataLinkLayer #ChannelAllocationAloha | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Channel allocation and ALOHA: static (FDM/TDM) vs dynamic allocation, pure
ALOHA vulnerable period, slotted ALOHA, throughput S = G e^-2G and S = G e^-G,
the 18.4% and 36.8% maxima found by computing, and a seeded Monte-Carlo
simulation. Implements the Medium Access Control (ALOHA) part of the Data Link
chapter."""
import math
import random

# ===== SECTION 1: STATIC ALLOCATION IS WASTEFUL FOR BURSTY TRAFFIC =====
print("===== SECTION 1: STATIC VS DYNAMIC ALLOCATION =====")
print("Mean delay of an M/M/1 queue: T = 1 / (mu*C - lambda)")
C = 100e6  # channel bits/s
frame_bits = 10_000
lam = 5000  # frames/s total arrival rate
mu = 1 / frame_bits  # frames per bit
T_single = 1 / (mu * C - lam)
N = 10
T_fdm = 1 / (mu * (C / N) - lam / N)
print(f"C = {C / 1e6:.0f} Mbps, frame = {frame_bits} bits, total load = {lam} frames/s")
print(f"one shared channel      : T = {T_single * 1000:.3f} ms")
print(f"FDM/TDM split into N={N}  : T = {T_fdm * 1000:.3f} ms  (= N x worse)")
assert abs(T_fdm / T_single - N) < 1e-9
print("Static allocation: each user owns a fixed slice even when idle -> waste when bursty.")
print("Dynamic allocation: stations compete (ALOHA, CSMA) or take turns (token/polling).")

# ===== SECTION 2: PURE ALOHA =====
print("\n===== SECTION 2: PURE ALOHA FORMULA =====")
print("Frame time T. A frame sent at t collides with any other started in (t-T, t+T):")
print("vulnerable (vacuum) period = 2T. G = mean frames offered per frame time T.")
print("P(no other start in 2T) = e^(-2G)  ->  S = G * e^(-2G)")
print(f"{'G':>5} {'S pure':>8}")
for G in [0.1, 0.25, 0.5, 1.0, 2.0, 3.0]:
    print(f"{G:>5} {G * math.exp(-2 * G):>8.4f}")
best_g = max((g / 10000 for g in range(1, 50000)), key=lambda g: g * math.exp(-2 * g))
best_s = best_g * math.exp(-2 * best_g)
print(f"numeric search for the maximum: G = {best_g:.4f}, S = {best_s:.4f} = {best_s * 100:.1f}%")
print(f"calculus: dS/dG = e^(-2G)(1 - 2G) = 0 -> G = 1/2, S = 1/(2e) = {1 / (2 * math.e):.4f}")
assert abs(best_s - 1 / (2 * math.e)) < 1e-6

# ===== SECTION 3: SLOTTED ALOHA =====
print("\n===== SECTION 3: SLOTTED ALOHA FORMULA =====")
print("Stations may start only at slot boundaries -> vulnerable period shrinks to T.")
print("P(no other start in T) = e^(-G)  ->  S = G * e^(-G)")
print(f"{'G':>5} {'S slotted':>10}")
for G in [0.1, 0.5, 1.0, 2.0, 3.0]:
    print(f"{G:>5} {G * math.exp(-G):>10.4f}")
best_g2 = max((g / 10000 for g in range(1, 50000)), key=lambda g: g * math.exp(-g))
best_s2 = best_g2 * math.exp(-best_g2)
print(f"numeric search: G = {best_g2:.4f}, S = {best_s2:.4f} = {best_s2 * 100:.1f}%")
print(f"calculus: dS/dG = e^(-G)(1 - G) = 0 -> G = 1, S = 1/e = {1 / math.e:.4f}")
assert abs(best_s2 - 1 / math.e) < 1e-6
print("Pure max 18.4% (G = 0.5), slotted max 36.8% (G = 1): slotting doubles it.")

# ===== SECTION 4: EXAM STYLE NUMERIC EXAMPLE =====
print("\n===== SECTION 4: EXAM EXAMPLE =====")
rate, size = 1_000_000, 1000  # 1 Mbps channel, 1000-bit frames
Tf = size / rate
print(f"Channel 1 Mbps, frame 1000 bits -> T = {Tf * 1000:.1f} ms; 500 frames/s offered")
G = 500 * Tf
print(f"G = 500 * {Tf} = {G}")
print(f"pure ALOHA   : S = {G * math.exp(-2 * G):.4f} -> "
      f"{G * math.exp(-2 * G) / Tf:.1f} frames/s succeed")
print(f"slotted ALOHA: S = {G * math.exp(-G):.4f} -> {G * math.exp(-G) / Tf:.1f} frames/s succeed")
print("TRAP: more load is not better. G = 3 (pure):", f"{3 * math.exp(-6):.4f}",
      "vs G = 0.5:", f"{0.5 * math.exp(-1):.4f}")

# ===== SECTION 5: MONTE-CARLO SIMULATION =====
print("\n===== SECTION 5: MONTE-CARLO (seeded measurement, not theory) =====")


def sim_pure(g: float, n: int, seed: int) -> float:
    rng = random.Random(seed)
    t, starts = 0.0, []
    for _ in range(n):
        t += rng.expovariate(g)  # time in units of T
        starts.append(t)
    ok = 0
    for i, s in enumerate(starts):
        prev_ok = i == 0 or s - starts[i - 1] >= 1.0
        next_ok = i == n - 1 or starts[i + 1] - s >= 1.0
        ok += prev_ok and next_ok
    return ok / starts[-1]  # successes per frame time = S


def sim_slotted(g: float, slots: int, seed: int) -> float:
    rng = random.Random(seed)
    ok = 0
    for _ in range(slots):
        # arrivals per slot ~ Poisson(g), counted by inter-arrival sums
        k, acc = 0, rng.expovariate(1.0)
        while acc < g:
            k += 1
            acc += rng.expovariate(1.0)
        ok += k == 1
    return ok / slots


print(f"{'G':>5} {'pure sim':>9} {'pure theory':>12} {'slot sim':>9} {'slot theory':>12}")
for G in [0.25, 0.5, 1.0, 2.0]:
    ps = sim_pure(G, 100_000, 1)
    ss = sim_slotted(G, 100_000, 2)
    print(f"{G:>5} {ps:>9.4f} {G * math.exp(-2 * G):>12.4f} "
          f"{ss:>9.4f} {G * math.exp(-G):>12.4f}")
    assert abs(ps - G * math.exp(-2 * G)) < 0.01 and abs(ss - G * math.exp(-G)) < 0.01
print("measured values (seeds 1 and 2, 100000 frames/slots) sit within 0.01 of theory: check: OK")
