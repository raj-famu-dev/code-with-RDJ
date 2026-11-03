# `_5_Ipv6.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
IPv6 is the successor to IPv4: it uses 128-bit addresses (about 3.4 x 10^38 of them) so the Internet never runs out of addresses, and a simpler fixed 40-byte header so routers can forward faster. It was designed because IPv4's 2^32 addresses are exhausted and NAT breaks the end-to-end model.

**Address notation.** Eight groups of four hex digits separated by colons: `2001:0db8:0000:0000:0000:ff00:0042:8329`. Two compression rules:
1. Leading zeros in each group may be dropped (`0042` -> `42`; `0000` -> `0`).
2. One run of consecutive all-zero groups (at least two, and the longest run; the first if tied) may be replaced by `::`. It may appear only once, otherwise the length of each gap is ambiguous. Result: `2001:db8::ff00:42:8329`.
To expand, count the groups present and insert enough zero groups at `::` to reach eight.

**Address types.**

| Type | Prefix / form | Notes |
|---|---|---|
| Unicast, global | `2000::/3` | routable on the Internet |
| Unicast, link-local | `fe80::/10` | on every interface, never routed; used for Neighbor Discovery |
| Unique local | `fc00::/7` (in practice `fd..`) | like IPv4 private space |
| Loopback | `::1` | like 127.0.0.1 |
| Unspecified | `::` | like 0.0.0.0 |
| Multicast | `ff00::/8` | 4-bit scope field: `ff02::1` all nodes on link, `ff02::2` all routers on link |
| Anycast | taken from the unicast space | same address on several nodes; delivery to the nearest |
| IPv4-mapped | `::ffff:a.b.c.d` | represents an IPv4 address inside IPv6 |

There is no broadcast in IPv6; multicast does that job.

**Base header: 40 bytes, fixed.**

| Field | Bits | Meaning |
|---|---|---|
| Version | 4 | 6 |
| Traffic class | 8 | like DSCP/ToS |
| Flow label | 20 | identifies a flow for special handling |
| Payload length | 16 | bytes after the 40-byte header (extension headers included) |
| Next header | 8 | type of the next header (like IPv4's Protocol): 6 TCP, 17 UDP, 58 ICMPv6, 44 Fragment... |
| Hop limit | 8 | like TTL |
| Source / Destination | 128 + 128 | |

Removed vs IPv4: header checksum, IHL, identification/flags/offset (moved to an extension header), options (moved to extension headers).

**Extension headers** form a chain: each begins with a Next Header byte. Common: Hop-by-Hop (0), Routing (43), Fragment (44), ESP (50), AH (51), Destination Options (60). Only Hop-by-Hop is examined by every router.

**No router fragmentation.** Only the source may fragment (using the Fragment header). A router that cannot forward a packet because it exceeds the link MTU drops it and returns ICMPv6 Packet Too Big, and the source adjusts (Path MTU Discovery). Every IPv6 link must support an MTU of at least 1280 bytes.

**Other changes.** Auto-configuration (SLAAC) lets hosts build their own address from the router's advertised prefix; ARP is replaced by Neighbor Discovery (ICMPv6); IPsec is part of the design.

**Transition mechanisms.** Dual stack (run both), tunneling (IPv6 packet inside an IPv4 packet, protocol number 41), translation (NAT64/DNS64 converts between the two).

Typical exam questions: "Compress this address", "Header size and fields of IPv6", "Why no checksum?", "IPv4 vs IPv6 table", "Explain tunneling".

## Full Line-by-Line Breakdown

### SECTION 1: ADDRESS COMPRESSION
`compress` implements both rules: strip leading zeros, find the longest run of zero groups (first in a tie), replace it with `::` only if the run is at least 2 long. `expand` does the reverse by counting missing groups. Every result is asserted equal to the `ipaddress` module's output and round-trips. The traps: two runs (`0:1:0:0:0:1` compresses the longer one), a single zero group stays `0`, and two `::` are illegal.

Output from a real run:

```text
===== SECTION 1: ADDRESS COMPRESSION =====
2001:0db8:0000:0000:0000:ff00:0042:8329
   -> 2001:db8::ff00:42:8329
fe80:0000:0000:0000:0202:b3ff:fe1e:8329
   -> fe80::202:b3ff:fe1e:8329
0000:0000:0000:0000:0000:0000:0000:0001
   -> ::1
0000:0000:0000:0000:0000:0000:0000:0000
   -> ::
2001:0db8:0000:0001:0000:0000:0000:0001
   -> 2001:db8:0:1::1
2001:0db8:0000:0001:0001:0001:0001:0001
   -> 2001:db8:0:1:1:1:1:1
check: OK (compress == ipaddress, expand(compress(x)) == x)
TRAP: '::' may appear only ONCE (else ambiguous); 2001:db8::1::1 is invalid:
  ipaddress rejects it: At most one '::' permitted in '2001:db8::1::1'...
TRAP: a single all-zero group is NOT replaced by '::' (RFC 5952 says so).
```

### SECTION 2: ADDRESS TYPES
`kind` classifies by bit pattern: `::1` and `::` first, then the top byte `ff` for multicast (the scope nibble is the low 4 bits of the second byte), the top 10 bits `1111111010` for `fe80::/10`, the top 7 bits `1111110` for `fc00::/7`, and top 3 bits `001` for global unicast. `2001:db8::/32` is the documentation range, so it prints as global-looking. The text at the end explains anycast and the absence of broadcast.

Output from a real run:

```text
===== SECTION 2: ADDRESS TYPES =====
::1                  loopback (::1)
::                   unspecified (::)
fe80::1              link-local unicast fe80::/10
fd12:3456:789a::1    unique local fc00::/7 (private-like)
2001:db8::1          global unicast 2000::/3
2607:f8b0::1         global unicast 2000::/3
ff02::1              multicast ff00::/8, scope link-local
ff02::2              multicast ff00::/8, scope link-local
ff05::1:3            multicast ff00::/8, scope site-local
::ffff:192.0.2.1     IPv4-mapped ::ffff:0:0/96 (192.0.2.1)
check: OK (properties agree with ipaddress)
Anycast has no prefix of its own: the same unicast address is configured on several
nodes and the packet goes to the NEAREST one. There is NO broadcast in IPv6; ff02::1
(all nodes on link) replaces it.
A link-local address fe80::/10 exists on every IPv6 interface and is never routed.
```

### SECTION 3: THE 40-BYTE HEADER
The field widths add up to 320 bits = 40 bytes. `build_v6` packs the first 32 bits (version 6, traffic class, 20-bit flow label) with `struct` format `!IHBB`, then appends the two 16-byte addresses. `parse_v6` unpacks and checks the round trip. The first bytes `60 01 23 45` show version 6 followed by the flow label 0x12345.

Output from a real run:

```text
===== SECTION 3: THE 40-BYTE HEADER =====
field                bits
Version                 4
Traffic Class           8
Flow Label             20
Payload Length         16
Next Header             8
Hop Limit               8
Source Address        128
Destination Address   128
total = 320 bits = 40 bytes (always fixed)
bytes: 40 -> 60 01 23 45 00 20 11 40 ...
parsed: {'version': 6, 'traffic_class': 0, 'flow_label': 74565, 'payload_len': 32, 'next_header': 17, 'hop_limit': 64, 'src': '2001:db8::1', 'dst': '2001:db8:0:1::2'}
check: OK
No header checksum, no IHL (fixed size), no fragmentation fields in the base header.
```

### SECTION 4: EXTENSION HEADERS
Shows the Next Header chain base -> Fragment -> TCP and builds an 8-byte Fragment extension header with `struct`. The printed rules summarise who may fragment (only the source) and what a router does with an oversize packet (drop plus ICMPv6 Packet Too Big).

Output from a real run:

```text
===== SECTION 4: EXTENSION HEADERS =====
base header Next Header chain: base -> Fragment -> TCP
Each extension header starts with its own 'Next Header' byte, forming a linked list.
Routers (except Hop-by-Hop) do not look inside; only the endpoints process them.
Fragmentation in IPv6 is done ONLY by the source host (Fragment header, next-header 44).
Routers NEVER fragment: if a packet is too big they drop it and send ICMPv6 'Packet Too Big'.
Minimum link MTU for IPv6 is 1280 bytes; hosts use Path MTU Discovery to learn the path MTU.
Fragment extension header is 8 bytes: 06 00 00 01 ab cd ef 01
```

### SECTION 5: TRANSITION AND COMPARISON
Builds an actual 6-in-4 tunnel packet: a 20-byte IPv4 header with protocol 41 (outer) wrapped around the 40-byte IPv6 packet (inner), and parses the inner destination back out. The closing table is the standard IPv4 vs IPv6 comparison.

Output from a real run:

```text
===== SECTION 5: TRANSITION AND COMPARISON =====
Dual stack : host/router runs IPv4 AND IPv6 side by side (most common approach).
Tunneling  : IPv6 packet is carried as payload inside an IPv4 packet (protocol 41) across an IPv4-only part.
Translation: a gateway converts IPv6 <-> IPv4 headers (e.g. NAT64 with DNS64).
tunnel packet: outer IPv4 20 B (protocol 41) + inner IPv6 40 B = 60 B
check: OK
feature          IPv4                 IPv6
Address size     32 bits              128 bits
Address count    2^32 = 4,294,967,296 2^128 = 3.403e+38
Header size      20-60 B variable     40 B fixed
Header checksum  yes                  no
Fragmentation    routers and source   source only
Broadcast        yes                  no (multicast)
Address config   manual / DHCP        SLAAC / DHCPv6
Options          in header            extension headers
Address notation dotted decimal       colon hex
ARP              ARP                  Neighbor Discovery (ICMPv6)
IPsec            optional             supported in the design (not forced on)
TTL / hop        TTL                  Hop Limit
```

## Worked Example
**Q:** Compress `2001:0db8:0000:0001:0000:0000:0000:0001`, and say what `fe80::1` is.

1. Drop leading zeros: `2001:db8:0:1:0:0:0:1`.
2. Zero runs: one group (position 3) and three groups (positions 5-7). Replace the longest: `2001:db8:0:1::1`.
3. Do not also compress the lone `0`, since `::` may be used once.
4. `fe80::1` begins with `fe80::/10`, so it is a link-local unicast address: valid only on the local link, never routed.

The script prints `2001:db8:0:1::1` and classifies `fe80::1` as link-local.

## Key Rules / Gotchas Recap
- 128 bits = 8 groups of 16 bits (4 hex digits).
- `::` once only; longest zero run; never for a single zero group.
- Base header is exactly 40 bytes with no checksum and no options inside.
- Next Header chains extension headers; Fragment header = next header 44.
- Routers never fragment IPv6; they send ICMPv6 Packet Too Big. Minimum MTU 1280.
- No broadcast; use multicast (`ff02::1`). No ARP; use Neighbor Discovery.
- `fe80::/10` link-local, `fc00::/7` unique local, `ff00::/8` multicast, `::1` loopback.
- Transition: dual stack, tunneling (protocol 41), translation (NAT64).

## Why This Matters
Cloud providers, mobile networks and CDNs increasingly serve traffic over IPv6, and services that only parse IPv4 break or leak. For security work, IPv6 changes scanning, firewalling and logging (extension headers, link-local, multicast), and for any network engineer, being fluent in compression avoids misreading addresses in logs.
