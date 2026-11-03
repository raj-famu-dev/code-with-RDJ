# `_3_TcpHeaderAndSegments.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
TCP (Transmission Control Protocol, RFC 9293, originally RFC 793) turns the unreliable IP network into a reliable, ordered, full-duplex byte stream between two processes. Everything it needs to do that (ports, sequence numbers, acknowledgements, flags, window size) lives in a header of at least 20 bytes in front of each segment's data.

**The TCP header**

| Field | Size | Purpose |
|---|---|---|
| Source port | 16 bits | Sender's process |
| Destination port | 16 bits | Receiver's process |
| Sequence number | 32 bits | Byte number of the first data byte in this segment (or the ISN on a SYN) |
| Acknowledgment number | 32 bits | Next byte the sender of this segment expects to receive (valid if ACK set) |
| Data offset (header length) | 4 bits | Header size in 32-bit words (5 to 15, so 20 to 60 bytes) |
| Reserved | 4 bits | Zero (the old NS flag lived here) |
| Flags | 8 bits | CWR, ECE, URG, ACK, PSH, RST, SYN, FIN |
| Window size | 16 bits | Receiver's advertised free buffer in bytes (flow control) |
| Checksum | 16 bits | Covers pseudo-header + header + data (mandatory) |
| Urgent pointer | 16 bits | Offset of urgent data if URG is set |
| Options | 0 to 40 bytes | MSS, window scale, SACK, timestamps... |

Fixed part = 160 bits = 20 bytes. Because the data offset is 4 bits, the largest header is 15 x 4 = 60 bytes, leaving 40 bytes for options. Many textbook diagrams show 6 reserved bits and 6 flags (URG ACK PSH RST SYN FIN); modern TCP uses 4 bits and 8 flags (CWR and ECE were added for explicit congestion notification). The layout is the same.

**Flags**
- **SYN**: synchronise sequence numbers; used to open a connection.
- **ACK**: the acknowledgment field is valid. Set on every segment after the first SYN.
- **FIN**: the sender has no more data (graceful close).
- **RST**: abort the connection immediately (error, or segment for a non-existent connection).
- **PSH**: push; deliver buffered data to the application now.
- **URG**: the urgent pointer field is meaningful (rarely used today).
- **CWR / ECE**: congestion window reduced / ECN echo, used with explicit congestion notification.

**Sequence and acknowledgment numbers are byte offsets, not segment counts.** The initial sequence number (ISN) is chosen at connection start. A SYN and a FIN each consume one sequence number even though they carry no data. If a segment has sequence number `S` and carries `n` bytes, the receiver replies with ACK `S + n`, meaning "I have everything before byte S+n; send that one next". ACKs are cumulative. Sequence arithmetic is modulo 2^32.

**Options**
- **MSS** (kind 2, length 4): the largest data chunk the sender is willing to receive in one segment. On Ethernet, MTU 1500 minus 20 (IP) minus 20 (TCP) = 1460. Exchanged only in SYN segments.
- **Window scale** (kind 3, length 3): the 16-bit window caps at 65535, which is too small for fast, long paths. A shift count `s` multiplies the advertised window by 2^s (RFC 7323). Negotiated in the SYNs only.
- **SACK-permitted** (kind 4), **timestamps** (kind 8) and **NOP** (kind 1, padding) are also common. Options are padded to a multiple of 4 bytes.

**Byte stream, not messages.** TCP promises that the bytes arrive complete and in order. It does NOT promise that a receiver's `recv()` call returns what one `send()` call sent. Two sends may arrive as one read; one send may arrive as two reads. Applications must add their own message framing.

**Segmentation.** The application hands TCP a stream; TCP chops it into segments no larger than the MSS, numbering each by the offset of its first byte. The receiver reassembles by sequence number.

**TCP vs UDP header:** 20+ bytes vs 8 bytes. The extra bytes buy reliability, ordering, flow control and congestion control.

**Typical exam questions:** draw the TCP header with sizes; what is the minimum and maximum header length (20 and 60); what is the purpose of the data offset; which flags are set in each step of the handshake; given a segment with seq and length, what is the ACK; why window scaling exists; why does TCP need a checksum when IP has a header checksum (IP's covers only its header; TCP's covers the data too).

## Full Line-by-Line Breakdown

### SECTION 1: HEADER FIELDS AND FLAG BITS
The `FIELDS` list holds each header field with its width in bits and the script sums them: 160 bits, 20 bytes, asserted in code. It then explains why the maximum header is 60 bytes (a 4-bit data offset counts words: 15 x 4). The `FLAGS` dictionary maps each flag name to its bit value in the flag byte (SYN is 0x02, ACK is 0x10 and so on) and `flags_to_names` decodes a byte back into names, so `0x12` reads as ACK|SYN, which is a SYN-ACK.

Output from a real run:

```text
===== SECTION 1: HEADER FIELDS AND FLAG BITS =====
  source port                                16 bits
  destination port                           16 bits
  sequence number                            32 bits
  acknowledgment number                      32 bits
  data offset (header len in 32-bit words)    4 bits
  reserved                                    4 bits
  flags CWR ECE URG ACK PSH RST SYN FIN       8 bits
  window size                                16 bits
  checksum                                   16 bits
  urgent pointer                             16 bits
fixed header = 160 bits = 20 bytes; options add 0..40 bytes
data offset is 4 bits -> max 15 words x 4 = 60 bytes header -> max options = 40 bytes

flag bits (one byte):
  CWR  0x80  10000000
  ECE  0x40  01000000
  URG  0x20  00100000
  ACK  0x10  00010000
  PSH  0x08  00001000
  RST  0x04  00000100
  SYN  0x02  00000010
  FIN  0x01  00000001
SYN=0x02 -> SYN ; SYN+ACK=0x12 -> ACK|SYN ; FIN+ACK=0x11 -> ACK|FIN ; PSH+ACK=0x18 -> ACK|PSH
meaning: SYN open/sync seq | ACK ack field valid | FIN sender done | RST abort | PSH deliver now | URG urgent ptr valid
```

### SECTION 2: OPTIONS (MSS, WINDOW SCALE)
TCP options are a sequence of kind-length-value triples, except the one-byte NOP (1) and end-of-list (0). `build_options` writes MSS as `02 04 05 b4` (kind 2, length 4, value 0x05b4 = 1460), SACK-permitted as `04 02`, then a NOP so the 3-byte window-scale option `03 03 07` starts on a word boundary, and a final NOP pads the whole thing to 12 bytes. `parse_options` walks the bytes back into readable values. The numbers show why window scaling matters: with the plain 16-bit field a 100 ms path can carry at most 65535 bytes per round trip, which is about 5.24 Mbit/s however fast the link is, while a scale of 7 raises the ceiling to 65535 x 128 bytes.

Output from a real run:

```text
===== SECTION 2: OPTIONS (MSS, WINDOW SCALE) =====
options bytes: 02 04 05 b4 04 02 01 03 03 07 01 01 (12 bytes)
parsed       : ['MSS=1460', 'SACK-permitted', 'WindowScale=7 (x128)']
MSS 1460 = Ethernet MTU 1500 - 20 (IP) - 20 (TCP).  MSS is the max DATA per segment.
Window field is only 16 bits -> max 65535 bytes. Window scale 7 multiplies by 2**7 = 128:
  max scaled window = 65535 x 128 = 8388480 bytes (about 8 MB)
Why: on a 100 ms path a 65535-byte window caps throughput at 65535 / 0.1 s = 5.24 Mbit/s, no matter how fast the link is.
```

### SECTION 3: PACK AND UNPACK A SEGMENT
`struct.Struct("!HHIIBBHHH")` is the fixed 20-byte header in network byte order. The data-offset byte is `(header_length_in_words) << 4`, so the 32-byte SYN gives `0x80` (offset 8). `Segment.pack` builds the header with checksum 0, prepends nothing, then computes the TCP checksum over the pseudo-header (source IP, destination IP, zero, protocol 6, TCP length) plus the segment, and patches the result into bytes 16 and 17. `Segment.unpack` recomputes the sum and demands 0xffff. In the real hex dump you can read the fields: `c0 30` is port 49200, `00 50` is port 80, `00 00 03 e8` is sequence 1000, `80 02` is offset 8 with the SYN flag, `ff ff` is window 65535, then the checksum `96 a6`, urgent pointer `00 00`, and the 12 option bytes. Flipping one bit in the sequence number makes the checksum fail. The second segment is a data segment with PSH and ACK: 38 bytes is 20 header plus 18 data bytes.

Output from a real run:

```text
===== SECTION 3: PACK AND UNPACK A SEGMENT =====
SYN segment bytes: 32 (20 fixed + 12 options + 0 data)
hex: c0 30 00 50 00 00 03 e8 00 00 00 00 80 02 ff ff 96 a6 00 00 02 04 05 b4 04 02 01 03 03 07 01 01
data offset nibble = 8 -> header = 8 x 4 = 32 bytes
unpacked: 49200->80 seq=1000 ack=0 flags=SYN win=65535 opts=['MSS=1460', 'SACK-permitted', 'WindowScale=7 (x128)']
check: pack/unpack round trip with checksum: OK
one flipped bit in the sequence number -> bad TCP checksum
data segment: 38 bytes total = 20 header + 18 data, flags ACK|PSH
```

### SECTION 4: SEQUENCE NUMBERS ARE BYTE OFFSETS
A table splits 3500 bytes into segments with MSS 1000. The handshake's SYN used sequence number 1000 so data starts at 1001. Segment 1 carries bytes 1001 to 2000, so the receiver's ACK is 2001, the number of the next byte it wants. The last segment has only 500 bytes, and the final ACK is 4501, which equals ISN + 1 for the SYN + 3500 data bytes. The code asserts this. Notice the ACK never counts segments.

Output from a real run:

```text
===== SECTION 4: SEQUENCE NUMBERS ARE BYTE OFFSETS =====
send 3500 bytes with MSS 1000; the SYN used up seq 1000, so data starts at 1001
  seg   seq     bytes   covers            expected ACK back
  1     1001    1000    1001..2000          2001
  2     2001    1000    2001..3000          3001
  3     3001    1000    3001..4000          4001
  4     4001    500     4001..4500          4501
ACK number = next byte the receiver expects (NOT 'segment number received').
final ACK: 4501 = ISN + 1 (SYN) + 3500 bytes:  4501
a FIN also consumes one sequence number; a pure ACK consumes none.
32-bit sequence space wraps after 2**32 = 4294967296 bytes (4 GiB); arithmetic is mod 2**32.
```

### SECTION 5: BYTE STREAM VS MESSAGE BOUNDARIES (LOOPBACK)
A loopback server accepts one connection and waits until the client has sent everything. The client calls `sendall` three times with `AAA`, `BBB`, `CCC`. The server then reads. Because TCP is a stream, the OS typically hands back all nine bytes in one `recv`, so the three messages arrive fused as `AAABBBCCC`. The script prints the joined stream (stable), whether fewer than three reads were needed (true here; the exact count depends on timing, and the code says so) and the MSS the OS reports for the loopback connection. That MSS is a measurement that differs between operating systems; on loopback it is far larger than 1460 because loopback's MTU is large. The fix, adding a length prefix, is implemented in topic 9.

Output from a real run:

```text
===== SECTION 5: BYTE STREAM VS MESSAGE BOUNDARIES (LOOPBACK) =====
MSS reported by this OS for the loopback connection (a measurement, varies by OS): 32741
sender called send() 3 times: b'AAA', b'BBB', b'CCC'
receiver stream (all chunks joined): b'AAABBBCCC'
receiver recv() calls that returned data fewer than 3: True (the OS merged the sends; exact count is timing dependent)
TRAP: TCP preserves ORDER and CONTENT, never message boundaries.
FIX: the application adds framing (length prefix or delimiter): see topic 9.
```

## Worked Example
**Problem.** A client's SYN has ISN 1000. The server's SYN-ACK has ISN 5000. The client then sends 3 data segments of 1000, 1000 and 500 bytes. (a) What are the sequence numbers of the three segments? (b) What ACK does the server send after each? (c) What is the header length if the SYN carries MSS (4 bytes), SACK-permitted (2), NOP (1), window scale (3) and a final NOP?

**Solution.**
1. The client's SYN used 1000, so the first data byte is 1001. Segment sequence numbers: 1001, 2001, 3001.
2. ACKs: 1001 + 1000 = 2001; 2001 + 1000 = 3001; 3001 + 500 = 3501. ACK means "next byte expected".
3. The SYN-ACK's ACK field is 1001 (client's ISN + 1). Data ACKs never mention 5000, because the server's own sequence space is separate.
4. Options = 4 + 2 + 1 + 3 + 1 = 11 bytes, padded to 12. Header = 20 + 12 = 32 bytes, data offset = 8.

Section 3 of the code builds exactly this option set (MSS, SACK, NOP, window scale, NOP) and proves that 32 bytes and offset 8 come out. Section 4 repeats the byte-offset arithmetic with a table.

## Key Rules / Gotchas Recap
- Fixed header 20 bytes; max 60 bytes; the data offset counts 32-bit words.
- Sequence numbers count bytes. SYN and FIN each consume one number; pure ACKs consume none.
- ACK = next byte expected = last received sequence + 1 (cumulative).
- MSS and window scale appear only in SYN segments.
- 16-bit window = 65535 max; window scale shifts it left by up to 14 bits (field supports up to 14 in the standard).
- TCP keeps order and content, not message boundaries; frame your messages.
- Use `!` (network byte order) in `struct` formats.
- The TCP checksum is mandatory and uses the pseudo-header with protocol 6.
- Do not trust a single `recv` to return one logical message.

## Why This Matters
Wireshark, `tcpdump`, firewalls and load balancers all speak in these fields, so reading a header in hex is a core debugging skill. The byte-stream trap is the most common bug in hand-written network clients and in AI inference servers that stream tokens over raw sockets; the cure is a framing protocol.
