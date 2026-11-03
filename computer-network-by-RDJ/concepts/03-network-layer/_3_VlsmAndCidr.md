# `_3_VlsmAndCidr.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
VLSM (Variable Length Subnet Masking) lets you carve one address block into subnets of different sizes, and CIDR (Classless Inter-Domain Routing) drops the A/B/C class boundaries so any prefix length /0 to /32 is allowed. Together they stop address waste and, through aggregation (supernetting), keep the global routing table small.

**CIDR notation.** `a.b.c.d/p` means the first p bits are the network prefix. The block has 2^(32-p) addresses. Example: `200.10.20.0/22` has 1024 addresses (200.10.20.0 to 200.10.23.255). CIDR was introduced (RFC 1519, later RFC 4632) because classful allocation exhausted class B space and exploded routing tables.

**VLSM procedure (exam method):**
1. List requirements and sort largest first.
2. For each, find the smallest block with 2^h - 2 >= hosts (h host bits; prefix = 32 - h).
3. Allocate sequentially from the start of the block; each block starts right after the previous one.
4. Largest-first guarantees every block starts on a multiple of its own size (alignment). Smallest-first does not.
5. Point-to-point links get /30 (2 usable hosts).

**Supernetting / route aggregation.** Several contiguous networks are advertised as one shorter prefix. Conditions: the number of blocks is a power of two, they are contiguous, and the first block's address is divisible by the total size. The summary prefix = the number of leading bits all the networks share. Example: 200.10.0.0/24 to 200.10.3.0/24 aggregate to 200.10.0.0/22.

**Longest prefix match (LPM).** A router may match several table entries; it must choose the one with the longest prefix (most specific). The default route 0.0.0.0/0 matches everything but is the least specific. This is what lets an organisation punch a more specific route inside an aggregate.

**Comparison.**

| | Fixed-length subnetting | VLSM |
|---|---|---|
| Subnet sizes | all equal | different per need |
| Waste | high when needs differ | low |
| Routing protocol must carry the mask | no | yes (classless: RIPv2, OSPF, BGP) |

Typical exam questions: "Allocate 192.168.1.0/24 to departments needing 100, 50, 25, 10 hosts and two links", "Aggregate these four /24 routes", "Which interface does 200.10.1.200 go out of?".

## Full Line-by-Line Breakdown

### SECTION 1: CIDR NOTATION
For each CIDR string the script builds the mask from the prefix, ANDs to get the network, computes the block size 2^(32-p) and the last address, and asserts it equals what `ipaddress.ip_interface(...).network` says. Note `172.16.5.130/26` is in the network `172.16.5.128/26`: the host bits of the written address are ignored.

Output from a real run:

```text
===== SECTION 1: CIDR NOTATION =====
200.10.20.0/22    mask 255.255.252.0   network 200.10.20.0   addresses   1024 last 200.10.23.255
10.1.2.3/8        mask 255.0.0.0       network 10.0.0.0      addresses 16777216 last 10.255.255.255
172.16.5.130/26   mask 255.255.255.192 network 172.16.5.128  addresses     64 last 172.16.5.191
check: OK
CIDR drops class boundaries: prefix length can be any of /0../32.
```

### SECTION 2: VLSM ALLOCATION (LARGEST FIRST)
`prefix_for_hosts` adds 2 (network + broadcast) and takes `bit_length` of (need - 1) to find the host bits. `vlsm` sorts requirements descending, allocates sequentially and raises if the block runs out. 100 hosts needs 102 addresses so a /25 (128); 50 needs /26; 25 needs /27; 10 needs /28; links need /30. Total 248 of 256 addresses used; the last 8 are free.

Output from a real run:

```text
===== SECTION 2: VLSM ALLOCATION (LARGEST FIRST) =====
Block 192.168.1.0/24; requirements (hosts): {'LAN-A': 100, 'LAN-B': 50, 'LAN-C': 25, 'LAN-D': 10, 'Link-1': 2, 'Link-2': 2}
name    need subnet             mask            range                           bcast
LAN-A    100 192.168.1.0/25     255.255.255.128 192.168.1.1 - 192.168.1.126     192.168.1.127
LAN-B     50 192.168.1.128/26   255.255.255.192 192.168.1.129 - 192.168.1.190   192.168.1.191
LAN-C     25 192.168.1.192/27   255.255.255.224 192.168.1.193 - 192.168.1.222   192.168.1.223
LAN-D     10 192.168.1.224/28   255.255.255.240 192.168.1.225 - 192.168.1.238   192.168.1.239
Link-1     2 192.168.1.240/30   255.255.255.252 192.168.1.241 - 192.168.1.242   192.168.1.243
Link-2     2 192.168.1.244/30   255.255.255.252 192.168.1.245 - 192.168.1.246   192.168.1.247
Addresses used 248 of 256 -> 8 left for growth.
```

### SECTION 3: CHECKER (NO OVERLAP, FITS, CAPACITY)
Independent verification using the `ipaddress` module: every allocation must be a subnet of the parent, have enough usable hosts, and not overlap any other. The trap re-runs allocation smallest-first: after the two /30s the pointer is at .8, which is not a multiple of 16, so a /28 cannot legally start there. The fix is simply to sort descending.

Output from a real run:

```text
===== SECTION 3: CHECKER (NO OVERLAP, FITS, CAPACITY) =====
every subnet is inside the parent, big enough, and none overlap
check: OK
TRAP: allocating SMALLEST first breaks alignment.
  smallest-first fails: LAN-D (/28) would start at 192.168.1.8 - not a multiple of 16
  Fix: sort descending, so each block starts on its own size boundary.
```

### SECTION 4: SUPERNETTING / ROUTE AGGREGATION
Prints the four networks in binary; the first 22 bits are identical, so the summary is /22. `collapse_addresses` agrees. The trap: `.1.0/24` and `.2.0/24` are adjacent numerically but a /23 must start on an even third octet, so they cannot be merged into one prefix.

Output from a real run:

```text
===== SECTION 4: SUPERNETTING / ROUTE AGGREGATION =====
routes: ['200.10.0.0/24', '200.10.1.0/24', '200.10.2.0/24', '200.10.3.0/24']
  200.10.0.0  11001000000010100000000000000000
  200.10.1.0  11001000000010100000000100000000
  200.10.2.0  11001000000010100000001000000000
  200.10.3.0  11001000000010100000001100000000
common leading bits = 22 -> summary 200.10.0.0/22
ipaddress.collapse_addresses -> ['200.10.0.0/22']
check: OK
TRAP: 200.10.1.0/24 + 200.10.2.0/24 cannot merge: ['200.10.1.0/24', '200.10.2.0/24'] (not aligned on a /23 boundary: .1 and .2 straddle .0-.1 / .2-.3)
Rule: N blocks aggregate only if N is a power of 2, contiguous, and first block aligned.
```

### SECTION 5: LONGEST PREFIX MATCH
A five-entry forwarding table including a default route. For each destination the code finds all entries whose masked address matches and keeps the largest prefix length; a second implementation using `ipaddress` membership (`addr in network`) must agree. 200.10.1.200 matches /0, /16, /24 and /25 and goes out if2.

Output from a real run:

```text
===== SECTION 5: LONGEST PREFIX MATCH =====
200.10.1.200  matches 200.10.1.128/25  -> if2
200.10.1.5    matches 200.10.1.0/24    -> if1
200.10.9.9    matches 200.10.0.0/16    -> if0
10.9.9.9      matches 10.0.0.0/8       -> if3
8.8.8.8       matches 0.0.0.0/0        -> default via ISP
check: OK
200.10.1.200 matches /0, /16, /24 and /25; the /25 (longest) wins.
```

## Worked Example
**Q:** Given 192.168.1.0/24, allocate subnets for 100, 50, 25 and 10 hosts and two point-to-point links.

1. 100 hosts: 2^7 = 128 >= 102, h = 7, /25 -> 192.168.1.0/25 (.0 to .127).
2. 50 hosts: 2^6 = 64 >= 52, /26 -> 192.168.1.128/26 (.128 to .191).
3. 25 hosts: 2^5 = 32 >= 27, /27 -> 192.168.1.192/27 (.192 to .223).
4. 10 hosts: 2^4 = 16 >= 12, /28 -> 192.168.1.224/28 (.224 to .239).
5. Links: /30 each -> 192.168.1.240/30 and 192.168.1.244/30.
6. Used 128 + 64 + 32 + 16 + 4 + 4 = 248; 8 addresses remain (.248 to .255).

This is exactly the table the script prints and the checker verifies.

## Key Rules / Gotchas Recap
- Always allocate largest first; keep each block aligned to its own size.
- Hosts needed + 2 must fit in the block (2^h - 2 >= hosts).
- A CIDR address with host bits set (e.g. 172.16.5.130/26) belongs to the network obtained by masking.
- Aggregation needs power-of-two count, contiguity and alignment; .1.0 + .2.0 /24 cannot merge.
- Longest prefix wins; /0 is the default route.
- VLSM requires a classless routing protocol that carries the mask.

## Why This Matters
Cloud VPC design, route summarisation in data centres and firewall allow-lists are all VLSM/CIDR work, and LPM is literally the lookup every router and many software load balancers perform. Writing the allocator yourself and checking it against a library is the habit that stops silent overlapping-range bugs.
