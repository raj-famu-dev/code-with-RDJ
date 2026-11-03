# `_3_CompressionTechniques.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Compression reduces the number of bits needed to represent data so that it takes less storage and less time on the network. It is a presentation-layer function: the sender compresses, the receiver decompresses. Compression works because real data is redundant (repeated symbols, repeated patterns, details people cannot perceive).

**Lossless vs lossy**
- **Lossless**: the original is recovered exactly. Needed for text, source code, executables, medical data. Examples: ZIP, gzip, PNG, FLAC.
- **Lossy**: some information is permanently discarded to get much smaller files. Used for images, audio, video. Examples: JPEG, MP3, MPEG/H.264.

**Run-length encoding (RLE).** Replace a run of identical symbols by (symbol, count): `WWWWBB` becomes `4W2B`. Great for fax pages and simple graphics; bad when there are no runs (the output can be twice as large).

**Huffman coding.** A lossless, variable-length prefix code. Frequent symbols get short codes, rare symbols long codes, and no code is a prefix of another so decoding is unambiguous. Algorithm: (1) count frequencies; (2) put each symbol in a priority queue by frequency; (3) repeatedly remove the two lowest-weight nodes and join them under a new node whose weight is their sum; (4) when one tree remains, label left branches 0 and right branches 1; the path from the root is the code. Huffman is optimal among symbol-by-symbol prefix codes. Different tie-breaking gives different code tables with the same total length.

**Dictionary methods (LZ77, LZ78, LZW).** Instead of coding single symbols, code repeated sequences. *LZ77* uses a sliding window and emits (distance, length, next symbol) back-references to earlier text. *LZW* (used in GIF and Unix `compress`) builds a dictionary of strings while it encodes; the decoder rebuilds the same dictionary, so the dictionary is never sent. *DEFLATE* (ZIP, gzip, PNG, and Python's `zlib`) = LZ77 + Huffman coding.

**Lossy standards (overview, not implemented)**
- **JPEG** (images): convert to YCbCr colour, split into 8x8 blocks, apply the Discrete Cosine Transform, *quantize* (divide and round; this is the lossy step; small high-frequency values become zero), then zigzag scan, run-length and Huffman code.
- **MP3** (audio): psychoacoustic model removes sounds the ear would not hear (masked by louder sounds), quantizes the rest, then Huffman codes it.
- **MPEG** (video): compresses each frame like JPEG (I-frames) and stores only the differences between frames (P-frames predicted from the past, B-frames from past and future) using motion estimation.

**Compression ratio** = original size / compressed size (for example 3.83 : 1). Random or already-compressed data cannot be compressed further.

**Typical exam questions.** Build a Huffman tree for given frequencies and compute average code length. Apply RLE to a string. Lossless vs lossy with examples. Steps of JPEG.

## Full Line-by-Line Breakdown

### SECTION 1: LOSSLESS VS LOSSY
A tiny lossy example: values are quantized to multiples of 50, so `[10, 12, 11, 200, 202, 201]` becomes `[0, 0, 0, 200, 200, 200]`. Fewer distinct values compress better but the original is lost for good.

```text
===== SECTION 1: LOSSLESS VS LOSSY =====
Lossless: decompress gives back EXACT bytes (text, code, PNG, ZIP).
Lossy   : throws away detail humans barely notice (JPEG, MP3, MPEG).
lossy toy: values [10, 12, 11, 200, 202, 201] -> quantised to multiples of 50 -> [0, 0, 0, 200, 200, 200]
(original cannot be recovered exactly: that is the price of lossy)
```

### SECTION 2: RUN-LENGTH ENCODING
The 67-character classic string (12 W, 1 B, 12 W, 3 B, 24 W, 1 B, 14 W) becomes `12W1B12W3B24W1B14W`, 18 characters, and decodes back. The trap: `ABCDEFGH` has no runs, so every letter gets a count of 1 and the output is 16 characters, twice the input.

```text
===== SECTION 2: RUN-LENGTH ENCODING =====
input : WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW (67 chars)
pairs : [('W', 12), ('B', 1), ('W', 12), ('B', 3), ('W', 24), ('B', 1), ('W', 14)]
RLE   : 12W1B12W3B24W1B14W (18 chars)
check: OK (the classic Wikipedia sample decodes back)
TRAP  no runs: 'ABCDEFGH' (8) -> '1A1B1C1D1E1F1G1H' (16): RLE DOUBLED it
```

### SECTION 3: HUFFMAN CODING
`huffman_codes` uses a heap (`heapq`). The tie-break counter makes the tree deterministic. For `ABRACADABRA` the frequencies are A 5, B 2, R 2, C 1, D 1. A gets the 1-bit code `0`; the others get 3 bits. Total: 5 x 1 + 2 x 3 + 2 x 3 + 1 x 3 + 1 x 3 = 23 bits, against 33 bits for a fixed 3-bit code and 88 bits as 8-bit ASCII (ratio 3.83 : 1 against ASCII). Decoding reads bits until the buffer matches a code; that works because no code is a prefix of another. The code table printed is correct but another valid Huffman tree may give different bit patterns with the same 23-bit total.

```text
===== SECTION 3: HUFFMAN CODING =====
message: ABRACADABRA frequencies: {'A': 5, 'B': 2, 'C': 1, 'D': 1, 'R': 2}
code table (more frequent -> shorter):
  A: freq=5 code=0
  B: freq=2 code=110
  C: freq=1 code=100
  D: freq=1 code=101
  R: freq=2 code=111
encoded: 01101110100010101101110
Huffman 23 bits vs fixed 3-bit 33 bits vs ASCII 88 bits
compression ratio vs ASCII: 3.83 : 1
check: OK (decoded back to ABRACADABRA). Total 23 bits is the textbook optimum.
```

### SECTION 4: LZW (DICTIONARY CODING)
The dictionary starts with the 256 single bytes. The encoder grows `w` while `w + ch` is known; otherwise it outputs the code for `w` and adds `w + ch` as a new entry (256, 257, ...). `TOBEORNOTTOBEORTOBEORNOT` (24 symbols) becomes 16 codes; codes 256 and above are repeated phrases. The decoder rebuilds the table as it goes; the special case `k not in table` (the "KwKwK" case) happens in inputs such as `AAAAAAA`, which the code also tests.

```text
===== SECTION 4: LZW (DICTIONARY CODING) =====
input  : TOBEORNOTTOBEORTOBEORNOT (24 symbols)
output : [84, 79, 66, 69, 79, 82, 78, 79, 84, 256, 258, 260, 265, 259, 261, 263] (16 codes)
check: OK (incl. the tricky 'AAAAAAA' case). LZ77 is the sliding-window
cousin: it emits (distance, length) back-references. DEFLATE = LZ77 + Huffman.
```

### SECTION 5: zlib COMPARISON (MEASURED ON THESE INPUTS)
Python's `zlib` (DEFLATE) is used at level 9. The measured sizes for these three inputs: repeated text 1800 to 68 bytes, seeded random bytes 1800 to 1811 (it grows), long runs 1800 to 25. These are measurements of these inputs only. They show the rule: compression depends on redundancy.

```text
===== SECTION 5: zlib COMPARISON (MEASURED ON THESE INPUTS) =====
  repeated text   1800 ->   68 bytes  ratio  26.47 : 1
  random bytes    1800 -> 1811 bytes  ratio   0.99 : 1
  long runs       1800 ->   25 bytes  ratio  72.00 : 1
check: OK. Random (high-entropy) data does not shrink at all (it grows slightly);
highly repetitive data shrinks a lot. Always measure on YOUR data.
```

## Worked Example
**Problem.** Build a Huffman code for `ABRACADABRA` and compute its size.

1. Frequencies: A = 5, B = 2, R = 2, C = 1, D = 1 (total 11).
2. Join the two smallest: C(1) + D(1) = CD(2).
3. Now the smallest are B(2), R(2), CD(2); join two of them (a tie), say B + R = BR(4). Remaining: CD(2), BR(4), A(5).
4. Join CD(2) + BR(4) = 6. Remaining: A(5), 6.
5. Join A(5) + 6 = 11, the root.
6. Give A the branch next to the root: A gets 1 bit, and B, R, C, D each end up 3 levels deep, so 3 bits.
7. Size = 5 x 1 + 2 x 3 + 2 x 3 + 1 x 3 + 1 x 3 = 23 bits. Fixed 3-bit codes: 33 bits. ASCII: 88 bits.
8. Ratio against ASCII: 88 / 23 = 3.83. The code asserts 23 bits.

## Key Rules / Gotchas Recap
- Lossless returns the exact input; lossy does not.
- Huffman: frequent symbols short codes, prefix-free, optimal for symbol codes; the table must be sent or agreed.
- RLE only helps when there are runs; otherwise it can double the size.
- LZW and LZ77 code repeated phrases; DEFLATE = LZ77 + Huffman.
- You cannot compress random or already-compressed data; measure on real data.
- Compress before you encrypt, not after: encrypted data looks random and will not compress.
- JPEG's lossy step is quantization of DCT coefficients.

## Why This Matters
Compression decides bandwidth cost: HTTP uses gzip/brotli, datasets and model weights are shipped compressed, and logs are compressed before storage. In security, compressing secrets together with attacker-controlled text has been abused in attacks (such as CRIME/BREACH), which is why compression and encryption order matter.
