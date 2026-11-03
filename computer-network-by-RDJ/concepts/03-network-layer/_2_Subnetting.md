# `_2_Subnetting.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Subnetting splits one IP network into several smaller networks (subnets) by borrowing bits from the host part of the address and using them as extra network bits. It exists to match network size to real needs, reduce broadcast traffic, give each department or link its own network, and avoid wasting addresses.

**Subnet mask.** A 32-bit number of 1s followed by 0s. A 1 means "this bit belongs to the network/subnet part", a 0 means "host part". Written dotted (`255.255.255.224`) or as a prefix length (`/27` = 27 ones). The network address of any host is `IP AND mask`.

**Borrowing bits.** Start from the default prefix (class C = /24). To get at least S subnets borrow n bits where 2^n >= S. The new prefix is old + n. The host bits left are h = 32 - new prefix.

**Formulas (fixed-length subnetting):**
- Number of subnets = 2^n (modern); 2^n - 2 under the old RFC 950 rule that forbade subnet zero and the all-ones subnet.
- Hosts per subnet = 2^h - 2 (network address and broadcast address are not assignable).
- Block size (increment) = 2^h in the interesting octet, e.g. 32 for /27.
- Subnet n starts at n x block size.

**Per-subnet addresses.** Network address = host bits all 0; first host = network + 1; last host = broadcast - 1; broadcast = host bits all 1.

**Common masks** (last octet): /25 = 128 (126 hosts), /26 = 192 (62), /27 = 224 (30), /28 = 240 (14), /29 = 248 (6), /30 = 252 (2).

**Fixed-length weakness.** Every subnet has the same size, so a 2-host serial link wastes a /27. That is the motivation for VLSM (next topic).

Typical exam questions: "Subnet 192.168.10.0/24 into 6 subnets: give mask, hosts per subnet, ranges", "Which subnet does 192.168.10.77/27 belong to?", "How many hosts are on a /28?".

## Full Line-by-Line Breakdown

### SECTION 1: MASK, PREFIX AND BORROWED BITS
Starting from `192.168.10.0/24` the script needs 6 subnets. `(6-1).bit_length()` is the smallest n with 2^n >= 6, i.e. 3. The new prefix is /27, mask `255.255.255.224`, with 5 host bits left, so 30 hosts and a block size of 32.

Output from a real run:

```text
===== SECTION 1: MASK, PREFIX AND BORROWED BITS =====
Class C network 192.168.10.0/24; need 6 subnets
borrow n = 3 bits  (2^3 = 8 >= 6)
new prefix /27, mask 255.255.255.224
mask bits: 11111111.11111111.11111111.11100000
host bits left h = 5; hosts per subnet = 2^5 - 2 = 30
block size (increment in last octet) = 2^5 = 32
```

### SECTION 2: SUBNET TABLE
`split` creates 2^(new prefix - old prefix) subnets, each `block size` apart. A `Subnet` dataclass derives broadcast (`network | ~mask`), first and last host. The table is then compared row by row with `ipaddress.ip_network(...).subnets(new_prefix=27)`; `check: OK` means all 8 rows (network, broadcast, first and last host) agree. Asking for 6 gives 8: the extra 2 are spare, not an error.

Output from a real run:

```text
===== SECTION 2: SUBNET TABLE =====
 # network         first host      last host       broadcast      
 0 192.168.10.0    192.168.10.1    192.168.10.30   192.168.10.31  
 1 192.168.10.32   192.168.10.33   192.168.10.62   192.168.10.63  
 2 192.168.10.64   192.168.10.65   192.168.10.94   192.168.10.95  
 3 192.168.10.96   192.168.10.97   192.168.10.126  192.168.10.127 
 4 192.168.10.128  192.168.10.129  192.168.10.158  192.168.10.159 
 5 192.168.10.160  192.168.10.161  192.168.10.190  192.168.10.191 
 6 192.168.10.192  192.168.10.193  192.168.10.222  192.168.10.223 
 7 192.168.10.224  192.168.10.225  192.168.10.254  192.168.10.255 
check: OK (all 8 rows match the ipaddress module)
Requested 6 subnets but got 8: 2 are spare.
```

### SECTION 3: WHICH SUBNET IS THIS HOST IN?
The exam method: write the host and the mask in binary, AND them bit by bit. 77 = `01001101`, mask last octet `11100000`, AND = `01000000` = 64, so the host is in subnet 192.168.10.64/27 with broadcast .95 and usable range .65-.94. Checked against `ipaddress.ip_interface`.

Output from a real run:

```text
===== SECTION 3: WHICH SUBNET IS THIS HOST IN? =====
host 192.168.10.77/27  mask 255.255.255.224
host bits : 11000000101010000000101001001101
mask bits : 11111111111111111111111111100000
AND (net) : 11000000101010000000101001000000 = 192.168.10.64
broadcast : 192.168.10.95  usable range: 192.168.10.65 - 192.168.10.94
check: OK
```

### SECTION 4: TRAP - OFF-BY-TWO HOST COUNT
The most common marking error: giving 2^h instead of 2^h - 2. The loop prints both. Special cases: /30 (2 usable, typical point-to-point), /31 (both addresses usable on point-to-point links under RFC 3021, and Python's `hosts()` reflects that) and /32 (one host route).

Output from a real run:

```text
===== SECTION 4: TRAP - OFF-BY-TWO HOST COUNT =====
h=2: wrong 2^h =   4   right 2^h - 2 =   2
h=3: wrong 2^h =   8   right 2^h - 2 =   6
h=4: wrong 2^h =  16   right 2^h - 2 =  14
h=8: wrong 2^h = 256   right 2^h - 2 = 254
A /30 has 4 addresses but only 2 usable hosts: ideal for a point-to-point link.
A /31 (RFC 3021) is special: both addresses usable on point-to-point links.
ipaddress hosts() of 10.0.0.0/31: ['10.0.0.0', '10.0.0.1']
A /32 is a single host route.
```

### SECTION 5: TRAP - SUBNET-ZERO AND ALL-ONES SUBNET
Old textbooks (RFC 950 era) forbid the first and last subnet, giving 2^n - 2 subnets. Modern practice allows them (2^n). The script shows both counts for n = 2 and 3 and why the old rule can change the required n. Always check which rule the question assumes.

Output from a real run:

```text
===== SECTION 5: TRAP - SUBNET-ZERO AND ALL-ONES SUBNET =====
Old classful rule (RFC 950): the first (subnet-zero) and last (all-ones)
subnets were NOT allowed, so usable subnets = 2^n - 2.
  n=2: old rule 2 subnets, modern rule (CIDR era) 4 subnets
  n=3: old rule 6 subnets, modern rule (CIDR era) 8 subnets
Modern practice (CIDR era) allows subnet zero and the all-ones subnet.
Under the OLD rule our 6-subnet need would force n = 3 with only 6 usable subnets: just enough.
Under the OLD rule 4 subnets would need n = 3 (not 2), because 2^2 - 2 = 2 < 4.
Exam tip: read the question - if it says 'subnet zero is not used', subtract 2.
```

## Worked Example
**Q:** A company is given `192.168.10.0/24` and needs 6 subnets. Find the mask, hosts per subnet, and the range of the subnet containing `192.168.10.77`.

1. Need 6 subnets: 2^3 = 8 >= 6, so n = 3 borrowed bits.
2. New prefix 24 + 3 = /27, mask 255.255.255.224.
3. Host bits h = 5, hosts = 2^5 - 2 = 30.
4. Block size 32: subnets start at .0, .32, .64, .96, .128, .160, .192, .224.
5. 77 lies between 64 and 95, so subnet .64: network 192.168.10.64, hosts .65 to .94, broadcast .95.

The code prints exactly these numbers and agrees with the `ipaddress` module.

## Key Rules / Gotchas Recap
- Subnets: 2^n (n borrowed bits). Hosts: 2^h - 2 (h host bits left).
- Network = IP AND mask; broadcast = network OR NOT mask.
- First host = network + 1, last host = broadcast - 1.
- Block size = 256 - (mask octet), e.g. 256 - 224 = 32.
- Check whether the question forbids subnet zero (then 2^n - 2 subnets).
- /30 for point-to-point links; /31 is an RFC 3021 exception; /32 is a host route.
- Fixed-length subnets waste addresses when requirements differ: use VLSM.

## Why This Matters
VPCs, Kubernetes pod ranges and firewall rules are all carved with subnet math; an off-by-two or a wrong block boundary gives overlapping ranges and broken routing. In security work, knowing the subnet tells you what is in scope and what a host can reach.
