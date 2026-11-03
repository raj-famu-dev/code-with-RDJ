# `_9_DhcpAndBootstrapping.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
DHCP (Dynamic Host Configuration Protocol) lets a host that has just joined a network obtain an IP address, subnet mask, default gateway, DNS servers and other settings automatically from a server, for a limited time called a lease. It exists because configuring addresses by hand does not scale and causes conflicts; with DHCP, addresses are reused as devices come and go. It runs over UDP: the client uses port 68 and the server port 67.

**DORA.** A client with no address goes through four steps:
1. DISCOVER: broadcast (source 0.0.0.0, destination 255.255.255.255) asking "any DHCP server?".
2. OFFER: a server proposes an address (field `yiaddr`) and options.
3. REQUEST: the client broadcasts that it accepts one offer, naming the chosen server (option 54); broadcasting lets losing servers release their offer.
4. ACK: the server confirms and gives the lease time, mask, router and DNS. If the address cannot be given the server sends NAK. A client that finds the address already in use (usually after an ARP probe) sends DECLINE; a client leaving sends RELEASE.

**Message format (RFC 2131, the same layout as BOOTP).** 236 fixed bytes: op (1 request, 2 reply), htype (1 = Ethernet), hlen (6), hops, xid (4-byte transaction id chosen by the client), secs, flags (the top bit asks for a broadcast reply), ciaddr (the client's address when renewing), yiaddr ("your" address, the one being offered), siaddr (next server), giaddr (relay agent address), chaddr (16 bytes, client MAC), sname (64) and file (128). Then a 4-byte magic cookie `63 82 53 63`, then options as type-length-value triples: 53 message type (1 DISCOVER, 2 OFFER, 3 REQUEST, 4 DECLINE, 5 ACK, 6 NAK, 7 RELEASE, 8 INFORM), 54 server identifier, 51 lease time, 1 subnet mask, 3 router, 6 DNS servers, 50 requested IP, 61 client identifier, 255 end.

**Lease timers.** T1 = 0.5 x lease: the client tries to renew by unicast with the server that gave the lease (REQUEST with `ciaddr` set, ACK extends the lease). T2 = 0.875 x lease: if renewing failed, the client rebinds by broadcasting to any server. When the lease ends the client must stop using the address and start again from DISCOVER. For an 8-hour lease: T1 = 4 h, T2 = 7 h.

**Relay agent.** Routers do not forward broadcasts, so each subnet would need its own DHCP server. A relay agent (a router interface) hears the client's broadcast and forwards it by unicast to a central server after writing its own address into `giaddr`; the server uses `giaddr` to choose the matching address scope, and sends the reply back through the relay.

**APIPA / link-local.** If no DHCP server answers, many systems assign themselves an address in 169.254.0.0/16 (IPv4 link-local, RFC 3927), after checking with ARP that nobody uses it. Hosts on the same link can talk to each other, but there is no gateway. Seeing a 169.254.x.x address is a classic sign that DHCP failed.

**Attacks and defences.**
- DHCP starvation: an attacker sends many DISCOVER/REQUEST messages with forged client MAC addresses until the pool is empty, so real clients get nothing (a denial of service, and often a first step to a rogue server). Defences: port security (limit the number of MAC addresses per switch port), DHCP snooping rate limiting.
- Rogue DHCP server: an unauthorised device answers first and hands out a wrong gateway or DNS server, enabling a man-in-the-middle attack. Defence: DHCP snooping, where the switch marks ports as trusted (where the real server is) or untrusted and drops OFFER/ACK messages from untrusted ports; snooping also builds a table of legitimate IP-MAC-port bindings used by dynamic ARP inspection.

**BOOTP and NTP.** BOOTP (RFC 951) is the earlier protocol with the same ports and packet layout: a static table maps MAC addresses to IP addresses and a boot file, without leases or pools; DHCP extends it. NTP (Network Time Protocol, UDP port 123) synchronises clocks. Servers are arranged in strata: stratum 0 is a reference clock (GPS, atomic), stratum 1 servers are connected directly to it, stratum 2 synchronise to stratum 1 and so on. From four timestamps (t0 client sends, t1 server receives, t2 server sends, t3 client receives) NTP computes the offset ((t1 - t0) + (t2 - t3)) / 2 and the round-trip delay (t3 - t0) - (t2 - t1).

**Typical exam questions.** Explain DORA with a timing diagram. Why are DISCOVER and REQUEST broadcast? What does a relay agent do and which field does it set? Compute T1 and T2 for a given lease. Name two DHCP attacks and their defences. What address is 169.254.x.x? Compute NTP offset and delay.

## Full Line-by-Line Breakdown

### SECTION 1: WHY DHCP AND THE DORA EXCHANGE
An ASCII timeline of Discover, Offer, Request, Acknowledge, with the ports and the reason for broadcasts.

Output from a real run:

```text
===== SECTION 1: WHY DHCP AND THE DORA EXCHANGE =====
A new host knows only its MAC address. It needs an IP, a mask, a default router and
a DNS server. DHCP (RFC 2131) hands these out automatically from a pool, for a LEASE.
  client (0.0.0.0)                              server
     | --- DISCOVER (broadcast 255.255.255.255) --> |   D: "is there a DHCP server?"
     | <-- OFFER   (yiaddr = proposed address) ---- |   O: "you may have 192.168.1.100"
     | --- REQUEST (broadcast, names the server) -> |   R: "I accept that offer"
     | <-- ACK     (lease time, mask, router, DNS) - |   A: "it is yours for N seconds"
  UDP: client port 68, server port 67. Broadcast because the client has no IP yet.
Why is REQUEST broadcast? So OTHER DHCP servers that made offers learn they lost.
Other messages: DECLINE (address in use), NAK (server refuses), RELEASE, INFORM.
```

### SECTION 2: THE MESSAGE FORMAT PACKED WITH struct
`HEADER = struct.Struct("!BBBBIHH4s4s4s4s16s64s128s")` mirrors the 14 fixed fields: `!` network byte order, `B` 1 byte, `H` 2 bytes, `I` 4 bytes, `4s` four raw bytes (an IP), `16s`, `64s`, `128s` raw strings. Its size is checked to be exactly 236 (the assertion adds the table's sizes). `pack_dhcp` writes the header, the magic cookie, a mandatory message-type option and extra options as code, length, value, then the end marker 255. The hex dump shows `01 01 06 00` (op, htype, hlen, hops), the xid `a1b2c3d4` in network order, flags `8000` (broadcast), and the options at byte 240: `35 01 01` (53, length 1, DISCOVER), `3d 07 ...` (61 client identifier) and `ff`. `parse_dhcp` checks the cookie and walks the TLV options into a dict. The round trip confirms xid, MAC and type.

Output from a real run:

```text
===== SECTION 2: THE MESSAGE FORMAT PACKED WITH struct =====
field    bytes  meaning
op           1  1 request, 2 reply
htype        1  1 = Ethernet
hlen         1  6 (MAC length)
hops         1  relay hop count
xid          4  transaction id
secs         2  seconds elapsed
flags        2  bit 15 = broadcast reply
ciaddr       4  client IP (renewing)
yiaddr       4  'your' IP (offered)
siaddr       4  next server
giaddr       4  relay agent IP
chaddr      16  client hardware address
sname       64  server name (unused)
file       128  boot file name
fixed part = 236 bytes, + 4-byte magic cookie 63 82 53 63, then options (TLV)

DISCOVER packed: 253 bytes. First 28 bytes in hex:
   01 01 06 00 a1 b2 c3 d4 00 00 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
   op=01 htype=01 hlen=06 hops=00 | xid=a1b2c3d4 | secs=0000 flags=8000 | ciaddr=0.0.0.0 ...
   options start at byte 240: 35 01 01 3d 07 01 02 00 00 00 00 01 ff
   = 53 (msg type) len 1 value 01 (DISCOVER) | 61 (client id) len 7 ... | ff (end)
check: OK (parse(pack(x)) gives back xid, MAC and message type)
```

### SECTION 3: AN IN-MEMORY DHCP SERVER
`Scope` holds the pool (here only three addresses), lease length, router, the lease table (MAC to address and expiry) and `pending` offers. `DhcpServer.handle` takes real packed bytes and returns packed bytes, so the client and server in the simulation communicate with the actual wire format. DISCOVER picks the existing lease for that MAC, else the requested address if free, else the first free address, reserves it as pending and answers OFFER; if the pool is empty it stays silent. REQUEST is accepted (ACK) only if it matches the pending offer or an existing lease; otherwise the reply is NAK; a REQUEST naming a different server withdraws our offer. RELEASE removes the lease. A simulated clock `now` drives expiry: `reclaim` frees leases whose expiry time is not in the future.

The printed story: A, B and C get .100, .101, .102 (free count falls to 0). D's DISCOVER gets no OFFER. At t=1800 (T1) A renews with a unicast REQUEST carrying `ciaddr` and no `yiaddr`: the ACK moves A's expiry from 3600 to 5400. At t=3601 B and C have expired, so D gets B's old address .101. A then releases, freeing .100.

Output from a real run:

```text
===== SECTION 3: AN IN-MEMORY DHCP SERVER =====
Pool 192.168.1.100-102 (3 addresses), lease 3600 s, simulated clock.

Client A:
  D  DISCOVER xid=0x7857dd86 yiaddr=0.0.0.0        ciaddr=0.0.0.0         [01] 0.0.0.0 -> 255.255.255.255
  O  OFFER    xid=0x7857dd86 yiaddr=192.168.1.100  ciaddr=0.0.0.0        lease=3600s router=192.168.1.1
  R  REQUEST  xid=0x7857dd86 yiaddr=0.0.0.0        ciaddr=0.0.0.0        wants=192.168.1.100
  A  ACK      xid=0x7857dd86 yiaddr=192.168.1.100  ciaddr=0.0.0.0        lease=3600s router=192.168.1.1
Client B:
  B got 192.168.1.101
Client C:
  C got 192.168.1.102
Client D (pool is full):
  D  DISCOVER xid=0x940eee3c yiaddr=0.0.0.0        ciaddr=0.0.0.0         [04] 0.0.0.0 -> 255.255.255.255
  (no OFFER: the pool is exhausted, the client keeps retrying)
t=0: free=0 leases=[01->192.168.1.100 (expires 3600), 02->192.168.1.101 (expires 3600), 03->192.168.1.102 (expires 3600)]

Renewal: at T1 = 1800 s client A unicasts REQUEST with ciaddr set (no new DORA):
  R  REQUEST  xid=0x00001111 yiaddr=0.0.0.0        ciaddr=192.168.1.100  
  A  ACK      xid=0x00001111 yiaddr=192.168.1.100  ciaddr=0.0.0.0        lease=3600s router=192.168.1.1
t=1800: free=0 leases=[01->192.168.1.100 (expires 5400), 02->192.168.1.101 (expires 3600), 03->192.168.1.102 (expires 3600)]

t=3601: B and C never renewed, so their leases ended; D tries again:
  D got 192.168.1.101 (a reclaimed address) | t=3601: free=1 leases=[01->192.168.1.100 (expires 5400), 04->192.168.1.101 (expires 7201)]
A releases politely (DHCPRELEASE, no reply):
  t=3700: free=2 leases=[04->192.168.1.101 (expires 7201)]
```

### SECTION 4: TRAP - REPLIES ARE BROADCAST; MATCH THE xid
The client has no IP when it gets the OFFER, so replies are broadcast (the client asked for that with the broadcast flag) and every client on the segment sees every reply. If two clients start at the same time and a client simply takes the first reply, it can grab the other client's offer. Here B's offer arrives first; the naive A takes `.100`, but the correct A ignores replies whose `xid` and `chaddr` do not match its own and gets `.101`.

Output from a real run:

```text
===== SECTION 4: TRAP - REPLIES ARE BROADCAST; MATCH THE xid =====
Both clients broadcast DISCOVER together. Offers (broadcast) arrive in this order:
   OFFER    xid=0x0000bbbb yiaddr=192.168.1.100  ciaddr=0.0.0.0        lease=3600s router=192.168.1.1 for 02
   OFFER    xid=0x0000aaaa yiaddr=192.168.1.101  ciaddr=0.0.0.0        lease=3600s router=192.168.1.1 for 01
naive client A takes the FIRST offer -> 192.168.1.100 (that was meant for B!)
correct client A filters on xid and chaddr -> 192.168.1.101
check: OK (xid + chaddr identify which reply belongs to which client)
```

### SECTION 5: LEASE TIMERS, REBINDING AND APIPA
Computes T1 and T2 for three lease lengths (0.5 and 0.875 of the lease) and verifies 8 h gives 4 h and 7 h. A small timeline shows what happens when the server dies right after the ACK: renewal fails at T1, rebinding fails at T2, the lease ends at 3600 s and the client must drop the address; then it falls back to a seeded random 169.254.x.x address, which is checked to lie inside 169.254.0.0/16.

Output from a real run:

```text
===== SECTION 5: LEASE TIMERS, REBINDING AND APIPA =====
T1 = 50% of lease: renew with the SAME server (unicast).
T2 = 87.5% of lease: if no answer, REBIND: broadcast to ANY server.
End of lease: stop using the address, restart DORA.
  lease   3600 s ( 1.00 h): T1=    1800 s (0.50 h)  T2=    3150 s (0.875 h)
  lease  28800 s ( 8.00 h): T1=   14400 s (4.00 h)  T2=   25200 s (7.000 h)
  lease  86400 s (24.00 h): T1=   43200 s (12.00 h)  T2=   75600 s (21.000 h)
check: OK (8 h lease -> T1 = 4 h, T2 = 7 h)

Timeline when the server dies right after the ACK (lease 3600 s):
  t=   0 s  ACK received, address in use
  t=1800 s  T1: unicast renew -> no reply
  t=3150 s  T2: broadcast rebind -> no reply
  t=3600 s  lease expired: drop the address
Fallback (APIPA / IPv4 link-local, RFC 3927): self-assign 169.254.83.77/16 from 169.254.0.0/16,
first probing with ARP to check nobody uses it. Works only on the local link: no
router, no Internet. Seeing 169.254.x.x on a PC means 'DHCP failed'.
```

### SECTION 6: RELAY AGENT
One server with three scopes. A DISCOVER with `giaddr` 0.0.0.0 comes from the local subnet and uses the first scope; `giaddr = 10.0.2.1` makes the server pick the 10.0.2.0/24 scope, and so on. Each client gets an address and router from its own subnet even though one server serves all.

Output from a real run:

```text
===== SECTION 6: RELAY AGENT =====
Broadcasts do not cross routers. A relay agent (usually the router) receives the
broadcast on each subnet and forwards it by UNICAST to the DHCP server, writing its
own interface address into giaddr. The server uses giaddr to pick the right scope.
  DISCOVER with giaddr=0.0.0.0   -> OFFER 10.0.0.50  router=10.0.0.1
  DISCOVER with giaddr=10.0.2.1  -> OFFER 10.0.2.100 router=10.0.2.1
  DISCOVER with giaddr=10.0.3.1  -> OFFER 10.0.3.100 router=10.0.3.1
One server, three subnets. Without a relay you would need a server on every subnet.
```

### SECTION 7: STARVATION, ROGUE SERVER AND DHCP SNOOPING
An in-memory model, nothing leaves the process. `starvation`: the attacker uses 40 forged MACs against a 10-address pool. With no defence it holds all 10 and a legitimate client later gets no answer (`None`). With `Switch(port_security_max=3)` the attacker's port may learn only 3 MAC addresses, so the other frames are dropped, the attacker holds 3 addresses, and the legitimate client is served. `rogue`: a rogue server on an untrusted port answers before the real one. Without snooping the client accepts the first offer, receiving the rogue as router. With snooping only the trusted uplink may send OFFER/ACK, so the rogue's reply is dropped.

Output from a real run:

```text
===== SECTION 7: STARVATION, ROGUE SERVER AND DHCP SNOOPING =====
(An in-memory model of the attack AND the defence. No real network is touched.)
  starvation, no defence                      : attacker holds 10/10 addresses; legit client gets None
  starvation, port security (max 3 MACs/port) : attacker holds  3/10 addresses; legit client gets 192.168.1.103
check: OK (undefended pool is drained; with port security the legit client is served)
Rogue DHCP server (it answers first and names ITSELF as the gateway -> traffic hijack):
  without snooping: offer accepted from 192.168.1.66, router 192.168.1.66
  with snooping   : offer accepted from 192.168.1.1, router 192.168.1.1 (OFFER/ACK from an untrusted port is dropped)
check: OK
Defences: DHCP snooping (trusted ports only for servers; builds a binding table that
also feeds dynamic ARP inspection), port security, rate limits, 802.1X.
```

### SECTION 8: BOOTP AND NTP OVERVIEW
Text about BOOTP and the NTP strata, then the NTP offset and delay formulas applied to timestamps. Client sent at 100.000, server received at 100.130 and replied at 100.134, client received at 100.044 (all in seconds on each side's own clock). Offset = ((0.130) + (0.090)) / 2 = 0.110 s, so the client's clock is 110 ms behind; delay = 0.044 - 0.004 = 0.040 s.

Output from a real run:

```text
===== SECTION 8: BOOTP AND NTP OVERVIEW =====
BOOTP (RFC 951): the ancestor of DHCP, same ports 67/68 and the SAME packet layout
(that is why DHCP's first 236 bytes above are 'BOOTP'). Static MAC->IP table, no
leases, no pool; used by diskless machines to learn their IP and boot file.
DHCP = BOOTP + dynamic pools + leases + options.

NTP (UDP port 123) keeps clocks in step. Stratum 0 = reference clock (GPS, atomic),
stratum 1 = servers wired to it, stratum 2 = clients of stratum 1, and so on.
Example timestamps (s): t0 client send=100.0, t1 server recv=100.13, t2 server send=100.134, t3 client recv=100.044
  offset = ((t1-t0)+(t2-t3))/2 = 0.110 s  (client clock is 110 ms behind)
  delay  = (t3-t0)-(t2-t1)     = 40 ms round trip on the network
check: OK (offset 0.110 s, delay 0.040 s)
```

## Worked Example
**Problem.** A DHCP server leases addresses for 6 hours. (a) Find T1 and T2. (b) A client's server fails at hour 2 and never returns; at what times does the client try what, and what happens at hour 6? (c) A host shows 169.254.12.9; what does that mean?

**Solution.** (a) T1 = 0.5 x 6 = 3 h; T2 = 0.875 x 6 = 5.25 h (5 h 15 min). (b) At 3 h it unicasts a renewing REQUEST to the same server (no reply); at 5.25 h it broadcasts a REQUEST to any server (no reply); at 6 h the lease expires, the client must stop using the address and restart DISCOVER; with no server it falls back to a 169.254.x.x address. (c) It is an automatic link-local address: no DHCP server answered, so the host can reach only its own link, not the Internet. Section 5 prints the same pattern for a 1-hour lease.

## Key Rules / Gotchas Recap
- DORA = Discover, Offer, Request, Acknowledge; UDP server port 67, client port 68.
- DISCOVER and REQUEST are broadcast because the client has no IP yet; REQUEST also tells losing servers.
- Match `xid` (and `chaddr`) before accepting a reply.
- T1 = 50 percent (renew, unicast), T2 = 87.5 percent (rebind, broadcast), then expire.
- `giaddr` is set by a relay agent so one server can serve many subnets.
- 169.254.0.0/16 means DHCP failed (APIPA / link-local).
- Starvation: forged MACs drain the pool; defend with port security. Rogue server: defend with DHCP snooping (trusted ports).
- NTP: offset = ((t1-t0)+(t2-t3))/2, delay = (t3-t0)-(t2-t1).

## Why This Matters
DHCP, DNS and NTP are the quiet infrastructure services every device depends on; a broken or hostile DHCP server silently breaks or hijacks a whole network, and wrong clocks break TLS certificates, logs and authentication. Understanding the packet format also helps when you debug or write network tools and when you configure switches for security.
