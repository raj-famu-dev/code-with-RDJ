# `_1_DataLinkLayerAndFraming.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The data link layer (layer 2) moves frames between two machines that are directly connected by one link or one shared medium. Its first job is framing: the physical layer delivers an unstructured stream of bits, so the data link layer must wrap each packet in a frame with clear start and end boundaries that the receiver can find even when the data itself looks like a boundary marker.

**Services of the data link layer.** Framing; physical (MAC) addressing of the next hop; error control (detect with CRC or checksum, correct with codes such as Hamming, or recover by retransmission with ARQ); flow control (stop a fast sender swamping a slow receiver); and, on shared media, access control (the MAC sublayer decides who may transmit). The layer is often split into LLC (logical link control, talks to layer 3) and MAC (medium access control, talks to the medium). Typical services offered upward are unacknowledged connectionless (Ethernet), acknowledged connectionless (Wi-Fi) and acknowledged connection-oriented (HDLC, PPP in reliable mode).

**Four classic framing methods.**

| Method | Idea | Weakness |
|---|---|---|
| Character (byte) count | First byte says how many bytes the frame has | One corrupted count loses every later boundary; the receiver cannot resynchronise |
| Flag bytes with byte stuffing | Frame starts and ends with a FLAG byte; if FLAG or ESC occurs in the data, the sender inserts an ESC before it | Tied to 8-bit characters; every FLAG/ESC in the data costs one extra byte |
| Flag bits with bit stuffing | Frame starts and ends with the flag `01111110`; after five consecutive 1s in the data the sender inserts a 0 | Output length depends on the data |
| Physical layer coding violations | Use signal patterns that never occur in data (for example Manchester code has a mid-bit transition in every bit, so "no transition" marks a boundary) | Only works if the line code has spare symbols |

Bit stuffing rule in one line: sender, after five 1s insert a 0; receiver, after five 1s remove the following 0. Because the stuffed body can never contain six 1s in a row, `01111110` can only be a real flag. Byte stuffing example (PPP-style, FLAG = 0x7E, ESC = 0x7D): data `41 7E 42 7D 43` is sent as `7E 41 7D 7E 42 7D 7D 43 7E`. Exam questions usually give a bit string and ask for the stuffed result, or give a stuffed string and ask for the original, or ask the maximum overhead (1 stuffed bit per 5 data bits for an all-ones payload, so 20 percent).

Advantages and disadvantages: character count is simple but fragile; byte stuffing is simple and robust but byte oriented; bit stuffing works with any bit stream (used by HDLC); coding violations cost nothing in bandwidth but constrain the physical layer.

## Full Line-by-Line Breakdown

### SECTION 1: DATA LINK LAYER SERVICES
The five services are printed as a small table so you can recite them. Nothing here is computed; it is the checklist an exam expects: framing, addressing, error control, flow control, access control.

Output from a real run:

```text
===== SECTION 1: DATA LINK LAYER SERVICES =====
  Framing              wrap packets into frames with start/end boundaries
  Physical addressing  MAC address of next hop in the frame header
  Error control        detect (CRC, checksum) or correct (Hamming) errors
  Flow control         stop a fast sender swamping a slow receiver
  Access control       decide who may use a shared medium (MAC sublayer)
```

### SECTION 2: CHARACTER COUNT FRAMING
`count_frame` puts one byte in front of each payload holding the total length including that byte (so `ABCD` becomes `5 A B C D`). `count_parse` walks the stream by jumping `n` bytes at a time. The round trip works on clean data. The trap flips one bit in the first count byte (5 becomes 4). The parser then cuts the first frame one byte short and treats the leftover `0x03` as a count byte, so every following frame is garbage. This is why character count is rarely used alone.

Output from a real run:

```text
===== SECTION 2: CHARACTER COUNT FRAMING =====
frames      : [b'ABCD', b'EF', b'GHI']
on the wire : [5, 65, 66, 67, 68, 3, 69, 70, 4, 71, 72, 73]
parsed back : [b'ABCD', b'EF', b'GHI']
TRAP: one bit error in first count (5 -> 4): [b'ABC', b'\x03EF\x04GHI']
  every later frame boundary is wrong; the receiver cannot resync.
```

### SECTION 3: BYTE STUFFING
`FLAG = 0x7E` and `ESC = 0x7D`. `byte_stuff` inserts `ESC` before any byte equal to FLAG or ESC and wraps the result in flags; `byte_unstuff` removes each ESC and keeps the byte after it literally. The trap section first shows naive framing (no stuffing): the data contains `7E`, so the receiver sees three flags and cuts the frame in the middle. After stuffing, the only flags are the two real ones, and unstuffing returns the original data exactly.

Output from a real run:

```text
===== SECTION 3: BYTE STUFFING =====
data   : 41 7e 42 7d 43
TRAP naive framing: 7e 41 7e 42 7d 43 7e
  receiver sees 3 flags -> splits into ['41', '427d43'] (frame cut short)
stuffed: 7e 41 7d 7e 42 7d 7d 43 7e
unstuff: 41 7e 42 7d 43
byte stuffing round-trip: check: OK
```

### SECTION 4: BIT STUFFING
`bit_stuff` counts consecutive 1s and, after the fifth, emits an extra 0 and resets the count. `bit_unstuff` does the reverse: after five 1s it skips the next bit. The chosen payload deliberately contains the flag pattern `01111110` inside the data, so the unstuffed frame would be cut early (trap). After stuffing, the pattern is gone. A seeded loop then round-trips 2000 random payloads and asserts the flag never appears inside the stuffed body. The worst case (all ones) grows by one bit per five.

Output from a real run:

```text
===== SECTION 4: BIT STUFFING =====
payload       : 10011111100111111111100
TRAP unstuffed frame: 011111101001111110011111111110001111110
  flag pattern hidden inside the data? True -> receiver would end the frame early
stuffed       : 10011111010011111011111000
stuffed frame : 011111101001111101001111101111100001111110
flag appears inside stuffed body? False
unstuffed     : 10011111100111111111100
2000 random payloads round-trip and never contain the flag: check: OK
worst case 11111111111111111111 -> 111110111110111110111110 (overhead 1 bit per 5)
```

### SECTION 5: PHYSICAL LAYER CODING VIOLATIONS
Manchester coding sends each bit as two half-bit levels: `1` as low-then-high (`LH`), `0` as high-then-low (`HL`). Both legal pairs have a transition in the middle. A pair like `HH` or `LL` has no mid-bit transition, so it can never be data; Ethernet-style and other physical layers use such violations to mark frame boundaries. The code scans a line signal and reports the illegal positions (2 and 3).

Output from a real run:

```text
===== SECTION 5: PHYSICAL LAYER CODING VIOLATIONS =====
bits 1 0 1 1 -> LH HL LH LH
start delimiter uses illegal pairs, e.g. 'HH LL' (no mid-bit transition)
line signal : LH HL HH LL LH
violations at positions: [2, 3]
Cost: needs a physical layer with spare symbols; 4B/5B etc. do the same.
```

### SECTION 6: COMPARISON
A summary table that you should be able to reproduce: overhead and weakness of each of the four methods.

Output from a real run:

```text
===== SECTION 6: COMPARISON =====
method          overhead              weakness
char count      1 byte/frame          one error loses sync
byte stuffing   ESC per FLAG/ESC      byte oriented only
bit stuffing    1 bit per 5 ones      variable length output
coding viol.    none (bits)           needs spare symbols
```

## Worked Example
**Problem.** The payload is `10011111100111111111100`. (a) Bit-stuff it for a link with flag `01111110`. (b) What is the overhead in bits?

**Solution.** The payload is 23 bits: `1 0 0 1 1 1 1 1 1 0 0 1 1 1 1 1 1 1 1 1 1 0 0`. Scan left to right counting consecutive 1s. The first run of 1s is six long: after its fifth 1 insert a 0, and the sixth 1 starts a new count. The second run is ten long: insert a 0 after the fifth 1 and another after the tenth. Result: `10011111` `0` `1` `00` `11111` `0` `11111` `0` `00`, which is `10011111010011111011111000`. That is 26 bits for 23 data bits, an overhead of 3 bits. The program prints exactly this string and checks that unstuffing restores the payload (`check: OK`).

## Key Rules / Gotchas Recap
- Character count: one flipped bit in a count byte destroys all later framing.
- Byte stuffing needs an ESC for both FLAG and ESC themselves; forgetting to escape ESC itself is a classic bug.
- Bit stuffing: after FIVE 1s insert a 0 (not after six), because the flag has six 1s.
- The receiver removes a 0 only when it follows exactly five 1s.
- Worst-case bit-stuffing overhead is 1 bit per 5 data bits (all-ones data).
- Coding violations use no extra bits but need spare symbols in the line code.
- A flag inside the data is the central trap that all stuffing schemes exist to defeat.

## Why This Matters
Every real link protocol (Ethernet preamble/SFD, HDLC, PPP, USB, serial protocols such as SLIP and COBS) must solve framing, and the same flag-inside-data bug shows up in custom TCP protocols that use delimiters. Parsers that trust a length field are also a classic source of security bugs, which is the character-count trap in modern clothes.
