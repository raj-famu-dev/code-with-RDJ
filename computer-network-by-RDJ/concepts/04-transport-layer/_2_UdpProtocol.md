# `_2_UdpProtocol.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
UDP (User Datagram Protocol, RFC 768) is the simplest transport protocol: it adds only port numbers and an optional-looking checksum on top of IP, and nothing else. There is no handshake, no acknowledgement, no retransmission, no ordering and no congestion control, which makes it fast, light (8-byte header) and perfect for traffic that prefers fresh data over perfect data.

**Characteristics**
- Connectionless: each datagram is independent; the sender keeps no state.
- Unreliable (best effort): a datagram can be lost, duplicated or reordered and UDP will never tell you.
- Message oriented: one `sendto` becomes exactly one datagram and one `recvfrom` returns exactly one datagram. Boundaries are preserved.
- Small header: 8 bytes (TCP is at least 20).
- Supports broadcast and multicast (TCP cannot).
- No flow control and no congestion control: a fast sender can overwhelm a slow receiver or a congested network.

**The UDP header (8 bytes = 64 bits)**

| Field | Size | Meaning |
|---|---|---|
| Source port | 16 bits | Sender's port (optional in theory; 0 if unused) |
| Destination port | 16 bits | Receiver's port, picks the process |
| Length | 16 bits | Header + data in bytes; minimum 8 |
| Checksum | 16 bits | Covers pseudo-header + header + data |

**The checksum and the pseudo-header.** The Internet checksum is the 16-bit one's-complement of the one's-complement sum of all 16-bit words. For UDP and TCP the sum also covers a *pseudo-header* that is never transmitted: source IP (4 bytes), destination IP (4 bytes), a zero byte, the protocol number (17 for UDP, 6 for TCP) and the UDP length (2 bytes). Including it means a segment delivered to the wrong host or wrong protocol fails verification, even though the transport header itself is intact. Steps:
1. Build pseudo-header + UDP header (checksum field set to 0) + data, padded with a zero byte if the length is odd (the pad is not sent).
2. Add all 16-bit words; whenever a carry goes past 16 bits, add it back at the bottom (end-around carry).
3. Take the one's complement (flip every bit). That is the checksum. If it computes to 0x0000, send 0xFFFF, because 0 means "no checksum".
4. Receiver adds everything including the received checksum; a good segment gives 0xFFFF (so its complement is 0).

In IPv4 the UDP checksum is optional (a value of 0 means unused). In IPv6 it is mandatory, because IPv6 has no header checksum of its own. The checksum detects most accidental corruption, but it is weak; it is not security.

**Who uses UDP:** DNS queries (port 53), DHCP (67 and 68), NTP (123), TFTP (69), SNMP, VoIP and live video, online games, and QUIC (the transport under HTTP/3). The common theme: small request/response exchanges where a handshake would double the cost, or real-time media where a retransmitted old packet is worthless.

**TCP vs UDP at a glance** is covered fully in topic 8. **Typical exam questions:** draw the UDP header and give field sizes; why is UDP called unreliable and connectionless; what is the pseudo-header and why is it used; compute a UDP checksum; why does DNS prefer UDP; what is the minimum value of the length field (8).

## Full Line-by-Line Breakdown

### SECTION 1: THE 8-BYTE UDP HEADER
`struct.Struct("!HHHH")` describes four unsigned 16-bit fields in network (big-endian) byte order; the `!` is what makes it network order, and forgetting it is a classic bug. The script packs source port 54321, destination 53 and length `8 + len(payload) = 13`, with checksum 0, prints the bytes in hex (54321 = 0xd431, 53 = 0x0035, 13 = 0x000d) and unpacks them again. It also shows that the 16-bit length field caps a datagram at 65535 bytes, and IPv4's 20-byte header takes another 20, leaving 65507 bytes of payload at most.

Output from a real run:

```text
===== SECTION 1: THE 8-BYTE UDP HEADER =====
header size: 8 bytes = 4 fields x 2 bytes
fields: source port | destination port | length (header+data) | checksum
length = 8 + 5 = 13
packed header (hex): d4 31 00 35 00 0d 00 00
  54321 = 0xd431, 53 = 0x0035, length = 0x000d
unpacked: {'src': 54321, 'dst': 53, 'length': 13, 'checksum': 0}
check: pack/unpack round trip: OK
max datagram: length field is 16 bits -> 65535 bytes total, so max payload = 65527 (IPv4 itself limits it a little more: 65535 - 20 - 8 = 65507 )
```

### SECTION 2: INTERNET CHECKSUM WITH PSEUDO-HEADER
`ones_complement_sum` adds 16-bit words and folds the carry back in after every addition. It is first tested against the worked example in RFC 1071 (words 0001 f203 f4f5 f6f7 give sum 0xddf2 and checksum 0x220d), so you know the core is right before using it. `pseudo_header` builds the 12 bytes using the `ipaddress` module. `udp_checksum` computes the value for 192.168.1.10:54321 to 192.168.1.20:53 with payload `hello`, giving 0x642c. A hand sum of the 13 words (c0a8, 010a, c0a8, 0114, 0011, 000d, d431, 0035, 000d, 0000, 6865, 6c6c, 6f00) is done in the code and printed: sum 0x9bd3, complement 0x642c. Note the last data word `6f00`: the odd final byte `o` is padded with a zero byte. The receiver check adds everything including the checksum and expects 0xffff. Three experiments: intact passes; one flipped payload bit fails; the same bytes "delivered" to a different destination IP fail because the pseudo-header changed. The trap shows what you lose by leaving the pseudo-header out: a different value (0xe7b9), and misdelivery would go undetected.

Output from a real run:

```text
===== SECTION 2: INTERNET CHECKSUM WITH PSEUDO-HEADER =====
RFC 1071 example sum  : 0xddf2 (expected 0xddf2)
RFC 1071 example cksum: 0x220d (expected 0x220d)
check: matches RFC 1071 textbook answer: OK
checksum for 192.168.1.10:54321 -> 192.168.1.20:53 payload 'hello': 0x642c
hand sum of 13 words: 0x9bd3 -> complement: 0x642c
check: hand-computed checksum equals the function: OK
receiver verify (intact): True
receiver verify (1 bit flipped): False
receiver verify (delivered to WRONG dst ip, pseudo-header differs): False
trap: forgetting the pseudo-header still 'works' locally but misses misdelivery:
  checksum without pseudo-header = 0xe7b9 vs correct 0x642c -> different
UDP over IPv4: checksum optional (0 = unused); over IPv6 it is mandatory.
```

### SECTION 3: REAL LOOPBACK UDP ECHO (TIMEOUTS)
A UDP server thread binds `127.0.0.1` port 0, loops with a 0.3 s timeout so it can notice a stop flag, and replies with the uppercased data. The client sends three messages, including an empty one, which UDP happily delivers as a zero-length datagram. **Trap A:** three `sendto` calls produce three separate `recvfrom` results, so boundaries survive (TCP would be free to merge them). **Trap B:** `recvfrom(4)` on a 10-byte datagram returns only 4 bytes and the remainder is discarded permanently; always read with a buffer at least as large as your largest datagram. Last, a datagram aimed at a closed port: UDP has no connection, so the only feedback is the OS relaying an ICMP port-unreachable, which shows up as `ConnectionRefusedError` on a connected socket (on some systems you would just see a timeout). The server thread is stopped and joined and every socket is closed.

Output from a real run:

```text
===== SECTION 3: REAL LOOPBACK UDP ECHO (TIMEOUTS) =====
sent b'ping'            got b'PING'
sent b'udp is simple'   got b'UDP IS SIMPLE'
sent b''                got b''
note: an EMPTY datagram (b'') is legal in UDP and was delivered as a message.

trap A: boundaries are preserved (unlike TCP):
  3 sends -> 3 separate receives: [b'ONE', b'TWO', b'THREE']
trap B: recv buffer smaller than the datagram TRUNCATES the rest:
  sent 10 bytes, recvfrom(4) returned: b'ABCD' -> the other 6 bytes are gone for good
  fix: always recvfrom(65535) or a size you know is larger than any datagram.
send to a port with no listener -> recv raised: ConnectionRefusedError (UDP itself never reports it; the OS may relay ICMP port unreachable)
sockets closed, thread joined
```

### SECTION 4: LOSS AND REORDERING (SEEDED SIMULATION)
Loopback almost never loses packets, so the script simulates a lossy, jittery network with `random.Random(42)`: each of 10 packets is dropped with probability 0.3 and the rest get a random extra delay, which can swap their order. Seeded, so it prints the same result each run. The receiver sees four packets missing and `pkt4` before `pkt3`. UDP offers nothing to detect or repair this; applications that care add sequence numbers and acknowledgements themselves.

Output from a real run:

```text
===== SECTION 4: LOSS AND REORDERING (SEEDED SIMULATION) =====
sent    : ['pkt0', 'pkt1', 'pkt2', 'pkt3', 'pkt4', 'pkt5', 'pkt6', 'pkt7', 'pkt8', 'pkt9']
arrived : ['pkt0', 'pkt4', 'pkt3', 'pkt5', 'pkt7', 'pkt9']
lost    : ['pkt1', 'pkt2', 'pkt6', 'pkt8']
arrived in original order: False -> UDP delivers whatever shows up, as it shows up
If you need reliability over UDP you must add it yourself: sequence numbers, ACKs,
timeouts (this is what QUIC and many game/streaming protocols do).

Typical UDP users: DNS (53), DHCP (67/68), NTP (123), TFTP (69), SNMP, VoIP/video
streaming, online games, QUIC (HTTP/3). Reason: low latency, no handshake, small header,
and the application can tolerate or handle loss itself.
```

## Worked Example
**Problem.** A UDP datagram carries the 5-byte payload `hello` from 192.168.1.10 port 54321 to 192.168.1.20 port 53. Find the length field and the checksum.

**Solution.**
1. Length = 8 + 5 = 13 = 0x000d.
2. Pseudo-header words: c0a8 010a | c0a8 0114 | 0011 (zero byte, protocol 17) | 000d (UDP length).
3. UDP header words: d431 (54321) | 0035 (53) | 000d | 0000 (checksum placeholder).
4. Data words: 6865 ("he") | 6c6c ("ll") | 6f00 ("o" plus pad).
5. Add all with end-around carry: sum = 0x9bd3.
6. Complement: 0xffff - 0x9bd3 = 0x642c. The checksum is 0x642c.
7. Receiver adds all words again with 0x642c in place of 0000: result 0xffff, so it accepts.

The code confirms this exactly (`check: hand-computed checksum equals the function: OK`).

## Key Rules / Gotchas Recap
- UDP header = 4 fields x 16 bits = 8 bytes. Length counts header plus data.
- Use `!` in `struct` formats for network byte order.
- Pseudo-header is used for the checksum but never sent.
- Odd-length data is padded with a zero byte for the sum only.
- A computed checksum of 0 is transmitted as 0xffff; a received 0 means "no checksum" (IPv4 only).
- UDP keeps message boundaries; one send = one datagram = one receive.
- A receive buffer smaller than the datagram silently loses the rest.
- No retransmission, no ordering, no flow or congestion control. The application owns all of that.
- Zero-length datagrams are legal.

## Why This Matters
DNS, DHCP, VoIP, games and HTTP/3 all ride on UDP, so you meet it in production debugging constantly. Writing your own checksum shows exactly what packet capture tools verify, and understanding that UDP gives you nothing "for free" is the foundation for designing reliable protocols on top of it, which is exactly what QUIC does.
