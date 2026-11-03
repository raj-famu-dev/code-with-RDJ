# Tags: #Python #ComputerNetworks #DataLinkLayer #DataLinkLayerFraming | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Data link layer services and framing: character count, byte stuffing, bit
stuffing with flag 01111110, and physical-layer coding violations.
Implements the framing part of the Data Link chapter of a CN syllabus."""
import random

# ===== SECTION 1: DATA LINK LAYER SERVICES =====
print("===== SECTION 1: DATA LINK LAYER SERVICES =====")
services = [
    ("Framing", "wrap packets into frames with start/end boundaries"),
    ("Physical addressing", "MAC address of next hop in the frame header"),
    ("Error control", "detect (CRC, checksum) or correct (Hamming) errors"),
    ("Flow control", "stop a fast sender swamping a slow receiver"),
    ("Access control", "decide who may use a shared medium (MAC sublayer)"),
]
for name, what in services:
    print(f"  {name:<20} {what}")

# ===== SECTION 2: CHARACTER COUNT FRAMING + ITS TRAP =====
print("\n===== SECTION 2: CHARACTER COUNT FRAMING =====")


def count_frame(payloads: list[bytes]) -> bytes:
    """Each frame starts with one byte = total length including that byte."""
    return b"".join(bytes([len(p) + 1]) + p for p in payloads)


def count_parse(stream: bytes) -> list[bytes]:
    out, i = [], 0
    while i < len(stream):
        n = stream[i]
        out.append(stream[i + 1:i + n])
        i += n
    return out


frames = [b"ABCD", b"EF", b"GHI"]
wire = count_frame(frames)
print("frames      :", frames)
print("on the wire :", list(wire))
print("parsed back :", count_parse(wire))
assert count_parse(wire) == frames
bad = bytearray(wire)
bad[0] ^= 0x01  # flip one bit in the first count: 5 -> 4
print("TRAP: one bit error in first count (5 -> 4):", count_parse(bytes(bad)))
print("  every later frame boundary is wrong; the receiver cannot resync.")

# ===== SECTION 3: BYTE STUFFING (FLAG + ESC) =====
print("\n===== SECTION 3: BYTE STUFFING =====")
FLAG, ESC = 0x7E, 0x7D  # PPP-style: FLAG '~', ESC '}'


def byte_stuff(data: bytes) -> bytes:
    out = bytearray([FLAG])
    for b in data:
        if b in (FLAG, ESC):
            out.append(ESC)
        out.append(b)
    out.append(FLAG)
    return bytes(out)


def byte_unstuff(frame: bytes) -> bytes:
    assert frame[0] == FLAG and frame[-1] == FLAG
    out, esc = bytearray(), False
    for b in frame[1:-1]:
        if esc:
            out.append(b)
            esc = False
        elif b == ESC:
            esc = True
        else:
            out.append(b)
    return bytes(out)


data = bytes([0x41, FLAG, 0x42, ESC, 0x43])
print("data   :", data.hex(" "))


def naive(data: bytes) -> bytes:
    return bytes([FLAG]) + data + bytes([FLAG])


nv = naive(data)
print("TRAP naive framing:", nv.hex(" "))
print("  receiver sees", nv.count(FLAG), "flags -> splits into",
      [p.hex() for p in nv.split(bytes([FLAG])) if p], "(frame cut short)")
st = byte_stuff(data)
print("stuffed:", st.hex(" "))
print("unstuff:", byte_unstuff(st).hex(" "))
assert byte_unstuff(st) == data
print("byte stuffing round-trip: check: OK")

# ===== SECTION 4: BIT STUFFING (FLAG 01111110) =====
print("\n===== SECTION 4: BIT STUFFING =====")
FLAG_BITS = "01111110"


def bit_stuff(bits: str) -> str:
    """After five consecutive 1s insert a 0."""
    out, ones = [], 0
    for b in bits:
        out.append(b)
        ones = ones + 1 if b == "1" else 0
        if ones == 5:
            out.append("0")
            ones = 0
    return "".join(out)


def bit_unstuff(bits: str) -> str:
    """After five consecutive 1s remove the following 0."""
    out, ones, i = [], 0, 0
    while i < len(bits):
        b = bits[i]
        out.append(b)
        ones = ones + 1 if b == "1" else 0
        if ones == 5:
            i += 1  # skip the stuffed 0
            ones = 0
        i += 1
    return "".join(out)


payload = "10011111100111111111100"
print("payload       :", payload)
print("TRAP unstuffed frame:", FLAG_BITS + payload + FLAG_BITS)
print("  flag pattern hidden inside the data?", FLAG_BITS in payload,
      "-> receiver would end the frame early")
s = bit_stuff(payload)
print("stuffed       :", s)
print("stuffed frame :", FLAG_BITS + s + FLAG_BITS)
print("flag appears inside stuffed body?", FLAG_BITS in s)
print("unstuffed     :", bit_unstuff(s))
assert bit_unstuff(s) == payload
assert FLAG_BITS not in s
rng = random.Random(7)
for _ in range(2000):
    p = "".join(rng.choice("01") for _ in range(rng.randint(1, 60)))
    q = bit_stuff(p)
    assert bit_unstuff(q) == p and FLAG_BITS not in q
print("2000 random payloads round-trip and never contain the flag: check: OK")
worst = "1" * 20
print(f"worst case {worst} -> {bit_stuff(worst)} (overhead 1 bit per 5)")

# ===== SECTION 5: PHYSICAL LAYER CODING VIOLATIONS =====
print("\n===== SECTION 5: PHYSICAL LAYER CODING VIOLATIONS =====")
# Manchester (IEEE 802.3): 1 = low->high, 0 = high->low, so EVERY bit has a
# mid-bit transition. Two half-bit levels per bit: HL / LH are legal; HH / LL
# never occur in data, so they can mark frame start/end.
MAN = {"1": "LH", "0": "HL"}


def manchester(bits: str) -> str:
    return " ".join(MAN[b] for b in bits)


print("bits 1 0 1 1 ->", manchester("1011"))
print("start delimiter uses illegal pairs, e.g. 'HH LL' (no mid-bit transition)")
line = "LH HL HH LL LH"
pairs = line.split()
legal = {"LH", "HL"}
print("line signal :", line)
print("violations at positions:", [i for i, p in enumerate(pairs) if p not in legal])
print("Cost: needs a physical layer with spare symbols; 4B/5B etc. do the same.")

# ===== SECTION 6: COMPARISON =====
print("\n===== SECTION 6: COMPARISON =====")
print(f"{'method':<16}{'overhead':<22}{'weakness'}")
print(f"{'char count':<16}{'1 byte/frame':<22}{'one error loses sync'}")
print(f"{'byte stuffing':<16}{'ESC per FLAG/ESC':<22}{'byte oriented only'}")
print(f"{'bit stuffing':<16}{'1 bit per 5 ones':<22}{'variable length output'}")
print(f"{'coding viol.':<16}{'none (bits)':<22}{'needs spare symbols'}")
