# Tags: #Python #ComputerNetworks #PhysicalLayer #SignalsEncoding | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Signals and encoding: analog vs digital, bandwidth, the Nyquist and Shannon
capacity formulas with worked numbers, and line coding (NRZ-L, NRZ-I, RZ,
Manchester, Differential Manchester, AMI, 4B/5B) implemented and printed as level
sequences. Implements the 'signals, bandwidth and line coding' syllabus topic."""
import math

# ===== SECTION 1: ANALOG vs DIGITAL, BIT RATE vs BAUD RATE =====
print("===== SECTION 1: ANALOG vs DIGITAL, BIT RATE vs BAUD RATE =====")
print(f"{'':<16}{'analog':<36}{'digital'}")
for r in [("values", "continuous range", "discrete levels (e.g. 2)"),
          ("bandwidth unit", "hertz (f_max - f_min)", "bits per second (bit rate)"),
          ("noise", "adds smoothly, hard to remove", "can be regenerated if small"),
          ("example", "voice on old phone line, AM radio", "Ethernet, USB, 5G data")]:
    print(f"{r[0]:<16}{r[1]:<36}{r[2]}")
print()


def baud_rate(bit_rate: float, levels: int) -> float:
    """Signal elements per second = bit rate / bits per element (log2 of levels)."""
    return bit_rate / math.log2(levels)


for levels in (2, 4, 16):
    print(f"1000 bps with {levels:>2} levels -> {math.log2(levels):.0f} bit(s) per element -> baud = {baud_rate(1000, levels):.0f}")
print("Bandwidth of a band-pass signal = f_high - f_low, e.g. 40 kHz to 100 kHz -> 60 kHz.")
print("Telephone voice: bandwidth about 4 kHz (3.1 kHz used); sampled 8000 times/s x 8 bits = 64 kbps PCM.")
assert 8000 * 8 == 64000


# ===== SECTION 2: NYQUIST AND SHANNON CAPACITY =====
print("\n===== SECTION 2: NYQUIST AND SHANNON CAPACITY =====")


def nyquist(bandwidth_hz: float, levels: int) -> float:
    """Noiseless channel: C = 2 * B * log2(L)."""
    return 2 * bandwidth_hz * math.log2(levels)


def shannon(bandwidth_hz: float, snr_linear: float) -> float:
    """Noisy channel: C = B * log2(1 + SNR)."""
    return bandwidth_hz * math.log2(1 + snr_linear)


def snr_from_db(snr_db: float) -> float:
    return 10 ** (snr_db / 10)


print("Nyquist (noiseless), B = 3000 Hz:")
for L in (2, 4, 8, 16):
    print(f"  L={L:>2} levels -> C = 2 x 3000 x log2({L}) = {nyquist(3000, L):,.0f} bps")
need_L = 2 ** (265_000 / (2 * 20_000))
print(f"Levels needed for 265 kbps over 20 kHz: L = 2^(265000 / 40000) = {need_L:.1f} -> use at least {math.ceil(need_L)}")
print("  (more levels = harder for the receiver to tell them apart: noise limits this, which Shannon captures)")
snr = snr_from_db(35)
c = shannon(3000, snr)
print(f"Shannon, telephone line B=3000 Hz, SNR = 35 dB = {snr:,.1f} (ratio) -> C = 3000 x log2(1 + {snr:,.1f}) = {c:,.0f} bps")
print(f"Shannon, SNR = 0 (pure noise): C = {shannon(3000, 0):.0f} bps  (no information gets through)")
# Combined problem: B = 1 MHz, SNR = 63 -> Shannon limit, then Nyquist levels to reach it.
cap = shannon(1e6, 63)
levels = 2 ** (cap / (2 * 1e6))
print(f"B = 1 MHz, SNR = 63: Shannon C = {cap:,.0f} bps; levels to reach it by Nyquist = {levels:.0f}")
assert round(cap) == 6_000_000 and round(levels) == 8
# Trap: SNR in dB must be converted to a ratio before using Shannon.
wrong = shannon(3000, 35)
print(f"Trap: plugging 35 (dB) straight in gives {wrong:,.0f} bps; the correct ratio is {snr:,.1f} and gives {c:,.0f} bps.")
assert abs(c - 34_881) < 2
print("check: OK")


# ===== SECTION 3: LINE CODING IMPLEMENTATIONS =====
print("\n===== SECTION 3: LINE CODING IMPLEMENTATIONS =====")
# Every coder returns TWO half-bit levels per bit as a flat list: +1 high, 0 zero, -1 low.
Level = int


def nrz_l(bits: str) -> list[Level]:
    """1 -> high, 0 -> low (level = data). Convention used here; some books invert it."""
    return [lv for b in bits for lv in ((+1, +1) if b == "1" else (-1, -1))]


def nrz_i(bits: str, start: Level = -1) -> list[Level]:
    """1 -> invert level at the start of the bit, 0 -> keep. (Inversion on ones.)"""
    out, cur = [], start
    for b in bits:
        if b == "1":
            cur = -cur
        out += [cur, cur]
    return out


def rz(bits: str) -> list[Level]:
    """1 -> high then zero, 0 -> low then zero (three levels, returns to zero mid-bit)."""
    return [lv for b in bits for lv in ((+1, 0) if b == "1" else (-1, 0))]


def manchester(bits: str) -> list[Level]:
    """Transition in the MIDDLE of every bit. Here 1 = low->high, 0 = high->low (books differ!)."""
    return [lv for b in bits for lv in ((-1, +1) if b == "1" else (+1, -1))]


def diff_manchester(bits: str, start: Level = -1) -> list[Level]:
    """Always a mid-bit transition; a 0 also has a transition at the START of the bit, a 1 has none."""
    out, cur = [], start
    for b in bits:
        if b == "0":
            cur = -cur          # extra transition at the beginning of the bit
        out += [cur, -cur]      # mid-bit transition always
        cur = -cur
    return out


def ami(bits: str) -> list[Level]:
    """Bipolar AMI: 0 -> zero volts, 1s alternate +1 / -1 (first 1 is +)."""
    out, last = [], -1
    for b in bits:
        if b == "1":
            last = -last
            out += [last, last]
        else:
            out += [0, 0]
    return out


def draw(levels: list[Level]) -> list[str]:
    """Three-row ASCII waveform (high / zero / low), two characters per half-bit."""
    return ["      " + "".join("--" if lv == row else "  " for lv in levels) for row in (+1, 0, -1)]


def sym(levels: list[Level]) -> str:
    return " ".join({+1: "+", 0: "0", -1: "-"}[lv] for lv in levels)


def transitions(levels: list[Level]) -> int:
    return sum(a != b for a, b in zip(levels, levels[1:]))


DATA = "10110010"
print(f"data bits: {DATA}   (two half-bit levels per bit; + high, - low, 0 zero)")
header = "      " + "".join(f"{b:<4}" for b in DATA)
coders = [("NRZ-L", nrz_l), ("NRZ-I", nrz_i), ("RZ", rz), ("Manchester", manchester),
          ("Diff. Manchester", diff_manchester), ("AMI", ami)]
for name, fn in coders:
    lv = fn(DATA)
    print(f"{name:<17}{sym(lv)}   transitions={transitions(lv)}")
print()
print("Waveform of Manchester (high row, zero row, low row):")
print(header)
for line in draw(manchester(DATA)):
    print(line)
print("Waveform of AMI:")
print(header)
for line in draw(ami(DATA)):
    print(line)
assert manchester("1") == [-1, 1] and ami("111") == [1, 1, -1, -1, 1, 1]
assert nrz_i("11") == [1, 1, -1, -1]
assert diff_manchester("0")[0] != -1 and diff_manchester("1")[0] == -1
print("check: OK")


# ===== SECTION 4: SYNCHRONISATION TRAP AND 4B/5B =====
print("\n===== SECTION 4: SYNCHRONISATION TRAP AND 4B/5B =====")
zeros = "0" * 12
for name, fn in [("NRZ-L", nrz_l), ("NRZ-I", nrz_i), ("AMI", ami), ("Manchester", manchester)]:
    lv = fn(zeros)
    print(f"{name:<11} on 12 zeros: transitions={transitions(lv):>2}  levels={sym(lv[:8])} ...")
print("Trap: NRZ-L, NRZ-I (zeros) and AMI (zeros) show NO transitions on long runs of zeros, so the receiver's")
print("clock drifts and it cannot count bits. Manchester always has mid-bit transitions (self-clocking) but needs 2x bandwidth.")
assert transitions(nrz_l(zeros)) == 0 and transitions(manchester(zeros)) > 0

FOURB_FIVEB = {
    "0000": "11110", "0001": "01001", "0010": "10100", "0011": "10101",
    "0100": "01010", "0101": "01011", "0110": "01110", "0111": "01111",
    "1000": "10010", "1001": "10011", "1010": "10110", "1011": "10111",
    "1100": "11010", "1101": "11011", "1110": "11100", "1111": "11101",
}


def encode_4b5b(bits: str) -> str:
    if len(bits) % 4:
        raise ValueError("4B/5B needs a multiple of 4 bits")
    return "".join(FOURB_FIVEB[bits[i:i + 4]] for i in range(0, len(bits), 4))


def max_zero_run(s: str) -> int:
    return max(len(r) for r in s.split("1"))


raw = "0000" * 4
enc = encode_4b5b(raw)
print(f"\nraw bits   : {raw}  (16 zeros)")
print(f"4B/5B      : {enc}  ({len(enc)} bits, +25% overhead, longest zero run {max_zero_run(enc)})")
print(f"NRZ-I of it: {sym(nrz_i(enc)[::2])}  (a '1' = transition; transitions={transitions(nrz_i(enc))})")
worst = max(max_zero_run(encode_4b5b(f"{a:04b}{b:04b}")) for a in range(16) for b in range(16))
print(f"Over every pair of nibbles, the longest run of zeros in the 4B/5B stream is {worst} (so a 1 appears at least every 4 bits).")
assert worst == 3 and len(set(FOURB_FIVEB.values())) == 16
print("Efficiency: 4 data bits per 5 line bits = 80%. Manchester = 50%. The 32-16 = 16 unused 5-bit codes are used as control symbols or are invalid.")
print("check: OK")


# ===== SECTION 5: WORKED EXAMPLE =====
print("\n===== SECTION 5: WORKED EXAMPLE =====")
bits = "01001110"
print(f"Encode {bits} with NRZ-I (start low), Manchester (1 = low->high) and AMI:")
for name, fn in [("NRZ-I", nrz_i), ("Manchester", manchester), ("AMI", ami)]:
    print(f"  {name:<11}{sym(fn(bits))}")
print("NRZ-I by hand: start - ; bit0=0 stay -; bit1=1 flip +; bit2=0 +; bit3=0 +; bit4=1 flip -; bit5=1 flip +; bit6=1 flip -; bit7=0 -")
assert nrz_i(bits)[::2] == [-1, +1, +1, +1, -1, +1, -1, -1]
print("AMI by hand: 0->0, then ones alternate +,-,+,- : 0 + 0 0 - + - 0")
assert ami(bits)[::2] == [0, 1, 0, 0, -1, 1, -1, 0]
print("check: OK")
