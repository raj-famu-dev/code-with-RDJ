# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Ethernet (IEEE 802.3) frame layout and MAC addressing: preamble, SFD,
destination, source, type, payload, FCS packed and parsed with struct, address
bits (OUI, I/G, U/L), size limits 64..1518, and FCS verified with zlib.crc32.
Implements the Ethernet part of the Data Link chapter."""
import struct
import zlib

# ===== SECTION 1: MAC ADDRESS STRUCTURE =====
print("===== SECTION 1: MAC ADDRESS STRUCTURE =====")


def mac_to_bytes(mac: str) -> bytes:
    parts = mac.split(":")
    assert len(parts) == 6
    return bytes(int(p, 16) for p in parts)


def mac_to_str(b: bytes) -> str:
    return ":".join(f"{x:02x}" for x in b)


def describe_mac(mac: str) -> None:
    b = mac_to_bytes(mac)
    first = b[0]
    group = bool(first & 0b01)  # least significant bit of first byte: I/G
    local = bool(first & 0b10)  # second least significant bit: U/L
    kind = "broadcast" if mac == "ff:ff:ff:ff:ff:ff" else ("multicast" if group else "unicast")
    print(f"  {mac}  first byte {first:08b}  OUI={b[:3].hex(':')}  NIC={b[3:].hex(':')}")
    ul = ("n/a (all ones)" if kind == "broadcast" else
          "locally administered" if local else "universally (vendor) assigned")
    print(f"      I/G bit={int(group)} -> {kind};  U/L bit={int(local)} -> {ul}")


for m in ["00:1a:2b:3c:4d:5e", "01:00:5e:00:00:fb", "02:42:ac:11:00:02", "ff:ff:ff:ff:ff:ff"]:
    describe_mac(m)
print("48 bits = 6 bytes = 12 hex digits; OUI = first 24 bits, NIC part = last 24 bits.")
print("Bytes go on the wire in order, but each byte is sent least significant bit first.")

# ===== SECTION 2: FRAME LAYOUT AND SIZES =====
print("\n===== SECTION 2: FRAME LAYOUT AND SIZES =====")
layout = [("Preamble", 7), ("SFD", 1), ("Destination", 6), ("Source", 6),
          ("Type/Length", 2), ("Payload", "46..1500"), ("FCS", 4)]
for name, size in layout:
    print(f"  {name:<12} {size} byte(s)")
MIN_PAYLOAD, MAX_PAYLOAD, HEADER, FCS = 46, 1500, 14, 4
print(f"min frame = {HEADER} + {MIN_PAYLOAD} + {FCS} = {HEADER + MIN_PAYLOAD + FCS} bytes")
print(f"max frame = {HEADER} + {MAX_PAYLOAD} + {FCS} = {HEADER + MAX_PAYLOAD + FCS} bytes")
print("Preamble (7 x 10101010) + SFD (10101011) = 8 bytes for clock sync; not counted in 64/1518.")
for payload in (46, 1500):
    wire = 8 + HEADER + payload + FCS + 12  # 12 bytes = 96-bit interframe gap
    print(f"link efficiency with payload {payload:>4}: {payload}/{wire} = {payload / wire:.4f}")

# ===== SECTION 3: BUILD A FRAME =====
print("\n===== SECTION 3: BUILD A FRAME WITH struct =====")
PREAMBLE = b"\xaa" * 7
SFD = b"\xab"
ETH_IPV4, ETH_ARP, ETH_IPV6, ETH_VLAN = 0x0800, 0x0806, 0x86DD, 0x8100


def build_frame(dst: str, src: str, ethertype: int, payload: bytes) -> bytes:
    if len(payload) < MIN_PAYLOAD:
        payload += bytes(MIN_PAYLOAD - len(payload))  # pad with zeros
    assert len(payload) <= MAX_PAYLOAD
    header = struct.pack("!6s6sH", mac_to_bytes(dst), mac_to_bytes(src), ethertype)
    body = header + payload
    fcs = zlib.crc32(body)  # covers dst..payload only
    return PREAMBLE + SFD + body + struct.pack("<I", fcs)  # FCS low byte first


frame = build_frame("ff:ff:ff:ff:ff:ff", "00:1a:2b:3c:4d:5e", ETH_IPV4, b"hello, ethernet")
print("payload 'hello, ethernet' is 15 bytes -> padded to 46")
print("total on wire (with preamble/SFD):", len(frame), "bytes; frame proper:", len(frame) - 8)
print("hex:", frame[:22].hex(" "), "...", frame[-4:].hex(" "))
assert len(frame) - 8 == 64

# ===== SECTION 4: PARSE AND VERIFY FCS =====
print("\n===== SECTION 4: PARSE AND VERIFY FCS =====")


def parse_frame(raw: bytes) -> dict:
    assert raw[:7] == PREAMBLE and raw[7:8] == SFD, "bad preamble/SFD"
    body, fcs_bytes = raw[8:-4], raw[-4:]
    dst, src, etype = struct.unpack("!6s6sH", body[:14])
    (fcs,) = struct.unpack("<I", fcs_bytes)
    return {"dst": mac_to_str(dst), "src": mac_to_str(src), "type": etype,
            "payload": body[14:], "fcs": fcs, "fcs_ok": zlib.crc32(body) == fcs,
            "size": len(body) + 4}


info = parse_frame(frame)
print("dst   :", info["dst"], "(broadcast)")
print("src   :", info["src"])
print(f"type  : 0x{info['type']:04x} (IPv4)")
print("size  :", info["size"], "bytes")
print(f"FCS   : {info['fcs']:08x}  ok={info['fcs_ok']}")
print("payload still has the padding:", info["payload"][:15], "+", len(info["payload"]) - 15, "zero bytes")
print("TRAP: the receiver cannot tell padding from data unless the upper layer carries a length"
      " (IP header total length does).")
assert info["fcs_ok"] and info["payload"].rstrip(b"\0") == b"hello, ethernet"
print("build/parse round-trip: check: OK")

corrupt = bytearray(frame)
corrupt[30] ^= 0x01
print("flip one payload bit -> fcs_ok =", parse_frame(bytes(corrupt))["fcs_ok"])
wrong_cover = zlib.crc32(frame[:-4])  # TRAP: includes preamble+SFD
print("TRAP: FCS over preamble+SFD too ->", f"{wrong_cover:08x}", "!=", f"{info['fcs']:08x}")
residue = zlib.crc32(frame[8:])  # CRC over frame INCLUDING its FCS
print(f"CRC over whole frame incl. FCS = {residue:08x} (fixed 'magic' residue 2144df1c)")
assert residue == 0x2144DF1C

# ===== SECTION 5: TYPE VS LENGTH, SPEEDS =====
print("\n===== SECTION 5: TYPE/LENGTH FIELD AND SPEED GRADES =====")
for v in (46, 1500, 1501, 1535, 0x0800, 0x0806, 0x86DD, 0x8100):
    kind = "length (802.3)" if v <= 1500 else ("undefined" if v < 1536 else "EtherType (DIX)")
    print(f"  value {v:>5} (0x{v:04x}) -> {kind}")
print()
print(f"{'name':<12}{'speed':<10}{'medium':<26}{'note'}")
for row in [("10BASE-T", "10 Mbps", "twisted pair, 2 pairs", "Manchester, CSMA/CD"),
            ("100BASE-TX", "100 Mbps", "Cat5 twisted pair", "Fast Ethernet"),
            ("1000BASE-T", "1 Gbps", "Cat5e, 4 pairs", "Gigabit; usually full duplex"),
            ("1000BASE-SX", "1 Gbps", "multimode fibre", "short-reach optical")]:
    print(f"{row[0]:<12}{row[1]:<10}{row[2]:<26}{row[3]}")
print("Switched full-duplex links need no CSMA/CD; the 64-byte minimum remains for compatibility.")
