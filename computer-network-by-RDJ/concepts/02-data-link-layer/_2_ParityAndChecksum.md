# `_2_ParityAndChecksum.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Error detection adds redundant bits so the receiver can tell whether a frame was damaged in transit. Parity bits, two-dimensional parity and the Internet checksum are the simple schemes; they are cheap but each misses some error patterns, which is why links use a CRC instead.

**Single (even) parity.** Append one bit so the total number of 1s is even (odd parity: odd). The receiver counts the 1s. It detects every odd number of flipped bits (1, 3, 5...) and misses every even number (2, 4...). Overhead is 1 bit per block; it cannot correct anything.

**Two-dimensional (block) parity.** Arrange data in rows, add a parity bit to each row and a parity row for the columns. A single-bit error makes exactly one row and one column fail, and their intersection is the bad bit, so 2D parity corrects one error and detects any 1, 2 or 3 errors. It misses a rectangle of four flips (same two rows, same two columns) because every row and column parity stays even.

**Internet checksum (RFC 1071).** Used in IP, ICMP, UDP and TCP. Treat the data as 16-bit words, add them with one's complement arithmetic (any carry out of bit 16 is added back in, called end-around carry), then complement the sum. The sender puts the result in the checksum field. The receiver adds all words including the checksum; the result must be all ones (`0xFFFF`). An odd-length message is padded with a zero byte for the calculation only. Exam style with k-bit words: add the words, wrap carries, complement.

| Scheme | Overhead | Always detects | Misses |
|---|---|---|---|
| Single parity | 1 bit | any odd number of bit errors | any even number of bit errors |
| 2D parity | r + c + 1 bits | 1, 2, 3 errors; corrects 1 | some patterns of 4 or more (rectangles) |
| Internet checksum | 16 bits | most single and burst errors | swapped 16-bit words, +x/-x compensating errors, inserted or deleted zero words |
| CRC (next file) | r bits | all bursts up to r bits | about 1 in 2^r random patterns |

Advantages of the checksum: very cheap in software. Disadvantage: weak against reordering and compensating errors, so link layers add a CRC while IP and TCP keep the checksum as an end-to-end safety net.

## Full Line-by-Line Breakdown

### SECTION 1: SINGLE PARITY BIT
`even_parity_bit` returns the bit that makes the count of 1s even. For `1011001` (four 1s) the parity bit is 0. The code flips one, two and three bits and checks the receiver. One flip and three flips are detected; the two-flip case is MISSED. Rule: odd flips caught, even flips missed.

Output from a real run:

```text
===== SECTION 1: SINGLE PARITY BIT =====
data 1011001 has 4 ones -> parity bit 0 -> codeword 10110010
receiver check on clean codeword: True
flip bits (2,): 10010010  -> DETECTED
flip bits (0, 5): 00110110  -> MISSED
flip bits (1, 3, 6): 11100000  -> DETECTED
Rule: single parity catches every ODD number of flips, misses every EVEN number.
```

### SECTION 2: 2D PARITY
`build_2d` appends a parity bit to each row and then builds a parity row from the columns. `locate_errors` lists the rows and columns with odd parity. A single flip at (1,2) shows up as bad row 1 and bad column 2; flipping that cell back corrects it (asserted). Three flips are still detected. The trap flips the four corners of a rectangle (rows 0 and 2, columns 0 and 3): every row and column still has even parity, so the list of bad rows and columns is empty and the error is missed.

Output from a real run:

```text
===== SECTION 2: 2D PARITY =====
block with row parity (last column) and column parity (last row):
   1011001 0
   0110100 1
   1110011 1
   0001010 0
   0010100 0
clean check: ([], [])
single flip at (1,2): bad rows [1], bad cols [2] -> intersection is the error; flip it back to CORRECT
single-bit correction: check: OK
3 flips -> ([2], [0, 1, 3]) (always detected: any 1, 2 or 3 errors)
TRAP rectangle of 4 flips at rows 0,2 x cols 0,3 -> ([], []) (empty = MISSED)
```

### SECTION 3: INTERNET CHECKSUM
`ones_complement_sum16` pads odd data with a zero byte, adds 16-bit words and folds the carry back in after every addition. The RFC 1071 section 3 example bytes `00 01 f2 03 f4 f5 f6 f7` sum to `0x2ddf0` before folding; folding the carry gives `0xddf2`, and the complement is `0x220d`. The code asserts both values. The receiver adds the data plus the checksum and gets `0xffff`, which means valid. A final 4-bit example shows the same wrap-around method for tiny words, the version most exams use.

Output from a real run:

```text
===== SECTION 3: INTERNET CHECKSUM =====
words : ['0001', 'f203', 'f4f5', 'f6f7']
sum   : 2ddf0 -> fold carry -> ddf2
checksum (complement): 220d
matches RFC 1071 (sum ddf2): check: OK
receiver: sum(data + checksum) = ffff (all ones = valid)
4-bit exam example words 0110 1101 1011 0111 -> wrapped sum 0111 checksum 1000
```

### SECTION 4: WHAT THE CHECKSUM MISSES
Three traps against `HELLO WORLD!`: swapping two 16-bit words gives the same sum (addition is commutative); adding 1 to one word and subtracting 1 from another keeps the sum; appending zero words adds nothing. A single bit flip changes the sum and is detected. These are the practical weaknesses of the checksum.

Output from a real run:

```text
===== SECTION 4: WHAT THE CHECKSUM MISSES =====
original b'HELLO WORLD!' checksum 2e91
TRAP swap two 16-bit words : b'LLHEO WORLD!' 2e91 MISSED
TRAP +1 here, -1 there     : b'HFLKO WORLD!' 2e91 MISSED
TRAP append zero words     : 2e91 MISSED
single bit flip            : 2e8d detected
```

### SECTION 5: MEASURED DETECTION RATE (seeded measurement)
A seeded measurement: 20000 trials of random 2- or 4-bit flips against single parity (all missed, as theory says), and random 3-bit flips against the checksum over 16 random bytes (a small number missed). The checksum miss count is a measurement for this seed, not a universal constant.

Output from a real run:

```text
===== SECTION 5: MEASURED DETECTION RATE (seeded measurement) =====
parity, random 2 or 4 flips : missed 20000/20000
checksum, random 3 flips    : missed 51/20000
(measurement with seed 2024; parity misses all even flips by construction)
```

## Worked Example
**Problem.** Words (4-bit) are `0110 1101 1011 0111`. Find the checksum.

**Solution.** `0110 + 1101 = 10011`; the carry wraps: `0011 + 1 = 0100`. Add `1011`: `0100 + 1011 = 1111`. Add `0111`: `1111 + 0111 = 10110`; wrap: `0110 + 1 = 0111`. Sum is `0111`, complement (the checksum) is `1000`. The receiver adds data plus `1000`: `0111 + 1000 = 1111` (all ones), so accept. The program prints sum `0111`, checksum `1000`.

## Key Rules / Gotchas Recap
- Single parity: detects odd, misses even number of flips.
- 2D parity corrects one error, detects up to three, misses 4 flips forming a rectangle.
- Internet checksum: one's complement sum, end-around carry, then complement; receiver sum must be all ones.
- Odd-length data is padded with a zero byte for the calculation only.
- Checksum cannot see reordered words or +x/-x compensating errors.
- Measured miss rates are measurements for one seed; do not quote them as universal.

## Why This Matters
You meet the Internet checksum whenever you debug packets (a wrong checksum is why captures show a packet the receiver silently drops) and when you write packet crafters or parsers. Knowing what parity and checksum miss is exactly the reasoning behind choosing CRCs or cryptographic hashes for integrity.
