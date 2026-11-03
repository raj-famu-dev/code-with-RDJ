# Tags: #Python #ComputerNetworks #PhysicalLayer #TransmissionMedia | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Transmission media: guided (twisted pair, coax, fibre) vs unguided (radio,
microwave, infrared), attenuation in decibels, why twisting cancels noise (EMI),
and wavelength from frequency. Implements the 'transmission media' syllabus topic."""
import math
import random

C = 299_792_458.0   # speed of light in vacuum, m/s


# ===== SECTION 1: GUIDED MEDIA COMPARISON =====
print("===== SECTION 1: GUIDED MEDIA COMPARISON =====")
UTP = [
    # category, max rated speed (typical standards), note
    ("Cat 3", "10 Mbps", "old telephone/10BASE-T"),
    ("Cat 5", "100 Mbps", "100BASE-TX"),
    ("Cat 5e", "1 Gbps", "1000BASE-T, 100 m"),
    ("Cat 6", "1 Gbps (10 Gbps up to about 55 m)", "tighter twist, often with a spline"),
    ("Cat 6a", "10 Gbps at 100 m", "10GBASE-T, usually shielded or thicker"),
]
print("Twisted-pair categories (UTP; STP adds a foil/braid shield):")
for cat, speed, note in UTP:
    print(f"  {cat:<7}{speed:<38}{note}")
print("Ethernet over twisted pair reaches 100 m per segment (90 m permanent link + patch cords).")
print()
media = [
    ("UTP twisted pair", "copper", "cheap, easy; EMI/crosstalk, 100 m", "LAN cabling"),
    ("STP twisted pair", "copper+shield", "less EMI, costlier, heavier", "noisy sites"),
    ("Coaxial", "copper core+shield", "better shielding and bandwidth than UTP; bulky", "cable TV, old 10BASE2/5"),
    ("Fibre, multimode", "glass, 50/62.5 um core", "light takes many paths -> modal dispersion; shorter reach", "buildings, campus"),
    ("Fibre, single-mode", "glass, ~9 um core", "one path, lowest loss; costly gear; longest reach", "long haul, ISPs"),
]
print(f"{'medium':<19}{'material':<24}{'characteristics':<62}{'use'}")
for m in media:
    print(f"{m[0]:<19}{m[1]:<24}{m[2]:<62}{m[3]}")
print("Fibre is immune to EMI, very high bandwidth, hard to tap casually; downsides: cost, fragile, special tools to splice.")


# ===== SECTION 2: ATTENUATION IN DECIBELS =====
print("\n===== SECTION 2: ATTENUATION IN DECIBELS =====")


def db(p_in: float, p_out: float) -> float:
    """Loss/gain in dB = 10 log10(P_out / P_in); negative = loss (attenuation)."""
    return 10 * math.log10(p_out / p_in)


print(f"P drops 100 mW -> 50 mW : {db(100, 50):+.2f} dB (half the power is about -3 dB)")
print(f"P drops 100 mW -> 1 mW  : {db(100, 1):+.2f} dB")
assert round(db(100, 50), 2) == -3.01

# Link budget with ILLUSTRATIVE per-km losses (round numbers chosen for practice, not a spec).
loss_per_km = {"illustrative copper": 20.0, "illustrative multimode fibre": 3.0, "illustrative single-mode fibre": 0.4}
launch_dbm, receiver_min_dbm = 0.0, -28.0   # transmit power and receiver sensitivity, assumed
budget = launch_dbm - receiver_min_dbm
print(f"Assumed budget = {launch_dbm} dBm launch - ({receiver_min_dbm} dBm) sensitivity = {budget} dB")
for name, per_km in loss_per_km.items():
    print(f"  {name:<32} {per_km:>5.1f} dB/km -> max length about {budget / per_km:7.2f} km")
print("Amplifiers/repeaters are placed so total loss between them stays inside the budget.")
# Trap: dB are logarithmic - losses ADD, ratios MULTIPLY.
a, b = db(1, 0.5), db(0.5, 0.25)
print(f"Trap: two halvings in a row = {a:.2f} + {b:.2f} = {a + b:.2f} dB (adding), "
      f"i.e. power ratio {10 ** ((a + b) / 10):.2f}. Losing 50% twice leaves 25%, not 0%.")
assert abs(10 ** ((a + b) / 10) - 0.25) < 1e-12
print("check: OK")


# ===== SECTION 3: WHY TWISTING CANCELS NOISE (EMI) =====
print("\n===== SECTION 3: WHY TWISTING CANCELS NOISE (EMI) =====")
rng = random.Random(42)
bits = [1, 0, 1, 1, 0, 0, 1, 0]
# Differential signalling: wire A carries +v or -v, wire B carries the opposite.
sent_a = [+1.0 if b else -1.0 for b in bits]
sent_b = [-x for x in sent_a]
noise_scale = 2.0                       # strong interference, larger than the signal
common = [rng.uniform(-noise_scale, noise_scale) for _ in bits]   # same noise couples into BOTH wires (twisted)
rx_a = [s + n for s, n in zip(sent_a, common)]
rx_b = [s + n for s, n in zip(sent_b, common)]
diff = [(a_ - b_) / 2 for a_, b_ in zip(rx_a, rx_b)]       # receiver subtracts the two wires
single_ended = [a_ > 0 for a_ in rx_a]                      # a receiver looking at ONE wire vs ground
diff_bits = [1 if d > 0 else 0 for d in diff]
print("sent bits          :", bits)
print("common-mode noise  :", [f"{n:+.1f}" for n in common])
print("single-wire decode :", [int(x) for x in single_ended], f"errors={sum(int(x) != y for x, y in zip(single_ended, bits))}")
print("differential decode:", diff_bits, f"errors={sum(x != y for x, y in zip(diff_bits, bits))}")
assert diff_bits == bits and single_ended != [bool(b) for b in bits]
print("Twisting makes both wires pick up (nearly) the same interference, so the receiver's subtraction removes it.")
print("Unequal pickup (untwisted pairs, bad connectors) breaks the cancellation; that residual is crosstalk/EMI damage.")
print("check: OK")


# ===== SECTION 4: UNGUIDED MEDIA AND WAVELENGTH =====
print("\n===== SECTION 4: UNGUIDED MEDIA AND WAVELENGTH =====")
bands = [
    ("AM radio (example)", 1.0e6, "radio waves, omnidirectional, follow the ground/ionosphere"),
    ("FM radio (example)", 100e6, "radio waves, line of sight"),
    ("Wi-Fi 2.4 GHz band", 2.4e9, "ISM band, walls ok, crowded (Bluetooth, microwave ovens)"),
    ("Wi-Fi 5 GHz band", 5.0e9, "shorter range, more channels"),
    ("Terrestrial microwave link", 10e9, "narrow beam, needs line of sight and towers"),
    ("Infrared remote", 3.0e13, "short range, blocked by walls, no licence"),
]
print(f"{'band':<28}{'frequency':>14}{'wavelength':>14}  notes")
for name, f, note in bands:
    lam = C / f
    print(f"{name:<28}{f / 1e9:>10.3f} GHz{lam:>12.4g} m  {note}")
print("wavelength = speed of light / frequency; higher frequency -> shorter wavelength -> more directional, less wall penetration.")
print("Textbook spectrum: radio ~3 kHz-1 GHz, microwave ~1-300 GHz, infrared ~300 GHz-400 THz (boundaries vary by book).")
print("Satellite: geostationary orbit is about 35,786 km up; a hop is very long (see _9_DelayAndThroughput).")
print("Guided = signal follows a cable (needs wires, secure, cheap per bit). Unguided = through air/space (mobility, but shared, interceptable).")
assert abs(C / 2.4e9 - 0.1249) < 1e-3


# ===== SECTION 5: WORKED EXAMPLE =====
print("\n===== SECTION 5: WORKED EXAMPLE =====")
# A signal of 10 mW enters a cable with 2 dB/km loss. After 5 km what power remains?
p_in, per_km, km = 10.0, 2.0, 5
loss_db = per_km * km
p_out = p_in * 10 ** (-loss_db / 10)
print(f"loss = {per_km} dB/km x {km} km = {loss_db} dB")
print(f"P_out = {p_in} mW x 10^(-{loss_db}/10) = {p_out:.2f} mW")
assert abs(p_out - 1.0) < 1e-9
print("check: OK")
