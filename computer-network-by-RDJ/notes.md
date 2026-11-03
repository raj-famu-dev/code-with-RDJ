# 🌐 computer-network-by-RDJ — Complete Study Notes

> One consolidated reference covering all 7 modules and 70 topics, with detailed explanations.
> Every topic here has a runnable demo (`_N_Name.py`) that prints the worked example and checks its own answer — CRC-32 against `zlib`, subnets against `ipaddress`, packed headers against `struct`. All demos are loopback-only and run on Python 3.13 with the standard library alone.

---

## 📑 Table of Contents

1. [Module 01 — Introduction & Physical Layer](#module-01--introduction--physical-layer)
2. [Module 02 — Data Link Layer](#module-02--data-link-layer)
3. [Module 03 — Network Layer](#module-03--network-layer)
4. [Module 04 — Transport Layer](#module-04--transport-layer)
5. [Module 05 — Session & Presentation Layer](#module-05--session--presentation-layer)
6. [Module 06 — Application Layer](#module-06--application-layer)
7. [Module 07 — Wireless, Security & Tools](#module-07--wireless-security--tools)

---

# Module 01 — Introduction & Physical Layer

*Folder:* [`concepts/01-introduction-and-physical-layer`](./concepts/01-introduction-and-physical-layer) · ✅ 10 topics

### 1. Network Types & Uses
- **PAN** (Bluetooth), **LAN** (one building), **MAN** (a city), **WAN** (countries; the Internet is the biggest). The scope determines the technology: LANs get cheap shared links; WANs get expensive leased ones.
- The Internet = a network of networks: autonomous systems interconnected by routers and undersea cables, with no owner.

### 2. Network Topologies
- **Bus** (one shared cable, collisions, cheap, breaks kill all), **ring** (token passing, orderly), **star** (central switch, one cable per host, hub is a single point of failure), **mesh** (full or partial cabling, resilient, expensive), **hybrid**.
- The demo computes links needed: full mesh of n nodes = n(n−1)/2 — that quadratic is why full mesh dies at scale.

### 3. Switching Techniques
- **Circuit switching** (reserve the whole path first; phone networks; zero congestion but wasted idle capacity).
- **Packet switching** (the Internet: independent, self-routed packets; statistical multiplexing; needs buffers and can drop).
- **Message switching** (store-and-forward whole messages; historical). Packet switching won because it's fault-tolerant and efficient.

### 4. OSI Model
- Seven layers: **P**hysical, **D**ata link, **N**etwork, **T**ransport, **S**ession, **P**resentation, **A**pplication.
- What each layer does in one line: bits on wire / frames between neighbors / packets across networks / process-to-process segments / dialogs / format + encryption / user-facing protocols.
- **Encapsulation:** each layer wraps the one above it in a header; the receiving side unwraps in reverse (peer-to-peer logically, hop-by-hop physically at layers 1–3, end-to-end at 4+).

### 5. TCP/IP Model & Encapsulation
- The model the Internet actually runs: **Link – Internet – Transport – Application** (OSI's 5–7 collapse into Application).
- The demo walks a byte through the stack: data → +TCP header (segment) → +IP header (packet) → +Ethernet header/trailer (frame) → bits, and computes the per-layer overhead.
- **Multiplexing/demultiplexing** by port number and protocol field — how the receiver hands each PDU to the right process.

### 6. Transmission Media
- **Guided:** twisted pair (cheap, LAN), coax (cable TV), fiber (light, immunity to interference, long haul, bandwidth king).
- **Unguided:** radio, microwave, satellite — the wireless story (latency of satellite: ~250 ms per GEO hop).
- The tradeoffs: attenuation, noise, bandwidth, cost, and distance.

### 7. Signals & Encoding
- **Analog vs digital; baseband vs broadband.** Digital signaling on a wire is an encoding problem: **NRZ** (long runs of 1s lose sync), **Manchester** (self-clocking — a transition in every bit; 10 Mbps Ethernet), **differential Manchester**.
- **Modulation:** AM/FM shifts for carrying bits on analog carriers; baud vs bits per second (they differ when a symbol carries multiple bits).

### 8. Multiplexing
- Share one expensive link: **FDM/TDM** (frequency/time slots; phone trunks), **WDM** (fiber, colors of light), **statistical multiplexing** (the Internet's packet-by-packet version — no reserved slots, links used on demand).
- The demo computes TDM slot capacity: a link divided into frames and slots carries n conversations at 1/n each.

### 9. Delay & Throughput
- The four delays: **processing** (router's lookup), **queueing** (waiting for the output link — the only one that grows with load), **transmission** (packet size ÷ link rate) and **propagation** (distance ÷ speed in medium).
- `Total = proc + queue + tx + prop`; throughput is bottlenecked by the slowest hop (min of link rates); **bandwidth-delay product** = how many bits fit "in the wire" — the right window size for full utilization.
- The demo works a numeric example: 1,500-byte packet over a 1 Gbps link, 1,000 km of fiber.

### 10. Network Devices & Cabling
- **Hub** (repeats bits to all ports — one collision domain), **switch** (forwards frames by MAC — microsegmentation), **router** (forwards packets by IP across networks), plus repeaters, bridges, NICs.
- Cable types: straight-through (unlike devices) vs crossover (like devices, before auto-MDIX), rollover (console).

---

# Module 02 — Data Link Layer

*Folder:* [`concepts/02-data-link-layer`](./concepts/02-data-link-layer) · ✅ 12 topics

### 1. Data Link Layer & Framing
- The layer's five jobs: **framing, physical addressing, reliable delivery (sometimes), flow control (sometimes), media access**.
- **Framing formats:** character count (fragile — one bit error ruins the count), **byte stuffing** (escape `ESC` before `FLAG`/`ESC` bytes), **bit stuffing** (insert a 0 after five 1s; receiver deletes it) — HDLC and PPP use bit stuffing.

### 2. Parity & Checksum
- **Parity:** one extra bit to catch any single-bit flip (odd/even); useless for two-bit flips.
- **Internet checksum (RFC 1071):** sum 16-bit words with end-around carry, take the one's complement; the receiver sums everything and expects all-1s. Cheap, weak (misses many patterns) — used in IP/UDP/TCP headers.
- The demo computes the classic RFC 1071 example and verifies it.

### 3. Cyclic Redundancy Check
- Treat the frame as a big binary number; divide by a generator polynomial; the **remainder rides as the FCS**; the receiver divides again and expects remainder 0.
- **Detects all single-bit errors, all double-bit errors (with the right polynomial), all odd numbers of flips (with x+1 factors), all bursts ≤ degree of the generator** — dramatically stronger than checksums.
- The demo implements CRC bitwise, then cross-checks its CRC-32 against `zlib.crc32` — matching output.

### 4. Hamming Code
- Position check bits at powers of 2; each covers the positions whose binary index includes that power; a flipped bit shows up as the **binary sum of failing checks = the exact error position** — so it corrects, not just detects.
- Trade-off: k redundant bits fix any single flip in 2^k positions. The demo flips a bit, recomputes the syndrome, and pinpoints the flip.

### 5. Stop-and-Wait
- Send one frame, wait for the ACK, retransmit on timeout. **Efficiency = frame size ÷ (frame + RTT)** — on long fat pipes it's a disaster (one frame per round trip).
- Frames and ACKs are numbered (0/1 alternating) so a **lost ACK** doesn't cause a duplicate to be accepted.

### 6. Go-Back-N
- A **sliding window** of up to N unacknowledged frames; cumulative ACKs; on loss, **everything from the lost frame is re-sent** (the receiver discards out-of-order frames).
- Window size N keeps ≤ N frames in flight; efficiency ≈ min(1, W × frame/RTT+frame).
- The demo simulates a loss and prints the retransmit cascade.

### 7. Selective Repeat
- The window again, but the receiver **buffers out-of-order frames** and ACKs each individually; only missing frames are re-sent.
- Needs per-frame sequence numbers (window ≤ half the sequence space) and more receiver state — the accuracy/complexity tradeoff vs Go-Back-N.
- TCP is a hybrid: selective ACKs (SACK) with cumulative base.

### 8. Channel Allocation & ALOHA
- **Pure ALOHA:** transmit whenever; collisions are likely; throughput caps at ~18%. **Slotted ALOHA:** align transmissions to time slots (capped at ~37%) — the slot halves the vulnerable period.
- The demo computes the vulnerable window for both and why slotted wins.

### 9. CSMA Family
- **CSMA:** listen before talking (1-persistent = talk when idle; non-persistent = wait a random time; p-persistent = talk with probability p).
- **CSMA/CD** (classic Ethernet): detect collisions while sending, **abort, jam, back off exponentially** (binary exponential backoff — after each collision double the range). Collisions only happen in shared half-duplex (hubs); switches made it mostly historical.
- Minimum frame size exists so a collision is detectable before transmission ends (64-byte Ethernet minimum = the reason).

### 10. Ethernet & MAC Addressing
- 48-bit MAC addresses (OUI + device), burned into the NIC; **flat addressing** (no hierarchy, no location meaning) vs IP's hierarchical addresses.
- Ethernet frame: preamble + SFD, destination, source, length/type, payload (46–1500), **FCS**. Switches learn by source MAC and forward by destination MAC (flooding unknowns).
- MTU 1500 and what jumbo frames change.

### 11. Switches, Bridges & VLANs
- A **switch is a many-port bridge**: backward learning fills the MAC table, forwarding decisions are per-frame; store-and-forward vs cut-through.
- **VLANs** partition one physical switch into isolated broadcast domains (by port or tag — 802.1Q adds a 4-byte tag with the VLAN ID); **trunks** carry multiple VLANs between switches.
- Broadcast domains vs collision domains — the two isolation levels.

### 12. HDLC, PPP & ARP
- **HDLC:** bit-oriented, flag-delimited, bit-stuffed; reliable optional. **PPP:** the point-to-point dial-up/serial successor — framing + negotiation (LCP) + authentication (PAP/CHAP) + network-layer setup (NCP).
- **ARP:** the glue between layers 2 and 3 — "who has 192.168.1.1? Tell 192.168.1.10" broadcast, unicast reply, MAC↔IP cached with a timeout. The demo builds a tiny ARP table and resolves a lookup.

---

# Module 03 — Network Layer

*Folder:* [`concepts/03-network-layer`](./concepts/03-network-layer) · ✅ 13 topics

### 1. Network Layer Services & IPv4 Addressing
- The network layer's job: **host-to-host delivery across networks** — addressing, routing, and (in IP) best-effort, connectionless service.
- IPv4: 32-bit, dotted decimal; **network part vs host part**; the mask draws the line. Special addresses: loopback (127/8), broadcast, private ranges (RFC 1918).
- The demo works the classful history (A/B/C defaults) as the entry point to prefix thinking.

### 2. Subnetting
- **Borrow host bits to make more networks:** need s subnets → borrow n bits where 2ⁿ ≥ s; each subnet loses 2 host addresses (network + broadcast).
- Worked example: 192.168.10.0/24 split into 6 subnets → borrow 3 bits → /27, 30 hosts each, masks and ranges printed and cross-checked against Python's `ipaddress` module.
- Exam skill: given an address and a need, produce the mask, the subnets, and the broadcast addresses.

### 3. VLSM & CIDR
- **VLSM:** subnets of different sizes from one network — give the big LAN a short prefix, the point-to-point links a /30.
- **CIDR:** abandon classes entirely; route on arbitrary prefixes — `192.168.0.0/22`; aggregation shrinks routing tables (supernetting).
- The demo allocates a VLSM plan by need (sort descending, allocate first-fit) and verifies it with `ipaddress`.

### 4. IPv4 Header & Fragmentation
- The 20-byte header field by field: version/IHL, **total length, identification, flags, fragment offset, TTL, protocol, checksum**, source/destination.
- **Fragmentation:** when a packet exceeds a link's MTU, routers split it — identification ties the pieces together, offset says where, the **MF (more fragments) flag** chains them; only the final fragment closes; the destination reassembles.
- Why it's bad (loss of one fragment kills the packet; reassembly state at the endpoint) — and why IPv6 dropped it for sender-side path-MTU discovery.

### 5. IPv6
- **128-bit addresses, fixed 40-byte header, no checksum, no fragmentation in routers**; extension headers for options.
- Notation: hexadecimal colon groups, compression rules (:: once, leading zeros dropped); address types (link-local fe80::/10 for neighbors, global unicast).
- Transition mechanisms: **dual stack, tunneling, NAT64**.

### 6. Routing Basics & Dijkstra
- Routing = building the forwarding table; **least-cost path** over a graph.
- **Dijkstra's algorithm:** from a source, repeatedly finalize the nearest unsettled node and relax its edges — greedy, works with non-negative costs. O(E log V) with a heap.
- The demo runs Dijkstra on a small graph, prints the settle order, distance and predecessor table, and derives the shortest path trees.

### 7. Distance-Vector Routing
- **Bellman-Ford in distributed form:** each router knows only its neighbors' distance vectors; iterate "my distance to X = min over neighbors (cost to neighbor + neighbor's distance to X)" until it stabilizes.
- **Count-to-infinity problem:** a link failure makes routers slowly escalate distances; fixes — **split horizon** (don't advertise back where you learned it) and **poisoned reverse** (advertise ∞ back).
- The demo runs the iteration on a 4-router graph, kills a link, and shows the count-to-infinity and its cure.

### 8. Link-State Routing
- The OSPF approach: **flood link-state packets so every router learns the whole topology**, then every router independently runs Dijkstra.
- Steps: discover neighbors → measure costs → flood LSAs → compute the SPF tree. No count-to-infinity (failure floods fast), but more state and CPU.
- DV = know only neighbors, gossip; LS = know everything, compute. The two families of routing protocol.

### 9. Internet Routing Protocols
- **Intradomain (IGP): RIP** (distance-vector, hop count ≤ 15, slow convergence — historical), **OSPF** (link-state, areas, cost by bandwidth, the enterprise standard), **IS-IS** (link-state, ISPs).
- **Interdomain: BGP** — the protocol between autonomous systems; path-vector (carries whole AS paths to kill loops); policy over metrics (business relationships beat shortest path); eBGP vs iBGP.
- The demo builds a tiny AS graph and prints the BGP path selection logic.

### 10. ICMP & Tools
- **ICMP** is IP's control plane: error and diagnostic messages — type 8/0 echo request/reply (**ping**), type 11 TTL exceeded (**traceroute** — how it probes hop by hop with increasing TTLs), type 3 destination/host/port unreachable, redirect.
- The demo crafts an ICMP echo header by hand (type, code, checksum) and decodes it.

### 11. NAT & PAT
- **NAT:** the box rewrites the private source IP to its public one and remembers the mapping (table: inside ip:port ↔ outside ip:port).
- **PAT/NAPT:** also rewrites the **port**, which is what lets one public IP serve thousands of flows — the port is the disambiguator.
- Consequences: breaks inbound connections (port forwarding is the workaround), saves IPv4, complicates peer-to-peer (the reason for STUN/TURN/ICE).

### 12. Congestion Control & QoS
- **Where it belongs:** network-layer queues observe it, transport-layer TCP causes and fixes it (module 04 has the algorithms); this topic covers the router's view — RED (drop early before the queue fills to signal senders), QoS classes, scheduling (FIFO vs priority vs weighted fair queuing).
- Leaky bucket (shape to a constant rate) vs token bucket (allow bursts up to the bucket depth) — the two classic traffic shapers, both simulated in the demo.

### 13. Multicast, IGMP & Mobile IP
- **Multicast:** one-to-many of a group — class D addresses (224/4), the group membership protocol **IGMP** (hosts join/leave, routers track), distribution trees built by routing protocols.
- **Mobile IP:** a host keeps its home address while roaming — home agent + foreign agent + tunnel to the care-of address; triangle routing is the cost.

---

# Module 04 — Transport Layer

*Folder:* [`concepts/04-transport-layer`](./concepts/04-transport-layer) · ✅ 9 topics

### 1. Transport Layer Services & Ports
- **Process-to-process** delivery (the network layer only reaches hosts); the **port number (16 bits)** is the demultiplexing key: well-known 0–1023, registered, ephemeral.
- Sockets: the API endpoint (IP + port); the tuple (src IP, src port, dst IP, dst port) identifies a connection exactly — that's how one server holds thousands of clients.
- `netstat`/`ss` show the tables; the demo parses a `/proc/net/tcp`-style listing.

### 2. UDP Protocol
- An 8-byte header: source port, destination port, length, checksum. **No handshake, no ACKs, no order, no flow control** — just send.
- Use when speed matters more than reliability: DNS queries, VoIP, games, DHCP. Optional checksum (IPv4) but you want it on.
- The demo builds a UDP header with `struct` and shows a DNS query as the case study.

### 3. TCP Header & Segments
- The 20+ byte header: ports, **sequence and acknowledgment numbers (byte positions, not frame counts)**, data offset, the 9 flags (**SYN, ACK, FIN, RST, PSH, URG**...), window, checksum, urgent pointer.
- Sequence numbers count **bytes** of the byte stream; the ACK says "next byte I expect" — cumulative acknowledgment by construction.
- Options: MSS (negotiated in the SYN), SACK-permitted, window scale, timestamps. The demo packs and unpacks a real header with `struct`.

### 4. TCP Connection Management
- **Three-way handshake:** client SYN(seq=x) → server SYN-ACK(seq=y, ack=x+1) → client ACK(ack=y+1) — both sides get their initial sequence numbers confirmed; both know the other's ISN.
- **Teardown:** FIN, ACK, FIN, ACK (each direction closes separately); TIME_WAIT on the closer (2 MSL) so a wandering FIN doesn't kill a new incarnation of the connection.
- **The state machine:** LISTEN → SYN-SENT/SYN-RECEIVED → ESTABLISHED → FIN-WAIT/CLOSE-WAIT → CLOSED. The demo prints the transitions as it walks a simulated connection.

### 5. TCP Reliability & Retransmission
- **ACK + timeout + retransmit** with cumulative ACKs; **adaptive RTT estimation:** `sRTT = α·sRTT + (1−α)·sample`, deviation tracking, RTO = sRTT + 4·dev.
- **Fast retransmit:** 3 duplicate ACKs = a loss, retransmit without waiting for the timer. **SACK** option reports the holes precisely.
- The demo simulates loss with a seed, runs both slow timeout recovery and fast retransmit, and prints the timeline.

### 6. TCP Flow Control
- The receiver advertises `rwnd` in every ACK — "my buffer has this much room"; the sender keeps `in-flight ≤ rwnd`. Zero window → sender probes (window probe) until the receiver drains.
- The demo runs a producer faster than a consumer and shows the window closing and reopening — no drops, pure pacing.

### 7. TCP Congestion Control
- **The difference:** flow control protects the receiver; congestion control protects the network.
- **Slow start:** cwnd doubles per RTT (exponential) until ssthresh; **congestion avoidance:** +1 MSS per RTT (linear — AIMD); **loss = multiplicative decrease** (ssthresh = cwnd/2, restart).
- **Fast recovery** after 3 dup ACKs (Reno); CUBIC (the Linux default) grows cwnd on a cubic curve after loss. The demo plots cwnd over time for a simulated flow with one loss.

### 8. TCP vs UDP & Modern Transport
- Choose TCP for correctness (HTTP/1.1, email, SSH); UDP for speed and control (DNS, QUIC's base).
- **QUIC** (HTTP/3): UDP-carried, integrated TLS, no head-of-line blocking across streams, 0/1-RTT handshakes — TCP's lessons rebuilt at the application layer.
- The demo tabulates the header costs and handshake latencies side by side.

### 9. Socket Programming
- The real thing, on loopback: TCP server (`socket → bind → listen → accept → recv/send`), client (`socket → connect → send/recv`), UDP (`sendto`/`recvfrom`), `settimeout`, graceful `shutdown`, and **framing over the TCP byte stream** (length-prefix) — because `recv` returns whatever arrived, not messages.
- All of it bound to `127.0.0.1` — the ethics rule, in code.

---

# Module 05 — Session & Presentation Layer

*Folder:* [`concepts/05-session-and-presentation-layer`](./concepts/05-session-and-presentation-layer) · ✅ 7 topics

### 1. Session Layer
- Dialog control: establish, manage, synchronize and tear down sessions; **full-duplex/half-duplex modes**; checkpoints (synchronization points) so a long transfer can resume rather than restart.
- In the modern stack the session layer is mostly absorbed into applications and protocols (RPC, TLS sessions, SIP), but the concept — conversation state and recovery — remains.

### 2. Data Representation & Encoding
- The presentation problem: byte order (**big-endian network order** vs host order — `htons`/`ntohl`), character encodings (ASCII → UTF-8), and structured formats (XDR, ASN.1, and today's JSON/Protocol Buffers).
- The demo packs the same struct in both endiannesses with `struct` and shows what a mismatched reader sees (the mojibake class of bug).

### 3. Compression Techniques
- **Lossless:** run-length encoding (long runs → count+symbol), Huffman coding (frequent symbols get short bit strings — the prefix property guarantees unambiguous decoding), LZW (dictionary of seen strings; GIF, old ZIP).
- **Lossy:** DCT-based JPEG, quantization. The demo builds a Huffman code from a measured frequency table, encodes text, and prints the compression ratio.

### 4. Cryptography Fundamentals
- **Symmetric ciphers:** one shared key; fast; the key-distribution problem. Stream vs block ciphers; **ECB mode leaks patterns** (the penguin picture lesson), CBC/GCM chain and authenticate.
- **One-time pads:** perfect secrecy, unusable in practice; Kerckhoffs's principle — the system's security rests on the key, not the secrecy of the algorithm.
- The demo implements a toy substitution cipher, breaks it by frequency analysis, and shows why real ciphers resist it.

### 5. Public-Key Crypto & Key Exchange
- **Asymmetric:** a key pair — public encrypts, private decrypts; the hard problems (factorization for RSA, discrete log for DH). Slow, so it's used to agree on a symmetric key, not to bulk-encrypt.
- **Diffie-Hellman key exchange:** both sides mix their private number with the shared public one; the mixtures cross and arrive at the same secret without it ever being sent. Vulnerable to the man in the middle — fixed by authenticating the exchange (certificates).
- The demo runs the DH math on small numbers and prints the shared secret agreeing on both sides.

### 6. Hashing, MAC & Digital Signatures
- **Hash functions:** one-way, fixed output, collision-resistant — MD5 (broken), SHA-1 (broken), SHA-256 family (fine). Use cases: integrity, fingerprints, password storage (with salts and slow KDFs — bcrypt/scrypt/argon2, never plain SHA).
- **MAC/HMAC:** hash + shared key = integrity *and* authenticity; attacker can't forge without the key.
- **Digital signatures:** hash the message, encrypt the digest with the *private* key; anyone verifies with the public one — authenticity + integrity + non-repudiation.
- The demo hashes, signs, and verifies, then flips a bit and shows both checks failing.

### 7. TLS / SSL & Secure Channels
- The **TLS handshake** (in slow motion): client hello (cipher suites) → server hello + **certificate** → key exchange → both derive the same session keys → ChangeCipherSpec → Finished (the first message encrypted, and it verifies the handshake itself).
- What the certificate chain proves (identity via a CA signature) and why the handshake defeats eavesdropping and tampering — but only MITM if certificates are actually validated.
- TLS 1.3: one-RTT (and 0-RTT resumption) handshakes, forward secrecy by default. The demo walks the message sequence and derives the keys step by step.

---

# Module 06 — Application Layer

*Folder:* [`concepts/06-application-layer`](./concepts/06-application-layer) · ✅ 11 topics

### 1. Application Layer & Client-Server
- The layer the user meets: processes communicating via transport services. **Client-server** vs **P2P** architectures; **process addressing** = IP + port + protocol; what an app needs from transport (reliability? ordering? latency?) and picking TCP vs UDP accordingly.
- The demo builds a minimal request/response server on loopback TCP.

### 2. DNS Fundamentals
- **The Internet's phone book:** hierarchical, distributed, cached. **Domain name space:** root → TLDs → registrable domains; **resource records** (A, AAAA, CNAME, MX, TXT, NS); **zones and delegation**.
- **Resolution:** stub resolver → recursive resolver → root → TLD → authoritative — iterative queries down the hierarchy; **caching with TTLs** is what makes it scale.
- The demo crafts a real DNS query message (header flags, question section) with `struct` and parses a response.

### 3. DNS Server on Loopback
- A working miniature: a UDP server on `127.0.0.1` that answers A queries from an in-memory zone file, plus the client that formats the query and parses the answer — the full iterative-resolution logic in miniature, including the header's recursion flags and response codes (NOERROR, NXDOMAIN).

### 4. HTTP Basics
- **Request/response, stateless:** methods (GET, POST, PUT, DELETE, HEAD), status codes (**2xx** success, **3xx** redirect, **4xx** client error, **5xx** server error), URL structure.
- Message anatomy: request line + headers + blank line + body; response: status line + headers + body. The demo builds raw requests by hand and reads the raw responses — no library, the wire format itself.

### 5. HTTP Headers, Cookies & Caching
- **Headers** as the negotiation layer: `Host`, `Content-Type`/`Content-Length`, `Authorization`, `Cache-Control`, `ETag`.
- **Cookies:** server sets `Set-Cookie`, client echoes `Cookie:` — session state bolted onto a stateless protocol (with `HttpOnly`, `Secure`, `SameSite`).
- **Conditional requests:** `ETag`/`If-None-Match` and `Last-Modified`/`If-Modified-Since` → **304 Not Modified**; `Cache-Control` freshness rules. The demo walks a cache hit and a revalidation.

### 6. HTTP Versions & Web Architecture
- **1.0** (a connection per request) → **1.1** (persistent connections, pipelining, `Host` header for virtual hosts) → **2** (binary frames, multiplexed streams on one connection — no head-of-line blocking at HTTP level, header compression HPACK) → **3** (QUIC over UDP — no TCP-level HOL blocking, faster handshakes).
- The proxy/CDN/load-balancer tier: where caching, TLS termination and routing live. The demo tabulates per-version wire behavior.

### 7. Email: SMTP, POP3, IMAP
- The three-protocol split: **SMTP** to *push* mail between clients and servers (port 25, `MAIL FROM`/`RCPT TO`/`DATA`, 7-bit history), **POP3** (download-and-delete, port 110) and **IMAP** (server-side folders and flags, port 143) to *pull* it.
- The envelope vs the headers vs the MIME body (attachments as base64 multipart). The demo runs a scripted SMTP conversation on loopback and drops the message into a mailbox file.

### 8. FTP, TFTP, Telnet & SSH
- **FTP:** two channels — control (21, persistent) and data (20, per transfer) — active vs passive mode; the demo runs the control conversation.
- **TFTP:** UDP, trivial, no auth — PXE boot's loader. **Telnet:** plaintext everything (why it's dead) vs **SSH:** encrypted, authenticated, port 22, and the host-key fingerprint trust model.

### 9. DHCP & Bootstrapping
- **The four-packet dance:** Discover (broadcast) → Offer (a server proposes an address) → Request (client broadcasts acceptance — so other servers retract) → ACK. **Lease time** and renewal at T1/T2.
- The magic: a host with no address uses 0.0.0.0 → 255.255.255.255 broadcasts and `chaddr` (its MAC) as identity. DHCP options carry DNS, gateway, boot files (PXE).
- The demo simulates the four exchanges with a lease table.

### 10. SNMP & Network Management
- **SNMP:** the manager polls agents with **Get/GetNext/Set**, agents push **Traps**; the **MIB** is the tree of object IDs (OIDs); versions v1/v2c (community strings — effectively plaintext passwords) and v3 (real auth + encryption).
- The demo walks an OID tree and encodes a GetRequest PDU.

### 11. Peer-to-Peer & Streaming
- **P2P:** no central server; **DHTs** (Chord-style) route lookups in O(log n) hops; BitTorrent's tit-for-tat economics — peers trade pieces, seeders give. NAT traversal (STUN/TURN) is the practical pain.
- **Streaming:** the buffer is the trick — play while downloading; **DASH** adapts quality to measured throughput; CDN edge caching puts the bits near the viewer. The demo computes buffer occupancy over time and the ABR decision.

---

# Module 07 — Wireless, Security & Tools

*Folder:* [`concepts/07-wireless-security-and-tools`](./concepts/07-wireless-security-and-tools) · ✅ 8 topics

### 1. Wireless LANs & Wi-Fi
- **802.11** basics: radio as a shared medium — everyone hears everyone, collisions can't be detected while sending → **CSMA/CA** (avoid, not detect): ACKs, interframe spaces, optional RTS/CTS to solve the **hidden terminal** problem.
- The **BSS/ESS** structure (access point, SSID, roaming); channels and the 1/6/11 non-overlapping set in 2.4 GHz; security evolution WEP (broken) → **WPA2-PSK (4-way handshake)** → WPA3 (SAE).
- The demo computes airtime and shows why CSMA/CA ACKs every frame.

### 2. Mobile & Cellular Networks
- The **handover** problem: move without dropping the call; **cells and frequency reuse** (the N-cell reuse pattern that multiplies capacity); HLR/VLR-style tracking of where a phone is.
- Generations in one line each: 1G analog voice → 2G digital + SMS → 3G data → 4G LTE all-IP → 5G (mmWave, network slicing, low latency).
- The demo works a frequency-reuse plan and a handover decision.

### 3. Firewalls & Access Control
- **Packet filters** (stateless ACLs on IP/port), **stateful firewalls** (connection tracking — established flows pass, unsolicited inbound doesn't), **application-layer/proxy firewalls** (inspect the payload).
- **ACLs** in and out; default-deny as the design principle; DMZ architecture (public servers isolated from the interior). NAT as an accidental firewall.
- The demo evaluates an ACL rule list against a flow table and prints the verdicts.

### 4. Common Network Attacks Explained
- **Eavesdropping/sniffing** (plaintext protocols invite it; the fix is TLS), **ARP spoofing** (fake MAC↔IP mappings on the LAN — the fix is dynamic ARP inspection), **IP spoofing**, **DoS/DDoS** (SYN floods exhausting the accept queue — the fix is SYN cookies and clean-up), **DNS spoofing/hijacking** (wrong answers — the fix is DNSSEC/DoT), **port scanning/reconnaissance** (the fix is detection, and the ethics: only your own hosts).
- Each attack is an **in-memory simulation shown next to its defense** — nothing touches a real host, by construction.

### 5. Packet Dissection & Headers
- Reading a packet top to bottom: **Ethernet** (MACs, type) → **IP** (version, IHL, TTL, protocol, checksum) → **TCP/UDP** (ports, seq/ack, window) → payload — exactly what Wireshark shows.
- `struct.unpack` on real captured bytes (loopback demos), checking checksums, identifying the protocol chain by the type/protocol fields.
- The demo builds a valid nested header stack and then dissects it back layer by layer.

### 6. VPN, Tunneling & Network Security Models
- **Tunneling:** wrap packets of one protocol inside another — the encapsulate/decapsulate pair at the tunnel's ends. **VPNs:** IPsec (site-to-site, ESP encryption + AH authentication, IKE for keys) and TLS VPNs; what a VPN does and doesn't hide.
- **Security models:** perimeter (castle-and-moat) vs **zero trust** (authenticate every flow, no implicit trust by network location) — the modern replacement.
- The demo encapsulates a packet through a simulated tunnel and checks integrity at the far end.

### 7. Network Tools & Troubleshooting
- The toolbox, each mapped to its layer and use: **ping** (ICMP echo — reachability and RTT), **traceroute** (TTL trick — where the path breaks), **ipconfig/ifconfig**, **netstat/ss** (sockets and listeners), **nslookup/dig** (DNS), **arp**, **route/ip route**, **tcpdump/Wireshark** (the truth on the wire), **nmap** (only on your own systems).
- **The troubleshooting method:** check the cable → check the address → check the ARP/DNS → check the route → check the port → capture the wire. Bottom-up, layer by layer.

### 8. Data Center, Cloud & SDN
- The topology of a data center: **spine-leaf** (every leaf connects to every spine, predictable hops, East-West traffic), top-of-rack switches, server virtualization.
- **SDN:** split the control plane (the brain — a controller) from the data plane (the muscle — switches that just forward by flow table); **OpenFlow** as the southbound API; network virtualization, overlay networks, microsegmentation.
- The demo builds a tiny flow table and a controller's route decision over a leaf-spine fabric.

---

## How to Study These Notes

1. **Predict** the worked example's output before running the demo.
2. **Run** the matching file: `python3 _N_Name.py` — every one exits 0 on Python 3.13, standard library only, loopback only.
3. **Check the self-check:** each demo verifies its own answer (`zlib`, `ipaddress`, `struct`) — read how it checks.
4. **Explain** the protocol in plain English: the problem, the mechanism, the failure mode.
5. **Ship** — the repo's method: write, run, break, explain, ship.

*Consolidated from the completed files in this repository (70 topics, ~14,300 lines of Python, ~11,300 lines of walkthroughs). Every claim here is checkable against the source files next to it.*
