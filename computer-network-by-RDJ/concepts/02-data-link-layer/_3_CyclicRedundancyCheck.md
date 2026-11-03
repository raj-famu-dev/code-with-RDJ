# `_3_CyclicRedundancyCheck.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A cyclic redundancy check (CRC) treats the frame as one huge binary polynomial, divides it by an agreed generator polynomial using modulo-2 arithmetic, and sends the remainder as extra bits. The receiver divides again; a nonzero remainder means the frame was damaged. CRCs catch burst errors far better than parity or checksums and are cheap in hardware, so Ethernet, Wi-Fi, HDLC, PPP, USB and storage all use them.

**Procedure (sender).** Pick a generator G(x) of degree r (r+1 bits, highest and lowest bit 1). (1) Append r zeros to the data. (2) Divide by G using modulo-2 division, which is XOR with no borrows. (3) The r-bit remainder is the CRC. (4) Transmit data followed by the CRC. This is the same as sending T(x) = D(x)*x^r + R(x), which is exactly divisible by G(x).

**Procedure (receiver).** Divide the whole received frame by G. A zero remainder means accept; anything else means reject.

**Mod-2 division by hand.** Line up G under the leftmost 1 of the current bits, XOR, drop the leading zero, bring down the next bit. If the leading bit is 0, do not XOR, just shift. Exam example: data `100100`, G = `1101` (x^3 + x^2 + 1), r = 3, padded data `100100000`, remainder `001`, transmitted `100100001`.

**What a CRC detects.** If E(x) is the error pattern, the receiver sees T(x) + E(x) and the remainder is E(x) mod G(x). Detection fails only if G(x) divides E(x). Consequences: all single-bit errors if G has at least two terms; all double errors for suitable G; all odd numbers of errors if G has the factor (x+1); every burst of length up to r; bursts of length r+1 are missed with probability 2^-(r-1) and longer ones with probability about 2^-r. The unavoidable undetected pattern: any E(x) that is a multiple of G(x), including G(x) itself.

| Name | Width | Generator (hex, normal form) | Typical use |
|---|---|---|---|
| CRC-16-CCITT | 16 | 0x1021 | HDLC/X.25 (as reflected variant), others |
| CRC-32 | 32 | 0x04C11DB7 | Ethernet FCS, zip, PNG |

Real implementations add conventions that must match on both ends: bit reflection (least significant bit first), initial register value (all ones for CRC-32), and a final XOR (all ones). The reflected form of CRC-32's polynomial is `0xEDB88320`, the constant used in the code.

## Full Line-by-Line Breakdown

### SECTION 1: MODULO-2 DIVISION (textbook example)
`mod2_div` implements the paper method on strings: whenever the leading bit is 1 it XORs the generator in place, otherwise it just shifts. With `show=True` it prints each XOR step. For data `100100` and `1101` it appends three zeros, divides, and gets remainder `001`, matching the textbook answer. The receiver divides the transmitted frame `100100001` and gets `000`.

Output from a real run:

```text
===== SECTION 1: MODULO-2 DIVISION (textbook example) =====
data = 100100, generator = 1101 (x^3 + x^2 + 1), r = 3
append r zeros -> 100100000
  1001
  1101  (XOR)
   1000
   1101  (XOR)
    1010
    1101  (XOR)
     1110
     1101  (XOR)
      (bit 4 is 0: no subtraction)
       1100
       1101  (XOR)
remainder (CRC) = 001
transmitted frame = data + CRC = 100100001
receiver remainder on clean frame: 000 (all zeros = accept)
textbook answer 001: check: OK
```

### SECTION 2: ERRORS AND THE UNDETECTABLE PATTERN
Single-bit and 3-bit-burst errors are rejected. The trap error pattern `000110100` is equal to the generator itself (shifted), so the frame XOR error is still divisible by G and is ACCEPTED (missed). An exhaustive loop tries every burst of length up to 3 in the 9-bit frame (31 bursts): none missed. A second exhaustive loop tries all 511 nonzero error patterns: 63 are missed, which is 2^(9-3)-1, about 1 in 2^r = 1/8, the error patterns that are nonzero multiples of G.

Output from a real run:

```text
===== SECTION 2: ERRORS AND THE UNDETECTABLE PATTERN =====
one bit flipped : 100110001 accepted? False
burst of 3 bits : 100011001 accepted? False
TRAP error = generator pattern 000110100 -> 100010101 accepted? True (MISSED: E(x) is a multiple of G(x))
all 31 bursts of length <= 3 in a 9-bit frame: missed 0
CRC with r check bits detects every burst of length <= r: check: OK
exhaustive: of 511 nonzero error patterns, 63 are missed (= 63/511, about 1 in 2^r = 1/8)
```

### SECTION 3: TRAPS
Two implementation traps. First, forgetting to append r zeros: dividing bare data gives the wrong CRC (`111` instead of `001`) and the receiver rejects that frame. Second, a receiver using another generator (`1011`) rejects a perfectly good frame. Both sides must agree on G and on the conventions.

Output from a real run:

```text
===== SECTION 3: TRAPS =====
TRAP forgot to append zeros: remainder computed on bare data = 111
  frame 100100111 accepted by receiver? False (correct CRC is 001)
  correct frame 100100001 accepted? True
TRAP receiver uses a different generator 1011 on frame 100100001 -> 100 (nonzero: good frame REJECTED)
Sender and receiver must agree on G(x), width and conventions.
```

### SECTION 4: CRC-32 BITWISE VS zlib.crc32
`crc32_bitwise` is the standard reflected algorithm: start the register at all ones, XOR each byte in, shift right eight times applying `0xEDB88320` when a 1 falls out, then XOR with all ones at the end. It is compared with `zlib.crc32` for empty data, `a`, `123456789`, `hello world` and 200 random buffers. The well known check value for `123456789` is `0xcbf43926`.

Output from a real run:

```text
===== SECTION 4: CRC-32 BITWISE VS zlib.crc32 =====
b''              mine=00000000 zlib=00000000 OK
b'a'             mine=e8b7be43 zlib=e8b7be43 OK
b'123456789'     mine=cbf43926 zlib=cbf43926 OK
b'hello world'   mine=0d4a1185 zlib=0d4a1185 OK
standard CRC-32 check value for '123456789' is cbf43926: check: OK
200 random buffers agree with zlib: check: OK
```

### SECTION 5: CRC-32 BURST DETECTION (seeded measurement)
A seeded measurement: 5000 random bursts of length 1 to 32 bits are injected into a 100-byte payload and zlib's CRC-32 compares. Zero are missed, consistent with the guarantee that CRC-32 detects every burst up to 32 bits. The printed theory line states the miss rate for longer bursts; that figure is theory, not something this script measures.

Output from a real run:

```text
===== SECTION 5: CRC-32 BURST DETECTION (seeded measurement) =====
5000 random bursts of length 1..32 in 100 bytes: missed 0
Theory: all bursts <= 32 bits are detected; longer ones slip through ~1 in 2^32.
```

## Worked Example
**Problem.** Data `100100`, G(x) = x^3 + x^2 + 1. Find the transmitted frame.

**Solution.** G is `1101`, r = 3. Append three zeros: `100100000`. Divide: XOR `1001` with `1101` gives `0100`; continue bringing bits down, XOR whenever the leading bit is 1. The steps in the program output end with remainder `001`. Transmit `100100` followed by `001`, that is `100100001`. Receiver check: dividing `100100001` by `1101` leaves `000`, so accept. The code prints the same remainder and asserts it.

## Key Rules / Gotchas Recap
- Append r zeros BEFORE dividing; transmit data + remainder (not the zeros).
- Division is XOR without borrow; zero remainder at the receiver means accept.
- CRC with r check bits detects every burst of length <= r.
- Errors that are multiples of G(x) are always missed, including G itself.
- Sender and receiver must agree on polynomial, width, reflection, init and final XOR.
- CRC-32 reflected polynomial constant: 0xEDB88320; check value for '123456789' is 0xCBF43926.
- A CRC detects accidental errors only; it gives no protection against a deliberate attacker.

## Why This Matters
CRCs guard every Ethernet frame, every zip and PNG file, and storage blocks. When you debug corrupted data, knowing that the CRC is a polynomial remainder, and that it is not a security hash, tells you what it can and cannot prove.
