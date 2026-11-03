# `_1_NetworkLayerServicesAndIpv4Addressing.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The network layer (layer 3) moves packets from a source host to a destination host across many networks, using a logical address (the IP address) that is independent of the physical hardware. It exists because the data link layer only delivers frames within one local network; something has to choose a path across the whole internet.

**Services and functions.** Packetizing (wrapping transport data in a datagram), logical addressing, routing (choosing paths), forwarding (moving each packet to the right outgoing link), fragmentation, and congestion/error reporting (ICMP). Two service models exist:

| | Datagram (connectionless) | Virtual circuit (connection-oriented) |
|---|---|---|
| Set-up | none | a path is set up first |
| Each packet carries | full destination address | a short VC number |
| Router state | forwarding table keyed by destination | per-connection table (in-VC -> out-VC) |
| Packets of one flow | may take different paths, may arrive out of order | all follow the same path, in order |
| Router failure | only packets in flight are lost; routes re-converge | all circuits through it break |
| Example | the Internet (IP) | X.25, Frame Relay, ATM |

**Forwarding vs routing.** Forwarding is the local, per-packet action inside one router: look up the destination in the forwarding table and push the packet out the right port (data plane, nanoseconds to microseconds). Routing is the network-wide process (RIP, OSPF, BGP) that computes the table contents (control plane, seconds).

**IPv4 address.** A 32-bit number written as four decimal octets (dotted decimal), e.g. `192.168.10.77`. It has two parts: a network id (identifies the network) and a host id (identifies the machine in it). Total space is 2^32 = 4,294,967,296 addresses.

**Classful addressing** (historic, still asked in exams) chooses the split by the leading bits of the first octet:

| Class | Leading bits | First octet | Default mask | Network bits | Host bits |
|---|---|---|---|---|---|
| A | 0 | 0-127 | 255.0.0.0 (/8) | 8 | 24 |
| B | 10 | 128-191 | 255.255.0.0 (/16) | 16 | 16 |
| C | 110 | 192-223 | 255.255.255.0 (/24) | 24 | 8 |
| D | 1110 | 224-239 | none (multicast) | - | - |
| E | 1111 | 240-255 | none (reserved) | - | - |

Hosts per network are 2^h - 2 because the all-0 host part is the network address and the all-1 host part is the broadcast address. Class A has 126 usable networks in the classic answer (0.x.x.x and 127.x.x.x are special).

**Special addresses.**
- `127.0.0.0/8` loopback (`127.0.0.1` = "this machine"), never leaves the host.
- `0.0.0.0` unspecified / "this host"; `0.0.0.0/8` is "this network".
- Private (RFC 1918): `10.0.0.0/8`, `172.16.0.0/12` (172.16.0.0 to 172.31.255.255), `192.168.0.0/16`. Not routable on the public Internet; use NAT to reach it.
- APIPA / link-local `169.254.0.0/16`: self-assigned by a host when DHCP fails.
- Limited broadcast `255.255.255.255`: all hosts on the local network, never forwarded by routers.
- Directed broadcast: network id + all-1 host bits (e.g. `192.168.10.255`); addresses all hosts of a specific, possibly remote, network.

Typical exam questions: "Find the class, network id and host id of X", "How many hosts in a class B network?", "Is 172.20.1.1 private?", "Datagram vs virtual circuit".

## Full Line-by-Line Breakdown

### SECTION 1: DATAGRAM VS VIRTUAL-CIRCUIT SERVICE
Two tiny forwarding-table models of the chain A - R1 - R2 - B. The datagram tables are keyed by destination address and every packet is looked up independently. The VC tables are keyed by (incoming neighbour, incoming VC number) and rewrite the VC number hop by hop (5 -> 9 -> 2), which is how real virtual-circuit networks keep the numbers short and locally unique. Both reach B along the same path here; the difference is the state and what each packet carries.

Output from a real run:

```text
===== SECTION 1: DATAGRAM VS VIRTUAL-CIRCUIT SERVICE =====
Datagram path of 2 packets (each carries full dest address): ['A', 'R1', 'R2', 'B'] ['A', 'R1', 'R2', 'B']
Virtual-circuit path (packets carry only a short VC id):
  at R1: in-VC 5 -> out-VC 9, next R2
  at R2: in-VC 9 -> out-VC 2, next B
   ['A', 'R1', 'R2', 'B']
Forwarding = per-packet table lookup inside one router (data plane).
Routing    = algorithm that FILLS the tables (control plane).
```

### SECTION 2: DOTTED DECIMAL <-> 32-BIT
`to_int` shifts each octet into place (`<<24`, `<<16`, `<<8`, `<<0`); `to_dotted` reverses it with shift and mask. The script prints the binary in four 8-bit groups, which is what you do by hand in an exam, and checks the integer against `ipaddress.IPv4Address`.

Output from a real run:

```text
===== SECTION 2: DOTTED DECIMAL <-> 32-BIT =====
address : 192.168.10.77
binary  : 11000000.10101000.00001010.01001101
integer : 3232238157 hex: 0xc0a80a4d
back    : 192.168.10.77
check: OK
```

### SECTION 3: CLASSFUL ADDRESSING (A-E)
Prints the class table with the number of networks (2^(network bits - leading bits)) and hosts (2^host bits - 2). `addr_class` finds the class from the first octet; `split_net_host` applies the default mask (AND for the network id, AND-NOT for the host id). Classes D and E have no network/host split.

Output from a real run:

```text
===== SECTION 3: CLASSFUL ADDRESSING (A-E) =====
cls first octet lead bits default mask       nets / hosts per net
A     0-127     0         255.0.0.0                128 / 16777214
B   128-191     10        255.255.0.0            16384 / 65534
C   192-223     110       255.255.255.0        2097152 / 254
D   224-239     1110      (none, multicast)  -
E   240-255     1111      (none, reserved)   -
Note: class A is 0-127 by bit pattern, but 0/8 and 127/8 are special,
so usable class A nets = 2^7 - 2 = 126 in the classic exam answer.
10.4.5.6        class A  network id 10.0.0.0     host id 0.4.5.6
172.16.9.1      class B  network id 172.16.0.0   host id 0.0.9.1
192.168.10.77   class C  network id 192.168.10.0 host id 0.0.0.77
224.0.0.5       class D  network id n/a          host id n/a
250.1.1.1       class E  network id n/a          host id n/a
```

### SECTION 4: SPECIAL ADDRESSES + CLASSIFIER
`classify` is a hand-written decision chain (limited broadcast, 0/8, loopback, RFC 1918, APIPA, multicast, reserved, else public). `lib_classify` answers the same question with the `ipaddress` module's properties; the assertion proves they agree on 12 test addresses. The trap: 172.32.0.9 is NOT private, because the private block is only 172.16.0.0/12, i.e. second octet 16 to 31.

Output from a real run:

```text
===== SECTION 4: SPECIAL ADDRESSES + CLASSIFIER =====
127.0.0.1        -> loopback (127/8)
10.1.2.3         -> private (RFC 1918)
172.16.0.9       -> private (RFC 1918)
172.32.0.9       -> public unicast
192.168.1.1      -> private (RFC 1918)
169.254.7.7      -> APIPA / link-local (169.254/16)
255.255.255.255  -> limited broadcast
224.0.0.9        -> multicast (class D)
8.8.8.8          -> public unicast
0.0.0.0          -> this network / unspecified (0/8)
250.0.0.1        -> reserved (class E)
11.0.0.1         -> public unicast
check: OK (own classifier agrees with the ipaddress module on all)
TRAP: 172.32.0.9 looks private but RFC1918 stops at 172.31.255.255.
```

### SECTION 5: LIMITED VS DIRECTED BROADCAST
Uses `ip_network` to show the three special addresses of 192.168.10.0/24: network (host bits 0), directed broadcast (host bits 1) and the limited broadcast that never leaves the link, and the usable host count 254.

Output from a real run:

```text
===== SECTION 5: LIMITED VS DIRECTED BROADCAST =====
Directed broadcast for 192.168.10.0/24 = 192.168.10.255 (host bits all 1; reaches every host on THAT network, can be routed)
Limited broadcast = 255.255.255.255 (this network only, routers never forward)
Network address   = 192.168.10.0 (host bits all 0, names the network, not a host)
Usable hosts      = 254 = 2^8 - 2
```

## Worked Example
**Q:** Address `172.20.45.9`. Find class, network id, host id, whether it is private, and the directed broadcast.

1. First octet 172 lies in 128-191, so class B (leading bits `10`), default mask 255.255.0.0.
2. Network id = first two octets: `172.20.0.0`. Host id = `0.0.45.9`.
3. Private? Second octet 20 is within 16-31, so yes (172.16.0.0/12).
4. Directed broadcast (host bits all 1): `172.20.255.255`.
5. Hosts per class B network: 2^16 - 2 = 65,534.

Same method applied to `192.168.10.77` in the script gives class C, network `192.168.10.0`, host `0.0.0.77`.

## Key Rules / Gotchas Recap
- Datagram = no setup, full address per packet, can reorder; VC = setup, short VC id, in order, state in every router.
- Forwarding is local and per packet; routing builds the tables.
- Class by first octet: 0-127 A, 128-191 B, 192-223 C, 224-239 D, 240-255 E.
- Hosts = 2^h - 2 (network and broadcast addresses are not assignable).
- 127/8 is loopback (not just 127.0.0.1); 0.0.0.0 is not a normal host address.
- Private 172 block is 172.16-172.31 only; 172.32.x.x is public.
- 169.254/16 means "DHCP failed, host assigned itself an address".
- Limited broadcast is never routed; directed broadcast can be (and is usually blocked today).

## Why This Matters
Every cloud network, container network and firewall rule is written in terms of these addresses and ranges; mistaking a private or link-local range for public is a classic configuration and security bug. Being able to classify an address by hand is also how you read logs and debug "why can't it reach X" in minutes.
