# `_5_TcpIpModelAndEncapsulation.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The TCP/IP model is the four-layer (sometimes five-layer) protocol suite the Internet actually runs: Application, Transport, Internet (Network) and Network Access. As data moves down the stack each layer wraps it in its own header (encapsulation), so the bytes on the wire are Ethernet header + IP header + TCP header + data + Ethernet trailer.

**TCP/IP layers.**

| TCP/IP layer | Job | Protocols | PDU | OSI equivalent |
|--------------|-----|-----------|-----|----------------|
| Application | user-facing protocols, data representation, sessions | HTTP, DNS, SMTP, FTP, TLS | message / data | 7, 6, 5 |
| Transport | process-to-process delivery | TCP (reliable, stream), UDP (unreliable, datagram) | segment / user datagram | 4 |
| Internet | addressing and routing between networks | IP, ICMP, IGMP, routing protocols | packet (datagram) | 3 |
| Network access | delivery on one link, physical signalling | Ethernet, Wi-Fi, PPP | frame / bits | 2, 1 |

Many books use a five-layer hybrid: Application, Transport, Network, Data Link, Physical.

**OSI vs TCP/IP.**

| Point | OSI | TCP/IP |
|-------|-----|--------|
| Layers | 7 | 4 (or 5) |
| Development | model first, protocols later (ISO) | protocols first, model described later (DARPA) |
| Session/presentation | separate layers | part of application |
| Connection-oriented and connectionless | both at network layer, connection-oriented at transport | connectionless at the Internet layer, both at transport |
| Reputation | reference and troubleshooting vocabulary | the real Internet |

**Headers and their real sizes** (no options):
- Ethernet II header: 14 bytes = destination MAC (6) + source MAC (6) + EtherType (2, 0x0800 means IPv4). Trailer FCS: 4 bytes (CRC-32). Minimum frame 64 bytes (including FCS), maximum standard frame 1518 bytes. The 8-byte preamble and start delimiter precede the frame but are not counted in it.
- IPv4 header: 20 bytes = version/IHL (1), type of service/DSCP (1), total length (2), identification (2), flags + fragment offset (2), TTL (1), protocol (1: 6 = TCP, 17 = UDP, 1 = ICMP), header checksum (2), source address (4), destination address (4). IHL counts 32-bit words, so 5 means 20 bytes; maximum 15 words = 60 bytes.
- TCP header: 20 bytes = source port (2), destination port (2), sequence number (4), acknowledgement number (4), data offset (4 bits) + reserved + flags (URG, ACK, PSH, RST, SYN, FIN) (2 bytes), window (2), checksum (2), urgent pointer (2). Offset 5 words = 20 bytes; up to 60 with options.
- UDP header: 8 bytes = source port, destination port, length, checksum.

**Key size rules.** MTU = largest IP packet a link carries (1500 for Ethernet). TCP MSS = MTU - IP header - TCP header = 1460. UDP max payload without fragmentation = 1500 - 20 - 8 = 1472. Frame on the wire = MTU + 14 + 4 = 1518.

**The Internet checksum (RFC 1071).** Add all 16-bit words using one's-complement addition (carry out wraps around to the low bit), then take the one's complement. A receiver adds everything including the checksum; a valid result is 0 after complementing. TCP and UDP checksums also cover a *pseudo-header* (source IP, destination IP, zero byte, protocol, length) so misdelivered segments are detected. The Ethernet FCS is a different, stronger check (CRC-32).

**Encapsulation walk-through.** Application writes data. TCP adds a header to form a segment. IP adds a header to form a packet. Ethernet adds a header and a trailer to form a frame; the NIC sends bits. The receiver reverses each step and the EtherType, IP protocol and TCP port fields tell each layer which protocol to hand data to (demultiplexing).

**Typical exam questions.** Compare OSI and TCP/IP; name layer protocols; compute header overhead or efficiency; compute number of segments; find the checksum of a header; explain MTU and MSS.

## Full Line-by-Line Breakdown

### SECTION 1: TCP/IP LAYERS AND OSI COMPARISON
Prints the layer mapping and the OSI vs TCP/IP comparison as tables. Nothing is computed; it is the vocabulary used for the rest of the file.

```text
===== SECTION 1: TCP/IP LAYERS AND OSI COMPARISON =====
TCP/IP layer                                            protocols               OSI layers
Application (4-layer: includes 5,6,7)                   HTTP, DNS, SMTP, TLS    L7 + L6 + L5
Transport                                               TCP, UDP                L4
Internet                                                IP, ICMP, ARP*          L3
Network access / link (5-layer: Data link + Physical)   Ethernet, Wi-Fi         L2 + L1
* ARP is placed between the link and Internet layers by most books.
4-layer TCP/IP: Application, Transport, Internet, Network access.
5-layer hybrid (most textbooks): Application, Transport, Network, Data link, Physical.

                        OSI                                         TCP/IP
layers                  7                                           4 (or 5)
origin                  ISO reference model, theory first           DARPA/ARPANET, protocols first
session + presentation  separate layers                             merged into application
approach                generic, protocol independent               built around TCP and IP
in real use             teaching and troubleshooting vocabulary     what the Internet runs
```

### SECTION 2: REAL HEADER SIZES WITH struct
`struct` packs Python values into bytes. The format string describes the layout: `!` means network byte order (big endian), `B` = 1 byte, `H` = 2 bytes, `I` = 4 bytes, `6s` = 6 raw bytes. `struct.calcsize` gives the size, and the `assert` confirms the textbook sizes 14, 20, 20 and 8.

```text
===== SECTION 2: REAL HEADER SIZES WITH struct =====
Ethernet header            struct '!6s6sH' -> 14 bytes
IPv4 header (no options)   struct '!BBHHHBBH4s4s' -> 20 bytes
TCP header (no options)    struct '!HHIIHHHH' -> 20 bytes
UDP header                 struct '!HHHH' -> 8 bytes
Ethernet trailer FCS = 4 bytes (CRC-32). Preamble+SFD (8 bytes) is sent first but is not part of the frame.
check: OK
```

### SECTION 3: INTERNET CHECKSUM (RFC 1071)
`inet_checksum()` pads to an even length, sums all 16-bit words, folds the carry back in until it fits in 16 bits and complements the result. It is cross-checked against a well-known textbook IPv4 header whose checksum is 0xb861. A header with the checksum filled in sums to 0. The trap leaves junk in the checksum field while computing, giving a wrong answer; always zero the field first.

```text
===== SECTION 3: INTERNET CHECKSUM (RFC 1071) =====
textbook IPv4 header (checksum zeroed) -> checksum = 0xb861 (expected 0xb861)
verifying the filled header gives 0 (a valid header sums to 0)
Trap: leaving junk 0x1234 in the checksum field gives 0xa62d (wrong); zero it first.
check: OK
```

### SECTION 4: BUILD AND PARSE A REAL FRAME
`build_tcp` creates a TCP header with data offset 5 and flags ACK+PSH (0x18) and computes the TCP checksum over pseudo-header, header and data. `build_ip` creates the IPv4 header (version 4, IHL 5, DF flag, TTL 64, protocol 6) with a correct header checksum. `build_frame` prepends the Ethernet header, pads to the 60-byte minimum if needed and appends a CRC-32 FCS from `zlib`. The example addresses are private/locally-administered values and never touch a network. The frame is then parsed back with `struct.unpack` and the IP checksum, TCP checksum and FCS are all verified. Byte `45` is version 4 / IHL 5; `00 58` is total length 88; `c9 3a` is port 51514; `00 50` is port 80.

```text
===== SECTION 4: BUILD AND PARSE A REAL FRAME =====
application data   : 48 bytes
+ TCP header (20)  : segment = 68 bytes
+ IPv4 header (20) : packet  = 88 bytes
+ Eth hdr 14 + FCS 4: frame   = 106 bytes
first 54 bytes (Ethernet+IP+TCP headers) in hex:
  Ethernet 02 00 00 00 00 bb 02 00 00 00 00 aa 08 00
  IPv4     45 00 00 58 1c 46 40 00 40 06 9a eb c0 a8 01 0a c0 a8 01 14
  TCP      c9 3a 00 50 00 00 03 e8 00 00 07 d0 50 18 ff ff 0d c6 00 00
Ethernet: dst=02:00:00:00:00:bb src=02:00:00:00:00:aa type=0x0800 (IPv4)
IPv4    : version=4 ihl=5 total_length=88 ttl=64 protocol=6 (TCP) src=192.168.1.10 dst=192.168.1.20
TCP     : sport=51514 dport=80 seq=1000 ack=2000 data_offset=5 words flags=0x18 (ACK+PSH) window=65535
IP checksum, TCP checksum (with pseudo-header) and Ethernet FCS all verify; check: OK
```

### SECTION 5: OVERHEAD, MTU, MSS AND PADDING
Shows how efficiency depends on payload size: 1 byte of data costs a 64-byte frame (1.6% efficiency) because of the 60-byte padding rule, while a full 1460-byte segment achieves 96.2% (1460 of 1518). The worked example splits 3000 bytes into segments of 1460, 1460 and 80 bytes; each frame adds 58 bytes (14 + 20 + 20 + 4), so 3000 + 3 x 58 = 3174 bytes. Preamble and inter-frame gap are not counted.

```text
===== SECTION 5: OVERHEAD, MTU, MSS AND PADDING =====
Ethernet MTU = 1500 bytes of IP packet; TCP MSS = 1500 - 20 - 20 = 1460; UDP max payload = 1472
Trap: 1500 is the MTU (IP packet size), not the frame size; the frame is 1518 bytes with header and FCS.
      1 B of data -> frame   64 B  efficiency   1.6%
     10 B of data -> frame   68 B  efficiency  14.7%
    100 B of data -> frame  158 B  efficiency  63.3%
   1460 B of data -> frame 1518 B  efficiency  96.2%
A 1-byte message still costs a 64-byte minimum frame (padding added), so efficiency is tiny.

Worked example: send 3000 bytes over TCP on Ethernet.
segments = [1460, 1460, 80] -> 3 frames, 3174 bytes on the wire, overhead = 174 bytes (5.5%)
check: OK
```

## Worked Example
**Problem.** An application sends 3000 bytes with TCP over Ethernet (MTU 1500). How many segments are needed and how many bytes travel on the wire (excluding preamble)?

1. MSS = 1500 - 20 (IP) - 20 (TCP) = 1460 bytes.
2. 3000 / 1460 = 2.05, so 3 segments: 1460, 1460 and 3000 - 2920 = 80 bytes.
3. Per frame overhead = 14 (Eth) + 20 (IP) + 20 (TCP) + 4 (FCS) = 58 bytes. The 80-byte segment is already above the 46-byte minimum payload, so no padding.
4. Wire bytes = 3000 + 3 x 58 = 3174. Overhead = 174 bytes = 5.5%.

The code prints exactly 3 frames, 3174 bytes and 5.5%.

## Key Rules / Gotchas Recap
- MTU 1500 limits the IP packet; the Ethernet frame is up to 1518 bytes.
- MSS = MTU - 40 for TCP over IPv4 without options; UDP payload max = 1472.
- Network byte order is big-endian: use `!` in struct.
- Zero the checksum field before computing; verifying a full header must give 0.
- TCP/UDP checksums include a pseudo-header; the IP checksum covers only the IP header.
- Small payloads are padded to the 64-byte minimum Ethernet frame.
- Header lengths are in 32-bit words (IHL, TCP data offset).

## Why This Matters
Reading and crafting packets with `struct` is the basis of packet-capture analysis, protocol parsers and security tooling (carefully, on your own lab). Header overhead explains real throughput numbers for model-serving and file transfer, and MTU/MSS mistakes are a classic source of mysterious stalls.
