# `_6_VpnTunnelingAndNetworkSecurityModels.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

> The "cipher" in this file is a toy built from SHA-256 to show structure only. It is not real cryptography; never use it to protect data. Use vetted libraries and protocols (TLS, IPsec, WireGuard).

## Concept
A VPN (virtual private network) uses tunnelling and cryptography to make a private network appear to extend across a public one such as the internet. Tunnelling means encapsulation: a whole packet is placed inside the payload of another packet, so the intermediate routers forward based only on the outer header.

**Encapsulation and overhead.** Wrapping adds bytes. IP-in-IP adds one 20-byte IPv4 header; GRE adds the outer IPv4 header plus a 4-byte basic GRE header (24 bytes). On a 1500-byte link the largest inner packet is therefore 1480 (IP-in-IP) or 1476 (GRE). A full-size packet will not fit: it is fragmented, or Path MTU Discovery tells the sender to shrink, or the tunnel endpoint clamps the TCP MSS. Broken PMTUD (ICMP blocked) causes the classic "small packets work, large transfers hang" symptom.

**GRE** (IP protocol 47) is a simple tunnel with no security; it can carry multicast and routing protocols, so it is often combined with IPsec.

**IPsec** is a suite at the IP layer. *AH* (Authentication Header, IP protocol 51) provides integrity and authentication, including parts of the outer IP header (the fields that do not change in transit), but no encryption; because it covers addresses, NAT breaks it. *ESP* (Encapsulating Security Payload, IP protocol 50) provides encryption and (normally) integrity and authentication of the payload; it works through NAT with NAT traversal (UDP port 4500). *IKE* (UDP 500) negotiates keys and security associations (SAs). Two modes: *transport mode* protects only the payload and keeps the original IP header (host-to-host); *tunnel mode* encapsulates the entire original packet inside ESP (or AH) with a new outer IP header (gateway-to-gateway and most remote access). ESP tunnel overhead = new IP header (20) + ESP header (SPI 4 + sequence 4) + IV + padding and 2-byte trailer + authentication tag (ICV).

**SSL/TLS VPN** runs over TCP (often port 443), so it traverses most firewalls; it can be clientless (a web portal for specific applications) or a full-tunnel client. A TCP-over-TCP design can behave badly under loss, so many products also offer a UDP/DTLS mode.

**WireGuard** is a modern VPN with a deliberately small codebase and fixed, modern primitives (Noise-based handshake, Curve25519, ChaCha20-Poly1305, BLAKE2s) over UDP; each peer is identified by a public key and a list of allowed IPs.

**Remote-access vs site-to-site.** Remote-access: one user device to a gateway. Site-to-site: two networks joined permanently by a pair of gateways.

**Security models.**
- *Perimeter model* ("castle and moat"): traffic inside the boundary is trusted; protection is concentrated at the firewall. Weakness: once an attacker or a malicious insider is inside, lateral movement is easy.
- *Zero trust:* no implicit trust from network location. Every request is authenticated and authorised using identity, device health and context, with least privilege and micro-segmentation, and everything is logged.
- *Defence in depth:* multiple independent layers (physical, network, host, application, data, people) so that a single failure does not mean compromise. Companion principles: least privilege, default deny, fail secure, separation of duties, assume breach.

**CIA and AAA.** Confidentiality, Integrity, Availability are the goals. AAA is the access-control process: Authentication (prove identity), Authorization (what the identity may do), Accounting (record what it did). RADIUS (UDP 1812 authentication, 1813 accounting), TACACS+ (TCP 49) and Diameter implement AAA for network access.

Typical exam questions: compare AH and ESP; transport vs tunnel mode; why AH fails through NAT; why a VPN reduces the effective MTU; define CIA and AAA; contrast perimeter and zero trust.

## Full Line-by-Line Breakdown

### SECTION 1: TUNNELLING = ENCAPSULATION AND ITS OVERHEAD
A frozen dataclass `Pkt` is nested: the outer packet (between public gateways) carries the inner packet (private addresses) as payload, and decapsulation returns the original. The overhead arithmetic gives 1480 and 1476. The trap line explains why the full-size packet no longer fits.

```text
===== SECTION 1: TUNNELLING = ENCAPSULATION AND ITS OVERHEAD =====
inner (original): Pkt(src='10.1.0.5', dst='10.2.0.9', proto='TCP', payload='data from site A to site B', ttl=64)
outer (tunnel):   Pkt(src='203.0.113.1', dst='198.51.100.1', proto='GRE', payload='<inner packet>', ttl=64)
The Internet routes on the OUTER header only; the private inner addresses are carried as opaque payload.
check: OK (decapsulation at the far gateway returns the original packet)
Overhead per scheme (bytes added to each packet):
  IP-in-IP             +20 B  -> largest inner packet that fits a 1500-byte link: 1480
  GRE (basic header)   +24 B  -> largest inner packet that fits a 1500-byte link: 1476
TRAP: a full-size 1500-byte inner packet no longer fits after adding 24 B -> it must be fragmented,
      or the sender must learn a smaller MTU (Path MTU Discovery), or the tunnel clamps TCP MSS. Broken PMTUD => stalls.
```

### SECTION 2: IPSEC - AH VS ESP, TRANSPORT VS TUNNEL
The tables state the protocol numbers and the AH/ESP and transport/tunnel differences. `esp_tunnel_size` computes the ESP tunnel-mode size for a 100-byte inner packet using an *example* suite (AES-CBC with 16-byte IV and block, HMAC-SHA1-96 with a 12-byte tag): 100 + 2 trailer bytes = 102, padded to 112, so 20 + 8 + 16 + 112 + 12 = 168. `ah_protect` computes an HMAC over source, destination, protocol and payload but not the TTL (a mutable field): the genuine packet verifies, a changed payload fails, a NAT-rewritten source fails (why AH and NAT clash), and a TTL decrement still passes. The toy keystream (SHA-256 in counter mode) shows what "ESP encrypts" means structurally; `esp_seal` and `esp_open` use encrypt-then-MAC and verify the tag before decrypting, so a flipped bit is rejected with no decryption.

```text
===== SECTION 2: IPSEC - AH VS ESP, TRANSPORT VS TUNNEL =====
IPsec = IP protocol suite: AH = IP protocol 51, ESP = IP protocol 50, key exchange IKE on UDP 500 (UDP 4500 for NAT-T).
Feature                  AH                         ESP
Integrity + authenticity yes                        yes (optional but normally used)
Confidentiality          NO                         yes (encryption)
Covers outer IP header   yes (immutable fields)     no (tunnel mode: only the inner packet)
Works through NAT        no (address change breaks) yes, with NAT-T (UDP encapsulation)
Mode          What is protected                              Typical use
Transport     payload only; original IP header stays        host-to-host
Tunnel        whole original packet, NEW outer IP header     gateway-to-gateway site VPN, remote access
Example: 100-byte inner packet in ESP tunnel mode (AES-CBC + HMAC-SHA1-96): 20 + 8 + 16 + 112 + 12 = 168 bytes (overhead 68).
check: OK (the 112 = 100 + 2 trailer bytes + 10 padding, a multiple of 16)
AH-like: genuine packet verifies: True
AH-like: payload changed in transit verifies: False
AH-like: NAT rewrote the source address, verifies: False <- why AH and NAT clash
AH-like: router decremented TTL, verifies: True (mutable field excluded)
ESP-like (TOY cipher): ciphertext hex = cc93ad31e4779c44b386c11dc7 | decrypts back: True
ESP-like open(genuine): b'transfer $100' | open(1 bit flipped): None
check: OK (tampering is rejected before any decryption happens)
```

### SECTION 3: VPN FAMILIES COMPARED
A comparison table of GRE, IPsec, SSL/TLS VPN and WireGuard by layer, what they provide and notable properties.

```text
===== SECTION 3: VPN FAMILIES COMPARED =====
Tech        Layer / transport              Gives                         Notes
GRE         IP protocol 47                 tunnelling only (no crypto)   carries multicast/routing protocols; often paired with IPsec
IPsec       L3: ESP(50)/AH(51), IKE UDP    auth + encryption             site-to-site standard; many options = complex to configure
SSL/TLS VPN L4-7: TCP (often 443)          auth + encryption             passes through most firewalls; portal (clientless) or full tunnel
WireGuard   UDP, own protocol (Noise)      auth + encryption             small codebase, fixed modern primitives (Curve25519,
                                                                         ChaCha20-Poly1305, BLAKE2s), peers identified by public key
Remote-access VPN = one user to a gateway; site-to-site = two networks joined permanently; both extend a private network.
```

### SECTION 4: PERIMETER VS ZERO TRUST
Two decision functions run on three requests. The perimeter function checks one thing, the source network, so a compromised internal PC reaches payroll while a legitimate employee in a cafe is refused. The zero-trust function checks role against the resource, device posture and MFA, so the compromised PC is denied and the legitimate remote employee is allowed. Policies and users are invented for the demo.

```text
===== SECTION 4: PERIMETER VS ZERO TRUST =====
Perimeter ('castle and moat'): inside = trusted. Zero trust: never trust by location; verify every request.
case                                                   perimeter  zero-trust
alice, managed laptop, MFA, internal -> payroll        allow      allow
bob (dev) on a compromised internal PC -> payroll      allow      deny
alice, managed laptop, MFA, from a cafe -> payroll     deny       allow
check: OK (perimeter lets lateral movement from a compromised inside host through; zero trust does not)
Zero trust building blocks: strong identity, device posture, least privilege, micro-segmentation, continuous logging.
```

### SECTION 5: DEFENCE IN DEPTH
If each layer independently stops 90 percent of attempts (an assumed number for illustration, not a measurement), n layers let 0.1^n through. The trap is that layers are not independent in practice, so real improvement is smaller.

```text
===== SECTION 5: DEFENCE IN DEPTH =====
Layers: physical, network (firewall, segmentation), host (patching, EDR), application (input validation), data (encryption), people (training).
Illustration with ASSUMED numbers, not measurements: if each independent layer stops 90% of attempts,
  1 layer(s): 10% get through
  2 layer(s): 1% get through
  3 layer(s): 0.1% get through
  4 layer(s): 0.01% get through
TRAP: layers are rarely independent (one stolen admin password can defeat several), so real risk falls less than this.
Principles: least privilege, fail secure (default deny), avoid single point of failure, assume breach.
```

### SECTION 6: CIA TRIAD AND AAA
Definitions, then a small AAA flow: users are stored as PBKDF2-HMAC-SHA256 hashes with a per-user salt (derived from the name only to keep the demo deterministic; real systems use random salts). `aaa` authenticates (constant-time compare), authorises by role, and appends to an audit log (accounting). The three attempts show success, authenticated-but-not-authorised, and failed authentication. The trap compares unsalted SHA-256 of two identical passwords (equal, so one cracked hash exposes both users) with salted PBKDF2 (different).

```text
===== SECTION 6: CIA TRIAD AND AAA =====
Confidentiality: only authorised parties read data   -> encryption, access control
Integrity:       data is not altered undetected      -> hashes, MACs, signatures
Availability:    service is usable when needed        -> redundancy, DoS defence, backups
AAA: Authentication (who are you?), Authorization (what may you do?), Accounting (what did you do?)
Protocols: RADIUS (UDP 1812/1813), TACACS+ (TCP 49), Diameter (successor to RADIUS).
  alice tries 'write': authorised
  bob tries 'write': authenticated but NOT authorised
  bob tries 'read': authentication failed
  accounting log: ['alice: write ok', 'bob: write DENIED', 'bob: login FAILED']
TRAP: unsalted SHA-256 of bob's and carol's identical password are equal: True -> one cracked hash exposes every user with that password.
      salted PBKDF2 hashes of the same password differ: True (use a per-user random salt and a slow KDF: PBKDF2/bcrypt/scrypt/Argon2)
check: OK
```

## Worked Example
**Q.** A 100-byte IP packet is sent through an IPsec ESP tunnel using AES-CBC (16-byte IV, 16-byte blocks) and HMAC-SHA1-96 (12-byte ICV). What is the size of the outer packet, and what is the overhead?

1. Encrypted part = inner packet + padding + pad-length (1) + next-header (1) = 100 + pad + 2, which must be a multiple of 16. 102 needs 10 bytes of padding to reach 112.
2. Outer packet = new IP header 20 + ESP header 8 (SPI + sequence number) + IV 16 + encrypted part 112 + ICV 12 = 168 bytes.
3. Overhead = 168 - 100 = 68 bytes.

The code asserts 168.

## Key Rules / Gotchas Recap
- Tunnelling = encapsulation; routers see only the outer header.
- Every tunnel reduces the usable MTU; watch PMTUD and TCP MSS clamping.
- AH: integrity, no encryption, breaks under NAT. ESP: encryption plus integrity. Tunnel mode hides the original header; transport mode keeps it.
- Protocol numbers: ESP 50, AH 51, GRE 47; IKE UDP 500, NAT-T UDP 4500.
- A VPN protects the path, not the endpoints; a compromised device inside a VPN is still inside.
- Zero trust: verify each request, least privilege. Defence in depth: independent layers (but not truly independent).
- Passwords need salted, slow hashes. Encrypt-then-MAC, and verify before decrypting.

## Why This Matters
Engineers connect cloud VPCs, offices and GPU clusters with VPNs and need to reason about MTU and performance. Zero trust, least privilege and audit logging are how modern AI services protect model weights, data and APIs. AAA is the pattern behind every login and permission system.
