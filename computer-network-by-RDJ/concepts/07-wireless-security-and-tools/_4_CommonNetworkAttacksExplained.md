# `_4_CommonNetworkAttacksExplained.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

> Safety note: this module is written for defenders. Everything is an in-memory model with made-up hosts; no packets are sent and no tool for attacking anything is provided. Practise real techniques only on systems you own or on legal training labs and CTF platforms.

## Concept
Network attacks exploit the fact that many original protocols (ARP, IP, TCP, DNS) trust the sender and do not authenticate it. Knowing how each attack works, which security property it breaks and which control defeats it is the basis of network defence.

**Security properties (CIA).** Confidentiality (only authorised readers), Integrity (no undetected change), Availability (service works when needed). Attacks are *passive* (only observe: eavesdropping, traffic analysis) or *active* (inject, modify, impersonate, disrupt).

**Taxonomy.**
- *Eavesdropping / sniffing:* reading traffic that passes by (shared Wi-Fi, a tapped link). Breaks confidentiality. Defence: encryption (TLS, WPA2/3, IPsec).
- *Spoofing:* forging a source identity (IP address, MAC address, e-mail sender). Breaks authenticity. Defence: ingress/egress filtering, authentication, cryptographic signatures.
- *Man-in-the-middle (MITM):* the attacker sits on the path and relays or alters traffic between two parties who think they talk directly. Enabled by ARP poisoning, rogue access points, DNS tampering. Defence: mutual authentication and certificate validation (TLS), Dynamic ARP Inspection.
- *DoS / DDoS:* exhaust bandwidth, CPU or state so legitimate users cannot be served; DDoS uses many sources. Breaks availability. Defence: rate limiting, scrubbing and CDNs, anycast, capacity planning.
- *SYN flood:* a DoS on TCP. Each SYN makes the server allocate a half-open entry in its SYN backlog and wait for the final ACK; spoofed sources never reply, so the backlog fills and real clients are refused. Defence: SYN cookies, larger backlog, shorter timeouts, upstream filtering.
- *ARP poisoning:* ARP has no authentication, so a host on the same LAN can claim "the gateway's IP is at my MAC", redirecting traffic through itself (MITM or DoS). Defence: static entries for critical hosts, Dynamic ARP Inspection (DAI) using DHCP-snooping bindings, port security, segmentation.
- *DNS cache poisoning:* convincing a resolver to cache a forged answer. A resolver accepts a reply if its question, 16-bit transaction ID and (nowadays) source port match; blind guessing is made hard by randomising both. Defence: random ID and port, DNSSEC validation, 0x20 case randomisation.
- *Session hijacking:* taking over an authenticated session by stealing or guessing the session token (or, in old TCP, the sequence numbers). Defence: unpredictable tokens, TLS, Secure and HttpOnly cookies, short lifetimes, rotating the token at login.
- *Port scan:* probing which ports respond, as reconnaissance. A scan is not itself an intrusion, but it precedes one. Defence: default-deny firewalls, minimal exposed services, detection and rate limiting. Scanning hosts you do not own or have no written permission to test may be illegal.

Typical exam questions: classify attacks as active or passive; explain a SYN flood and SYN cookies; why is ARP vulnerable; differentiate DoS and DDoS; list defences against MITM.

## Full Line-by-Line Breakdown

### SECTION 1: TAXONOMY
A table of attack, layer, which CIA property it breaks, active or passive, and the main defence. It is a revision aid; the later sections simulate three of these.

```text
===== SECTION 1: TAXONOMY =====
Attack             Layer    Breaks (CIA)       Type     Main defence
Eavesdropping      any      Confidentiality    passive  encryption (TLS, WPA2/3, IPsec)
Spoofing           2-4      Authenticity       active   ingress/egress filtering, authentication
MITM               2-7      Conf. + Integrity  active   mutual auth, certificate validation, DAI
DoS / DDoS         3-7      Availability       active   rate limiting, scrubbing, anycast, capacity
SYN flood          4        Availability       active   SYN cookies, bigger backlog, timeouts
ARP poisoning      2        Conf. + Integrity  active   static ARP, Dynamic ARP Inspection, port security
DNS cache poison   7        Integrity          active   random ID + source port, DNSSEC
Session hijack     4-7      Conf. + Integrity  active   unpredictable IDs, TLS, short lifetimes
Port scan          4        (recon, precursor) active   firewall default deny, detect + rate limit
Passive = only observes (hard to detect); active = modifies/injects/disrupts. DoS = one source; DDoS = many.
```

### SECTION 2: SYN BACKLOG FILLING AND SYN COOKIES (SIMULATION)
`BacklogServer` keeps at most 8 half-open entries. Eight spoofed SYNs fill it, so a legitimate SYN at tick 9 is dropped. Entries expire after 60 ticks, so at tick 70 the server accepts again, which shows the attacker must keep sending. `CookieServer` stores nothing: the ISN it returns is the first 4 bytes of an HMAC-SHA-256 over the client tuple and a time slice, using a server secret. When the final ACK returns (ack = ISN + 1) the server recomputes the cookie and accepts if it matches (checking the current and previous time slice). A forged ACK from a host that never saw the SYN-ACK cannot produce a valid number. This is the *idea* of SYN cookies; the real Linux implementation packs a coarse timestamp and a compressed MSS into the 32-bit ISN, which is why some TCP options can be lost.

```text
===== SECTION 2: SYN BACKLOG FILLING AND SYN COOKIES (SIMULATION) =====
Backlog size 8, entry lifetime 60 ticks. Spoofed sources never answer the SYN-ACK, so entries just sit.
  after 8 spoofed SYNs: half-open table 8/8
  legitimate client SYN at tick 9: DROPPED (backlog full)
  legitimate client SYN at tick 70 (old entries expired): SYN-ACK sent, entry stored
So the attacker must keep sending; the flood costs the server memory per half-open entry and costs the attacker almost nothing.
check: OK
SYN-cookie server: SYN from alice answered with ISN 3092109431 (derived, not stored). Table size stays 0.
  alice's real ACK (ack = ISN+1):          True
  forged ACK from a host that never saw the SYN-ACK: False
check: OK
Real SYN cookies pack a time counter and an encoded MSS into the 32-bit ISN (so some TCP options are lost);
this model keeps only the core idea: state is rebuilt from the returning ACK, so flooding SYNs cannot fill memory.
```

### SECTION 3: ARP CACHE POISONING AND ITS DEFENCE (SIMULATION)
An `ArpCache` is a dictionary. A cache that accepts unsolicited replies lets any host overwrite the gateway's MAC with its own. Defence 1: a static entry is never overwritten. Defence 2: a switch running DAI checks each ARP packet against a trusted binding table (built from DHCP snooping) of IP, MAC and port; the genuine reply on port 1 matches, the forged reply from a different port and MAC does not and is dropped. Only hosts on the same LAN segment can do this, so segmentation limits the exposure.

```text
===== SECTION 3: ARP CACHE POISONING AND ITS DEFENCE (SIMULATION) =====
victim learns the gateway normally:     {'192.168.1.1': 'aa:aa:aa:aa:aa:01'}
unsolicited reply claiming the gateway:  {'192.168.1.1': '02:00:00:00:00:66'} <- traffic for the gateway now goes to the wrong MAC
Cause: ARP has no authentication; any host on the LAN segment can send a reply and many stacks cache it.
-- Defence 1: static entry on a critical host --
  cache after the same forged reply: {'192.168.1.1': 'aa:aa:aa:aa:aa:01'}
-- Defence 2: Dynamic ARP Inspection (switch checks ARP against a trusted IP->MAC binding table) --
  genuine gateway reply on port1:   True
  forged reply from port2 host:     False -> switch drops it and can log it
check: OK
Also: ARP poisoning needs the attacker on the SAME LAN segment, so port security and segmentation reduce exposure.
```

### SECTION 4: RATE LIMITER (TOKEN BUCKET)
A token bucket holds up to `burst` tokens and refills `rate` per tick; each request costs one token. One source firing 100 requests at once gets the burst (10) and is refused 90. Then at 5 requests per tick for 10 ticks it gets only the refill rate (2 x 10 = 20). The trap: 200 different sources, each polite, all pass a per-source limiter (1000 requests total) while the server still has to cope with 1000. DDoS needs aggregate limits, upstream filtering and spare capacity, not only per-source limits.

```text
===== SECTION 4: RATE LIMITER (TOKEN BUCKET) =====
Single source sends 100 requests at once: 10 allowed (the burst), 90 refused
Then 5 requests/tick for 10 ticks (50 total): 20 allowed ~ refill rate 2/tick x 10 = 20
check: OK
TRAP: per-source limiting vs DDoS: 200 sources x 5 requests = 1000 offered, 1000 pass (each source stays under its own limit)
      legit user still gets 3/3, but the SERVER still has to handle 1000 attack requests. Defence: global limits, upstream scrubbing/CDN, capacity.
DoS vs DDoS: one fast source is easy to limit or block; many slow sources need aggregate detection.
```

### SECTION 5: DNS CACHE POISONING PROBABILITY MODEL
A `Resolver` has one pending query with a random 16-bit transaction ID and optionally a random source port. A forged reply is accepted only if both match. The model shows a wrong guess is rejected. The arithmetic: 65,536 possibilities for the ID alone, and 65,536 x 64,512 = 4,227,858,432 with a random port in 1024-65535. This illustrates why randomisation raised the cost of blind guessing; it does not make DNSSEC unnecessary, since DNSSEC adds signatures that cannot be guessed at all.

```text
===== SECTION 5: DNS CACHE POISONING PROBABILITY MODEL =====
A resolver accepts a reply only if it matches the pending query: question, 16-bit transaction ID, (and source port).
A forged reply with a wrong guess is rejected: True | cache: {}
Guess space with txid only: 65,536 -> one forged reply succeeds with p = 1/65,536
Guess space with txid + random source port: 4,227,858,432 -> p = 1/4,227,858,432 per attempt
Extra work factor from port randomisation = 64,512x. DNSSEC goes further: signatures, not luck.
check: OK
```

### SECTION 6: SESSION HIJACKING, MITM AND SESSION-ID STRENGTH
A counter-based session ID is predictable (the next one is obvious); `secrets.token_hex(16)` gives 128 bits from the OS random source. The script prints only the length, never the value. With 2^128 possibilities guessing is infeasible, so the realistic threats are theft (plain-text transport, cross-site scripting) which TLS and cookie flags address. The last line states the MITM defence: verify the peer's identity, not only encrypt.

```text
===== SECTION 6: SESSION HIJACKING, MITM AND SESSION-ID STRENGTH =====
Session hijack = taking over an authenticated session by learning or guessing its token (or TCP sequence numbers).
Predictable IDs (counter): ['sess001000', 'sess001001', 'sess001002', 'sess001003'] -> guess the next one trivially
Unpredictable ID: 128 random bits from secrets.token_hex(16) (value not printed)
Search space 2^128 = 3.403e+38; brute force is infeasible, so theft (sniffing, XSS) is the realistic risk.
Defences: random ID, TLS everywhere, Secure + HttpOnly cookie flags, rotate ID at login, expire idle sessions.
MITM defence in one line: the client must verify WHO it talks to (certificate chain + hostname), not just encrypt.
check: OK
```

## Worked Example
**Q.** A token bucket allows a burst of 10 and refills 2 tokens per tick. A client sends 100 requests in one tick, then 5 requests per tick for the next 10 ticks. How many are accepted in total?

1. First tick: the bucket starts full with 10 tokens, so 10 of the 100 are accepted.
2. The bucket is empty. In each following tick it gains 2 tokens, and the client asks for 5, so only 2 pass per tick.
3. Over 10 ticks: 10 x 2 = 20.
4. Total accepted = 10 + 20 = 30.

The code printed 10 for the burst and 20 for the steady phase.

## Key Rules / Gotchas Recap
- Passive attacks are hard to detect, so prevent them with encryption; active attacks can be detected and blocked.
- SYN flood fills half-open state; SYN cookies move the state into the returned ACK number.
- ARP and plain DNS have no authentication; use DAI, static entries, randomised IDs/ports and DNSSEC.
- Per-source limits do not stop a distributed attack.
- Session tokens must be random, long and sent only over TLS.
- Encryption alone does not stop a MITM; authentication of the peer does.
- Only test on systems you own or legal labs.

## Why This Matters
Defenders, SRE and platform engineers meet these failure modes as outages (SYN backlogs, noisy neighbours, bad ARP entries) and as incidents. AI services need rate limiting, authenticated sessions and TLS exactly as other APIs do, and the same reasoning (find the missing authentication, then add it) is how security tooling is designed.
