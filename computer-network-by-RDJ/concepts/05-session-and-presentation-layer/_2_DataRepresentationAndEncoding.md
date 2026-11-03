# `_2_DataRepresentationAndEncoding.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The presentation layer (layer 6 of OSI) makes sure that data sent by one computer can be understood by another, even if they store numbers and text differently. It handles data representation and encoding (text, numbers, structures), and also compression and encryption. In TCP/IP there is no separate presentation layer: the application protocol (HTTP, SMTP, DNS) defines the formats itself.

**Why representation matters.** A computer stores everything as bytes, but different machines may disagree on what the bytes mean: which character does byte `0xE9` mean, which end of a 32-bit integer comes first in memory, how is a record laid out? The sender and receiver must agree on a format, called the transfer syntax.

**Character encodings**
- **ASCII**: 7 bits, 128 characters (letters, digits, punctuation, control codes). `A` = 65 = `0x41`.
- **Latin-1 (ISO 8859-1)**: 8 bits, adds Western European letters; every byte is a character.
- **Unicode** is a table of code points (`U+20AC` is the euro sign); it is not itself an encoding of bytes.
- **UTF-8** is the standard byte encoding: code points up to `U+007F` use 1 byte (identical to ASCII), up to `U+07FF` 2 bytes, up to `U+FFFF` 3 bytes, up to `U+10FFFF` 4 bytes. Bit patterns: `0xxxxxxx`, `110xxxxx 10xxxxxx`, `1110xxxx 10xxxxxx 10xxxxxx`, `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx`.

**Byte order (endianness).** A 32-bit integer `0x12345678` is 4 bytes. *Big-endian* stores the most significant byte first (`12 34 56 78`); *little-endian* stores the least significant first (`78 56 34 12`). x86 and most ARM systems are little-endian; Internet protocols use **network byte order = big-endian**. C has `htons/htonl`; Python has `struct` with `!` or `>` for big-endian.

**Text-safe encodings.** *Hex* uses 2 characters per byte (100% overhead). *Base64* maps every 3 bytes to 4 characters from `A-Z a-z 0-9 + /`, with `=` padding (about 33% overhead); it is used in email (MIME), data URLs and JSON/HTTP headers. Base64 is not encryption.

**TLV and ASN.1.** Type-Length-Value is a self-describing format: each field is a type tag, a length, then the value bytes. A parser can skip unknown types. ASN.1 is a notation for defining data structures and BER/DER are their TLV byte encodings; X.509 certificates, SNMP and LDAP use them (DER INTEGER tag = `0x02`, UTF8String = `0x0C`).

**Formats compared**

| Format | Human readable | Size | Needs schema | Typical use |
|---|---|---|---|---|
| JSON | yes | medium | no | web APIs |
| XML | yes | largest (tags repeated) | optional (XSD) | legacy APIs, documents |
| Binary (struct, protobuf, ASN.1) | no | smallest | yes | RPC, low-level protocols |

Protobuf has a schema file; each field is encoded as a tag (field number and wire type) plus a value, with integers written as variable-length varints. It is not implemented here, only the idea is shown by `struct`.

**Typical exam questions.** Functions of the presentation layer (translation, compression, encryption). What is big-endian? Why Base64? Convert a character to UTF-8 bytes. Difference between ASCII and Unicode.

## Full Line-by-Line Breakdown

### SECTION 1: ASCII AND UTF-8
Five characters are encoded with `str.encode("utf-8")` and the bytes shown in hex. `A` and `e` are 1 byte (ASCII compatible); `é` is 2; the euro sign is 3; the emoji is 4. Then the euro sign is built by hand: code point `0x20AC` needs the 3-byte pattern `1110xxxx 10xxxxxx 10xxxxxx`, so the code shifts and masks the bits (`cp >> 12`, `(cp >> 6) & 0x3F`, `cp & 0x3F`) and an assertion confirms the result equals Python's own encoding.

```text
===== SECTION 1: ASCII AND UTF-8 =====
  'A'        U+0041  UTF-8 bytes: 41           (1 byte(s))
  'e'        U+0065  UTF-8 bytes: 65           (1 byte(s))
  'é'        U+00E9  UTF-8 bytes: c3 a9        (2 byte(s))
  '€'        U+20AC  UTF-8 bytes: e2 82 ac     (3 byte(s))
  '😀'        U+1F600  UTF-8 bytes: f0 9f 98 80  (4 byte(s))
ASCII is 7 bits (0-127); UTF-8 keeps ASCII identical and uses 2-4 bytes beyond.
  by hand: 11100010 10000010 10101100 = e2 82 ac
check: OK (hand-built UTF-8 matches str.encode)
```

### SECTION 2: BYTE ORDER
`struct.pack(">I", n)` writes an unsigned 32-bit integer big-endian, `"<I"` little-endian. The trap: the sender writes little-endian but the receiver reads big-endian, so `0x12345678` turns into `0x78563412` (2018915346). The fix is that both sides use `!` (network order), and the round trip returns the original value.

```text
===== SECTION 2: BYTE ORDER =====
  value 0x12345678
  big-endian (network order): 12 34 56 78
  little-endian             : 78 56 34 12
  TRAP  read little bytes as big: 0x78563412 = 2018915346
  FIX   agree on '!' (network order) both sides: True
check: OK
```

### SECTION 3: HEX AND BASE64
Six raw bytes become 12 hex characters or 8 Base64 characters. `Man` gives `TWFu`, the classic textbook example. The padding line encodes 1, 2 and 3 bytes: `TQ==`, `TU0=`, `TU1N`; the `=` fills the last group of 4 when the input is not a multiple of 3 bytes.

```text
===== SECTION 3: HEX AND BASE64 =====
  raw bytes : [0, 255, 16, 128, 127, 1]
  hex       : 00ff10807f01 (2 chars per byte, +100% size)
  base64    : AP8QgH8B (4 chars per 3 bytes, ~+33% size)
  text 'Man': TWFu (textbook example: TWFu)
  padding   : ['TQ==', 'TU0=', 'TU1N']
check: OK (round trips)
Base64 is encoding, NOT encryption: anyone can decode it.
```

### SECTION 4: TLV ENCODING
`tlv(t, v)` builds `[type][length][value]`. The record (age 21, name "Raj") becomes `02 01 15 | 0c 03 52 61 6a`. `decode_tlv` walks the bytes: read type, read length, slice that many bytes, move on. The decoder needs no schema to find field boundaries, which is the strength of TLV.

```text
===== SECTION 4: TLV ENCODING =====
  encoded: 02 01 15 0c 03 52 61 6a -> 02 01 15 | 0c 03 52 61 6a
  type=0x02 len=1 value=21
  type=0x0C len=3 value='Raj'
check: OK. ASN.1 (used in X.509 certificates, SNMP, LDAP) is TLV with
many types; BER/DER are its byte encodings. Real DER: INTEGER=0x02, UTF8String=0x0C.
```

### SECTION 5: SIZE COMPARISON (SAME RECORD)
One record (`id=7, name=Raj, score=91.5, active=true`) is encoded three ways. JSON is 48 bytes, XML is 83 (every field has an opening and closing tag), and the fixed binary layout `!I8sf?` (uint32, 8-byte string, float32, bool) is 17 bytes. These numbers are measured on this one record; they are not a general ratio. The binary version only works because both sides know the layout and the 8-byte name limit.

```text
===== SECTION 5: SIZE COMPARISON (SAME RECORD) =====
  JSON  : {"id":7,"name":"Raj","score":91.5,"active":true}
  XML   : <record><id>7</id><name>Raj</name><score>91.5</score><active>True</active></record>
  binary: 00 00 00 07 52 61 6a 00 00 00 00 00 42 b7 00 00 01
  JSON            48 bytes
  XML             83 bytes
  struct binary   17 bytes
Binary is smallest but needs a shared schema and is not human readable.
Protobuf uses the same idea (schema + field tags + varints), not shown here.
check: OK (measured on this record only; ratios vary with the data)
```

### SECTION 6: MOJIBAKE TRAP
The text `café €5` is encoded as UTF-8 and wrongly decoded as Latin-1: each byte becomes its own character, giving garbage such as `Ã©` (shown with `ascii()` so the output is plain). Decoding as ASCII fails with `UnicodeDecodeError` because bytes above 127 are not ASCII. Since Latin-1 maps every byte to a character, the mistake can be undone by encoding back to Latin-1 and decoding as UTF-8. The rule: always declare the encoding.

```text
===== SECTION 6: MOJIBAKE TRAP =====
  original          : café €5
  UTF-8 bytes       : 63 61 66 c3 a9 20 e2 82 ac 35
  decoded as latin-1: 'caf\xc3\xa9 \xe2\x82\xac5' (garbled)
  decoded as ascii  : UnicodeDecodeError: ordinal not in range(128)
  repaired          : café €5
check: OK. Rule: always state the encoding (HTTP charset, open(..., encoding='utf-8')).
```

## Worked Example
**Problem.** Encode the character `€` (U+20AC) in UTF-8, and write the 32-bit number `0x0A0B0C0D` in network byte order.

1. `U+20AC` is above `U+07FF`, so it needs 3 bytes: `1110xxxx 10xxxxxx 10xxxxxx`.
2. `0x20AC` in 16 bits is `0010 0000 1010 1100`. Split into 4 + 6 + 6 bits: `0010`, `000010`, `101100`.
3. Fill the pattern: `11100010 10000010 10101100` = `E2 82 AC`. Section 1 prints exactly `e2 82 ac`.
4. Network byte order is big-endian: most significant byte first, so `0A 0B 0C 0D` (little-endian would be `0D 0C 0B 0A`).

## Key Rules / Gotchas Recap
- Unicode is the table of code points; UTF-8 is one way to write them as bytes (1 to 4 bytes).
- ASCII text is valid UTF-8, but not the other way round.
- Network byte order is big-endian; use `struct` with `!`.
- Base64 grows data by about 33% and is not encryption.
- TLV lets parsers skip unknown fields; binary formats need a shared schema.
- JSON is readable but larger; binary is compact but opaque; XML is the most verbose.
- Mojibake (`Ã©`) means bytes were decoded with the wrong encoding; fix the declaration, do not guess.

## Why This Matters
Every network parser, log pipeline and ML data loader has hit an encoding or byte-order bug, and protocol reverse-engineering and security tools read TLV fields (certificates, packets) all the time. Choosing JSON or a binary format is a real cost trade-off for APIs and model-serving traffic.
