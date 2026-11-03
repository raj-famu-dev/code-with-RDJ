# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""OSI Presentation layer: how data is represented on the wire. ASCII, UTF-8
byte sequences, byte order (struct), Base64/hex, TLV (the ASN.1 idea) and a
JSON vs XML vs binary size comparison on the same record."""
from __future__ import annotations

import base64
import json
import struct
import xml.etree.ElementTree as ET


# ===== SECTION 1: ASCII AND UNICODE / UTF-8 =====
print("===== SECTION 1: ASCII AND UTF-8 =====")
for ch in ["A", "e", "é", "€", "\U0001F600"]:
    b = ch.encode("utf-8")
    print(f"  {ch!r:<10} U+{ord(ch):04X}  UTF-8 bytes: {b.hex(' '):<12} ({len(b)} byte(s))")
print("ASCII is 7 bits (0-127); UTF-8 keeps ASCII identical and uses 2-4 bytes beyond.")
# Work the bit pattern of the euro sign by hand: U+20AC -> 1110xxxx 10xxxxxx 10xxxxxx
cp = 0x20AC
b1 = 0b11100000 | (cp >> 12)
b2 = 0b10000000 | ((cp >> 6) & 0b111111)
b3 = 0b10000000 | (cp & 0b111111)
print(f"  by hand: {b1:08b} {b2:08b} {b3:08b} = {bytes([b1, b2, b3]).hex(' ')}")
assert bytes([b1, b2, b3]) == "€".encode("utf-8")
print("check: OK (hand-built UTF-8 matches str.encode)")


# ===== SECTION 2: BYTE ORDER (ENDIANNESS) WITH struct =====
print("\n===== SECTION 2: BYTE ORDER =====")
n = 0x12345678
big = struct.pack(">I", n)      # network byte order = big endian
little = struct.pack("<I", n)
print(f"  value 0x{n:08X}")
print(f"  big-endian (network order): {big.hex(' ')}")
print(f"  little-endian             : {little.hex(' ')}")
# TRAP: sender writes little endian, receiver assumes network order.
wrong = struct.unpack(">I", little)[0]
print(f"  TRAP  read little bytes as big: 0x{wrong:08X} = {wrong}")
right = struct.unpack("<I", little)[0]
print(f"  FIX   agree on '!' (network order) both sides: {struct.unpack('!I', struct.pack('!I', n))[0] == n}")
assert right == n and wrong != n
print("check: OK")


# ===== SECTION 3: HEX AND BASE64 =====
print("\n===== SECTION 3: HEX AND BASE64 =====")
raw = bytes([0x00, 0xFF, 0x10, 0x80, 0x7F, 0x01])
print("  raw bytes :", list(raw))
print("  hex       :", raw.hex(), "(2 chars per byte, +100% size)")
b64 = base64.b64encode(raw).decode()
print("  base64    :", b64, "(4 chars per 3 bytes, ~+33% size)")
print("  text 'Man':", base64.b64encode(b"Man").decode(), "(textbook example: TWFu)")
print("  padding   :", [base64.b64encode(b"M" * k).decode() for k in (1, 2, 3)])
assert base64.b64decode(b64) == raw and bytes.fromhex(raw.hex()) == raw
print("check: OK (round trips)")
print("Base64 is encoding, NOT encryption: anyone can decode it.")


# ===== SECTION 4: TLV (TYPE-LENGTH-VALUE), THE ASN.1 BER IDEA =====
print("\n===== SECTION 4: TLV ENCODING =====")
T_INT, T_STR = 0x02, 0x0C


def tlv(t: int, v: bytes) -> bytes:
    assert len(v) < 256
    return bytes([t, len(v)]) + v


def encode_record(age: int, name: str) -> bytes:
    return tlv(T_INT, age.to_bytes(1, "big")) + tlv(T_STR, name.encode("utf-8"))


def decode_tlv(data: bytes) -> list[tuple[int, bytes]]:
    out, i = [], 0
    while i < len(data):
        t, ln = data[i], data[i + 1]
        out.append((t, data[i + 2 : i + 2 + ln]))
        i += 2 + ln
    return out


enc = encode_record(21, "Raj")
print("  encoded:", enc.hex(" "), "-> 02 01 15 | 0c 03 52 61 6a")
for t, v in decode_tlv(enc):
    shown = int.from_bytes(v, "big") if t == T_INT else v.decode()
    print(f"  type=0x{t:02X} len={len(v)} value={shown!r}")
assert decode_tlv(enc) == [(2, b"\x15"), (12, b"Raj")]
print("check: OK. ASN.1 (used in X.509 certificates, SNMP, LDAP) is TLV with")
print("many types; BER/DER are its byte encodings. Real DER: INTEGER=0x02, UTF8String=0x0C.")


# ===== SECTION 5: JSON VS XML VS BINARY ON THE SAME RECORD =====
print("\n===== SECTION 5: SIZE COMPARISON (SAME RECORD) =====")
record = {"id": 7, "name": "Raj", "score": 91.5, "active": True}
as_json = json.dumps(record, separators=(",", ":")).encode()
root = ET.Element("record")
for k, v in record.items():
    ET.SubElement(root, k).text = str(v)
as_xml = ET.tostring(root)
# Fixed binary layout both sides agree on: uint32 id, 8-byte name, float32, bool.
as_bin = struct.pack("!I8sf?", 7, b"Raj", 91.5, True)
print("  JSON  :", as_json.decode())
print("  XML   :", as_xml.decode())
print("  binary:", as_bin.hex(" "))
for label, data in [("JSON", as_json), ("XML", as_xml), ("struct binary", as_bin)]:
    print(f"  {label:<14}{len(data):>4} bytes")
print("Binary is smallest but needs a shared schema and is not human readable.")
print("Protobuf uses the same idea (schema + field tags + varints), not shown here.")
assert len(as_bin) < len(as_json) < len(as_xml)
print("check: OK (measured on this record only; ratios vary with the data)")


# ===== SECTION 6: TRAP - MOJIBAKE (WRONG CHARACTER DECODING) =====
print("\n===== SECTION 6: MOJIBAKE TRAP =====")
text = "café €5"
data = text.encode("utf-8")
bad = data.decode("latin-1")
print("  original          :", text)
print("  UTF-8 bytes       :", data.hex(" "))
print("  decoded as latin-1:", ascii(bad), "(garbled)")
try:
    data.decode("ascii")
except UnicodeDecodeError as e:
    print("  decoded as ascii  : UnicodeDecodeError:", e.reason)
fixed = bad.encode("latin-1").decode("utf-8")
print("  repaired          :", fixed)
assert fixed == text
print("check: OK. Rule: always state the encoding (HTTP charset, open(..., encoding='utf-8')).")
