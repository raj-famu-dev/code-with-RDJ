# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Error detection basics: single parity bit, 2D parity, and the Internet
checksum (RFC 1071, one's complement sum). Shows which errors each one misses.
Implements the 'error detection' part of the Data Link chapter."""
import random

# ===== SECTION 1: SINGLE PARITY BIT =====
print("===== SECTION 1: SINGLE PARITY BIT =====")


def even_parity_bit(bits: str) -> str:
    """Return the bit that makes the total number of 1s even."""
    return str(bits.count("1") % 2)


def check_even(codeword: str) -> bool:
    return codeword.count("1") % 2 == 0


data = "1011001"
cw = data + even_parity_bit(data)
print(f"data {data} has {data.count('1')} ones -> parity bit {cw[-1]} -> codeword {cw}")
print("receiver check on clean codeword:", check_even(cw))


def flip(bits: str, *positions: int) -> str:
    b = list(bits)
    for p in positions:
        b[p] = "1" if b[p] == "0" else "0"
    return "".join(b)


for pos in [(2,), (0, 5), (1, 3, 6)]:
    bad = flip(cw, *pos)
    verdict = "DETECTED" if not check_even(bad) else "MISSED"
    print(f"flip bits {pos}: {bad}  -> {verdict}")
print("Rule: single parity catches every ODD number of flips, misses every EVEN number.")

# ===== SECTION 2: 2D (BLOCK) PARITY =====
print("\n===== SECTION 2: 2D PARITY =====")
rows = ["1011001", "0110100", "1110011", "0001010"]


def build_2d(rows: list[str]) -> list[str]:
    body = [r + even_parity_bit(r) for r in rows]
    cols = "".join(even_parity_bit("".join(r[i] for r in body))
                   for i in range(len(body[0])))
    return body + [cols]


def locate_errors(grid: list[str]) -> tuple[list[int], list[int]]:
    bad_rows = [i for i, r in enumerate(grid) if r.count("1") % 2]
    bad_cols = [j for j in range(len(grid[0]))
                if sum(r[j] == "1" for r in grid) % 2]
    return bad_rows, bad_cols


grid = build_2d(rows)
print("block with row parity (last column) and column parity (last row):")
for r in grid:
    print("  ", r[:-1], r[-1])
print("clean check:", locate_errors(grid))


def flip_cells(grid: list[str], cells: list[tuple[int, int]]) -> list[str]:
    g = [list(r) for r in grid]
    for r, c in cells:
        g[r][c] = "1" if g[r][c] == "0" else "0"
    return ["".join(r) for r in g]


one = flip_cells(grid, [(1, 2)])
br, bc = locate_errors(one)
print(f"single flip at (1,2): bad rows {br}, bad cols {bc} -> intersection is the error;"
      " flip it back to CORRECT")
fixed = flip_cells(one, [(br[0], bc[0])])
assert fixed == grid
print("single-bit correction: check: OK")
three = flip_cells(grid, [(0, 0), (0, 1), (2, 3)])
print("3 flips ->", locate_errors(three), "(always detected: any 1, 2 or 3 errors)")
rect = flip_cells(grid, [(0, 0), (0, 3), (2, 0), (2, 3)])
print("TRAP rectangle of 4 flips at rows 0,2 x cols 0,3 ->", locate_errors(rect),
      "(empty = MISSED)")

# ===== SECTION 3: INTERNET CHECKSUM (RFC 1071) =====
print("\n===== SECTION 3: INTERNET CHECKSUM =====")


def ones_complement_sum16(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"  # pad odd length with a zero byte
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i + 1]
        total = (total & 0xFFFF) + (total >> 16)  # end-around carry
    return total


def internet_checksum(data: bytes) -> int:
    return ~ones_complement_sum16(data) & 0xFFFF


# The 8 bytes used as the worked example in RFC 1071 section 3.
rfc = bytes.fromhex("0001f203f4f5f6f7")
words = [int.from_bytes(rfc[i:i + 2], "big") for i in range(0, 8, 2)]
print("words :", [f"{w:04x}" for w in words])
print("sum   :", f"{sum(words):05x}", "-> fold carry ->", f"{ones_complement_sum16(rfc):04x}")
ck = internet_checksum(rfc)
print("checksum (complement):", f"{ck:04x}")
assert ones_complement_sum16(rfc) == 0xDDF2 and ck == 0x220D
print("matches RFC 1071 (sum ddf2): check: OK")
verify = rfc + ck.to_bytes(2, "big")
print("receiver: sum(data + checksum) =", f"{ones_complement_sum16(verify):04x}",
      "(all ones = valid)")
assert ones_complement_sum16(verify) == 0xFFFF

# exam style: 4-bit words with wraparound
w4 = [0b0110, 0b1101, 0b1011, 0b0111]
s = 0
for w in w4:
    s += w
    s = (s & 0xF) + (s >> 4)
print("4-bit exam example words 0110 1101 1011 0111 -> wrapped sum",
      format(s, "04b"), "checksum", format(~s & 0xF, "04b"))

# ===== SECTION 4: WHAT THE CHECKSUM MISSES =====
print("\n===== SECTION 4: WHAT THE CHECKSUM MISSES =====")
msg = b"HELLO WORLD!"
base = internet_checksum(msg)
print("original", msg, f"checksum {base:04x}")
swapped = msg[2:4] + msg[0:2] + msg[4:]
print("TRAP swap two 16-bit words :", swapped, f"{internet_checksum(swapped):04x}",
      "MISSED" if internet_checksum(swapped) == base else "detected")
m = bytearray(msg)
m[1] += 1  # +1 in word 0 (low byte)
m[3] -= 1  # -1 in word 1 (low byte)
print("TRAP +1 here, -1 there     :", bytes(m), f"{internet_checksum(bytes(m)):04x}",
      "MISSED" if internet_checksum(bytes(m)) == base else "detected")
z = msg + b"\x00\x00"
print("TRAP append zero words     :", f"{internet_checksum(z):04x}",
      "MISSED" if internet_checksum(z) == base else "detected")
one_bit = bytearray(msg)
one_bit[5] ^= 0x04
print("single bit flip            :", f"{internet_checksum(bytes(one_bit)):04x}",
      "MISSED" if internet_checksum(bytes(one_bit)) == base else "detected")

# ===== SECTION 5: MEASURED DETECTION RATE (seeded) =====
print("\n===== SECTION 5: MEASURED DETECTION RATE (seeded measurement) =====")
rng = random.Random(2024)
trials, miss_par, miss_ck = 20000, 0, 0
for _ in range(trials):
    d = "".join(rng.choice("01") for _ in range(16))
    c = d + even_parity_bit(d)
    k = rng.choice([2, 4])  # even number of flips
    if check_even(flip(c, *rng.sample(range(len(c)), k))):
        miss_par += 1
    raw = bytes(rng.randrange(256) for _ in range(16))
    bad = bytearray(raw)
    for p in rng.sample(range(128), 3):  # 3 random bit flips
        bad[p // 8] ^= 1 << (p % 8)
    if internet_checksum(bytes(bad)) == internet_checksum(raw):
        miss_ck += 1
print(f"parity, random 2 or 4 flips : missed {miss_par}/{trials}")
print(f"checksum, random 3 flips    : missed {miss_ck}/{trials}")
print("(measurement with seed 2024; parity misses all even flips by construction)")
