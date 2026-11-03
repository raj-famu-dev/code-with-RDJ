# `_12_HdlcPppAndArp.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
HDLC and PPP are point-to-point data link protocols that frame data on serial and dial-up style links, and ARP is the small protocol that lets a host find the MAC address that goes with an IP address on the same LAN. Together they show how layer 2 delimits frames, negotiates a link and binds to layer 3.

**HDLC (High-level Data Link Control).** Bit-oriented, synchronous. Frame: Flag (01111110) | Address (8 bits) | Control (8 bits) | Information | FCS (16 bits, CRC-CCITT/X.25) | Flag. Bit stuffing keeps the flag out of the data. Control field kinds: I-frames (data; N(S) send sequence, N(R) receive sequence for piggybacked ACK, P/F poll/final), S-frames (supervisory: RR receive ready, RNR receive not ready, REJ go-back-N reject, SREJ selective reject) and U-frames (unnumbered: link set-up and teardown, e.g. SABM, UA, DISC). Three-bit sequence numbers give a window of up to 7 (modulo 8).

**PPP (Point-to-Point Protocol, RFC 1661).** Used for dial-up, DSL and many tunnels. Frame: Flag 0x7E | Address 0xFF | Control 0x03 | Protocol (2 bytes) | Payload | FCS | Flag. PPP uses BYTE stuffing: 0x7E and 0x7D inside the data become 0x7D followed by the byte XOR 0x20. Protocol field: 0x0021 IPv4, 0xC021 LCP, 0x8021 IPCP, 0xC023 PAP, 0xC223 CHAP.

PPP phases: Link Dead -> Link Establishment (LCP negotiates options such as MRU and authentication) -> Authentication (optional PAP or CHAP) -> Network-Layer (an NCP per protocol, IPCP for IPv4) -> Open -> Termination. **PAP** sends the password in cleartext once; **CHAP** uses a challenge and a hash response (MD5 of identifier + secret + challenge), so the secret never crosses the link, and it can re-challenge later.

**ARP (RFC 826).** Resolves IPv4 address to MAC address on one LAN. A host broadcasts an ARP request ("who has IP X? tell Y") in an Ethernet frame with type 0x0806; the owner of X replies unicast with its MAC; the asker caches the answer for a few minutes (timeout). The 28-byte packet for IPv4/Ethernet:

| Field | Bytes | Value |
|---|---|---|
| Hardware type | 2 | 1 = Ethernet |
| Protocol type | 2 | 0x0800 = IPv4 |
| HLEN / PLEN | 1 / 1 | 6 / 4 |
| Operation | 2 | 1 request, 2 reply (3/4 RARP) |
| Sender MAC (SHA) | 6 | |
| Sender IP (SPA) | 4 | |
| Target MAC (THA) | 6 | zeros in a request |
| Target IP (TPA) | 4 | |

Variants: **RARP** maps MAC to IP (obsolete, replaced by BOOTP and DHCP); **proxy ARP** lets a router answer for hosts behind it with its own MAC; **gratuitous ARP** has sender IP equal to target IP and announces or refreshes a binding (also used to detect duplicate addresses). ARP has no authentication, which is why ARP spoofing exists; defences include static entries and switch ARP inspection. For a destination outside the subnet, the host ARPs for its default gateway, not for the far host.

## Full Line-by-Line Breakdown

### SECTION 1: HDLC FRAME
Shows the HDLC frame layout and the three control-field families. `i_control` builds the 8-bit control field in transmission order (bit 1 first): 0, then the 3-bit N(S) sent least significant bit first, the P/F bit, then N(R). For N(S) = 2, N(R) = 5, P/F = 1 the bits are `00101101`, kind I.

Output from a real run:

```text
===== SECTION 1: HDLC FRAME =====
| Flag 01111110 | Address 8 | Control 8 | Information | FCS 16 | Flag 01111110 |
Control field (bits in transmission order, bit 1 first):
  I-frame (data)        : 0 | N(S) 3 | P/F 1 | N(R) 3
  S-frame (supervisory) : 1 0 | type 2 (RR, RNR, REJ, SREJ) | P/F | N(R) 3
  U-frame (unnumbered)  : 1 1 | type 2 | P/F | type 3 (SABM, UA, DISC...)
I-frame N(S)=2 N(R)=5 P/F=1 -> control bits 00101101, kind I
3-bit sequence numbers -> window up to 7 (modulo 8), 7 bits is the extended mode.
```

### SECTION 2: HDLC BUILD, BIT STUFFING, FCS
The FCS is CRC-16/X.25 (reflected polynomial 0x8408, initial value and final XOR all ones); the standard check value for `123456789` is `0x906e` and the code asserts it. A frame with address 0xff, control 0xb4, and data `7e ff 3f` (deliberately containing the flag byte) is turned into bits (each byte least significant bit first, which is how HDLC sends it), bit-stuffed, and wrapped in two flags. The flag appears only at the ends; the receiver unstuffs, rebuilds bytes and the FCS verifies.

Output from a real run:

```text
===== SECTION 2: HDLC BUILD, BIT STUFFING, FCS =====
CRC-16/X.25 (the HDLC FCS) of '123456789' = 906e: check: OK
address 0xff, control 0xb4 info 7e ff 3f FCS 8f2a
raw bits    : 11111111001011010111111011111111111111000101010011110001
stuffed bits: 111110111001011010111110101111101111101111000101010011110001
flag only at the two ends? True
receiver: unstuffed ff b4 7e ff 3f 2a 8f FCS ok = True
HDLC round-trip: check: OK
```

### SECTION 3: PPP FRAME
PPP frame with byte stuffing: payload `data~with}specials` contains `~` (0x7E) and `}` (0x7D). They become `7d 5e` and `7d 5d`. The frame is parsed again, the FCS is verified and the protocol field says IPv4. HDLC uses bit stuffing, PPP byte stuffing, which is a favourite exam contrast.

Output from a real run:

```text
===== SECTION 3: PPP FRAME =====
| Flag 7E | Address FF | Control 03 | Protocol 2 | Payload | FCS 2 | Flag 7E |
  protocol 0x0021 = IPv4
  protocol 0xc021 = LCP
  protocol 0x8021 = IPCP
  protocol 0xc023 = PAP
  protocol 0xc223 = CHAP
PPP frame: 7e ff 03 00 21 64 61 74 61 7d 5e 77 69 74 68 7d 5d 73 70 65 63 69 61 6c 73 7d 5d ee 7e
0x7e inside payload became 7d 5e, 0x7d became 7d 5d (byte stuffing, unlike HDLC bit stuffing)
parsed protocol: IPv4 payload: b'data~with}specials'
check: OK
```

### SECTION 4: PPP PHASES
The six phases are listed. PAP is cleartext. For CHAP the code shows that the response is the MD5 of identifier, secret and challenge; the secret is not sent, the authenticator checks with its own copy (right secret True, wrong secret False). The demo uses a fake secret in memory. MD5 is obsolete for new designs; the lesson is the challenge-response shape.

Output from a real run:

```text
===== SECTION 4: PPP PHASES =====
  1. Link Dead            no carrier / physical layer down
  2. Link Establishment   LCP: Configure-Request/Ack negotiate MRU, auth method, magic number
  3. Authentication       optional: PAP or CHAP
  4. Network-Layer        NCP (IPCP for IPv4): negotiate IP address
  5. Link Open            IP datagrams flow
  6. Link Termination     LCP Terminate-Request, then carrier drop

PAP: peer sends name+password in CLEARTEXT, once, in one message.
CHAP: authenticator sends a random challenge; peer replies MD5(id + secret + challenge)
  response sent on the wire: ab83868379e98d941924e0ad2f69db53 (the secret itself never travels)
  authenticator verifies with its own copy of the secret: True | wrong secret: False
  CHAP can re-challenge during the session. MD5 is dated; modern links use EAP/TLS.
PAP vs CHAP: PAP simple, replayable, cleartext; CHAP 3-way, challenge/response.
```

### SECTION 5: ARP REQUEST/REPLY FORMAT
`arp_pkt` packs the 28-byte packet with `struct.pack("!HHBBH6s4s6s4s", ...)`, and `arp_parse` unpacks it. The request from 192.168.1.10 asking for 192.168.1.20 has all-zero THA. The reply swaps sender and target.

Output from a real run:

```text
===== SECTION 5: ARP REQUEST/REPLY FORMAT =====
28 bytes for IPv4 over Ethernet, carried in an Ethernet frame with type 0x0806:
  HTYPE 2 (1=Ethernet) | PTYPE 2 (0x0800) | HLEN 1 (6) | PLEN 1 (4) | OPER 2
  SHA 6 (sender MAC) | SPA 4 (sender IP) | THA 6 (target MAC) | TPA 4 (target IP)
request: 00 01 08 00 06 04 00 01 02 00 00 00 00 01 c0 a8 01 0a 00 00 00 00 00 00 c0 a8 01 14
parsed : {'op': 'request', 'sha': '02.00.00.00.00.01', 'spa': '192.168.1.10', 'tha': '00.00.00.00.00.00', 'tpa': '192.168.1.20'} (THA all zeros = unknown; sent to ff.ff.ff.ff.ff.ff)
reply  : {'op': 'reply', 'sha': '02.00.00.00.00.02', 'spa': '192.168.1.20', 'tha': '02.00.00.00.00.01', 'tpa': '192.168.1.10'} (unicast back to the asker)
```

### SECTION 6: ARP CACHE WITH TIMEOUT
Three `Host` objects on an in-memory LAN. A looks up 192.168.1.20 at t = 0 (miss, broadcast request, reply from B), t = 10 and 59 (hits), t = 60 (entry older than the 60 second TTL, expired: new request) and t = 200 (expired again). A sent 3 requests for 5 lookups; the request also taught B about A (the target caches the asker). A lookup of an absent host gets no reply. The assert counts 4 requests after that last lookup.

Output from a real run:

```text
===== SECTION 6: ARP CACHE WITH TIMEOUT =====
A (TTL 60 s) wants to reach 192.168.1.20 at several times:
  t=  0: cache miss -> BROADCAST request, reply from B: 02.00.00.00.00.02
  t= 10: cache HIT 192.168.1.20 -> 02.00.00.00.00.02
  t= 59: cache HIT 192.168.1.20 -> 02.00.00.00.00.02
  t= 60: cache expired -> BROADCAST request, reply from B: 02.00.00.00.00.02
  t=200: cache expired -> BROADCAST request, reply from B: 02.00.00.00.00.02
A sent 3 requests for 5 lookups
B learned A from the request: {'192.168.1.10': ('02.00.00.00.00.01', 200)}
lookup of 192.168.1.99 : cache miss -> BROADCAST request, no reply (host down)
TRAP: ARP only works inside one LAN; for off-subnet hosts ask for the ROUTER's MAC.
ARP has no authentication; defences include static entries and switch-level ARP inspection.
```

### SECTION 7: RARP, PROXY ARP, GRATUITOUS ARP
RARP uses opcodes 3 and 4 and is obsolete. Proxy ARP is described in words. The gratuitous ARP has sender IP equal to target IP. B holds a stale entry for A (as after a network card replacement); the gratuitous announcement refreshes it, while C, which has no entry, learns nothing.

Output from a real run:

```text
===== SECTION 7: RARP, PROXY ARP, GRATUITOUS ARP =====
RARP: reverse lookup MAC -> IP, opcode 3/4: RARP request (obsolete: replaced by BOOTP and DHCP)
Proxy ARP: a router answers an ARP request for a host behind it using ITS OWN MAC,
  so hosts think the remote host is on-link; the router then forwards.
Gratuitous ARP: {'op': 'request', 'sha': '02.00.00.00.00.01', 'spa': '192.168.1.10', 'tha': '00.00.00.00.00.00', 'tpa': '192.168.1.10'}
  sender IP == target IP: True -> announces 'I am here' / refreshes
  neighbours' caches, and a reply would mean a duplicate IP address on the LAN.
B's stale entry for A      : ('02.00.00.00.00.ff', 0)
after the announcement B   : ('02.00.00.00.00.01', 5)
C (had no entry) cache     : {}
```

## Worked Example
**Problem.** Host 192.168.1.10 has an empty ARP cache and an ARP timeout of 60 s. It sends to 192.168.1.20 at t = 0, 10 and 70 s. How many ARP requests are broadcast?

**Solution.** t = 0: miss, request 1. t = 10: cache hit (age 10 < 60). t = 70: age 70 >= 60, expired, request 2. Total 2 requests. The program shows the same pattern at t = 0, 10, 59, 60, 200 (misses at 0, 60 and 200).

## Key Rules / Gotchas Recap
- HDLC = bit stuffing + flag 01111110; PPP = byte stuffing (0x7D escape, XOR 0x20) + flag 0x7E.
- HDLC control: I (0 bit), S (10), U (11); P/F = poll/final.
- PPP phases: Dead, Establish (LCP), Authenticate (PAP/CHAP), Network (NCP/IPCP), Open, Terminate.
- PAP sends a cleartext password; CHAP sends a hashed response to a random challenge.
- ARP: request is a broadcast, reply is unicast; packet is 28 bytes for IPv4/Ethernet.
- ARP cache entries expire; stale entries are refreshed by a new request or a gratuitous ARP.
- ARP is unauthenticated; for off-subnet destinations ARP for the gateway.

## Why This Matters
Reading and building protocol frames with struct and CRCs is daily work in packet analysis and embedded systems. Knowing how ARP works (and that it is unauthenticated) is essential for network debugging and for defending a LAN.
