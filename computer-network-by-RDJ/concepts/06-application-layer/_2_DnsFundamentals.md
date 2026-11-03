# `_2_DnsFundamentals.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The Domain Name System (DNS) is the Internet's distributed phone book: it translates human-friendly names such as `www.example.com` into the IP addresses that routers and sockets actually use (and back again, plus mail routing and other data). It exists because people cannot remember numbers, and because a single central file (the old `HOSTS.TXT`) could never scale or be kept current for the whole world.

**Hierarchy.** Names are read right to left. The invisible root `.` has top-level domains (TLDs: `com`, `org`, `edu`, country codes like `us`). Each TLD delegates second-level domains (`example.com`) to whoever owns them, and the owner may delegate further (`www.example.com`, `cs.example.com`). Each dot-separated piece is a label (at most 63 bytes); the full name is at most 255 bytes on the wire. Names are case-insensitive. A name ending in a dot is a fully qualified domain name (FQDN).

**Zones and servers.** A zone is the part of the tree one organisation administers. The server that holds the real, original records for a zone is authoritative for it (it sets the AA flag). There are 13 named root server identities (a to m), each served by many machines using anycast. Top-level domain servers know which name servers are authoritative for each domain below them. A recursive resolver (at your ISP, company or a public provider) does the lookup work for clients and caches. Your OS contains only a stub resolver that asks that recursive resolver.

**Recursive vs iterative queries.** In a recursive query the client says "get me the final answer"; the server must either return it or an error. In an iterative query the server answers with the best it knows, often a referral ("ask the .com servers at this address"), and the asker continues. Typical practice: the stub sends one recursive query (RD flag set) to the recursive resolver, which sends iterative queries to root, TLD and authoritative servers.

**Resource records (RR).** Each record has name, type, class (almost always IN = Internet), TTL (seconds it may be cached) and data.

| Type | Code | Data |
|---|---|---|
| A | 1 | IPv4 address |
| NS | 2 | name server for the zone |
| CNAME | 5 | canonical name (alias); a CNAME name cannot hold other records |
| SOA | 6 | primary server, admin mailbox, serial, refresh, retry, expire, minimum |
| PTR | 12 | name for a reverse lookup (`d.c.b.a.in-addr.arpa`) |
| MX | 15 | preference (lower wins) and mail server name |
| TXT | 16 | text strings (SPF, domain verification) |
| AAAA | 28 | IPv6 address |

**Caching and TTL.** Resolvers cache answers until the TTL runs out, which removes most load from upper levels of the tree. Short TTL: changes spread fast but more queries. Long TTL: fewer queries, but a change takes longer to be seen. Negative answers (NXDOMAIN, "name does not exist") are cached too.

**The message format (RFC 1035).** UDP port 53 (and TCP port 53 for large answers and zone transfers). Every message is: a 12-byte header, then four sections (question, answer, authority, additional).

| Header field | Bits | Meaning |
|---|---|---|
| ID | 16 | transaction id, copied into the reply to match them |
| QR | 1 | 0 query, 1 response |
| Opcode | 4 | 0 standard query |
| AA | 1 | authoritative answer |
| TC | 1 | truncated, retry over TCP |
| RD / RA | 1 / 1 | recursion desired / available |
| Z | 3 | reserved |
| RCODE | 4 | 0 no error, 1 format error, 2 server failure, 3 NXDOMAIN, 5 refused |
| QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT | 16 each | number of entries in each section |

A name on the wire is a sequence of length-prefixed labels ending with a zero byte: `www.example.com` is `03 www 07 example 03 com 00`. To save space, a name (or its tail) that already appeared may be replaced by a 2-byte pointer: the first two bits are `11`, the other 14 are the offset from the message start (so `c0 0c` points to byte 12).

**Typical exam questions.** Explain recursive vs iterative resolution with a diagram; list the steps to resolve a name with an empty cache; difference between authoritative and recursive servers; why DNS uses UDP; what does TTL do; which record maps a name to a mail server; what is reverse lookup.

## Full Line-by-Line Breakdown

### SECTION 1: THE NAMESPACE HIERARCHY
An ASCII tree of the namespace and a split of `www.example.com.` into labels from root outward (`com`, `example`, `www`). It also restates the key limits and who plays which role (root, TLD, authoritative, recursive, stub).

Output from a real run:

```text
===== SECTION 1: THE NAMESPACE HIERARCHY =====
            . (root)
       +-------+-------+
      com     org     edu   <- top-level domains (TLDs)
       |
    example              <- second-level domain (owned by someone)
    +---+---+
   www  mail  ns1        <- hosts / subdomains

FQDN: www.example.com. -> labels (right to left = general to specific): ['com', 'example', 'www']
Limits: label <= 63 bytes, whole name <= 255 bytes on the wire, case-insensitive.
Root servers know where each TLD is; TLD servers know who runs each domain;
the AUTHORITATIVE server for example.com holds the real answers for it.
A stub resolver (your OS) asks a recursive resolver (ISP or public) to do the work.
```

### SECTION 2: RECORD TYPES
A formatted table of the eight common record types with type codes and an example line in zone-file style. All addresses are documentation addresses (RFC 5737 / RFC 3849), never real hosts.

Output from a real run:

```text
===== SECTION 2: RECORD TYPES =====
type   code  meaning                             example
A         1  name -> IPv4 address                www.example.com. A 192.0.2.10
AAAA     28  name -> IPv6 address                www.example.com. AAAA 2001:db8::10
CNAME     5  alias -> canonical name             web.example.com. CNAME www.example.com.
NS        2  zone -> its name server             example.com. NS ns1.example.com.
MX       15  domain -> mail server + preference  example.com. MX 10 mail.example.com.
TXT      16  free text (SPF, verification)       example.com. TXT "v=spf1 -all"
PTR      12  IP -> name (reverse lookup)         10.2.0.192.in-addr.arpa. PTR www.example.com.
SOA       6  zone start of authority             example.com. SOA ns1 admin 2024010101 ...
```

### SECTION 3: A DNS QUERY ON THE WIRE
`Writer.name` converts a dotted name into length-prefixed labels. `make_flags` and `decode_flags` pack and unpack the 16 flag bits with shifts (QR is bit 15, RD is bit 8). `build_query` uses `struct.pack("!HHHHHH", ...)`: `!` means network byte order (big endian), `H` is an unsigned 16-bit field, giving the 12-byte header. The hex dump is 29 bytes: 12 header + 13 name (`07 example 03 com 00`) + 4 (type A=1, class IN=1). The assertions compare to bytes written by hand, so the encoder is checked against an independent answer.

Output from a real run:

```text
===== SECTION 3: A DNS QUERY ON THE WIRE =====
query for example.com A, 29 bytes:
  0000  1a 2b 01 00 00 01 00 00 00 00 00 00 07 65 78 61  .+...........exa
  0010  6d 70 6c 65 03 63 6f 6d 00 00 01 00 01           mple.com.....
header (12 bytes): ID=0x1a2b flags=0x0100 (RD=1) QD=1 AN=0 NS=0 AR=0
question: 07 'example' 03 'com' 00 | QTYPE=0001 (A) | QCLASS=0001 (IN)
check: OK (matches hand-built bytes, 12 + 13 + 4 = 29)
```

### SECTION 4: RESPONSE, RECORDS AND NAME COMPRESSION
`write_rr` writes the name, then `!HHI` (type, class, TTL), a placeholder 2-byte RDLENGTH that is patched with `struct.pack_into` once the data is written, then the data. The response holds a CNAME and two A records. With compression the message is 83 bytes versus 139 without. In the dump: `c0 0c` at offset 0x21 is the owner name of the CNAME (points to the question name at offset 12); `c0 10` inside its data points to offset 16, the tail `example.com`, so `web` + pointer builds `web.example.com`; `c0 2d` in the A records points to offset 45, where `web.example.com` was just written. Header bytes `85 80` are QR=1, AA=1, RD=1, RA=1, RCODE=0.

Output from a real run:

```text
===== SECTION 4: RESPONSE, RECORDS AND NAME COMPRESSION =====
response with compression: 83 bytes; without: 139 bytes
  0000  1a 2b 85 80 00 01 00 03 00 00 00 00 03 77 77 77  .+...........www
  0010  07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00  .example.com....
  0020  01 c0 0c 00 05 00 01 00 00 01 2c 00 06 03 77 65  ..........,...we
  0030  62 c0 10 c0 2d 00 01 00 01 00 00 01 2c 00 04 c0  b...-.......,...
  0040  00 02 0a c0 2d 00 01 00 01 00 00 01 2c 00 04 c0  ....-.......,...
  0050  00 02 0b                                         ...
Look for 'c0 0c': a pointer. Top two bits 11 mean 'pointer', the other 14 bits
are an offset from the start of the message. 0x0c = 12 = right after the header,
i.e. the question name 'www.example.com' is reused instead of repeated.
```

### SECTION 5: PARSING (INCLUDING COMPRESSION)
`read_name` walks labels and follows pointers; it remembers where the name ended in the original stream (just after the first pointer) so parsing continues in the right place. `parse_message` unpacks the header, then each question and record, decoding the RDATA by type. The test: the compressed and uncompressed messages decode to equal record lists, and all eight kinds of record (A, AAAA, NS, MX, TXT, SOA, PTR, CNAME) survive build then parse unchanged.

Output from a real run:

```text
===== SECTION 5: PARSING (INCLUDING COMPRESSION) =====
ID: 0x1a2b flags: {'QR': 1, 'Opcode': 0, 'AA': 1, 'TC': 0, 'RD': 1, 'RA': 1, 'RCODE': 0}
question: [('www.example.com', 'A', 1)]
  www.example.com     300 IN CNAME web.example.com
  web.example.com     300 IN A     192.0.2.10
  web.example.com     300 IN A     192.0.2.11
check: OK (compressed and uncompressed messages parse to identical records)

All record types round-trip through the wire format:
  NS    ns1.example.com
  MX    (10, 'mail.example.com')
  TXT   ['v=spf1 -all', 'hello']
  SOA   ('ns1.example.com', 'admin.example.com', 2024010101, 7200, 900, 1209600, 300)
  PTR   www.example.com
  AAAA  2001:db8::10
check: OK (6 records, 209 bytes)
```

### SECTION 6: TRAP - A COMPRESSION POINTER LOOP
A hostile packet can contain a pointer that points at itself, so a naive parser would loop forever (a denial of service). The parser counts jumps and raises after 20. Any code that parses data from the network must bound every loop and check every length.

Output from a real run:

```text
===== SECTION 6: TRAP - A COMPRESSION POINTER LOOP =====
malformed packet: the name at offset 12 is a pointer to offset 12.
A naive parser follows it forever; ours counts jumps and refuses.
rejected: too many compression jumps (pointer loop?)
Real DNS software treats packets from the network as hostile input: bound every loop.
```

### SECTION 7: ITERATIVE RESOLUTION OVER A FAKE HIERARCHY
Three fake servers (root, `com` TLD, `example.com` authoritative) are dictionaries keyed by fake IP addresses; no network is used. `server_answer` returns an answer, a CNAME, a referral or NXDOMAIN. `Resolver` keeps a simulated clock `now`, an answer cache with TTLs and a delegation cache. Step 1 needs 3 queries (root, TLD, authoritative). Step 2 is served from cache (0 queries). Step 3, after the 300 s answer TTL expired, needs only 1 query because the NS delegation (172800 s) is still cached, so the resolver skips root and TLD. Step 4 follows a CNAME. Step 5 shows NXDOMAIN.

Output from a real run:

```text
===== SECTION 7: ITERATIVE RESOLUTION OVER A FAKE HIERARCHY =====
1) cold cache: www.example.com A (iterative: resolver walks root -> TLD -> auth)
    ask 198.51.100.1   (root): referral -> 198.51.100.2
    ask 198.51.100.2   (com TLD): referral -> 203.0.113.53
    ask 203.0.113.53   (example.com authoritative): answer -> ('192.0.2.10', 300)
   result: 192.0.2.10 | server queries: 3
2) same question again at t=10s
    cache HIT  www.example.com A -> 192.0.2.10
   result: 192.0.2.10 | server queries: 0
3) t=400s: answer TTL (300) expired, delegations (172800) still cached
    ask 203.0.113.53   (example.com authoritative): answer -> ('192.0.2.10', 300)
   result: 192.0.2.10 | server queries: 1
4) alias: web.example.com A (CNAME is followed)
    ask 203.0.113.53   (example.com authoritative): cname -> ('www.example.com', 300)
    cache HIT  www.example.com A -> 192.0.2.10
   result: 192.0.2.10 | server queries: 1
5) a name that does not exist
    ask 203.0.113.53   (example.com authoritative): nxdomain
   result: NXDOMAIN | server queries: 1
Recursive vs iterative: YOUR PC sends 1 recursive query to the resolver and gets
1 final answer; the resolver sends the 3 iterative queries above on your behalf.
```

## Worked Example
**Problem.** A resolver with an empty cache must resolve `www.example.com`. (a) How many DNS messages go out from the resolver? (b) A second client asks 200 s later with TTL = 300 s; how many? (c) And at 500 s, if the NS records have TTL 2 days?

**Solution.** (a) Root (returns referral to `.com`), `.com` TLD (referral to the example.com name server), authoritative (the answer): 3 queries. (b) The A record is still in cache (200 < 300): 0 queries. (c) The A record expired but the NS delegation is cached, so ask the authoritative server directly: 1 query. The simulation printed 3, 0 and 1 for the same pattern.

Wire size check: a query for `example.com` is 12 + (1+7+1+3+1) + 4 = 29 bytes, confirmed in Section 3.

## Key Rules / Gotchas Recap
- Names resolve right to left: root, TLD, domain, host. Root and TLD servers give referrals, authoritative servers give answers.
- Stub sends recursive queries; the recursive resolver does iterative ones.
- TTL decides cache lifetime; delegations (NS) usually live far longer than A records.
- Header is 12 bytes in network byte order; ID matches reply to query; TC means retry over TCP.
- A name pointer starts with bits `11`; the offset is from the start of the message.
- Never trust lengths and pointers in packets from the network; limit loops.
- CNAME is an alias and cannot coexist with other records at the same name.

## Why This Matters
DNS is behind every URL, API call and service-discovery system, and "it's always DNS" is a real debugging truth (stale TTLs, missing records, split-horizon surprises). Security tools parse DNS packets; a parser that trusts pointers is a classic vulnerability class.
