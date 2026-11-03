# `_10_SnmpNetworkManagementAndOtherProtocols.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
SNMP (Simple Network Management Protocol) lets a management station read and change the status of network devices (routers, switches, printers, servers) and lets those devices send an alarm when something happens. It exists because a network with hundreds of devices cannot be run by logging in to each one: a standard protocol and a standard data model let one tool monitor them all. This file also surveys other application-layer protocols (Syslog, NTP, LDAP, RADIUS, SIP, RTP and the older WWW/Telnet-era services) in a port-and-protocol table.

**Architecture.** The manager (network management station) sends requests. The agent is software on each managed device; it keeps the device's information in a MIB (Management Information Base). A MIB is a tree; every variable has an OID (object identifier), a dotted sequence of numbers describing the path from the root: `1.3.6.1.2.1.1.5.0` is iso(1).org(3).dod(6).internet(1).mgmt(2).mib-2(1).system(1).sysName(5) instance 0 (the `.0` marks a scalar). Table cells carry a row index at the end, e.g. `ifDescr.2` is the description of interface number 2. Vendors extend the tree under `1.3.6.1.4.1` (enterprises). The structure of management information (SMI, defined in ASN.1) gives the types: INTEGER, OCTET STRING, OBJECT IDENTIFIER, Counter32 (only grows, wraps), Gauge32 (goes up and down), TimeTicks (hundredths of a second). Messages are encoded with BER, a type-length-value format.

**Operations.**
- GetRequest: read named variables. GetNextRequest: read the variable that comes after an OID in numeric order; repeating it is a "walk" through a subtree without knowing its contents. GetBulkRequest (v2c): fetch many successors in one message.
- SetRequest: change a writable variable (e.g. disable an interface); needs write access.
- Response: the agent's answer to any request.
- Trap (and Inform, which is acknowledged): sent by the agent without being asked, e.g. link down, cold start, authentication failure.
Ports: the agent listens on UDP 161; the manager receives traps on UDP 162. UDP keeps agents light and works when the network is damaged, but messages can be lost.

**Versions.**

| | SNMPv1 | SNMPv2c | SNMPv3 |
|---|---|---|---|
| Authentication | community string | community string | user-based security model (USM): per-user keys, HMAC |
| Encryption | none | none | optional (privacy: AES) |
| Access control | by community | by community | view-based (VACM) |
| Added | basic Get, GetNext, Set, Trap | GetBulk, Inform, 64-bit counters | security and remote configuration |

The community string is a shared password sent in clear text (`public` read, `private` write are the notorious defaults), so v1 and v2c must never be exposed beyond a trusted management network. v3 has three levels: noAuthNoPriv, authNoPriv (integrity and identity) and authPriv (plus encryption); use authPriv.

**Syslog.** Devices write log lines and send them to a collector (classic UDP 514). The message begins with `<PRI>` where PRI = facility x 8 + severity. Facilities identify the source (kern 0, user 1, mail 2, daemon 3, auth 4, ..., local0 to local7 are 16 to 23); severities are 0 Emergency, 1 Alert, 2 Critical, 3 Error, 4 Warning, 5 Notice, 6 Informational, 7 Debug. `<34>` = 4 x 8 + 2 = auth.critical. Plain UDP syslog has no authentication or delivery guarantee.

**NTP.** Time synchronisation over UDP 123 organised in strata (0 reference clock, 1 directly connected servers, 2 clients of stratum 1, ..., 15; 16 = unsynchronised). The stratum is a distance from the reference, not a quality score. Offsets and delay are computed from four timestamps (see the DHCP file).

**Other protocols.** LDAP (TCP 389, LDAPS 636) queries and updates a hierarchical directory of users, groups and devices (entries named by distinguished names such as `cn=alice,ou=staff,dc=example,dc=test`); it is the backbone of central logins. RADIUS (UDP 1812 authentication, 1813 accounting) provides AAA (authentication, authorisation, accounting) for network access: a Wi-Fi access point or VPN gateway asks the RADIUS server whether the user may enter. SIP (UDP/TCP 5060, TLS 5061) sets up, modifies and ends VoIP calls (INVITE, ACK, BYE) and carries SDP to describe the media; RTP carries the voice or video itself over UDP, with a 12-byte header holding a sequence number (loss and reordering) and a timestamp (play-out timing and jitter), and RTCP provides feedback. Real-time media prefers UDP: a late packet is useless, so retransmission does not help. RTSP (TCP 554) is the remote control (play, pause) for stored streams. Older WWW-era services such as Gopher (70), Finger (79) and NNTP/Usenet (119) are mostly historic, and Telnet (23) survives only on legacy equipment.

**Typical exam questions.** Draw the SNMP manager-agent-MIB architecture. List the SNMP PDUs and which ports they use. What is an OID and how is `1.3.6.1.2.1.1.5.0` read? Difference between polling and traps. Compare SNMP v1, v2c and v3. Decode a syslog PRI. State port numbers and transport of common protocols.

## Full Line-by-Line Breakdown

### SECTION 1: SNMP CONCEPTS AND VERSIONS
An ASCII sketch of manager, agent, requests, responses and traps, the two ports, and a version table. The final lines state the main security fact: the v1/v2c community string is a clear-text password.

Output from a real run:

```text
===== SECTION 1: SNMP CONCEPTS AND VERSIONS =====
  manager (NMS) ---- GetRequest / GetNext / GetBulk / SetRequest --> agent (on router, switch, server)
  manager        <---------------------- Response -------------------- agent
  manager        <------ Trap / Inform (unsolicited alarm, UDP 162) ---- agent
  The agent keeps variables in a MIB (Management Information Base), a tree whose
  nodes are named by OIDs (Object Identifiers), e.g. 1.3.6.1.2.1.1.5.0 = sysName.
Agent listens on UDP 161; the manager listens for traps on UDP 162.
SMI/ASN.1 defines the data types (INTEGER, OCTET STRING, Counter32, Gauge32, TimeTicks...);
messages are encoded with BER (Basic Encoding Rules), shown in Section 3.

            v1                  v2c                                 v3
security    community string    community string                    users, auth (HMAC), privacy (encryption)
clear text  yes                 yes                                 only if you pick noAuthNoPriv
new in it   -                   GetBulk, 64-bit counters, Inform    USM + VACM access control
errors      noSuchName          noSuchObject / endOfMibView         same as v2c
verdict     legacy              common but weak                     use this one
A v1/v2c 'community string' (default 'public' for read, 'private' for write) is a
PASSWORD SENT IN CLEAR TEXT. Anyone on the path can read it; change the defaults.
```

### SECTION 2: THE OID TREE AND A SORTING TRAP
A tree drawing of the path to `mib-2`, the `system` and `interfaces` groups and the vendor branch. The trap: OIDs sorted as text give `...2.1.10.1` before `...2.1.2.1` because `'1' < '2'` character by character, but numerically 10 is greater than 2. Agents must store OIDs as tuples of integers so GETNEXT and WALK follow the true order. The assertion verifies that the two orders differ and the numeric one is right.

Output from a real run:

```text
===== SECTION 2: THE OID TREE AND A SORTING TRAP =====
  1 iso
  +-3 org
    +-6 dod
      +-1 internet
        +-2 mgmt
        | +-1 mib-2
        |   +-1 system      (1.3.6.1.2.1.1)   sysDescr .1, sysUpTime .3, sysName .5
        |   +-2 interfaces  (1.3.6.1.2.1.2)   ifNumber .1, ifTable .2
        +-4 private
          +-1 enterprises   (1.3.6.1.4.1)     vendors get a number, e.g. 8072
A trailing .0 means a scalar instance; table cells end in a row index (ifDescr.2).
TRAP: sorting OIDs as text:     ['1.3.6.1.2.1.1.5.0', '1.3.6.1.2.1.2.2.1.10.1', '1.3.6.1.2.1.2.2.1.2.1', '1.3.6.1.2.1.2.2.1.8.1']
FIX : compare each arc as a number: ['1.3.6.1.2.1.1.5.0', '1.3.6.1.2.1.2.2.1.2.1', '1.3.6.1.2.1.2.2.1.8.1', '1.3.6.1.2.1.2.2.1.10.1']
check: OK (as text '...1.10.1' sorts before '...1.2.1'; numerically it is after)
GETNEXT/WALK depend on the numeric order, so agents store OIDs as tuples of ints.
```

### SECTION 3: SNMP ON THE WIRE (ASN.1 BER)
A BER element is tag, length, value. `tlv` builds one (lengths under 128 use one byte; longer ones use `0x80 | number of length bytes` followed by the length). `enc_int` writes a minimal two's-complement integer, `enc_oid` packs the first two arcs as `40 x first + second` (so `1.3` becomes `0x2b`) and then each further arc in base 128, with the high bit set on all but the last byte (arc 8072 becomes `bf 08`). `snmp_message` assembles version, community and a GetRequest PDU (tag `a0`) holding request-id, error-status, error-index and the list of variable bindings, each an OID and a value (NULL for a request). The annotated byte list is what a capture would show, and the check compares with bytes derived by hand. Note that `public` is plainly visible in the hex (`70 75 62 6c 69 63`).

Output from a real run:

```text
===== SECTION 3: SNMP ON THE WIRE (ASN.1 BER) =====
GetRequest for sysDescr.0, SNMPv1, community 'public', request-id 1:
   30 26 02 01 00 04 06 70 75 62 6c 69 63 a0 19 02 01 01 02 01 00 02 01 00 30 0e 30 0c 06 08 2b 06 01 02 01 01 01 00 05 00
   30 26            SEQUENCE, 38 bytes follow
   02 01 00         INTEGER version = 0 (v1; v2c is 1)
   04 06 70 75 62 6c 69 63   OCTET STRING 'public' <-- the community, readable!
   a0 19            GetRequest PDU, 25 bytes
   02 01 01 | 02 01 00 | 02 01 00   request-id, error-status, error-index
   30 0e 30 0c      varbind list / one varbind
   06 08 2b 06 01 02 01 01 01 00    OID 1.3.6.1.2.1.1.1.0 (first byte 2b = 40*1+3)
   05 00            NULL (no value yet)
check: OK (matches the hand-derived bytes; arc 8072 needs two bytes: bf 08 = 63*128 + 8)
```

### SECTION 4: A SIMULATED AGENT: GET, GETNEXT, WALK, BULK, SET, TRAP
`Agent` holds a MIB dict from OID tuple to `[type, value, writable]`, plus a sorted key list for `bisect`. `get` returns a value, `noSuchObject` for an unknown OID, or nothing at all for a wrong community (real agents stay silent and may raise an authentication-failure trap). `getnext` uses `bisect_right` to find the first key greater than the given OID; the first lines walk three steps from `1.3.6.1.2.1.1`. `walk` repeats GETNEXT until the OID leaves the subtree: the interfaces walk lists `ifNumber`, all `ifDescr`, all `ifOperStatus`, then all `ifInOctets`, in numeric column order (2, 8, 10). `getbulk` returns several successors in one request. `set` needs the write community, a writable object and the correct type; the four test cases show success, `notWritable`, wrong community and `wrongType`. `link_event` changes the status in the MIB and records a trap, which is how an agent alerts the manager without waiting for a poll. All data are fictional (RFC 2606 `.test` addresses).

Output from a real run:

```text
===== SECTION 4: A SIMULATED AGENT: GET, GETNEXT, WALK, BULK, SET, TRAP =====
GET with the right community, a wrong one, and a missing object:
   sysName.0 = STRING: rtr1
   1.3.6.1.2.1.1.5.1 = noSuchObject
   (no reply at all: wrong community)

GETNEXT chain starting before the first object (this is how a WALK works):
   sysDescr.0 = STRING: RDJ demo router, simulated
   sysUpTime.0 = Timeticks: 123456
   sysContact.0 = STRING: admin@example.test

WALK of the interfaces subtree 1.3.6.1.2.1.2:
   ifNumber.0 = INTEGER: 2
   ifDescr.1 = STRING: eth0
   ifDescr.2 = STRING: eth1
   ifOperStatus.1 = INTEGER: 1
   ifOperStatus.2 = INTEGER: 1
   ifInOctets.1 = Counter32: 9000000
   ifInOctets.2 = Counter32: 42
   (numeric order: ...2.1.2.x, then ...2.1.8.x, then ...2.1.10.x)

GETBULK (v2c): 3 successors in ONE request instead of 3 round trips:
   sysName.0 = STRING: rtr1
   ifNumber.0 = INTEGER: 2
   ifDescr.1 = STRING: eth0

SET (needs the write community and a writable object of the right type):
   sysName.0 = 'core-rtr' -> OK -> sysName.0 = STRING: core-rtr
   sysDescr.0 (read-only)  -> notWritable
   sysName.0 with 'public' -> (no response: wrong community)
   sysName.0 as INTEGER    -> wrongType

Trap: interface eth1 goes down; the agent tells the manager unprompted:
   linkDown/linkUp trap: ifIndex=2 ifOperStatus=2(down)
   polling finds out within one poll period; a trap tells within one packet.
Traps recorded by the agent so far:
  - authenticationFailure (1.3.6.1.6.3.1.1.5.5)
  - authenticationFailure (1.3.6.1.6.3.1.1.5.5)
  - linkDown/linkUp trap: ifIndex=2 ifOperStatus=2(down)
check: OK
```

### SECTION 5: SYSLOG
Prints the severity names and shows three PRI calculations. The RFC 3164 sample message `<34>Oct 11 22:14:15 mymachine su: ...` is sent as a single UDP datagram from one loopback socket to another (port 0, timeouts, both closed in `finally`), then decoded: PRI 34 gives facility 4 (auth) and severity 2 (Critical), via integer division and remainder by 8.

Output from a real run:

```text
===== SECTION 5: SYSLOG =====
Syslog (UDP 514 classic): devices send one-line log messages to a collector.
Message starts with <PRI>, where PRI = facility x 8 + severity.
severity: 0 Emergency, 1 Alert, 2 Critical, 3 Error, 4 Warning, 5 Notice, 6 Informational, 7 Debug
  facility  4 (auth) x 8 + severity 2 = PRI 34
  facility 16 (local0) x 8 + severity 6 = PRI 134
  facility  0 (kern) x 8 + severity 0 = PRI 0

One datagram over loopback UDP: "<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8"
  decoded -> facility=auth, severity=Critical, text="Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8"
check: OK (PRI 34 = auth.critical)
Syslog over UDP is unauthenticated and can be lost or forged; use TCP+TLS for logs
that matter. Central logging is how you notice attacks and outages.
```

### SECTION 6: NTP STRATA, PORTS AND PROTOCOLS, VOIP NUMBERS
A short stratum chain, a table of 25 protocols with their ports and transports (TCP, UDP or both), short explanations of LDAP, RADIUS and SIP/RTP, and a VoIP bandwidth calculation. G.711 audio is 64 kbit/s, so a 20 ms packet holds 64000 / 8 x 0.020 = 160 bytes. Add RTP 12 + UDP 8 + IPv4 20 = 40 bytes of headers: 200 bytes per packet, 50 packets per second, which is 200 x 8 x 50 = 80,000 bit/s. (Ethernet framing would add more.)

Output from a real run:

```text
===== SECTION 6: NTP STRATA, PORTS AND PROTOCOLS, VOIP NUMBERS =====
NTP strata: 0 reference clock (GPS/atomic) -> 1 -> 2 -> ... 15; 16 = unsynchronised.
  stratum 0: GPS receiver (not on the network)
  stratum 1: primary server wired to it
  stratum 2: syncs to stratum 1 (e.g. your office server)
  stratum 3: your laptop syncs to that

protocol         port             transport        purpose
FTP              20/21            TCP              file transfer (data / control)
SSH              22               TCP              secure remote login, SFTP
Telnet           23               TCP              remote login, cleartext
SMTP             25               TCP              send mail between servers
DNS              53               UDP+TCP          name resolution
DHCP             67/68            UDP              address configuration
TFTP             69               UDP              trivial file transfer
Gopher           70               TCP              menu-based documents (WWW predecessor)
Finger           79               TCP              who is logged in (historic)
HTTP             80               TCP              web
POP3             110              TCP              mail retrieval
NNTP             119              TCP              Usenet news (historic)
NTP              123              UDP              time sync
IMAP             143              TCP              mail access
SNMP             161/162          UDP              management / traps
LDAP             389              TCP (+UDP)       directory lookup
HTTPS            443              TCP (QUIC: UDP)  web over TLS
Syslog           514              UDP              log messages
RTSP             554              TCP              control of media streams
SMTP submission  587              TCP              clients send mail
LDAPS            636              TCP              LDAP over TLS
IMAPS / POP3S    993 / 995        TCP              mail over TLS
RADIUS           1812/1813        UDP              authentication / accounting (AAA)
SIP              5060 (5061 TLS)  UDP/TCP          VoIP call signalling
RTP / RTCP       negotiated       UDP              voice/video media + feedback

LDAP: query a hierarchical directory (cn=alice,ou=staff,dc=example,dc=test) for users,
groups and attributes; bind = log in, search = look up. Used for central logins.
RADIUS: network access login/accounting (Wi-Fi 802.1X, VPN): switch asks RADIUS server.
SIP sets up the call (INVITE/ACK/BYE); SDP inside it describes the media; then RTP
carries the voice over UDP. RTP header = 12 bytes: version, payload type, sequence
number (detect loss/reorder) and timestamp (play-out timing, jitter).
VoIP numbers (G.711 codec, 20 ms packets): payload 160 B + 40 B headers
  = 200 B per packet, 50 packets/s -> 80 kbit/s on the IP layer
check: OK (64 kbit/s of audio costs 80 kbit/s once RTP/UDP/IP headers are added)
```

## Worked Example
**Problem.** (a) Syslog message begins `<165>`; decode facility and severity. (b) An SNMP manager walks `1.3.6.1.2.1.2.2.1.8` on a switch with 3 interfaces; which OIDs come back, in which order, and what does ifOperStatus value 2 mean? (c) A VoIP call uses a codec of 8 kbit/s with 20 ms packets over RTP/UDP/IPv4; what is the IP bandwidth?

**Solution.** (a) 165 // 8 = 20 and 165 % 8 = 5: facility 20 (local4), severity 5 (Notice). (b) `...2.2.1.8.1`, `...2.2.1.8.2`, `...2.2.1.8.3` in that order (row index increasing); 2 means down (1 is up). Then the walk leaves the subtree, so the agent's next OID (`...2.2.1.9.1`) is ignored by the manager. (c) Payload = 8000 / 8 x 0.020 = 20 bytes; + 40 header bytes = 60 bytes per packet, 50 packets/s: 60 x 8 x 50 = 24 kbit/s. Headers are two thirds of the traffic. Section 6 computed the same method for G.711 (80 kbit/s).

## Key Rules / Gotchas Recap
- Manager polls an agent on UDP 161; the agent's traps go to UDP 162.
- OIDs are compared arc by arc as numbers, never as text.
- v1 and v2c send the community string in clear text; use v3 authPriv and change the defaults.
- GetNext walks a subtree; GetBulk (v2c) does it with fewer round trips; Set needs write access and the right type.
- Counter32 wraps around; compute differences, and use 64-bit counters when possible.
- Syslog PRI = facility x 8 + severity; syslog over plain UDP is unauthenticated and lossy.
- NTP stratum counts hops from the reference clock.
- RTP uses UDP because late media is useless; the headers (RTP + UDP + IP = 40 bytes) matter for small codecs.
- Never poll or probe devices you do not own; this file only uses in-memory data and loopback.

## Why This Matters
Monitoring systems (Prometheus exporters, Zabbix, Nagios) often start from SNMP, and logs and alerts are how you see attacks and outages. Exposed SNMP with default community strings is a very common finding in security assessments, so knowing the data model and its weaknesses is useful on both the engineering and defence sides.
