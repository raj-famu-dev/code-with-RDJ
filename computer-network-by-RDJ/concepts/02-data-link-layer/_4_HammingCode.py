# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Hamming single-error-correcting code: redundancy bit formula, parity bits at
positions 2^k, encoding, syndrome decoding, Hamming distance, and the SEC-DED
extension with an overall parity bit. Implements the error-correction part of
the Data Link chapter."""
import itertools

# ===== SECTION 1: HOW MANY REDUNDANCY BITS? =====
print("===== SECTION 1: REDUNDANCY BITS FORMULA 2^r >= m + r + 1 =====")


def redundancy_bits(m: int) -> int:
    r = 0
    while 2 ** r < m + r + 1:
        r += 1
    return r


print(f"{'m':>4} {'r':>3} {'total n':>8}")
for m in [1, 4, 7, 8, 11, 16, 26, 57, 64]:
    r = redundancy_bits(m)
    print(f"{m:>4} {r:>3} {m + r:>8}")
assert redundancy_bits(4) == 3 and redundancy_bits(7) == 4 and redundancy_bits(11) == 4
print("m=4 -> (7,4) code; m=11 -> (15,11) code: check: OK")

# ===== SECTION 2: ENCODING A 7-BIT DATA WORD =====
print("\n===== SECTION 2: ENCODING (even parity) =====")


def encode(data: str) -> str:
    """Positions are numbered 1..n from the left. Positions 1,2,4,8.. are parity."""
    m = len(data)
    r = redundancy_bits(m)
    n = m + r
    word = [0] * (n + 1)  # index 0 unused
    it = iter(data)
    for pos in range(1, n + 1):
        if pos & (pos - 1):  # not a power of two -> data bit
            word[pos] = int(next(it))
    for k in range(r):
        p = 1 << k
        word[p] = sum(word[i] for i in range(1, n + 1) if i & p) % 2
    return "".join(map(str, word[1:]))


def explain(data: str) -> None:
    code = encode(data)
    n = len(code)
    print("data:", data, "-> codeword length", n)
    print("pos :", " ".join(f"{i:>2}" for i in range(1, n + 1)))
    print("bit :", " ".join(f" {b}" for b in code))
    k = 0
    while (1 << k) <= n:
        p = 1 << k
        covered = [i for i in range(1, n + 1) if i & p]
        ones = [code[i - 1] for i in covered]
        print(f"  P{p} covers positions {covered} -> bits {''.join(ones)}"
              f" ({ones.count('1')} ones, even)")
        k += 1


explain("1011001")

# ===== SECTION 3: SYNDROME DECODING =====
print("\n===== SECTION 3: INJECT ERROR, LOCATE, CORRECT =====")


def syndrome(code: str) -> int:
    s = 0
    for pos, b in enumerate(code, start=1):
        if b == "1":
            s ^= pos  # XOR of positions of 1s = failing-parity pattern
    return s


def correct(code: str) -> tuple[str, int]:
    s = syndrome(code)
    if s == 0:
        return code, 0
    c = list(code)
    c[s - 1] = "1" if c[s - 1] == "0" else "0"
    return "".join(c), s


def extract(code: str) -> str:
    return "".join(b for pos, b in enumerate(code, start=1) if pos & (pos - 1))


good = encode("1011001")
print("sent     :", good, "syndrome", syndrome(good))
for flip_pos in range(1, len(good) + 1):
    c = list(good)
    c[flip_pos - 1] = "1" if c[flip_pos - 1] == "0" else "0"
    fixed, s = correct("".join(c))
    assert s == flip_pos and fixed == good
bad = list(good)
bad[5] = "1" if bad[5] == "0" else "0"
bad_s = "".join(bad)
fixed, s = correct(bad_s)
print("received :", bad_s, "(bit 6 flipped)")
print("syndrome :", format(s, "04b"), "=", s, "-> error is at position", s)
print("corrected:", fixed, "data:", extract(fixed))
print("all", len(good), "single-bit errors located and corrected: check: OK")

# ===== SECTION 4: HAMMING DISTANCE =====
print("\n===== SECTION 4: HAMMING DISTANCE =====")


def dist(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


words = [encode(format(v, "04b")) for v in range(16)]
dmin = min(dist(a, b) for a, b in itertools.combinations(words, 2))
print("(7,4) code has", len(words), "codewords; minimum distance d =", dmin)
assert dmin == 3
print("detect up to d-1 =", dmin - 1, "errors, correct up to (d-1)//2 =", (dmin - 1) // 2)
print("example: distance(1011001, 0011010) =", dist("1011001", "0011010"))
print("TRAP two errors: a 2-bit error is 'corrected' to the WRONG codeword")
c = list(encode("1011"))
c[0] = "1" if c[0] == "0" else "0"
c[4] = "1" if c[4] == "0" else "0"
two = "".join(c)
fx, s = correct(two)
print("  sent", encode("1011"), "got", two, "-> 'fixed' to", fx, "(syndrome", s, ")")
print("  decoded data", extract(fx), "!= 1011: silent corruption")

# ===== SECTION 5: SEC-DED =====
print("\n===== SECTION 5: SEC-DED (extended Hamming) =====")


def secded_encode(data: str) -> str:
    h = encode(data)
    return h + str(h.count("1") % 2)  # overall even parity over everything


def secded_decode(word: str) -> str:
    h, overall = word[:-1], word.count("1") % 2
    s = syndrome(h)
    if s == 0 and overall == 0:
        return "no error"
    if overall == 1:
        return f"single error -> corrected (position {s if s else 'overall parity bit'})"
    return "DOUBLE error detected (cannot correct)"


w = secded_encode("1011")
print("codeword (8 bits):", w)


def flipw(word: str, *ps: int) -> str:
    c = list(word)
    for p in ps:
        c[p] = "1" if c[p] == "0" else "0"
    return "".join(c)


print("no error      :", secded_decode(w))
print("1 flip (pos 3):", secded_decode(flipw(w, 2)))
print("1 flip (parity):", secded_decode(flipw(w, 7)))
print("2 flips       :", secded_decode(flipw(w, 0, 4)))
print("SEC-DED corrects 1 error and detects 2 (distance 4); used in ECC memory.")
