# Tags: #Python #ComputerNetworks #DataLinkLayer #CyclicRedundancyCheck | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Cyclic Redundancy Check: modulo-2 polynomial division on bit strings,
appended zeros, remainder, verification, burst-error detection, and a bitwise
CRC-32 cross-checked against zlib.crc32. Implements the CRC part of the
Data Link chapter."""
import random
import zlib

# ===== SECTION 1: MODULO-2 DIVISION BY HAND =====
print("===== SECTION 1: MODULO-2 DIVISION (textbook example) =====")


def mod2_div(dividend: str, gen: str, show: bool = False) -> str:
    """Return the remainder (len(gen)-1 bits) of dividend / gen using XOR."""
    r = len(gen) - 1
    work = list(dividend)
    for i in range(len(dividend) - r):
        if work[i] == "1":
            before = "".join(work[i:i + len(gen)])
            for j in range(len(gen)):
                work[i + j] = str(int(work[i + j]) ^ int(gen[j]))
            if show:
                print(f"  {' ' * i}{before}")
                print(f"  {' ' * i}{gen}  (XOR)")
        elif show:
            print(f"  {' ' * i}(bit {i} is 0: no subtraction)")
    return "".join(work[-r:])


data, gen = "100100", "1101"  # G(x) = x^3 + x^2 + 1
r = len(gen) - 1
print(f"data = {data}, generator = {gen} (x^3 + x^2 + 1), r = {r}")
padded = data + "0" * r
print("append r zeros ->", padded)
rem = mod2_div(padded, gen, show=True)
print("remainder (CRC) =", rem)
frame = data + rem
print("transmitted frame = data + CRC =", frame)
print("receiver remainder on clean frame:", mod2_div(frame, gen), "(all zeros = accept)")
assert mod2_div(frame, gen) == "0" * r and rem == "001"
print("textbook answer 001: check: OK")

# ===== SECTION 2: ERRORS AND THE UNDETECTABLE PATTERN =====
print("\n===== SECTION 2: ERRORS AND THE UNDETECTABLE PATTERN =====")


def xor(a: str, b: str) -> str:
    return "".join("1" if x != y else "0" for x, y in zip(a, b))


def accepted(received: str) -> bool:
    return mod2_div(received, gen) == "0" * r


bad = xor(frame, "000010000")
print("one bit flipped :", bad, "accepted?", accepted(bad))
print("burst of 3 bits :", xor(frame, "000111000"), "accepted?", accepted(xor(frame, "000111000")))
E = "000" + gen + "00"  # error pattern equal to the generator itself
print("TRAP error = generator pattern", E, "->", xor(frame, E),
      "accepted?", accepted(xor(frame, E)), "(MISSED: E(x) is a multiple of G(x))")
n = len(frame)
missed = 0
total = 0
for length in range(1, r + 1):  # every burst of length <= r
    for start in range(n - length + 1):
        for mid in range(2 ** max(length - 2, 0)):
            if length == 1:
                pat = "1"
            elif length == 2:
                pat = "11"
            else:  # a burst starts and ends with 1; the middle is arbitrary
                pat = "1" + format(mid, f"0{length - 2}b") + "1"
            e = "0" * start + pat + "0" * (n - start - length)
            total += 1
            missed += accepted(xor(frame, e))
print(f"all {total} bursts of length <= {r} in a {n}-bit frame: missed {missed}")
assert missed == 0
print("CRC with r check bits detects every burst of length <= r: check: OK")
allmiss = sum(accepted(xor(frame, format(e, f"0{n}b"))) for e in range(1, 2 ** n))
print(f"exhaustive: of {2**n - 1} nonzero error patterns, {allmiss} are missed"
      f" (= {allmiss}/{2**n - 1}, about 1 in 2^r = 1/{2**r})")

# ===== SECTION 3: WRONG-POLYNOMIAL AND MISSING-ZEROS TRAPS =====
print("\n===== SECTION 3: TRAPS =====")
skipped = mod2_div(data, gen)  # divided WITHOUT appending r zeros
print("TRAP forgot to append zeros: remainder computed on bare data =", skipped)
print("  frame", data + skipped, "accepted by receiver?", accepted(data + skipped),
      "(correct CRC is", rem + ")")
print("  correct frame", frame, "accepted?", accepted(frame))
other = "1011"  # x^3 + x + 1, a different generator
print("TRAP receiver uses a different generator 1011 on frame", frame, "->",
      mod2_div(frame, other), "(nonzero: good frame REJECTED)")
print("Sender and receiver must agree on G(x), width and conventions.")

# ===== SECTION 4: CRC-32 BITWISE VS zlib =====
print("\n===== SECTION 4: CRC-32 BITWISE VS zlib.crc32 =====")
POLY_REFLECTED = 0xEDB88320  # 0x04C11DB7 bit-reversed (IEEE 802.3, zip, png)


def crc32_bitwise(buf: bytes) -> int:
    crc = 0xFFFFFFFF  # init all ones
    for byte in buf:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ POLY_REFLECTED if crc & 1 else crc >> 1
    return crc ^ 0xFFFFFFFF  # final xor


for text in [b"", b"a", b"123456789", b"hello world"]:
    mine, lib = crc32_bitwise(text), zlib.crc32(text)
    print(f"{text!r:<16} mine={mine:08x} zlib={lib:08x} {'OK' if mine == lib else 'DIFF'}")
    assert mine == lib
assert crc32_bitwise(b"123456789") == 0xCBF43926
print("standard CRC-32 check value for '123456789' is cbf43926: check: OK")
rng = random.Random(11)
for _ in range(200):
    blob = bytes(rng.randrange(256) for _ in range(rng.randint(0, 64)))
    assert crc32_bitwise(blob) == zlib.crc32(blob)
print("200 random buffers agree with zlib: check: OK")

# ===== SECTION 5: CRC-32 BURST DETECTION =====
print("\n===== SECTION 5: CRC-32 BURST DETECTION (seeded measurement) =====")
payload = bytes(rng.randrange(256) for _ in range(100))
good = zlib.crc32(payload)
missed32 = 0
for _ in range(5000):
    blen = rng.randint(1, 32)
    start = rng.randrange(len(payload) * 8 - blen)
    pat = (1 << (blen - 1)) | rng.getrandbits(blen - 1) | 1 if blen > 1 else 1
    big = int.from_bytes(payload, "big") ^ (pat << (len(payload) * 8 - start - blen))
    bad_pl = big.to_bytes(len(payload), "big")
    missed32 += zlib.crc32(bad_pl) == good
print("5000 random bursts of length 1..32 in 100 bytes: missed", missed32)
print("Theory: all bursts <= 32 bits are detected; longer ones slip through ~1 in 2^32.")
