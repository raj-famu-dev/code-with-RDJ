# `_3_DnsServerOnLoopback.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A DNS server is a program that listens on UDP port 53, receives small binary questions and returns small binary answers. This file builds a tiny authoritative server on `127.0.0.1` (the OS picks the port), a client written byte by byte, a TTL cache, and demonstrates the classic mistakes: ignoring the transaction ID, ignoring truncation, and trusting any datagram that arrives.

**Why UDP.** A DNS exchange is one question and one answer. A UDP datagram needs no connection set-up (no three-way handshake), so a lookup costs one round trip and the server keeps no per-client state. The price: no reliability (the client must time out and retry itself) and no protection against forged packets. Large answers (the classic limit is 512 bytes of UDP payload) set the TC (truncated) bit, and the client then repeats the query over TCP port 53. EDNS0 lets clients and servers agree on bigger UDP sizes. Zone transfers between a primary and secondary server use TCP.

**What an authoritative server does.** It holds the zone (a set of records). For each query: match the question name (case-insensitively) and type; reply with RCODE 0 and the matching records with AA=1 (authoritative answer); if the name does not exist reply with RCODE 3 (NXDOMAIN); if the name exists but has no record of the requested type, reply with RCODE 0 and no answers (this is called NODATA). It copies the query's transaction ID and question section into the reply so the client can match them.

**Response codes.** 0 NOERROR, 1 FORMERR (format error), 2 SERVFAIL, 3 NXDOMAIN, 4 NOTIMP, 5 REFUSED.

**Caching.** A client or resolver stores each answer with an expiry of `now + TTL`. Within the TTL it answers locally and sends no packet. After it, it asks again. TTL is chosen by the zone owner: a short TTL (60 s) lets you move a service quickly but costs more queries; a long TTL (a day) saves queries but delays changes.

**Security.**
- Forged replies and cache poisoning: UDP replies are matched to queries only by source address/port, destination port and the 16-bit transaction ID, plus the question. An attacker who can make a resolver ask a question and then race the real answer with a forged one may get a false record cached, redirecting all users of that resolver until the TTL ends. Defences: unpredictable IDs and source ports, matching the question, 0x20 case randomisation, limiting recursion to your own clients and DNSSEC.
- DNSSEC adds digital signatures to DNS data: RRSIG records sign record sets, DNSKEY holds public keys, and DS records link a child zone's key to the parent, forming a chain to the root. It proves the data came from the zone owner and was not changed, but does not encrypt anything.
- DNS over TLS (DoT, port 853) and DNS over HTTPS (DoH, RFC 8484) encrypt the hop between client and resolver. They protect privacy against eavesdroppers on the network, not the correctness of the zone data.
- Open recursive resolvers can be abused in amplification attacks (a small query produces a big answer sent to a victim's forged address), so resolvers should answer only their own clients.

**Typical exam questions.** Why does DNS use UDP? What happens when a response does not fit in 512 bytes? Distinguish NXDOMAIN and NODATA. How does a client match a response to its query? What is cache poisoning and how is it prevented? What does DNSSEC protect and what does it not?

## Full Line-by-Line Breakdown

### SECTION 1: WHAT THE SERVER MUST DO
Lists the five server steps and prints the fake zone. The zone is a dictionary mapping `(name, type)` to a list of addresses and a TTL; the names use the reserved `.test` TLD and RFC 5737 documentation addresses.

Output from a real run:

```text
===== SECTION 1: WHAT THE SERVER MUST DO =====
1. receive a UDP datagram, 2. parse header + question, 3. look up the zone,
4. build a reply with the SAME transaction ID and question,
5. RCODE 0 + answers, or RCODE 3 (NXDOMAIN) if the name does not exist,
   or RCODE 0 + zero answers (NODATA) if the name exists but not that type.
Zone (fake): {'www.example.test A': (['192.0.2.10', '192.0.2.11'], 60), 'mail.example.test A': (['192.0.2.25'], 300)}
```

### SECTION 2: THE PACKET LOGIC (NO SOCKETS YET)
`build_reply` is a pure function from query bytes to reply bytes, which makes it easy to test without any network. It reads the header and question, builds a key `(lowercased name, type)` and picks one of three outcomes. Each answer record starts with `c0 0c`, a compression pointer to the question name at offset 12 (see the previous file). Flags are `0x8400 | RD | RA | RCODE`: QR=1 (response) and AA=1. The test queries show mixed-case matching (`WWW.Example.TEST`), NXDOMAIN (`rcode=3`) and NODATA (type 28 AAAA, `rcode=0`, no IPs).

Output from a real run:

```text
===== SECTION 2: THE PACKET LOGIC (NO SOCKETS YET) =====
  www.example.test       type=1   -> rcode=0 aa=1 ips=['192.0.2.10', '192.0.2.11'] ttl=60
  WWW.Example.TEST       type=1   -> rcode=0 aa=1 ips=['192.0.2.10', '192.0.2.11'] ttl=60
  nothere.example.test   type=1   -> rcode=3 aa=1 ips=[] ttl=None
  www.example.test       type=28  -> rcode=0 aa=1 ips=[] ttl=None
check: OK (case-insensitive match, NXDOMAIN=3, NODATA=0 with no answers)
```

### SECTION 3: SERVER ON A UDP SOCKET + HAND-BUILT CLIENT
`DnsServer` binds a UDP socket to `127.0.0.1` port 0, uses `settimeout(0.2)` so its loop can notice the `stop` event, and answers each datagram with `sendto`. The `lookup` client opens a fresh UDP socket per query (a fresh random source port each time), sends and waits at most 2 seconds. UDP needs no `accept` or `connect`. A `try/finally` stops and joins the server thread so nothing is left running.

Output from a real run:

```text
===== SECTION 3: SERVER ON A UDP SOCKET + HAND-BUILT CLIENT =====
server listening on UDP 127.0.0.1 port <chosen by OS, port 0>
  www.example.test       id=0x1001 OK        ips=['192.0.2.10', '192.0.2.11'] ttl=60
  mail.example.test      id=0x1002 OK        ips=['192.0.2.25'] ttl=300
  ghost.example.test     id=0x1003 NXDOMAIN  ips=[] ttl=None
server saw 3 queries
```

### SECTION 4: CACHING WITH TTL
`CachingClient` keeps `name -> (ips, expiry)` and uses a simulated clock so the demo is instant and repeatable. TTL is 60 s, so a lookup at t=0 misses, 30 and 59 hit, 60 misses again (the entry expires when `now >= expiry`) and 61 hits the refreshed entry. The server's own counter proves only 2 of 5 lookups became packets.

Output from a real run:

```text
===== SECTION 4: CACHING WITH TTL =====
  t= 0s  www.example.test -> ['192.0.2.10', '192.0.2.11'] from server
  t=30s  www.example.test -> ['192.0.2.10', '192.0.2.11'] from cache (expires t=60s)
  t=59s  www.example.test -> ['192.0.2.10', '192.0.2.11'] from cache (expires t=60s)
  t=60s  www.example.test -> ['192.0.2.10', '192.0.2.11'] from server
  t=61s  www.example.test -> ['192.0.2.10', '192.0.2.11'] from cache (expires t=120s)
server queries used: 2 (TTL=60: t=0 and t=60 missed, the other three hit the cache)
check: OK (5 lookups, only 2 reached the server)
```

### SECTION 5: TRAP - TRANSACTION ID MISMATCH
A script-owned "fake server" socket receives the client's query, then sends the client two replies: first a forged one with a different transaction ID and a bogus address (a documentation address), then the genuine one. The naive client takes the first datagram it receives and gets the forged data. The strict client checks that the reply ID equals the one it sent and keeps waiting otherwise, so it gets the real answer. This is all on loopback and between sockets the script owns; it is a model of why the ID check matters, not an attack tool.

Output from a real run:

```text
===== SECTION 5: TRAP - TRANSACTION ID MISMATCH =====
UDP has no connection: ANY datagram that reaches the client's port looks like
a reply. Only the 16-bit ID (and source port/address) tell it apart.
naive client (accepts first datagram): id=0x1234 ips=['192.0.2.10', '203.0.113.66']
strict client (checks ID matches)    : id=0x7777 ips=['192.0.2.10', '192.0.2.11']
Even the ID is weak: 1 in 65536 per forged packet if the attacker can guess the
source port. Fix: random ID AND random source port, plus checking the question.
```

### SECTION 6: TRUNCATION (TC BIT)
A zone entry with 40 A records needs 674 bytes (12 header + 22 question + 40 x 16 bytes of records), more than 512. `build_reply` detects the size, returns only header and question, and sets TC=1. The client sees TC=1 and zero answers: it must retry over TCP. (The demo stops there; the retry is described, not implemented.)

Output from a real run:

```text
===== SECTION 6: TRUNCATION (TC BIT) =====
40 A records need 674 bytes; classic DNS-over-UDP limit is 512 bytes
over UDP the server answers tc=1, answers kept=0
TC=1 tells the client: 'incomplete, retry this query over TCP port 53'.
(EDNS0 lets clients advertise larger UDP sizes; TCP stays the fallback.)
check: OK
server thread stopped: True
```

### SECTION 7: DNS SECURITY NOTES (CONCEPTUAL)
Text only. It computes the guess odds (2^16 and 2^32), then summarises cache poisoning, its defences, DNSSEC and encrypted DNS. Nothing here sends forged data to any real resolver.

Output from a real run:

```text
===== SECTION 7: DNS SECURITY NOTES (CONCEPTUAL) =====
Spoofing / cache poisoning: an attacker tries to get a resolver to cache a
false answer by winning a race with the real reply. Success needs matching:
  the ID (16 bits) and, if randomised, the source port (up to 16 bits more).
  ID only          : 1 in 65,536 per forged packet
  ID + random port : 1 in 4,294,967,296 (upper bound; real port ranges are smaller)
A poisoned cache then sends EVERY user of that resolver to the wrong address
until the TTL expires. Defences: random ID + port, 0x20 case randomisation,
validating that the answer matches the question, and DNSSEC.
DNSSEC (RFC 4033-4035): zones SIGN their records (RRSIG), publish keys (DNSKEY)
and a chain of trust (DS records) up to the root. Proves AUTHENTICITY and
INTEGRITY; it does NOT hide which names you look up.
DNS over TLS (port 853) and DNS over HTTPS (RFC 8484, port 443) ENCRYPT the
client-to-resolver hop for privacy; they do not authenticate the zone data.
```

## Worked Example
**Problem.** A client sends a query with ID `0x7777` for `www.example.test`. Two UDP datagrams reach its socket: the first has ID `0x1234`, the second `0x7777`. Which does a correct client accept? Also: a response with 40 A records (16 bytes each as in this file) is built; will it fit in a 512-byte UDP reply?

**Solution.** It accepts the second (ID match), and ignores the first. Size: header 12 + question (`03 www 07 example 04 test 00` = 1+3+1+7+1+4+1 = 18, + 4 for type/class = 22) = 34 bytes; each answer is 2 (pointer) + 10 (type, class, TTL, length) + 4 (address) = 16 bytes, so 34 + 40 x 16 = 674 > 512. The server must truncate and set TC. The program prints 674 for `big.example.test` (the name there is `big.example.test`, also 18 bytes of name), matching.

## Key Rules / Gotchas Recap
- Always check the reply's transaction ID (and source) against your query; use a random ID and source port.
- Copy ID and question into the reply; match names case-insensitively.
- NXDOMAIN (name missing) is RCODE 3; NODATA is RCODE 0 with an empty answer.
- Over 512 bytes (without EDNS0): set TC and let the client retry over TCP.
- Cache until `now + TTL`; after that, ask again.
- Servers must never crash on malformed packets: catch parsing errors and drop.
- UDP sockets: `bind` the server, `sendto`/`recvfrom`, always set a timeout.
- DNSSEC = authenticity; DoT/DoH = privacy. Neither does the other's job.

## Why This Matters
Writing a toy server shows exactly what a resolver, a service-discovery system or a DNS-based security tool must parse and validate. Cache poisoning and amplification are real attack classes, and the ID-matching rule is the same principle behind validating any untrusted response.
