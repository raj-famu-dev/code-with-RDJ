# `_8_TcpVsUdpAndModernTransport.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
TCP and UDP are the two classic transport protocols: TCP gives a reliable, ordered byte stream at the cost of handshakes, delays and head-of-line blocking; UDP gives bare datagrams with almost no overhead and lets the application decide how much reliability it needs. Newer transports (SCTP and especially QUIC) try to combine the strengths of both.

**TCP vs UDP**

| Feature | TCP | UDP |
|---|---|---|
| Connection | Connection-oriented (three-way handshake) | Connectionless |
| Reliability | ACKs, retransmission | None, best effort |
| Ordering | Guaranteed | Not guaranteed |
| Data unit | Byte stream, no message boundaries | Datagrams, boundaries kept |
| Header | 20 to 60 bytes | 8 bytes |
| Flow control | Yes (receive window) | No |
| Congestion control | Yes | No (the application must be polite) |
| Broadcast / multicast | No | Yes |
| Speed / overhead | Slower to start, more state | Fast, minimal state |
| Examples | HTTP/1.1 and 2, HTTPS, SMTP, SSH, FTP | DNS, DHCP, NTP, VoIP, video, games, QUIC |

**When to use which.** Use TCP when every byte matters and order matters (web pages, files, email, database connections, APIs). Use UDP when low latency matters more than perfection (voice, live video, games), when a request and reply fit in one datagram each so a handshake would double the cost (DNS), when you need multicast, or when you are building your own transport on top (QUIC). A useful rule: if you find yourself re-implementing sequence numbers, ACKs and retransmission on UDP, ask whether you should be using TCP, or whether your needs are special enough (several independent streams, connection migration) to justify it.

**Head-of-line (HOL) blocking.** TCP delivers one ordered byte stream. If one packet is lost, every later byte, even bytes from unrelated requests multiplexed over the same connection, waits in the receiver's buffer until the lost segment is retransmitted. HTTP/2 multiplexes many requests over one TCP connection, so a single lost packet stalls all of them. Protocols with several independent streams (SCTP, QUIC) order data only within each stream, so loss on one stream does not delay the others.

**SCTP (Stream Control Transmission Protocol).** A reliable transport with message boundaries, defined in RFC 4960 and now RFC 9260 (IP protocol number 132). Key ideas: **multi-streaming** (several independent message streams in one *association*, avoiding cross-stream HOL blocking); **multi-homing** (each endpoint can have several IP addresses and traffic fails over to another path when one dies, which TCP cannot do); a **four-way handshake with a cookie** (INIT, INIT-ACK, COOKIE-ECHO, COOKIE-ACK) so the server holds no state until the client proves its address, which resists SYN-flood-style attacks. Used in telecom signalling (SIGTRAN) and WebRTC data channels. Rare on the public Internet because many NATs and firewalls do not pass unknown IP protocols.

**QUIC.** A transport built on UDP (RFC 9000, with TLS 1.3 integration in RFC 9001 and loss recovery in RFC 9002), the basis of HTTP/3 (RFC 9114).
- **Built-in TLS 1.3.** The transport and cryptographic handshakes are merged, so a new connection needs 1 RTT instead of TCP's 1 plus TLS's 1 or 2.
- **0-RTT resumption.** A client that has talked to the server before can send request data in its very first flight. Caveat: 0-RTT data can be replayed by an attacker, so only safe, idempotent requests should use it.
- **Streams.** Multiple independent streams per connection; loss on one only stalls that stream.
- **Connection IDs.** A connection survives a client's IP or port change (moving from Wi-Fi to mobile data), unlike a TCP 4-tuple.
- **User-space and encrypted.** Implemented in applications and libraries, so it can evolve quickly, and most of its headers are encrypted so middleboxes cannot meddle. It uses UDP because new IP protocols would be blocked by NATs and firewalls.

**Typical exam questions:** compare TCP and UDP in a table; choose a transport for given applications and justify; why does DNS use UDP; why is TCP not suitable for live video; what is head-of-line blocking; what are the advantages of SCTP over TCP; how does QUIC reduce connection setup latency.

## Full Line-by-Line Breakdown

### SECTION 1: TCP VS UDP COMPARISON AND CHOOSING
The table is printed from a list of tuples. `choose` encodes the rule of thumb as a function of five yes/no needs; the order of its `if` statements is the reasoning (multicast first, since only UDP can do it). It is labelled a heuristic. Five applications run through it: web pages and bank APIs get TCP, DNS and voice get UDP, IPTV gets UDP because of multicast. Two asserts check the web and voice cases.

Output from a real run:

```text
===== SECTION 1: TCP VS UDP COMPARISON AND CHOOSING =====
feature              TCP                                  UDP
--------------------------------------------------------------------------------
connection           connection-oriented (handshake)      connectionless
reliability          ACKs + retransmission                none (best effort)
ordering             in order                             not guaranteed
data unit            byte stream (no boundaries)          datagrams (boundaries kept)
header               20 to 60 bytes                       8 bytes
flow control         yes (rwnd)                           no
congestion control   yes (cwnd)                           no (app must do it)
broadcast/multicast  no (point to point)                  yes
speed/latency        slower start, extra delay on loss    fast, no setup
typical use          web, email, file transfer, SSH       DNS, DHCP, VoIP, games, QUIC

when to use which (heuristic):
  web page download      -> TCP (do not rebuild reliability yourself)
  DNS lookup             -> UDP (one datagram each way beats a handshake)
  live voice call        -> UDP (a retransmitted old packet is useless late)
  bank transfer API      -> TCP (do not rebuild reliability yourself)
  IPTV to many viewers   -> UDP (only it supports multicast/broadcast)
check: web=TCP, voice=UDP: OK
```

### SECTION 2: HEAD-OF-LINE BLOCKING (SIMULATION)
Twelve packets, sent one per 10 ms with a 20 ms one-way delay, belong to three streams A, B, C in rotation. Packet 4 (stream B) is lost; the model has its retransmission arrive one extra RTT (40 ms) later, at 100 ms instead of 60 ms. Two delivery rules are applied to the same arrival times. TCP: a packet is delivered only after all earlier ones, so delivery time is the running maximum of arrival times. QUIC-style: the running maximum is kept per stream. The table shows packets 5, 6 and 7 (streams C, A and B) are held up under TCP until 100 ms, although packets 5 and 6 have nothing to do with the lost data, while under QUIC-style streams only packet 7 (stream B, the same stream as the loss) waits. The assert confirms TCP hurts all three streams and the independent-stream model hurts only B. The timing values are model assumptions, not measurements.

Output from a real run:

```text
===== SECTION 2: HEAD-OF-LINE BLOCKING (SIMULATION) =====
Three streams (A, B, C) share one connection. Packets are sent 1 per 10 ms, one-way delay 20 ms.
packet 4 (stream B) is lost; its retransmission arrives at t=100 ms instead of t=60 ms (model: one extra RTT of 2 x 20 ms)
pkt strm  arrives  TCP delivers  QUIC delivers  TCP extra wait
  0    A       20            20             20               0
  1    B       30            30             30               0
  2    C       40            40             40               0
  3    A       50            50             50               0
  4    B      100           100            100               0
  5    C       70           100             70              30
  6    A       80           100             80              20
  7    B       90           100            100              10
  8    C      100           100            100               0
  9    A      110           110            110               0
 10    B      120           120            120               0
 11    C      130           130            130               0
packets delayed by the loss: TCP [5, 6, 7] | QUIC [7]
streams hurt: TCP ['A', 'B', 'C'] | QUIC ['B']
check: TCP stalls every stream; independent streams stall only the stream that lost data: OK
This is why HTTP/2 over TCP still suffers (many streams, one byte stream) and why HTTP/3 uses QUIC.
```

### SECTION 3: RELIABILITY ON TOP OF UDP (REAL LOOPBACK, STOP-AND-WAIT)
A real UDP server on loopback drops the first copy of sequence number 2 on purpose, to play the part of a lossy network. The client sends a one-byte sequence number plus payload, waits up to 0.15 s for an ACK byte, and retransmits on timeout. The log shows seq 2 timing out once and succeeding on attempt 2; the receiver ends up with all four messages in order, and the asserts check this. The receiver re-ACKs duplicates, which matters: if the ACK itself were lost, the sender's retransmission must still be answered. The lesson is the cost: to get reliability on UDP you have to build sequence numbers, ACKs and a timer. Stop-and-wait also only sends one message per round trip, the reason real protocols use windows. The thread is stopped and joined and both sockets are closed.

Output from a real run:

```text
===== SECTION 3: RELIABILITY ON TOP OF UDP (REAL LOOPBACK, STOP-AND-WAIT) =====
  seq 0 b'alpha': acknowledged after 1 attempt(s)
  seq 1 b'beta': acknowledged after 1 attempt(s)
  seq 2: timeout -> retransmit (attempt 2)
  seq 2 b'gamma': acknowledged after 2 attempt(s)
  seq 3 b'delta': acknowledged after 1 attempt(s)
receiver got, in order: [b'alpha', b'beta', b'gamma', b'delta']
retransmissions needed: 1
check: all 4 messages delivered in order despite one dropped datagram: OK
We needed sequence numbers + ACKs + a timer: that is TCP's job rebuilt by hand. Real
protocols over UDP (QUIC, RTP, DNS retry logic) do exactly this, in a smarter way.
Stop-and-wait sends one message per RTT; TCP/QUIC use windows to keep many in flight.
```

### SECTION 4: SCTP OVERVIEW (DESCRIBED, NOT IMPLEMENTED)
A printed summary table of SCTP features against TCP and UDP (see Concept). Nothing is run, because SCTP needs kernel or library support that cannot be assumed, and the brief is to describe it.

Output from a real run:

```text
===== SECTION 4: SCTP OVERVIEW (DESCRIBED, NOT IMPLEMENTED) =====
SCTP (Stream Control Transmission Protocol, IP protocol number 132, now specified in RFC 9260,
which replaced RFC 4960): a transport protocol that mixes ideas from TCP and UDP.

  feature            SCTP                                        compared with
  message oriented   keeps message boundaries                    like UDP, unlike TCP
  reliable           SACK-based retransmission, congestion ctl   like TCP
  multi-streaming    many independent streams in ONE association  a lost message blocks only its
                     (per-stream ordering, optional unordered)    stream: no cross-stream HOL blocking
  multi-homing       an endpoint has SEVERAL IP addresses; a      TCP is tied to one IP pair; if that
                     failed path => traffic moves to another      path dies the connection dies
  setup              4-way handshake with a signed cookie        server keeps no state until the
                     (INIT, INIT-ACK, COOKIE-ECHO, COOKIE-ACK)   cookie returns: resists SYN floods
  term               'association' instead of 'connection'

Used in telecom signalling (SIGTRAN) and WebRTC data channels (SCTP carried inside DTLS over UDP).
Little general deployment on the open Internet because many NATs and firewalls drop unknown protocols.
```

### SECTION 5: QUIC OVERVIEW (DESCRIBED, NOT IMPLEMENTED)
A short description of QUIC plus an arithmetic model of setup cost at an assumed RTT of 50 ms: TCP plus TLS 1.2 needs 1 RTT for the TCP handshake and 2 for TLS (3 RTT = 150 ms) before the first request byte is sent; TCP plus TLS 1.3 needs 2; a new QUIC connection needs 1; a resumed QUIC connection with 0-RTT data needs 0. These are counts of round trips under the standard protocol designs, converted to milliseconds at a hypothetical RTT, not measurements. The closing trap is the replay risk of 0-RTT.

Output from a real run:

```text
===== SECTION 5: QUIC OVERVIEW (DESCRIBED, NOT IMPLEMENTED) =====
QUIC (RFC 9000; TLS 1.3 integration in RFC 9001; loss recovery in RFC 9002; HTTP/3 in RFC 9114)
runs over UDP but provides reliable, ordered, congestion-controlled streams itself:

  - built-in TLS 1.3: transport and security handshake are combined; almost everything is encrypted
  - independent STREAMS: loss on one stream does not stall others (see Section 2)
  - connection IDs: a connection survives a change of IP/port (Wi-Fi -> mobile data)
  - runs in user space, so it can be updated without an OS upgrade
  - uses UDP because middleboxes block or mangle new IP protocols (SCTP's problem)
round trips BEFORE the first request byte can be sent (model, RTT = 50 ms):
  TCP + TLS 1.2          3 RTT = 150 ms handshake  (+ 50 ms for the response)
  TCP + TLS 1.3          2 RTT = 100 ms handshake  (+ 50 ms for the response)
  QUIC (new server)      1 RTT =  50 ms handshake  (+ 50 ms for the response)
  QUIC 0-RTT (resumed)   0 RTT =   0 ms handshake  (+ 50 ms for the response)
0-RTT trap: early data can be replayed by an attacker, so only idempotent requests (a GET
of public data) belong in 0-RTT. Never a payment. The server must apply replay protection.
Typical rule of thumb for modern apps: web = HTTP/3 (QUIC) with fallback to TCP; most
other bulk or transactional traffic = TCP; low-latency datagrams = UDP.
```

## Worked Example
**Problem.** Choose TCP or UDP for each and justify: (a) a video-call app, (b) an e-commerce checkout, (c) a DNS resolver query, (d) a multiplayer game's player-position updates 60 times a second, (e) a file download.

**Solution.**
1. (a) UDP (usually via RTP or QUIC): a lost frame is better skipped than shown late; low latency dominates.
2. (b) TCP (or HTTP/3 over QUIC): every byte must arrive, in order, exactly once.
3. (c) UDP: one small query, one small answer; a handshake would double the latency. If the answer is too large or the server demands it, retry over TCP.
4. (d) UDP: the next position update supersedes a lost one; retransmitting old positions wastes time.
5. (e) TCP: complete, ordered data; TCP's congestion control also shares the link fairly.

Head-of-line check: a browser loads 3 images over one HTTP/2-over-TCP connection and one packet carrying part of image B is lost. Under TCP, images A and C wait too. Over QUIC streams only B waits. Section 2 of the code reproduces this pattern numerically (TCP stalls A, B and C; independent streams stall B only).

## Key Rules / Gotchas Recap
- TCP is a byte stream (no boundaries); UDP keeps datagram boundaries.
- UDP is not "faster TCP": it just leaves the reliability work to you.
- UDP is the only one of the two that supports multicast/broadcast.
- HOL blocking: one loss stalls everything behind it in one ordered stream.
- SCTP: multi-streaming + multi-homing + cookie handshake; message oriented.
- QUIC: UDP-based, built-in TLS 1.3, streams, connection IDs, 1-RTT (0-RTT when resumed).
- 0-RTT data is replayable: use it only for idempotent requests.
- Reliable-over-UDP needs sequence numbers, ACKs and timers; consider whether TCP already does what you need.

## Why This Matters
Choosing a transport is an architecture decision with latency and reliability consequences: it is why DNS, VoIP and HTTP/3 look the way they do, and why game servers and streaming pipelines avoid TCP for real-time data. As more services move to HTTP/3, being able to read a QUIC handshake and know what 0-RTT risks is part of everyday web and security work.
