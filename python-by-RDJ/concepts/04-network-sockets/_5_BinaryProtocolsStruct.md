# `_5_BinaryProtocolsStruct.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Many network protocols are not text but tightly packed binary: a fixed header whose bytes mean things like "protocol version", "message type" and "payload length", followed by data. Python's `struct` module converts between Python numbers and those raw bytes using a compact format string such as `">HBBHHI"`. This file designs a tiny packet format, packs and parses it, adds a CRC-32 checksum, and parses a hand-typed byte string. It is **entirely offline**: no sockets, no packet capture, no network access.

## Full Line-by-Line Breakdown

### SECTION 1: struct basics
`struct.pack(">HB", 513, 7)` packs a 2-byte unsigned integer (`H`) and a 1-byte unsigned integer (`B`) into 3 bytes. The first character picks the byte order (`>` big-endian). `calcsize` tells you how many bytes a format needs, and `unpack` always returns a **tuple**, even for one value. Common codes: `B` 1 byte, `H` 2, `I` 4, `Q` 8 (unsigned); lowercase is signed; `s` is a byte string; `?` is a boolean.

```text
=== SECTION 1: struct basics ===
pack('>HB', 513, 7): b'\x02\x01\x07' | hex: 02 01 07
size: 3 bytes
unpack: (513, 7) <- always returns a TUPLE
format chars: B=1 byte, H=2, I=4, Q=8 (unsigned); b/h/i/q = signed; s = bytes; ? = bool

```

### SECTION 2: endianness
Endianness is the order of bytes within a multi-byte number. Big-endian ("network byte order") writes the most significant byte first: `0x0102` is `01 02`. Little-endian writes `02 01`. If you read big-endian bytes as little-endian you get `0x201` with no error, a silent bug. Without a prefix, `struct` uses the native order **and** native alignment, adding padding bytes (`@BI` is 8 bytes on this machine, but `>BI` is exactly 5). For wire formats always state the order explicitly.

```text
=== SECTION 2: endianness ===
0x0102 big-endian   : 01 02 (most significant byte first, 'network order')
0x0102 little-endian: 02 01
misread big as little: 0x201 <- TRAP: silently wrong
Native mode '@' adds alignment padding; '=' and '>' do not:
calcsize('@BI') = 8 | calcsize('>BI') = 5
(the '@BI' size is platform-dependent: padding is inserted for alignment)
RULE: for wire formats ALWAYS name the byte order explicitly; use '>' for network order.

```

### SECTION 3: designing a tiny packet
A protocol is just an agreement about byte layout. The invented "RDJ1" format has a 12-byte big-endian header: magic number `0xBEEF` (so you can recognise your own packets), version, message type, sequence number, payload length and a CRC-32 checksum, followed by the payload. The format string `">HBBHHI"` encodes exactly that, and `calcsize` confirms 12 bytes.

```text
=== SECTION 3: designing a tiny packet ===
Our made-up protocol 'RDJ1' (header = 12 bytes, big-endian):
  offset size field
   0     2    magic      0xBEEF  (identifies our protocol)
   2     1    version    1
   3     1    msg_type   1=PING 2=DATA 3=BYE
   4     2    seq        sequence number
   6     2    length     payload length in bytes
   8     4    checksum   CRC-32 of the payload
  12     n    payload
HEADER_SIZE computed by struct: 12

```

### SECTION 4: pack a packet with a CRC-32 checksum
`build_packet` computes `zlib.crc32(payload)` and packs the header, then appends the payload. The printed hex shows the layout: `be ef` magic, `01` version, `02` type, `00 2a` sequence 42, `00 05` length, `36 10 a6 86` checksum, then `68 65 6c 6c 6f` = "hello". A checksum lets the receiver detect corrupted data.

```text
=== SECTION 4: pack a packet with a CRC-32 checksum ===
packet hex: be ef 01 02 00 2a 00 05 36 10 a6 86 68 65 6c 6c 6f
total length: 17 = header 12 + payload 5
crc32(b'hello') = 0x3610a686

```

### SECTION 5: parse a packet (with validation)
`parse_packet` checks, in order: enough bytes for a header, correct magic, supported version, a payload that is as long as the header claims, and a matching CRC. Each failure raises `PacketError`. It uses `struct.unpack_from(fmt, data, offset)` to read from a position without slicing. **Validate before trusting any length field**; never assume incoming bytes are well-formed.

```text
=== SECTION 5: parse a packet (with validation) ===
round trip: Packet(version=1, msg_type=2, seq=42, payload=b'hello')

```

### SECTION 6: parse a HANDCRAFTED byte string (offline)
The script builds a packet by typing hex digits (`bytes.fromhex`) and appending `b"abc"`. Reading the bytes by hand matches the format: magic, version 1, type 2, sequence 7, length 3, the CRC of `abc` (`0x352441c2`, cross-checked with `zlib`), payload `abc`. If you guess the CRC wrong (zeros), the parser rejects it. This is how you test parsers: with explicit byte strings, no network required.

```text
=== SECTION 6: parse a HANDCRAFTED byte string (offline) ===
bytes: be ef 01 02 00 07 00 03 35 24 41 c2 61 62 63
parsed: Packet(version=1, msg_type=2, seq=7, payload=b'abc')
Reading it by hand: be ef=magic, 01=version, 02=DATA, 00 07=seq 7, 00 03=len 3,
35 24 41 c2 = CRC-32 of b'abc', then the payload 61 62 63 = 'abc'.
Cross-check with zlib: 0x352441c2 == 0x352441c2: True
TRAP: handcrafting with a wrong/zero CRC -> checksum mismatch

```

### SECTION 7: validation catches bad input
Six malformed inputs (empty, short, wrong magic, truncated, one flipped bit, wrong version) are all rejected with specific messages. A final note: CRC-32 catches accidental corruption but is **not security**, since anyone can recompute it; use an HMAC or TLS to detect tampering.

```text
=== SECTION 7: validation catches bad input ===
empty                -> rejected: too short: 0 < 12
short header         -> rejected: too short: 5 < 12
wrong magic          -> rejected: bad magic 0x0000
truncated payload    -> rejected: truncated payload: expected 5, got 3
flipped payload bit  -> rejected: checksum mismatch
wrong version        -> rejected: unsupported version 9
CRC-32 detects accidental corruption. It is NOT security: anyone can recompute it.
For tamper-proofing you need a keyed MAC (hmac) or TLS.

```

### SECTION 8: struct.error and variable-length data
`struct.error` is raised when the buffer is the wrong size or a value does not fit (`300` does not fit in one byte). A string whose length varies is sent as a **length byte followed by the bytes**. The `4s` code gives a fixed-width field padded with NUL bytes, and `iter_unpack` reads repeated fixed-size records.

```text
=== SECTION 8: struct.error and variable-length data ===
struct.error: unpack requires a buffer of 3 bytes
pack overflow -> error
length-prefixed string decoded: RDJ
fixed-width text with 's': b'ab\x00\x00' <- padded with NUL bytes
iter_unpack over repeated records: [(1, 2), (3, 4)]
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Binary packing | `ByteBuffer` (`putShort`, `putInt`, `getInt`) or `DataOutputStream` / `DataInputStream` | `struct.pack` / `struct.unpack` with a format string |
| Default byte order | **Big-endian** (network order) by default; `ByteBuffer.order(ByteOrder.LITTLE_ENDIAN)` to change | Native order unless you give `>`, `<` or `!`; always specify it |
| Unsigned types | No unsigned `byte`/`short`/`int`; you mask (`b & 0xFF`) or use `Byte.toUnsignedInt` | `B`, `H`, `I`, `Q` are unsigned directly; Python ints are arbitrary size |
| Checksum | `java.util.zip.CRC32` | `zlib.crc32` (returns an unsigned int) |
| Bytes type | `byte[]` (signed values from -128 to 127) | `bytes` (values 0 to 255) |
| Read from offset | `buffer.position(n)` / absolute `getInt(n)` | `struct.unpack_from(fmt, buf, n)` |
| Errors | `BufferUnderflowException` | `struct.error` |

## Key Rules / Gotchas Recap

- Always give the byte order (`>` for network order) in wire formats.
- `unpack` returns a tuple; unpack with `(x,) = ...`.
- Use `calcsize` rather than counting bytes by hand.
- Without a prefix, native alignment can insert padding bytes.
- Validate magic, version, length and checksum before using a payload; never trust a length field.
- CRC-32 detects accidents only; it is not a security control.
- Test parsers with handcrafted byte strings, offline.

## Why This Structure Exists
File formats, network protocols, game packets and many low-level tools are binary, and security work involves reading specifications and parsing bytes safely. Writing and validating a parser for your own tiny format (without touching a live network) teaches the discipline that prevents real parsing vulnerabilities.
