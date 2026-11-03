# `_10_EthernetAndMacAddressing.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Ethernet (IEEE 802.3) is the dominant wired LAN technology: it defines a frame format, a 48-bit MAC address scheme and the rules for sharing or switching a link. Every frame carries the destination and source MAC addresses so that a switch or a NIC can decide whether the frame is for it.

**Frame layout (802.3 / Ethernet II).**

| Field | Size (bytes) | Purpose |
|---|---|---|
| Preamble | 7 | 10101010 repeated; lets receiver clocks synchronise |
| SFD | 1 | 10101011; marks the start of the frame proper |
| Destination MAC | 6 | receiver address (unicast, multicast or broadcast) |
| Source MAC | 6 | sender address |
| Type / Length | 2 | value >= 1536 (0x0600) is an EtherType (0x0800 IPv4, 0x0806 ARP, 0x86DD IPv6, 0x8100 VLAN tag); value <= 1500 is a payload length (802.3) |
| Payload | 46-1500 | data from the network layer; padded with zeros if shorter than 46 |
| FCS | 4 | CRC-32 over destination, source, type and payload |

The minimum frame is 64 bytes (14 + 46 + 4) and the maximum 1518 bytes (14 + 1500 + 4); preamble and SFD are not counted. The minimum exists so that CSMA/CD can detect collisions (previous file); the 1500-byte maximum payload is the MTU. An interframe gap of 96 bit times separates frames. Link efficiency with a 1500-byte payload is 1500/1538 = 97.5 percent; with the 46-byte minimum payload it is only 54.8 percent.

**MAC addresses.** 48 bits, written as six hex pairs. The first 24 bits are the OUI (Organizationally Unique Identifier) assigned by the IEEE to a vendor; the last 24 bits are assigned by the vendor per NIC. Two bits in the first byte have meaning: the least significant bit (I/G) is 0 for unicast and 1 for group (multicast) addresses; the next bit (U/L) is 0 for universally administered (vendor) and 1 for locally administered addresses. Broadcast is `ff:ff:ff:ff:ff:ff`. IPv4 multicast addresses map into `01:00:5e:xx:xx:xx`. Because the data link address is flat and burned in by the vendor (but can be changed by software), it identifies an interface, not a location.

**Speeds.** 10BASE-T (10 Mbps, Manchester coding, CSMA/CD, hubs), 100BASE-TX Fast Ethernet (100 Mbps, same frame format), 1000BASE-T Gigabit (1 Gbps over four pairs). Modern switched links are full duplex and need no CSMA/CD, but the frame format and minimum size are unchanged.

**FCS.** The sender computes CRC-32 over everything from destination to payload and appends it, low byte first. The receiver recomputes; mismatch means silent discard. Receiving a frame including its own good FCS gives the constant CRC residue `0x2144DF1C` for the usual implementation.

## Full Line-by-Line Breakdown

### SECTION 1: MAC ADDRESS STRUCTURE
`describe_mac` splits an address into OUI and NIC part and reads the first byte bits. `00:1a:2b:...` is a normal universal unicast address (made-up example, not tied to a vendor). `01:00:5e:00:00:fb` has the I/G bit set: multicast. `02:42:...` has the U/L bit set: locally administered (typical of virtual interfaces). `ff:..:ff` is broadcast.

Output from a real run:

```text
===== SECTION 1: MAC ADDRESS STRUCTURE =====
  00:1a:2b:3c:4d:5e  first byte 00000000  OUI=00:1a:2b  NIC=3c:4d:5e
      I/G bit=0 -> unicast;  U/L bit=0 -> universally (vendor) assigned
  01:00:5e:00:00:fb  first byte 00000001  OUI=01:00:5e  NIC=00:00:fb
      I/G bit=1 -> multicast;  U/L bit=0 -> universally (vendor) assigned
  02:42:ac:11:00:02  first byte 00000010  OUI=02:42:ac  NIC=11:00:02
      I/G bit=0 -> unicast;  U/L bit=1 -> locally administered
  ff:ff:ff:ff:ff:ff  first byte 11111111  OUI=ff:ff:ff  NIC=ff:ff:ff
      I/G bit=1 -> broadcast;  U/L bit=1 -> n/a (all ones)
48 bits = 6 bytes = 12 hex digits; OUI = first 24 bits, NIC part = last 24 bits.
Bytes go on the wire in order, but each byte is sent least significant bit first.
```

### SECTION 2: FRAME LAYOUT AND SIZES
The layout table with sizes, then the arithmetic for the minimum (64) and maximum (1518) frame and the link efficiency including preamble, SFD and a 12-byte interframe gap: 46 / 84 = 0.5476 versus 1500 / 1538 = 0.9753.

Output from a real run:

```text
===== SECTION 2: FRAME LAYOUT AND SIZES =====
  Preamble     7 byte(s)
  SFD          1 byte(s)
  Destination  6 byte(s)
  Source       6 byte(s)
  Type/Length  2 byte(s)
  Payload      46..1500 byte(s)
  FCS          4 byte(s)
min frame = 14 + 46 + 4 = 64 bytes
max frame = 14 + 1500 + 4 = 1518 bytes
Preamble (7 x 10101010) + SFD (10101011) = 8 bytes for clock sync; not counted in 64/1518.
link efficiency with payload   46: 46/84 = 0.5476
link efficiency with payload 1500: 1500/1538 = 0.9753
```

### SECTION 3: BUILD A FRAME WITH struct
`build_frame` pads short payloads with zeros up to 46 bytes, packs destination, source and type with `struct.pack("!6s6sH", ...)` (network byte order), computes `zlib.crc32` over that header plus payload, and appends the FCS with `struct.pack("<I", ...)` (low byte first). A 15-byte payload becomes a 64-byte frame (72 bytes with preamble and SFD).

Output from a real run:

```text
===== SECTION 3: BUILD A FRAME WITH struct =====
payload 'hello, ethernet' is 15 bytes -> padded to 46
total on wire (with preamble/SFD): 72 bytes; frame proper: 64
hex: aa aa aa aa aa aa aa ab ff ff ff ff ff ff 00 1a 2b 3c 4d 5e 08 00 ... ad 4d cb a7
```

### SECTION 4: PARSE AND VERIFY FCS
`parse_frame` unpacks the header with `struct.unpack` and re-computes the CRC. It reports broadcast destination, type 0x0800, size 64 and FCS ok. The padding trap: the payload still contains 31 zero bytes after `hello, ethernet`; the receiver cannot know where data ends unless the upper layer (IP total length) says so. Flipping one payload bit makes the FCS check fail. Computing the CRC over preamble and SFD as well gives a different, wrong value. A CRC over the whole frame including its FCS produces the magic residue `2144df1c`.

Output from a real run:

```text
===== SECTION 4: PARSE AND VERIFY FCS =====
dst   : ff:ff:ff:ff:ff:ff (broadcast)
src   : 00:1a:2b:3c:4d:5e
type  : 0x0800 (IPv4)
size  : 64 bytes
FCS   : a7cb4dad  ok=True
payload still has the padding: b'hello, ethernet' + 31 zero bytes
TRAP: the receiver cannot tell padding from data unless the upper layer carries a length (IP header total length does).
build/parse round-trip: check: OK
flip one payload bit -> fcs_ok = False
TRAP: FCS over preamble+SFD too -> 88afee25 != a7cb4dad
CRC over whole frame incl. FCS = 2144df1c (fixed 'magic' residue 2144df1c)
```

### SECTION 5: TYPE/LENGTH FIELD AND SPEED GRADES
Type/length rule: values up to 1500 are lengths, 1501-1535 undefined, 1536 and above EtherTypes (shown with IPv4 0x0800, ARP 0x0806, IPv6 0x86DD, VLAN 0x8100). The speed table summarises 10, 100 and 1000 Mbps variants.

Output from a real run:

```text
===== SECTION 5: TYPE/LENGTH FIELD AND SPEED GRADES =====
  value    46 (0x002e) -> length (802.3)
  value  1500 (0x05dc) -> length (802.3)
  value  1501 (0x05dd) -> undefined
  value  1535 (0x05ff) -> undefined
  value  2048 (0x0800) -> EtherType (DIX)
  value  2054 (0x0806) -> EtherType (DIX)
  value 34525 (0x86dd) -> EtherType (DIX)
  value 33024 (0x8100) -> EtherType (DIX)

name        speed     medium                    note
10BASE-T    10 Mbps   twisted pair, 2 pairs     Manchester, CSMA/CD
100BASE-TX  100 Mbps  Cat5 twisted pair         Fast Ethernet
1000BASE-T  1 Gbps    Cat5e, 4 pairs            Gigabit; usually full duplex
1000BASE-SX 1 Gbps    multimode fibre           short-reach optical
Switched full-duplex links need no CSMA/CD; the 64-byte minimum remains for compatibility.
```

## Worked Example
**Problem.** A host sends 20 bytes of data in an Ethernet frame. How many bytes are on the wire (without preamble) and how many are padding?

**Solution.** Payload minimum is 46, so 46 - 20 = 26 bytes of padding. Frame = 14 header + 46 payload + 4 FCS = 64 bytes (72 with preamble and SFD). The program does the same for 15 bytes: 31 padding bytes, 64 byte frame, FCS `a7cb4dad`, and verifies it with `zlib.crc32`.

## Key Rules / Gotchas Recap
- Frame proper = 14-byte header + 46..1500 payload + 4 FCS = 64..1518 bytes; preamble/SFD are extra.
- FCS covers destination to payload only, not preamble/SFD.
- First byte: bit 0 = I/G (multicast), bit 1 = U/L (locally administered).
- Type >= 1536 is EtherType; <= 1500 is length.
- Short payloads are padded with zeros; the receiver needs the upper layer length to strip it.
- The FCS is sent low byte first; use `<I` for the FCS and `!` (network order) for header fields.

## Why This Matters
Packet capture, network testing and many embedded protocols require you to read and build Ethernet frames byte by byte; `struct` and a CRC are all you need. MAC address structure also matters in security and operations work (spotting multicast or locally administered addresses, tracking virtual NICs).
