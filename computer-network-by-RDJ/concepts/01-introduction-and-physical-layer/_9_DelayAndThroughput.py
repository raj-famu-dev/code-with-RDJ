# Tags: #Python #ComputerNetworks #PhysicalLayer #DelayThroughput | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Delay and throughput: transmission, propagation, queuing and processing delay,
RTT, bandwidth-delay product, throughput vs bandwidth, utilisation of a
stop-and-wait link, and jitter. Includes a seeded queue simulation checked against
the M/M/1 formula. Implements the 'performance metrics' syllabus topic."""
import random
import statistics

C_VACUUM = 3.0e8        # m/s, rounded as most textbooks do
V_COPPER = 2.0e8        # m/s, typical signal speed in cable/fibre (about 2/3 c)

# ===== SECTION 1: THE FOUR DELAYS ON ONE HOP =====
print("===== SECTION 1: THE FOUR DELAYS ON ONE HOP =====")


def d_trans(bits: float, rate_bps: float) -> float:
    """Transmission delay = L / R: time to push all bits onto the wire."""
    return bits / rate_bps


def d_prop(distance_m: float, speed: float = V_COPPER) -> float:
    """Propagation delay = d / s: time for one bit to travel the wire."""
    return distance_m / speed


L_BITS = 1500 * 8                       # one 1500-byte packet
R = 100e6                               # 100 Mbps
DIST = 2_000_000                        # 2000 km
d_proc = 20e-6                          # assumed router processing time 20 us (input, not a measurement)
d_queue = 150e-6                        # assumed average queuing time 150 us
t_tx, t_pr = d_trans(L_BITS, R), d_prop(DIST)
total = d_proc + d_queue + t_tx + t_pr
print(f"packet = {L_BITS:,} bits, link = {R / 1e6:.0f} Mbps, distance = {DIST / 1000:,.0f} km, signal speed = {V_COPPER:.1e} m/s")
print(f"  processing   (assumed) = {d_proc * 1e6:9.1f} us")
print(f"  queuing      (assumed) = {d_queue * 1e6:9.1f} us")
print(f"  transmission = L/R     = {t_tx * 1e6:9.1f} us")
print(f"  propagation  = d/s     = {t_pr * 1e6:9.1f} us")
print(f"  total nodal + link delay = {total * 1e3:.4f} ms")
assert round(t_tx * 1e6) == 120 and round(t_pr * 1e3) == 10
# Trap: confusing the two.
print(f"Trap: doubling the data rate to 200 Mbps changes transmission to {d_trans(L_BITS, 2 * R) * 1e6:.0f} us but propagation stays {t_pr * 1e6:.0f} us.")
print(f"      A longer cable changes propagation, not transmission: 4000 km -> {d_prop(2 * DIST) * 1e3:.0f} ms.")
print("Also: 100 Mbps means 100,000,000 bits per second (decimal), and 1500 BYTES = 12,000 BITS.")


# ===== SECTION 2: RTT AND BANDWIDTH-DELAY PRODUCT =====
print("\n===== SECTION 2: RTT AND BANDWIDTH-DELAY PRODUCT =====")
rtt = 2 * t_pr
print(f"RTT (propagation only) = 2 x {t_pr * 1e3:.0f} ms = {rtt * 1e3:.0f} ms")
for rate, label in [(100e6, "100 Mbps"), (1e9, "1 Gbps")]:
    bdp_bits = rate * rtt
    print(f"BDP at {label:<8} = {rate:,.0f} bps x {rtt:.3f} s = {bdp_bits:,.0f} bits = {bdp_bits / 8 / 1e6:.2f} MB (bits 'in flight')")
print("BDP = the data needed in flight to keep the pipe full; a sender window smaller than the BDP leaves the link idle.")
# Geostationary satellite: ground -> satellite -> ground, one way (altitude about 35,786 km).
sat_one_way = 2 * 35_786_000 / C_VACUUM
print(f"Geostationary satellite hop (ground -> satellite -> ground, straight overhead, c = 3e8 m/s): {sat_one_way * 1e3:.0f} ms one way, RTT about {2 * sat_one_way * 1e3:.0f} ms (physics only; real links add more).")
assert abs(sat_one_way - 0.2386) < 0.001


# ===== SECTION 3: THROUGHPUT VS BANDWIDTH AND UTILISATION =====
print("\n===== SECTION 3: THROUGHPUT VS BANDWIDTH AND UTILISATION =====")
links = [("access link", 100e6), ("ISP core", 10e9), ("server link", 20e6)]
print("Path link rates (bps):", {n: f"{r / 1e6:.0f} Mbps" for n, r in links})
bottleneck = min(links, key=lambda x: x[1])
print(f"End-to-end throughput <= bottleneck = {bottleneck[0]} = {bottleneck[1] / 1e6:.0f} Mbps (bandwidth is capacity, throughput is what you actually get)")

# Stop-and-wait utilisation: send one frame, wait for its ACK.
frame_bits = 12_000
rate = 100e6
one_way = 0.005                          # 5 ms
t_f = frame_bits / rate
cycle = t_f + 2 * one_way                # ignoring ACK transmission time
util = t_f / cycle
print(f"Stop-and-wait: frame time = {t_f * 1e6:.0f} us, RTT = {2 * one_way * 1e3:.0f} ms -> utilisation = {t_f * 1e6:.0f} / {cycle * 1e6:.0f} = {util:.2%}")
print(f"Effective throughput = {util * rate / 1e6:.2f} Mbps on a 100 Mbps link!")
window = round(cycle / t_f)
print(f"A sliding window of about {window} frames would keep the link full (window ~ 1 + RTT/frame_time).")
assert abs(util - 0.0119) < 1e-3 and 80 < window < 90
print("check: OK")


# ===== SECTION 4: QUEUING DELAY (SIMULATION vs M/M/1) =====
print("\n===== SECTION 4: QUEUING DELAY (SIMULATION vs M/M/1) =====")


def mm1_wait(rho: float, service_time: float) -> float:
    """Mean time waiting in the queue (excluding service) for the M/M/1 model (Poisson arrivals, exponential service): rho/(1-rho) * service_time."""
    return rho / (1 - rho) * service_time


def simulate(rho: float, n: int, service_time: float, seed: int) -> float:
    """Single FIFO link. Poisson arrivals, exponential service, mean queuing delay."""
    rng = random.Random(seed)
    arrival_rate = rho / service_time
    t_arr = 0.0
    server_free = 0.0
    total_wait = 0.0
    for _ in range(n):
        t_arr += rng.expovariate(arrival_rate)
        start = max(t_arr, server_free)
        total_wait += start - t_arr
        server_free = start + rng.expovariate(1 / service_time)
    return total_wait / n


svc = 120e-6        # mean service (transmission) time of a packet at 100 Mbps: 120 us
print(f"mean service time = {svc * 1e6:.0f} us; queuing delay vs traffic intensity rho (load / capacity):")
print(f"{'rho':>5}{'formula (us)':>14}{'simulated (us)':>16}")
sim_ok = True
for rho in (0.1, 0.5, 0.8, 0.9):
    f_us = mm1_wait(rho, svc) * 1e6
    s_us = simulate(rho, 200_000, svc, seed=11) * 1e6
    sim_ok &= abs(s_us - f_us) / f_us < 0.15
    print(f"{rho:>5.1f}{f_us:>14.1f}{s_us:>16.1f}")
print("Queuing delay explodes as rho -> 1; if rho > 1 the queue grows without bound and packets are dropped.")
print("Rule of thumb for design: keep utilisation well below 1.")
assert sim_ok
print("check: OK (simulated average within 15% of the formula)")


# ===== SECTION 5: JITTER =====
print("\n===== SECTION 5: JITTER =====")
rng = random.Random(3)
delays_ms = [20 + rng.expovariate(1 / 4) for _ in range(12)]    # 20 ms base + random queuing
diffs = [abs(b - a) for a, b in zip(delays_ms, delays_ms[1:])]
print("one-way delays (ms):", [round(d, 1) for d in delays_ms])
print(f"mean delay = {statistics.mean(delays_ms):.1f} ms, standard deviation = {statistics.pstdev(delays_ms):.1f} ms")
print(f"jitter (mean absolute difference between consecutive packets) = {statistics.mean(diffs):.1f} ms")
print("Jitter = variation in delay. Voice/video need low jitter: a playout (de-jitter) buffer trades a little extra fixed delay for smoothness.")
print("Trap: low AVERAGE delay does not mean low jitter; two links can have the same mean and very different jitter.")
steady = [30.0] * 12
print(f"steady link: mean {statistics.mean(steady):.1f} ms, jitter {statistics.mean([abs(b - a) for a, b in zip(steady, steady[1:])]):.1f} ms")


# ===== SECTION 6: WORKED EXAMPLE =====
print("\n===== SECTION 6: WORKED EXAMPLE =====")
# A 3000-byte file is sent as ONE packet over 2 links in series (store-and-forward), each 10 Mbps, 500 km, ignore queuing/processing.
bits = 3000 * 8
r = 10e6
per_link = d_trans(bits, r) + d_prop(500_000)
print(f"per link: {bits:,}/{r:,.0f} = {d_trans(bits, r) * 1e3:.1f} ms transmission + {d_prop(500_000) * 1e3:.1f} ms propagation = {per_link * 1e3:.1f} ms")
print(f"two store-and-forward links: 2 x {per_link * 1e3:.1f} = {2 * per_link * 1e3:.1f} ms")
assert round(2 * per_link * 1e3, 1) == 9.8
# (b) Window-limited throughput: 1 Gbps path, RTT 100 ms, sender window 64 KB (65,536 bytes).
rate_b, rtt_b, win_b = 1e9, 0.100, 65_536
bdp_b = rate_b * rtt_b / 8
thr_b = win_b * 8 / rtt_b
print(f"(b) 1 Gbps, RTT 100 ms: BDP = {bdp_b:,.0f} bytes ({bdp_b / 1e6:.1f} MB); a {win_b:,}-byte window gives "
      f"{thr_b / 1e6:.2f} Mbps = {thr_b / rate_b:.2%} of the link")
assert bdp_b == 12_500_000 and round(thr_b / 1e6, 2) == 5.24
print("check: OK")
