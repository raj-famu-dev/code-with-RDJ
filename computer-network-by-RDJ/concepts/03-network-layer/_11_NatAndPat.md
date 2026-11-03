# `_11_NatAndPat.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Network Address Translation (NAT) lets many hosts that use private IP addresses share one or a few public addresses: a border router rewrites the source address (and, with PAT, the port) of outgoing packets and reverses the rewrite for replies. It was invented to stretch the exhausted IPv4 address space and to let a site renumber without touching internal hosts.

**Private vs public.** Private (RFC 1918) ranges `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` can be reused by anyone but are never routed on the public Internet, so they must be translated to reach it.

**Types of NAT.**

| Type | Mapping | Needs | Use |
|---|---|---|---|
| Static NAT | one private <-> one public, permanent | one public address per mapped host | servers that must be reachable from outside |
| Dynamic NAT | one private <-> one public from a pool, temporary | pool at least as big as the number of simultaneous hosts | rarely used today |
| PAT / NAT overload / NAPT | many private <-> ONE public, told apart by port | one public address | home and office routers, the usual meaning of "NAT" |

**PAT operation.**
1. Inside host `192.168.1.10:51000` sends to `198.51.100.9:80`.
2. The router picks an unused public port (say 1024), stores (inside IP:port <-> public IP:port, remote) in the translation table and sends `203.0.113.1:1024 -> 198.51.100.9:80`. Two inside hosts may use the same source port; they get different public ports.
3. The reply to `203.0.113.1:1024` is looked up in the table and rewritten to `192.168.1.10:51000`.
4. The entry expires after a period of inactivity (or when a TCP connection closes).
5. A packet from outside with no table entry is dropped, which is why inbound connections need static mappings (port forwarding).

Terminology (Cisco style): inside local = private address of the inside host, inside global = the public address that represents it, outside global = remote host's address. Checksums (IP header, and TCP/UDP checksums that cover addresses) must be recalculated after rewriting.

**Advantages.** Saves public IPv4 addresses; hides the internal structure; changing ISP only needs a new public address on the router; gives a basic block on unsolicited inbound traffic (a side effect, not a replacement for a firewall).

**Disadvantages.** Breaks the end-to-end principle (a host's address is no longer globally meaningful); inbound connections, peer-to-peer, VoIP and some tunnelling need workarounds (port forwarding, STUN-type techniques, ALGs); protocols that carry IP addresses in their payload (active FTP, SIP) need an ALG to rewrite them; per-flow state limits scale and adds latency; port exhaustion; harder logging and auditing because many users share one address.

**Relation to IPv6.** IPv6 has enough addresses to give each device a global one, restoring end-to-end connectivity, so NAT is unnecessary for address conservation. Translators such as NAT64 exist only to bridge IPv6-only and IPv4-only parts.

Typical exam questions: "Fill in the NAT translation table", "How does PAT let 1000 hosts share one IP?", "Why does NAT break end-to-end?", "NAT vs IPv6".

## Full Line-by-Line Breakdown

### SECTION 1: PRIVATE VS PUBLIC
Checks addresses against the three RFC 1918 networks (note 172.32.4.4 is not private). The simulation uses `203.0.113.0/24` (an RFC 5737 documentation block) as the stand-in for public addresses so that no real address is used.

Output from a real run:

```text
===== SECTION 1: PRIVATE VS PUBLIC =====
192.168.1.10   RFC1918 private=True  
10.0.0.5       RFC1918 private=True  
172.16.4.4     RFC1918 private=True  
172.32.4.4     RFC1918 private=False 
203.0.113.5    RFC1918 private=False documentation range, used below as a stand-in for public addresses
8.8.8.8        RFC1918 private=False 
Private (RFC 1918) addresses are reused by millions of networks, so they are NOT unique
and routers on the Internet drop them. NAT swaps them for a public address at the border.
Simulation below uses 203.0.113.0/24 (RFC 5737 documentation) as the 'public' side.
```

### SECTION 2: STATIC AND DYNAMIC NAT
`Nat` keeps a private-to-public map and a reverse map. `192.168.1.100` has a static mapping. The next three hosts take addresses from a two-address pool in arrival order; the third dynamic host is dropped because the pool is exhausted. A reply to a mapped public address is reversed; a packet for an unknown public address is dropped. This is the reason static/dynamic NAT does not conserve addresses: one public address per active host.

Output from a real run:

```text
===== SECTION 2: STATIC AND DYNAMIC NAT =====
static : 192.168.1.100 <-> 203.0.113.10 (web server reachable from outside at a fixed address)
dynamic: pool = 203.0.113.11, 203.0.113.12 (first come, first served)
  192.168.1.100  -> 203.0.113.10:5000 -> 198.51.100.9:80
  192.168.1.21   -> 203.0.113.11:5000 -> 198.51.100.9:80
  192.168.1.22   -> 203.0.113.12:5000 -> 198.51.100.9:80
  192.168.1.23   -> DROPPED (pool exhausted: only 2 dynamic addresses for 3 hosts)
  reply to 203.0.113.11 is delivered to 192.168.1.21
  unknown public address 203.0.113.99 -> dropped
check: OK
Static NAT = 1:1 permanent; dynamic NAT = 1:1 temporary from a pool. Both need as many
public addresses as simultaneous inside hosts, so they do NOT save addresses.
```

### SECTION 3: PAT / NAT OVERLOAD WITH PORT TABLE
`Pat` has one public address and a port counter. Each new flow key (private IP, port, destination IP, port) gets the next free public port and is recorded both ways. The table printed in the middle is the "translation table" students are asked to complete. Notice that `192.168.1.10:51000` and `192.168.1.11:51000` use the same private port but become 1024 and 1025 outside. The reply to port 1025 is rewritten back to `192.168.1.11:51000`; the unsolicited packet has no entry and is dropped.

Output from a real run:

```text
===== SECTION 3: PAT / NAT OVERLOAD WITH PORT TABLE =====
inside (private)         outside (after PAT)       
192.168.1.10:51000       203.0.113.1:1024           to 198.51.100.9:80
192.168.1.11:51000       203.0.113.1:1025           to 198.51.100.9:80
192.168.1.10:51001       203.0.113.1:1026           to 198.51.100.9:443
192.168.1.12:40000       203.0.113.1:1027           to 198.51.100.77:53

NAT translation table (what the router stores):
inside local           inside global        outside
192.168.1.10:51000     203.0.113.1:1024     198.51.100.9:80
192.168.1.11:51000     203.0.113.1:1025     198.51.100.9:80
192.168.1.10:51001     203.0.113.1:1026     198.51.100.9:443
192.168.1.12:40000     203.0.113.1:1027     198.51.100.77:53

One public IP, many hosts: the PORT number tells replies apart.
reply 198.51.100.9:80 -> 203.0.113.1:1025 is translated back to 192.168.1.11:51000
unsolicited packet from 203.0.113.200:4444 to port 1025 -> dropped (no matching entry)
check: OK
```

### SECTION 4: TRAP - PORT EXHAUSTION
A PAT box with only 3 public ports serves 5 hosts: the first three get ports 1024-1026, the last two get nothing. In real devices the pool is much larger (tens of thousands of ports), but carrier-grade NAT sharing one address among many customers can still run out, so entries expire and pools can be enlarged.

Output from a real run:

```text
===== SECTION 4: TRAP - PORT EXHAUSTION =====
5 hosts, 3 usable ports -> [1024, 1025, 1026, None, None] (None = no free port, new flow is dropped)
Real PAT has tens of thousands of ports per public address, but busy sites
(carrier-grade NAT) can run out; fix = more public addresses in the pool or timeouts that
free idle entries.
```

### SECTION 5: ADVANTAGES, DISADVANTAGES, END-TO-END
Shows the end-to-end failure concretely: the packet header is correctly translated to the public address and port, but an FTP-style `PORT 192,168,1,10,200,10` command in the payload still carries the private address. The server would try to connect back to an unroutable address. The fixes and the list of pros and cons follow, and the relation to IPv6.

Output from a real run:

```text
===== SECTION 5: ADVANTAGES, DISADVANTAGES, END-TO-END =====
A protocol that writes its address INSIDE the payload (e.g. active FTP):
  header after PAT: 203.0.113.1:1024 -> 198.51.100.9:21
  payload still says: 'PORT 192,168,1,10,200,10' -> the server would try to connect to a private address
  Fix: an ALG (application-layer gateway) that rewrites payloads, or protocols avoiding embedded addresses.
Advantages: saves public IPv4 addresses, hides internal addressing, easy ISP changes, basic
  'unsolicited inbound drop' behaviour (this is a side effect, NOT a security feature by design).
Disadvantages: breaks end-to-end principle, inbound connections need port forwarding,
  complicates P2P/VoIP/IPsec AH, adds state and latency, per-flow logging needed for audit.
IPv6: with 2^128 addresses every host can have a public address, so NAT is not needed for
  address conservation (NAT66 and NAT64 exist for special cases).
```

## Worked Example
**Q:** Router with public address 203.0.113.1 does PAT. Host 192.168.1.10 (port 51000) and host 192.168.1.11 (port 51000) both connect to 198.51.100.9:80. Complete the table and handle a reply to 203.0.113.1:1025.

1. First flow: inside local `192.168.1.10:51000`, router assigns inside global `203.0.113.1:1024`, outside `198.51.100.9:80`.
2. Second flow: same private port but a different host: inside global `203.0.113.1:1025`.
3. The reply from `198.51.100.9:80` to `203.0.113.1:1025` matches the second entry; the router rewrites the destination to `192.168.1.11:51000` and forwards it inside.
4. A packet to `203.0.113.1:1999` with no entry is dropped.

The script's Section 3 prints exactly this table and behaviour.

## Key Rules / Gotchas Recap
- NAT/PAT rewrites headers (and recalculates checksums); payload addresses are untouched unless an ALG intervenes.
- PAT uses ports to multiplex: one public IP, many inside hosts; the table key includes ports.
- Static NAT for servers; dynamic NAT needs a pool as large as the active hosts; PAT is what routers actually do.
- Inbound connections need an existing entry or an explicit static/port-forward rule.
- NAT is not a firewall, and "hidden behind NAT" is not security.
- Port exhaustion and idle timeouts are real operational limits.
- IPv6 removes the need for NAT for address conservation.

## Why This Matters
Almost every device you test or deploy sits behind NAT, so "why can't I reach my local server from outside" and "why does my P2P/WebRTC app need STUN" are NAT questions. Cloud NAT gateways and Kubernetes egress behave the same way, and security investigators must map one public IP in a log back to many internal hosts.
