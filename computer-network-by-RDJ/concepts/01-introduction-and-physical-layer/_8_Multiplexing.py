# Tags: #Python #ComputerNetworks #PhysicalLayer #Multiplexing | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Multiplexing: FDM channel plans, synchronous TDM frame building, statistical TDM,
WDM wavelength maths, and spread spectrum (DSSS with the 11-chip Barker code, FHSS).
Includes a TDM simulator. Implements the 'multiplexing and spread spectrum' syllabus topic."""
import random

C = 299_792_458.0


# ===== SECTION 1: FDM CHANNEL PLAN =====
print("===== SECTION 1: FDM CHANNEL PLAN =====")


def fdm_plan(n: int, channel_khz: float, guard_khz: float, start_khz: float = 0.0) -> list[tuple[float, float]]:
    """Each channel gets its own frequency slice; guard bands stop neighbours overlapping."""
    plan, f = [], start_khz
    for _ in range(n):
        plan.append((f, f + channel_khz))
        f += channel_khz + guard_khz
    return plan


plan = fdm_plan(5, 100, 10)
for i, (lo, hi) in enumerate(plan, 1):
    print(f"  channel {i}: {lo:6.0f} - {hi:6.0f} kHz")
total = plan[-1][1] - plan[0][0]
print(f"minimum link bandwidth = 5 x 100 + 4 guard bands x 10 = {total:.0f} kHz")
assert total == 5 * 100 + 4 * 10
assert all(plan[i][1] < plan[i + 1][0] for i in range(len(plan) - 1)), "channels must not overlap"
voice = fdm_plan(12, 4, 0, start_khz=60)
print(f"12 voice channels of 4 kHz (a telephone 'group'): {voice[0][0]:.0f}-{voice[-1][1]:.0f} kHz = {voice[-1][1] - voice[0][0]:.0f} kHz")
print("FDM is ANALOG-style: signals share the medium at the SAME time, each on its own frequency band (carriers modulated).")
# Trap: forget the guard bands.
print(f"Trap: forgetting the 4 guard bands gives {5 * 100} kHz, but {total:.0f} kHz are needed.")


# ===== SECTION 2: SYNCHRONOUS TDM SIMULATOR =====
print("\n===== SECTION 2: SYNCHRONOUS TDM SIMULATOR =====")
print("Four 1 Mbps sources, one bit per slot:")
n_src, in_rate, bits_per_slot = 4, 1_000_000, 1
frame_bits = n_src * bits_per_slot
frame_rate = in_rate / bits_per_slot
out_rate = frame_rate * frame_bits
print(f"  frame = {n_src} slots x {bits_per_slot} bit = {frame_bits} bits; frame rate = {frame_rate:,.0f}/s")
print(f"  frame duration = {1e6 / frame_rate:.2f} us; slot duration = {1e6 / frame_rate / n_src:.2f} us; output rate = {out_rate / 1e6:.0f} Mbps")
assert out_rate == n_src * in_rate
print("  output rate = n x input rate (no framing bits); adding 1 framing bit makes each frame 5 bits -> 5 Mbps.\n")

# Input: what each source has to send at each tick ('.' = nothing to send). Fixed, hand-written.
arrivals = {
    "A": "A1 A2 .  A3 .  .  A4 .",
    "B": ".  B1 .  .  .  B2 .  .",
    "C": "C1 C2 C3 C4 C5 C6 C7 C8",
    "D": ".  .  .  D1 .  .  .  .",
}
queues = {k: [x if x != "." else None for x in v.split()] for k, v in arrivals.items()}
ticks = len(queues["A"])
sync_frames = []
for t in range(ticks):
    sync_frames.append([queues[k][t] for k in "ABCD"])   # slot k reserved for source k, used or not
print("tick | slot A slot B slot C slot D")
used = 0
for t, fr in enumerate(sync_frames):
    used += sum(x is not None for x in fr)
    print(f"{t:>4} | " + "  ".join(f"{(x or '--'):<6}" for x in fr).rstrip())
slots = ticks * n_src
print(f"slots sent = {slots}, slots carrying data = {used}, EMPTY = {slots - used} -> utilisation {used / slots:.0%}")
print("Synchronous TDM reserves slot k for source k in EVERY frame, so idle sources waste capacity.")
assert used == 15 and slots == 32


# ===== SECTION 3: STATISTICAL TDM =====
print("\n===== SECTION 3: STATISTICAL TDM =====")
DATA_BITS, ADDR_BITS = 8, 2
# Link carries only 2 slots per frame (it is sized for the AVERAGE load, not the peak). Each slot = address + data.
SLOTS_PER_FRAME = 2
stat_frames: list[list[tuple[str, str]]] = []
# At each tick, new arrivals join a FIFO; up to 2 slots leave per frame.
fifo: list[tuple[str, str]] = []
max_backlog = 0
t = 0
while t < ticks or fifo:
    if t < ticks:
        for k in "ABCD":
            x = queues[k][t]
            if x:
                fifo.append((k, x))
    frame = [fifo.pop(0) for _ in range(min(SLOTS_PER_FRAME, len(fifo)))]
    stat_frames.append(frame)
    max_backlog = max(max_backlog, len(fifo))
    t += 1
for t, fr in enumerate(stat_frames):
    print(f"frame {t:>2}: " + (" ".join(f"[{a}|{d}]" for a, d in fr) or "(empty)"))
sent_units = sum(len(f) for f in stat_frames)
sync_bits = slots * DATA_BITS
stat_slots = SLOTS_PER_FRAME * len(stat_frames)
stat_bits = stat_slots * (DATA_BITS + ADDR_BITS)
print(f"data units delivered: sync={used}, statistical={sent_units}")
print(f"synchronous : {slots} slots x {DATA_BITS} bits = {sync_bits} bits sent (no address needed)")
print(f"statistical : {stat_slots} slots x ({DATA_BITS}+{ADDR_BITS} address) = {stat_bits} bits sent (address needed: slots are not owned)")
print(f"Statistical TDM carried the same {sent_units} units on a link HALF as wide (2 slots per frame instead of 4),")
print(f"drained in {len(stat_frames)} frames; the price is {ADDR_BITS} address bits per slot and queueing (peak backlog after each frame = {max_backlog} unit(s) waiting).")
assert sent_units == used
print("check: OK")


# ===== SECTION 4: WDM =====
print("\n===== SECTION 4: WDM =====")
wavelengths, per_lambda_gbps = 8, 10
print(f"{wavelengths} wavelengths x {per_lambda_gbps} Gbps = {wavelengths * per_lambda_gbps} Gbps on ONE fibre")
lam = 1550e-9
df = 100e9
dlam = lam ** 2 * df / C
print(f"A 100 GHz DWDM grid slot near 1550 nm is about {dlam * 1e9:.2f} nm wide (delta-lambda = lambda^2 x delta-f / c)")
print("CWDM spaces channels far apart (20 nm), cheap lasers; DWDM packs 50-100 GHz slots, 40-96+ channels, costlier.")
print("WDM = FDM idea applied to LIGHT: a prism/grating combines on transmit and splits on receive.")
assert abs(dlam * 1e9 - 0.80) < 0.01


# ===== SECTION 5: SPREAD SPECTRUM =====
print("\n===== SECTION 5: SPREAD SPECTRUM =====")
BARKER = [+1, -1, +1, +1, -1, +1, +1, +1, -1, -1, -1]   # 11-chip Barker code (802.11 DSSS)


def dsss_spread(bits: list[int]) -> list[int]:
    """Each data bit (as +1/-1) is multiplied by the whole chip sequence -> 11 chips per bit."""
    return [(+1 if b else -1) * c for b in bits for c in BARKER]


def dsss_despread(chips: list[int]) -> list[int]:
    out = []
    for i in range(0, len(chips), len(BARKER)):
        corr = sum(c * k for c, k in zip(chips[i:i + len(BARKER)], BARKER))
        out.append(1 if corr > 0 else 0)
    return out


msg_bits = [1, 0, 1, 1, 0]
chips = dsss_spread(msg_bits)
print(f"data bits       : {msg_bits}")
print(f"chips (first 22): {chips[:22]}  ({len(chips)} chips total = {len(msg_bits)} bits x {len(BARKER)})")
rng = random.Random(5)
noisy = chips[:]
flip = rng.sample(range(len(noisy)), 12)           # corrupt 12 of 55 chips (about 22%)
for i in flip:
    noisy[i] = -noisy[i]
recovered = dsss_despread(noisy)
print(f"after flipping {len(flip)} of {len(chips)} chips: recovered bits = {recovered}")
assert dsss_despread(chips) == msg_bits and recovered == msg_bits
print("Spreading lowers the power per hertz and lets correlation vote the data out of burst noise/jamming (processing gain).")
print(f"Bandwidth grows by the spreading factor {len(BARKER)}; that is the cost.")


def hop_sequence(seed: int, hops: int, channels: int = 79) -> list[int]:
    """Both ends share a seed (a secret/standard), so both know the next channel (FHSS idea)."""
    g = random.Random(seed)
    return [g.randrange(channels) for _ in range(hops)]


tx = hop_sequence(2024, 10)
rx_ok = hop_sequence(2024, 10)
rx_bad = hop_sequence(7, 10)
print(f"FHSS transmitter channels : {tx}")
print(f"receiver with same seed   : match on {sum(a == b for a, b in zip(tx, rx_ok))}/10 hops")
print(f"receiver with wrong seed  : match on {sum(a == b for a, b in zip(tx, rx_bad))}/10 hops (it listens on the wrong channel)")
print("Bluetooth (classic) hops over 79 channels of 1 MHz; the seed idea is real, this PRNG is only a demonstration.")
assert tx == rx_ok
print("check: OK")


# ===== SECTION 6: WORKED EXAMPLE (T1) =====
print("\n===== SECTION 6: WORKED EXAMPLE (T1) =====")
channels, bits_ch, framing, fps = 24, 8, 1, 8000
frame_len = channels * bits_ch + framing
rate = frame_len * fps
print(f"T1 frame = {channels} x {bits_ch} + {framing} framing = {frame_len} bits; {fps:,} frames/s")
print(f"line rate = {frame_len} x {fps:,} = {rate:,} bps = {rate / 1e6:.3f} Mbps; payload = {channels * bits_ch * fps:,} bps")
print(f"each voice channel = {bits_ch * fps:,} bps = 64 kbps; framing overhead = {framing * fps:,} bps ({framing / frame_len:.2%})")
assert frame_len == 193 and rate == 1_544_000
print("check: OK")
