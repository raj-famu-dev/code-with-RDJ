# `_3_FirewallsAndAccessControl.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A firewall is a device or software that enforces a security policy on traffic crossing a boundary between networks of different trust, by allowing or denying packets or connections according to rules. It exists because most hosts run services that should not be reachable from everywhere, and it is the simplest place to say who may talk to what.

**Types.**
- *Packet-filtering firewall (stateless):* judges each packet alone using IP addresses, protocol, ports (and sometimes flags). Fast and simple, but it has no memory: to let replies back in, it must permit large ranges of inbound ports.
- *Stateful inspection:* keeps a *connection table*. An outbound packet creates an entry (source, source port, destination, destination port); an inbound packet is allowed only if it is the reverse of an existing entry. TCP state (SYN, established, FIN) can be tracked; for UDP, which has no handshake, the "connection" is an idle timer.
- *Proxy / application-layer firewall:* terminates the client's connection, inspects application content (for example HTTP methods, hosts, URLs), and opens a separate connection to the server. It can enforce rules no header filter can, at higher cost; encrypted traffic is opaque to it unless it decrypts.
- *Next-generation firewall (NGFW):* a commercial label for stateful inspection plus application identification, user identity and an intrusion-prevention engine.

**Access control lists (ACLs).** An ACL is an ordered list of rules (action, protocol, source, destination, port). Evaluation is *first match wins*: rules are checked top to bottom and the first match decides, so the order is part of the policy. If nothing matches, the *default* action applies; the safe default is *deny* ("default deny", also "implicit deny"). Best practice: most specific rules first, general rules last, explicit final deny, and remove shadowed rules (a rule that can never match because an earlier one catches everything it would).

**DMZ (demilitarised zone).** A separate network segment for servers that must be reachable from the internet (web, mail, DNS). Policy: internet to DMZ only the needed ports; DMZ to inside LAN almost nothing (only the specific database port, for example); LAN to DMZ allowed for administration. If a DMZ server is compromised, the attacker still has to cross another rule set to reach internal systems. Designs use one firewall with three interfaces, or two firewalls (screened subnet).

**IDS vs IPS.** An *intrusion detection system* watches a copy of traffic (a mirror or tap) and raises alerts; it does not change traffic. An *intrusion prevention system* sits inline and can drop packets or reset connections. *Signature-based* detection matches known-bad patterns (accurate for known attacks, blind to new ones); *anomaly-based* detection flags deviation from a baseline (can find new behaviour, produces more false positives). A *false positive* is a harmless event flagged as an attack; for an IPS that means blocked legitimate users. Host-based (HIDS) and network-based (NIDS) variants exist.

Typical exam questions: stateless vs stateful; what does default deny mean; evaluate this ACL for these packets; draw a DMZ; IDS vs IPS; why can a proxy block things a packet filter cannot.

## Full Line-by-Line Breakdown

### SECTION 1: FIREWALL TYPES
A comparison table: what each type looks at, whether it remembers, and its strength or weakness. Printed so you can revise from the output.

```text
===== SECTION 1: FIREWALL TYPES =====
Type                  Looks at                               Remembers?   Strength / weakness
Packet filter         L3/L4 headers (IP, proto, port)        no           fast, simple; blind to context and payload
Stateful inspection   headers + connection state             yes (table)  allows only replies to inside-initiated flows
Proxy / application   full L7 content (HTTP, FTP, SMTP ...)  yes           deepest checks, breaks the client-server link in two; slower
Next-gen (NGFW)       app identification, users, IPS         yes          a marketing name for stateful + L7 + IPS features
Placement: a firewall enforces policy at a boundary between zones of different trust (inside / DMZ / outside).
```

### SECTION 2: ACL RULE MATCHING - FIRST MATCH WINS
`Packet` and `Rule` are frozen dataclasses. `Rule.matches` uses the `ipaddress` module (`ip_address in ip_network`) for CIDR matching, treats "any" as a wildcard, and compares the port number. `evaluate` returns the first matching rule's action, or `deny` with the reason "implicit default deny" if none matches. The six sample packets are worked by hand in the Worked Example and checked against the expected list. The trap block moves the server permit above the deny: the packet from the bad network matches the permit first, so the deny is *shadowed* and never reached.

```text
===== SECTION 2: ACL RULE MATCHING - FIRST MATCH WINS =====
ACL (top to bottom):
  1. deny   any  src=198.51.100.0/24  dst=any            dport=any
  2. permit tcp  src=any              dst=192.0.2.10/32  dport=443
  3. permit tcp  src=10.0.0.0/8       dst=any            dport=22
  4. permit icmp src=10.0.0.0/8       dst=any            dport=any
  (implicit last rule: deny any any)
    203.0.113.9 -> 192.0.2.10    tcp /443  => PERMIT (rule 2)
   198.51.100.7 -> 192.0.2.10    tcp /443  => DENY   (rule 1)
    203.0.113.9 -> 192.0.2.10    tcp /23   => DENY   (implicit default deny)
       10.1.2.3 -> 203.0.113.50  tcp /22   => PERMIT (rule 3)
       10.1.2.3 -> 203.0.113.50  icmp/0    => PERMIT (rule 4)
     172.16.0.5 -> 192.0.2.10    udp /53   => DENY   (implicit default deny)
check: OK (verdicts match the hand-worked answers)
-- TRAP: rule order. Put the permit for the server above the deny for the bad network --
  packet from the bad network, correct ACL:   ('deny', 'rule 1')
  packet from the bad network, wrong order:   ('permit', 'rule 1') <- the deny is shadowed, never reached
Rule: most specific first, broadest last; always end with deny; review for shadowed rules.
check: OK
```

### SECTION 3: STATEFUL CONNECTION TABLE
An inside host (10.0.0.5, inside the private 10.0.0.0/8) starts a flow and the firewall stores the 4-tuple. A reply from exactly the reverse tuple is permitted. A reply from a different host, different source port or different destination port is dropped because no entry matches. After 59 idle ticks (the timeout is 30) the entry has aged out, so even the genuine reply is dropped; this is a real-world gotcha for long-idle connections, which applications handle with keepalives. The closing text explains why a stateless filter is weaker.

```text
===== SECTION 3: STATEFUL CONNECTION TABLE =====
  t= 0 10.0.0.5:50000 -> 203.0.113.80:80  PERMIT (new outbound flow, entry added)
  t= 1 203.0.113.80:80 -> 10.0.0.5:50000  PERMIT (reply to an inside-initiated flow)
  t= 2 203.0.113.99:80 -> 10.0.0.5:50000  DROP   (no matching entry: unsolicited inbound)
  t= 3 203.0.113.80:4444 -> 10.0.0.5:50000  DROP   (no matching entry: unsolicited inbound)
  t= 4 203.0.113.80:80 -> 10.0.0.5:50001  DROP   (no matching entry: unsolicited inbound)
  t=60 203.0.113.80:80 -> 10.0.0.5:50000  DROP   (no matching entry: unsolicited inbound)
check: OK
A STATELESS packet filter must allow all inbound high ports (to catch replies), which also admits unsolicited
packets to those ports. Stateful needs only 'outbound allowed' and remembers who spoke first. UDP 'state' is a
timeout guess because UDP has no handshake; TCP state can also track SYN/FIN.
```

### SECTION 4: APPLICATION-LAYER (PROXY-STYLE) FILTERING
`http_policy` parses the request line and Host header and applies an allowlist of methods and hosts and a path-traversal check. Five sample requests give one ALLOW and four BLOCKs, each with a different reason. All traffic here is plain strings; no sockets are used. A packet filter would see five identical "TCP to port 80" flows.

```text
===== SECTION 4: APPLICATION-LAYER (PROXY-STYLE) FILTERING =====
  GET /index.html HTTP/1.1                      -> ALLOW
  POST /upload HTTP/1.1                         -> BLOCK method POST not allowed
  GET /../../etc/passwd HTTP/1.1                -> BLOCK path traversal pattern
  GET / HTTP/1.1                                -> BLOCK host 'unknown.example' not on the allow list
  GARBAGE                                       -> BLOCK malformed request line
A packet filter sees only 'TCP to port 80/443' and cannot make any of these distinctions.
Cost: a proxy terminates the connection and opens a second one, so it must understand each protocol, and
encrypted traffic (TLS) hides the content unless the proxy decrypts it (which brings its own risks).
```

### SECTION 5: DMZ AND ZONE POLICY
A policy matrix maps (source zone, destination zone) to the set of allowed destination ports; a missing pair means default deny. The tests assert both allows and denies. The DMZ-to-LAN hole (port 5432 only) shows the idea of an explicit, minimal exception.

```text
===== SECTION 5: DMZ AND ZONE POLICY =====
Internet --[FW]-- DMZ (public web/mail/DNS servers)
             |
            LAN (users, databases)
  internet -> dmz      port 443   ALLOW
  internet -> lan      port 443   DENY 
  internet -> dmz      port 22    DENY 
       dmz -> lan      port 22    DENY 
       dmz -> lan      port 5432  ALLOW
       lan -> internet port 443   ALLOW
check: OK
Idea: if the web server in the DMZ is compromised, the attacker still faces a second firewall rule set before
reaching the LAN. Without a DMZ, public servers would sit inside, or be exposed outside with no protection.
```

### SECTION 6: IDS VS IPS
The same four log lines are processed twice: as an IDS (alert only, the packet has already been delivered) and as an IPS (dropped inline). Then a behaviour rule counts distinct destination ports per source. With a threshold of 20, only the scanner (40 ports) is flagged. With a threshold of 2, a normal web client using ports 80 and 443 is flagged too: a false positive, the trap of poorly tuned anomaly rules.

```text
===== SECTION 6: IDS VS IPS =====
-- IDS (passive, copy of traffic) --
  203.0.113.20  GET /index               pass
  203.0.113.21  GET /a?q=' OR 1=1        ALERT (SQL-injection-style signature); packet was already delivered
  203.0.113.22  GET /../../etc/passwd    ALERT (path-traversal signature); packet was already delivered
  203.0.113.20  GET /about               pass
-- IPS (inline, can drop) --
  203.0.113.20  GET /index               pass
  203.0.113.21  GET /a?q=' OR 1=1        DROPPED (SQL-injection-style signature)
  203.0.113.22  GET /../../etc/passwd    DROPPED (path-traversal signature)
  203.0.113.20  GET /about               pass
-- Anomaly (behaviour) rule: many distinct destination ports from one source in a short window --
  threshold 20 distinct ports -> ['203.0.113.30']
  threshold 2  distinct ports -> ['203.0.113.30', '203.0.113.40'] <- TRAP: a normal web client flagged (false positive)
check: OK
IDS: detects and alerts, no effect on traffic, so a miss is only a missed alert. IPS: acts, so a false positive
blocks real users and it is a point of failure. Signature = known bad; anomaly = unusual, more false alarms.
```

## Worked Example
**Q.** Using the ACL: (1) deny any from 198.51.100.0/24; (2) permit tcp any to 192.0.2.10 port 443; (3) permit tcp from 10.0.0.0/8 to any port 22; (4) permit icmp from 10.0.0.0/8. Decide the fate of (a) 198.51.100.7 -> 192.0.2.10 tcp/443 and (b) 172.16.0.5 -> 192.0.2.10 udp/53.

(a) Rule 1: source is inside 198.51.100.0/24, protocol any, destination any, port any, so it matches. First match wins: **DENY**, even though rule 2 would also have matched.
(b) Rule 1: source 172.16.0.5 not in 198.51.100.0/24, no. Rule 2: protocol is udp, not tcp, no. Rule 3: source not in 10.0.0.0/8, no. Rule 4: protocol is not icmp, no. No rule matches, so the implicit default applies: **DENY**.

The code printed DENY (rule 1) and DENY (implicit default deny) for these.

## Key Rules / Gotchas Recap
- First match wins; order matters; put specific rules above general ones.
- Always end with deny (or rely on an implicit deny and know it is there).
- Stateful firewalls allow replies only for connections started from the trusted side; idle timeouts remove entries.
- A proxy sees content but needs per-protocol knowledge and cannot read TLS without decrypting.
- DMZ = servers exposed to the internet, separated from the LAN by a second rule set.
- IDS alerts, IPS blocks; false positives are costly for an IPS. Tune thresholds.
- A firewall is not a complete defence: it does not stop attacks that arrive over allowed ports, insiders, or stolen credentials.

## Why This Matters
Every cloud security group, Kubernetes network policy and corporate perimeter is an ACL or stateful table in disguise, and misordered or over-broad rules are a common cause of both outages and breaches. Model-serving endpoints (for example an inference API) should sit behind exactly this kind of default-deny policy.
