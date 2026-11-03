# `_4_HammingCode.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A Hamming code is an error-correcting code: it adds just enough parity bits to a data word that the receiver can compute which single bit is wrong and flip it back, with no retransmission. It matters where retransmission is impossible or costly, such as memory (ECC RAM), satellite and storage.

**How many redundancy bits?** For m data bits and r parity bits, the r bits must be able to name any of the m + r bit positions or "no error": `2^r >= m + r + 1`. Examples: m = 4 needs r = 3 (7,4 code); m = 7 needs r = 4 (11 bits total); m = 11 needs r = 4 (15,11 code).

**Where the parity bits go.** Number positions from 1. Parity bits sit at positions that are powers of two (1, 2, 4, 8...); data bits fill the other positions. Parity bit P_k (at position 2^k) covers every position whose binary index has bit k set. So P1 covers 1,3,5,7,9,11...; P2 covers 2,3,6,7,10,11...; P4 covers 4,5,6,7,12...; P8 covers 8-15. With even parity each group must contain an even number of 1s.

**Decoding by syndrome.** Recompute each parity check; write the failed checks as a binary number (P8 P4 P2 P1). That number, the syndrome, is the position of the flipped bit (0 means no error). Flip it back. A neat equivalent: the XOR of the positions of all 1 bits is the syndrome.

**Hamming distance.** The Hamming distance between two words is the number of positions in which they differ. The minimum distance d of a code decides its power: it detects up to d-1 errors and corrects up to floor((d-1)/2). Hamming codes have d = 3: correct 1, detect 2 (but cannot tell the two cases apart).

**SEC-DED.** Add one overall parity bit across the whole codeword to reach d = 4: single-error correct, double-error detect. Decode: syndrome 0 and overall OK = no error; overall parity wrong = single error (correct it, syndrome 0 means the overall bit itself); syndrome nonzero and overall OK = double error, report uncorrectable.

| Code | d | Corrects | Detects |
|---|---|---|---|
| Single parity | 2 | 0 | 1 |
| Hamming (7,4) | 3 | 1 | 2 |
| SEC-DED (8,4) | 4 | 1 | 2 (and corrects 1) |

## Full Line-by-Line Breakdown

### SECTION 1: REDUNDANCY BITS FORMULA 2^r >= m + r + 1
`redundancy_bits` finds the smallest r with 2^r >= m + r + 1 and prints a table for common m. The asserts confirm the textbook (7,4) and (15,11) codes.

Output from a real run:

```text
===== SECTION 1: REDUNDANCY BITS FORMULA 2^r >= m + r + 1 =====
   m   r  total n
   1   2        3
   4   3        7
   7   4       11
   8   4       12
  11   4       15
  16   5       21
  26   5       31
  57   6       63
  64   7       71
m=4 -> (7,4) code; m=11 -> (15,11) code: check: OK
```

### SECTION 2: ENCODING (even parity)
`encode` places data in the non-power-of-two positions and computes each parity bit as the XOR of the covered positions. For data `1011001` it builds an 11-bit word and prints which positions each parity bit covers and that every group has an even number of 1s.

Output from a real run:

```text
===== SECTION 2: ENCODING (even parity) =====
data: 1011001 -> codeword length 11
pos :  1  2  3  4  5  6  7  8  9 10 11
bit :  1  0  1  0  0  1  1  1  0  0  1
  P1 covers positions [1, 3, 5, 7, 9, 11] -> bits 110101 (4 ones, even)
  P2 covers positions [2, 3, 6, 7, 10, 11] -> bits 011101 (4 ones, even)
  P4 covers positions [4, 5, 6, 7] -> bits 0011 (2 ones, even)
  P8 covers positions [8, 9, 10, 11] -> bits 1001 (2 ones, even)
```

### SECTION 3: INJECT ERROR, LOCATE, CORRECT
`syndrome` XORs the positions of all 1 bits; for a valid word it is 0. A loop flips each of the 11 positions in turn and checks that the syndrome equals the flipped position and the correction restores the word (asserted). The shown example flips bit 6: the syndrome is `0110` = 6, the code flips position 6 back and extracts the data.

Output from a real run:

```text
===== SECTION 3: INJECT ERROR, LOCATE, CORRECT =====
sent     : 10100111001 syndrome 0
received : 10100011001 (bit 6 flipped)
syndrome : 0110 = 6 -> error is at position 6
corrected: 10100111001 data: 1011001
all 11 single-bit errors located and corrected: check: OK
```

### SECTION 4: HAMMING DISTANCE
`dist` counts differing positions. Over all 16 codewords of the (7,4) code the minimum distance is 3. The trap injects two errors: the syndrome now points to a third, innocent position, the decoder changes a good bit and the extracted data is wrong without any alarm. Single-error-correcting codes silently miscorrect double errors.

Output from a real run:

```text
===== SECTION 4: HAMMING DISTANCE =====
(7,4) code has 16 codewords; minimum distance d = 3
detect up to d-1 = 2 errors, correct up to (d-1)//2 = 1
example: distance(1011001, 0011010) = 3
TRAP two errors: a 2-bit error is 'corrected' to the WRONG codeword
  sent 0110011 got 1110111 -> 'fixed' to 1111111 (syndrome 4 )
  decoded data 1111 != 1011: silent corruption
```

### SECTION 5: SEC-DED (extended Hamming)
`secded_encode` appends an overall parity bit. The decoder uses both the syndrome and the overall parity: a single flip is corrected (also if the flipped bit is the overall parity bit itself), and two flips are reported as a double error that cannot be corrected.

Output from a real run:

```text
===== SECTION 5: SEC-DED (extended Hamming) =====
codeword (8 bits): 01100110
no error      : no error
1 flip (pos 3): single error -> corrected (position 3)
1 flip (parity): single error -> corrected (position overall parity bit)
2 flips       : DOUBLE error detected (cannot correct)
SEC-DED corrects 1 error and detects 2 (distance 4); used in ECC memory.
```

## Worked Example
**Problem.** Encode data `1011001` with an even-parity Hamming code, then flip bit 6 and find it.

**Solution.** m = 7, so r = 4 (2^4 = 16 >= 7+4+1 = 12). Positions 1,2,4,8 are parity: data goes in positions 3,5,6,7,9,10,11 = 1,0,1,1,0,0,1. P1 covers positions 3,5,7,9,11 (data bits 1,0,1,0,1: three 1s), so P1 = 1 to make it even. P2 covers 3,6,7,10,11 holding 1,1,1,0,1 (four 1s, already even) so P2 = 0; P4 covers 5,6,7 holding 0,1,1 so P4 = 0; P8 covers 9,10,11 holding 0,0,1 so P8 = 1. The codeword is `10100111001`. Flip position 6 to get `10100011001`; the XOR of 1-positions equals 6 (`0110`), so flip position 6 back. The code prints the same syndrome 6 and the corrected word.

## Key Rules / Gotchas Recap
- 2^r >= m + r + 1.
- Parity bits live at power-of-two positions (1, 2, 4, 8...), counted from 1.
- Syndrome = position of the flipped bit; 0 = no error.
- Minimum distance d: detect d-1, correct (d-1)//2.
- Plain Hamming (d=3) turns a double error into a silent wrong correction; SEC-DED (d=4) detects it.
- Even vs odd parity must match on both sides.

## Why This Matters
ECC memory in servers and GPUs is SEC-DED, so understanding syndromes explains corrected-error counters in logs. The same ideas, extended, lead to Reed-Solomon and LDPC codes used in storage and wireless.
