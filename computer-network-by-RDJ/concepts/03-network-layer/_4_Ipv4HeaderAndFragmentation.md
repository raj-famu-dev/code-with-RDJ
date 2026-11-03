# `_4_Ipv4HeaderAndFragmentation.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The IPv4 header is the 20-to-60-byte control block that every IP datagram carries so routers know where it goes, how long it may live and how to reassemble it. Fragmentation exists because different links have different Maximum Transmission Units (MTU); a datagram bigger than the next link's MTU is cut into pieces that are reassembled only at the destination.

**Header layout (fixed 20 bytes, options optional):**

| Field | Bits | Meaning |
|---|---|---|
| Version | 4 | 4 for IPv4 |
| IHL | 4 | header length in 32-bit words; min 5 (20 B), max 15 (60 B) |
| DSCP / ToS | 8 | priority / service class (DSCP + ECN in modern use) |
| Total length | 16 | header + data in bytes; max 65,535 |
| Identification | 16 | same value on all fragments of one datagram |
| Flags | 3 | bit 0 reserved, DF (Don't Fragment), MF (More Fragments) |
| Fragment offset | 13 | where this fragment's data starts, in units of 8 bytes |
| TTL | 8 | hop limit, decremented by every router |
| Protocol | 8 | upper layer: 1 ICMP, 6 TCP, 17 UDP |
| Header checksum | 16 | covers the header only |
| Source / Destination | 32 + 32 | IPv4 addresses |
| Options + padding | 0-320 | rarely used (record route, timestamp...) |

**Header checksum.** Split the header into 16-bit words, add them with one's-complement arithmetic (carry out of bit 16 is added back in), and take the complement. The sender puts the checksum field as zero while computing. The receiver sums all words including the checksum; the result must be 0xFFFF (complement 0). Because TTL changes at every hop, each router must recompute it. IPv6 dropped the header checksum for this reason.

**TTL.** Set by the source (commonly 64, 128 or 255). Each router subtracts 1; when it reaches 0 the packet is discarded and an ICMP Time Exceeded message is returned. It prevents infinite loops and is what `traceroute` uses.

**Fragmentation rules.**
- Each fragment is a complete IP datagram with its own header (20 bytes).
- Data in every fragment except the last must be a multiple of 8 bytes, because the offset counts 8-byte units.
- Offset field = (byte position of the fragment's data) / 8.
- MF = 1 on all fragments except the last; the last has MF = 0. The first has offset 0.
- Identification is copied to all fragments; reassembly is done only by the destination (routers do not, because fragments may take different paths).
- If DF = 1 and the packet is too big, the router drops it and returns ICMP "Fragmentation needed". Path MTU Discovery uses this to find the smallest MTU on the path.
- Losing any one fragment means the whole datagram is lost (reassembly times out), so fragmentation hurts reliability.

Typical exam question: "A 4000-byte datagram crosses a link with MTU 1500. Give the total length, MF and offset of every fragment."

## Full Line-by-Line Breakdown

### SECTION 1: HEADER FIELDS
A table of the 12 fixed fields with their bit sizes; the script adds them to prove the fixed part is 160 bits = 20 bytes. Options can extend the header to at most 60 bytes because IHL is 4 bits (15 x 4).

Output from a real run:

```text
===== SECTION 1: HEADER FIELDS =====
Version                4 bits  always 4
IHL                    4 bits  header length in 32-bit words (min 5 = 20 B)
DSCP/ToS               8 bits  service/priority bits
Total Length          16 bits  header + data in bytes, max 65535
Identification        16 bits  same for all fragments of a datagram
Flags                  3 bits  reserved, DF, MF
Fragment Offset       13 bits  position in 8-byte units
TTL                    8 bits  hop limit
Protocol               8 bits  6 TCP, 17 UDP, 1 ICMP
Header Checksum       16 bits  covers header only
Source Address        32 bits  
Destination Address   32 bits  
fixed part = 160 bits = 20 bytes; options add up to 40 more (IHL max 15 -> 60 B)
```

### SECTION 2: BUILD, PARSE, CHECKSUM
`Ipv4Header.pack` uses `struct.pack("!BBHHHBBH4s4s", ...)`: `!` means network (big-endian) byte order, B = 1 byte, H = 2 bytes, 4s = 4 raw bytes. The first byte `0x45` is version 4 and IHL 5. The checksum is computed over the header with the checksum field zeroed and stored. `parse` reverses it. Verifying means summing all ten 16-bit words including the checksum: the function returns 0 for a valid header. Flipping one bit of TTL makes verification non-zero, so the receiver would drop it. As an independent cross-check, the same fields with DF=1 give `0xb1e6`, the value that appears in widely published textbook examples of this header (172.16.10.99 to 172.16.10.12); our default has DF=0, hence `0xf1e6`.

Output from a real run:

```text
===== SECTION 2: BUILD, PARSE, CHECKSUM =====
header bytes: 45 00 00 3c 1c 46 00 00 40 06 f1 e6 ac 10 0a 63 ac 10 0a 0c
16-bit words: 4500 003c 1c46 0000 4006 f1e6 ac10 0a63 ac10 0a0c
parsed       : Ipv4Header(ihl=5, tos=0, total_length=60, ident=7238, df=0, mf=0, frag_offset=0, ttl=64, proto=6, src='172.16.10.99', dst='172.16.10.12', csum=61926)
checksum field = 0xf1e6
verify: sum of all 10 words incl. checksum, folded, complemented = 0 (0 means valid)
check: OK
same header with DF=1 -> checksum 0xb1e6 (the widely published textbook value is 0xb1e6)
after flipping 1 bit of TTL, verify = 65279 (non-zero -> drop)
```

### SECTION 3: TTL DECREMENT AT EACH ROUTER
Each simulated router decrements TTL and must re-pack, which recomputes the checksum; the printed checksum rises by 0x0100 each time because TTL is the high byte of the word `TTL|Protocol`, so subtracting 1 from it adds 0x0100 to the complement. Every new header still verifies to 0.

Output from a real run:

```text
===== SECTION 3: TTL DECREMENT AT EACH ROUTER =====
router 1: TTL 63, new checksum 0xf2e6
router 2: TTL 62, new checksum 0xf3e6
router 3: TTL 61, new checksum 0xf4e6
TTL reaching 0 -> router drops the packet and sends ICMP 'time exceeded' to the source
This stops packets looping forever in a routing loop; traceroute exploits it.
```

### SECTION 4: FRAGMENTATION AND REASSEMBLY
A 4000-byte datagram (20 header + 3980 data) meets MTU 1500. Max data per fragment is floor((1500 - 20) / 8) x 8 = 1480. Result: fragments of data 1480, 1480, 1020 with offsets 0, 185, 370 and MF = 1, 1, 0. Total lengths are 1500, 1500, 1040. The reassembler sorts by offset, checks there are no holes and that the last has MF = 0; the test shuffles the arrival order to show order does not matter.

Output from a real run:

```text
===== SECTION 4: FRAGMENTATION AND REASSEMBLY =====
datagram total 4000 B (20 header + 3980 data), MTU 1500
max data per fragment = floor((1500-20)/8)*8 = 1480
frag total len  data MF offset field byte start
   1      1500  1480  1            0          0
   2      1500  1480  1          185       1480
   3      1040  1020  0          370       2960
reassembled from shuffled arrival order == original payload
check: OK
Only the destination reassembles; routers on the path never do.
```

### SECTION 5: TRAP - OFFSET NOT DIVIDED BY 8
The classic mistake is writing the byte position (1480) into the offset field instead of 1480 / 8 = 185. The section shows what the wrong value would mean (byte 11840), the 13-bit limit, and that with MTU 1000 the usable 980 bytes must round DOWN to 976 (a multiple of 8), producing 5 fragments. Finally the DF=1 case raises the "must drop and send ICMP" condition used by Path MTU Discovery.

Output from a real run:

```text
===== SECTION 5: TRAP - OFFSET NOT DIVIDED BY 8 =====
second fragment starts at byte 1480; correct offset field = 1480/8 = 185
WRONG: writing 1480 into the field would mean byte 11840.
Offset field is 13 bits -> max 8191 units x 8 B = 65528 bytes of start position.
Fragment data size must be a multiple of 8 (except the last): with MTU 1500 use 1480, not 1479.
MTU 1000: data per fragment 976 (980 rounds DOWN to 976), fragments = 5
offsets: [0, 122, 244, 366, 488]
DF=1 case: DF set: router must drop and send ICMP frag-needed (this is how Path MTU discovery works)
```

## Worked Example
**Q:** A datagram of total length 4000 bytes (20-byte header) is sent over a link with MTU 1500. Find the fragments.

1. Data = 4000 - 20 = 3980 bytes.
2. Max data per fragment = 1500 - 20 = 1480; 1480 / 8 = 185 exactly, so 1480 is allowed.
3. Fragment 1: data bytes 0-1479, total length 1500, MF = 1, offset 0.
4. Fragment 2: data bytes 1480-2959, total length 1500, MF = 1, offset 1480 / 8 = 185.
5. Remaining data = 3980 - 2960 = 1020. Fragment 3: total length 1040, MF = 0, offset 2960 / 8 = 370.

The script prints precisely 1500/1500/1040, offsets 0/185/370 and MF 1/1/0.

## Key Rules / Gotchas Recap
- Header is 20 bytes minimum; IHL counts 32-bit words (5 means 20 bytes).
- Total length includes the header; data = total - 4 x IHL.
- Offset is in 8-byte units: divide the byte position by 8.
- Fragment data must be a multiple of 8, except the last fragment.
- MF = 1 on all but the last fragment; DF = 1 forbids fragmenting.
- Identification is shared by all fragments; only the destination reassembles.
- Every router decrements TTL and recomputes the header checksum.
- Checksum covers the header only, not the data.
- If one fragment is lost the entire datagram is lost.

## Why This Matters
Reading a hex header with `struct` is the foundation of packet parsers, firewalls and tools like Wireshark. Fragmentation is also a security topic (overlapping or tiny fragments can evade naive filters), and MTU problems are a classic cause of "small packets work, big ones hang" bugs in VPNs and tunnels.
