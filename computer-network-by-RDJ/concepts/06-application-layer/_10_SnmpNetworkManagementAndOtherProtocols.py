# Tags: #Python #ComputerNetworks #ApplicationLayer #SnmpNetworkManagementOtherProtocols | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches SNMP network management (manager, agent, MIB, OID, GET/GETNEXT/SET/TRAP,
v1/v2c/v3), the ASN.1 BER bytes of a real SNMP message, a simulated MIB walk,
Syslog (PRI = facility*8 + severity), NTP strata, and a port-and-protocol table
for LDAP/RADIUS/SIP/RTP/VoIP and older web-era protocols.
Everything is an in-memory simulation (plus one UDP syslog datagram on loopback).
Syllabus idea: Network management and other application protocols.
"""
import bisect
import socket
import struct

HOST = "127.0.0.1"

# ===== SECTION 1: SNMP CONCEPTS AND VERSIONS =====
print("===== SECTION 1: SNMP CONCEPTS AND VERSIONS =====")
print("""  manager (NMS) ---- GetRequest / GetNext / GetBulk / SetRequest --> agent (on router, switch, server)
  manager        <---------------------- Response -------------------- agent
  manager        <------ Trap / Inform (unsolicited alarm, UDP 162) ---- agent
  The agent keeps variables in a MIB (Management Information Base), a tree whose
  nodes are named by OIDs (Object Identifiers), e.g. 1.3.6.1.2.1.1.5.0 = sysName.""")
print("Agent listens on UDP 161; the manager listens for traps on UDP 162.")
print("SMI/ASN.1 defines the data types (INTEGER, OCTET STRING, Counter32, Gauge32, TimeTicks...);")
print("messages are encoded with BER (Basic Encoding Rules), shown in Section 3.")
print(f"\n{'':<12}{'v1':<20}{'v2c':<36}{'v3'}")
for row in [("security", "community string", "community string", "users, auth (HMAC), privacy (encryption)"),
            ("clear text", "yes", "yes", "only if you pick noAuthNoPriv"),
            ("new in it", "-", "GetBulk, 64-bit counters, Inform", "USM + VACM access control"),
            ("errors", "noSuchName", "noSuchObject / endOfMibView", "same as v2c"),
            ("verdict", "legacy", "common but weak", "use this one")]:
    print(f"{row[0]:<12}{row[1]:<20}{row[2]:<36}{row[3]}")
print("A v1/v2c 'community string' (default 'public' for read, 'private' for write) is a")
print("PASSWORD SENT IN CLEAR TEXT. Anyone on the path can read it; change the defaults.")

# ===== SECTION 2: THE OID TREE AND A SORTING TRAP =====
print("\n===== SECTION 2: THE OID TREE AND A SORTING TRAP =====")
print("""  1 iso
  +-3 org
    +-6 dod
      +-1 internet
        +-2 mgmt
        | +-1 mib-2
        |   +-1 system      (1.3.6.1.2.1.1)   sysDescr .1, sysUpTime .3, sysName .5
        |   +-2 interfaces  (1.3.6.1.2.1.2)   ifNumber .1, ifTable .2
        +-4 private
          +-1 enterprises   (1.3.6.1.4.1)     vendors get a number, e.g. 8072""")
print("A trailing .0 means a scalar instance; table cells end in a row index (ifDescr.2).")
oids = ["1.3.6.1.2.1.2.2.1.2.1", "1.3.6.1.2.1.2.2.1.10.1", "1.3.6.1.2.1.2.2.1.8.1", "1.3.6.1.2.1.1.5.0"]
print("TRAP: sorting OIDs as text:    ", sorted(oids))
as_tuples = sorted(oids, key=lambda s: tuple(int(x) for x in s.split(".")))
print("FIX : compare each arc as a number:", as_tuples)
assert sorted(oids) != as_tuples and as_tuples[-1].endswith(".10.1")
print("check: OK (as text '...1.10.1' sorts before '...1.2.1'; numerically it is after)")
print("GETNEXT/WALK depend on the numeric order, so agents store OIDs as tuples of ints.")

# ===== SECTION 3: SNMP ON THE WIRE (ASN.1 BER) =====
print("\n===== SECTION 3: SNMP ON THE WIRE (ASN.1 BER) =====")
INTEGER, OCTETS, NULL, OID_T, SEQ = 0x02, 0x04, 0x05, 0x06, 0x30
COUNTER32, GAUGE32, TIMETICKS = 0x41, 0x42, 0x43
GET, GETNEXT, RESPONSE, SET, GETBULK, TRAP2 = 0xA0, 0xA1, 0xA2, 0xA3, 0xA5, 0xA7


def tlv(tag: int, content: bytes) -> bytes:
    n = len(content)
    if n < 128:
        length = bytes([n])                                  # short form: one length byte
    else:
        raw = n.to_bytes((n.bit_length() + 7) // 8, "big")   # long form: 0x80|count, then bytes
        length = bytes([0x80 | len(raw)]) + raw
    return bytes([tag]) + length + content


def enc_int(n: int) -> bytes:
    return tlv(INTEGER, n.to_bytes(n.bit_length() // 8 + 1, "big", signed=True))


def enc_oid(oid: tuple[int, ...]) -> bytes:
    arcs = [40 * oid[0] + oid[1], *oid[2:]]
    out = b""
    for a in arcs:
        chunk = [a & 0x7F]
        a >>= 7
        while a:
            chunk.append(0x80 | (a & 0x7F))
            a >>= 7
        out += bytes(reversed(chunk))
    return tlv(OID_T, out)


def read_tlv(data: bytes, pos: int = 0) -> tuple[int, bytes, int]:
    tag, length = data[pos], data[pos + 1]
    pos += 2
    if length & 0x80:
        count = length & 0x7F
        length = int.from_bytes(data[pos:pos + count], "big")
        pos += count
    return tag, data[pos:pos + length], pos + length


def dec_oid(content: bytes) -> tuple[int, ...]:
    arcs, value = [], 0
    for b in content:
        value = (value << 7) | (b & 0x7F)
        if not b & 0x80:
            arcs.append(value)
            value = 0
    first = arcs[0]
    return (first // 40, first % 40, *arcs[1:])


def snmp_message(version: int, community: bytes, pdu_tag: int, request_id: int,
                 varbinds: list[tuple[tuple[int, ...], bytes]], err: int = 0, idx: int = 0) -> bytes:
    vbl = b"".join(tlv(SEQ, enc_oid(o) + v) for o, v in varbinds)
    pdu = tlv(pdu_tag, enc_int(request_id) + enc_int(err) + enc_int(idx) + tlv(SEQ, vbl))
    return tlv(SEQ, enc_int(version) + tlv(OCTETS, community) + pdu)


SYS_DESCR = (1, 3, 6, 1, 2, 1, 1, 1, 0)
request = snmp_message(0, b"public", GET, 1, [(SYS_DESCR, tlv(NULL, b""))])
print("GetRequest for sysDescr.0, SNMPv1, community 'public', request-id 1:")
print("  ", request.hex(" "))
print("   30 26            SEQUENCE, 38 bytes follow")
print("   02 01 00         INTEGER version = 0 (v1; v2c is 1)")
print("   04 06 70 75 62 6c 69 63   OCTET STRING 'public' <-- the community, readable!")
print("   a0 19            GetRequest PDU, 25 bytes")
print("   02 01 01 | 02 01 00 | 02 01 00   request-id, error-status, error-index")
print("   30 0e 30 0c      varbind list / one varbind")
print("   06 08 2b 06 01 02 01 01 01 00    OID 1.3.6.1.2.1.1.1.0 (first byte 2b = 40*1+3)")
print("   05 00            NULL (no value yet)")
expected = bytes.fromhex("302602010004067075626c6963a0190201010201000201003 00e300c06082b060102010101 000500".replace(" ", ""))
assert request == expected, request.hex()
assert enc_oid((1, 3, 6, 1, 4, 1, 8072)) == bytes.fromhex("06072b06010401bf08")
assert dec_oid(enc_oid((1, 3, 6, 1, 4, 1, 8072))[2:]) == (1, 3, 6, 1, 4, 1, 8072)
print("check: OK (matches the hand-derived bytes; arc 8072 needs two bytes: bf 08 = 63*128 + 8)")

# ===== SECTION 4: A SIMULATED AGENT: GET, GETNEXT, WALK, BULK, SET, TRAP =====
print("\n===== SECTION 4: A SIMULATED AGENT: GET, GETNEXT, WALK, BULK, SET, TRAP =====")
class Agent:
    def __init__(self) -> None:
        self.mib: dict[tuple[int, ...], list] = {}          # oid -> [type, value, writable]
        self.names: dict[tuple[int, ...], str] = {}
        self.keys: list[tuple[int, ...]] = []
        self.traps: list[str] = []
        self.auth_failures = 0

        def add(oid: str, name: str, typ: int, val, rw: bool = False) -> None:
            t = tuple(int(x) for x in oid.split("."))
            self.mib[t], self.names[t] = [typ, val, rw], name

        add("1.3.6.1.2.1.1.1.0", "sysDescr.0", OCTETS, b"RDJ demo router, simulated")
        add("1.3.6.1.2.1.1.3.0", "sysUpTime.0", TIMETICKS, 123456)
        add("1.3.6.1.2.1.1.4.0", "sysContact.0", OCTETS, b"admin@example.test", True)
        add("1.3.6.1.2.1.1.5.0", "sysName.0", OCTETS, b"rtr1", True)
        add("1.3.6.1.2.1.2.1.0", "ifNumber.0", INTEGER, 2)
        for i, (d, st, rx) in enumerate([(b"eth0", 1, 9_000_000), (b"eth1", 1, 42)], 1):
            add(f"1.3.6.1.2.1.2.2.1.2.{i}", f"ifDescr.{i}", OCTETS, d)
            add(f"1.3.6.1.2.1.2.2.1.8.{i}", f"ifOperStatus.{i}", INTEGER, st)
            add(f"1.3.6.1.2.1.2.2.1.10.{i}", f"ifInOctets.{i}", COUNTER32, rx)
        self.keys = sorted(self.mib)                        # tuple order = numeric order

    def auth(self, community: str, write: bool = False) -> bool:
        ok = community == ("private" if write else "public") or (not write and community == "private")
        if not ok:
            self.auth_failures += 1
            self.traps.append("authenticationFailure (1.3.6.1.6.3.1.1.5.5)")
        return ok

    def fmt(self, oid) -> str:
        return ".".join(map(str, oid))

    def show(self, oid, entry) -> str:
        typ, val, _ = entry
        text = val.decode() if typ == OCTETS else val
        label = {INTEGER: "INTEGER", OCTETS: "STRING", COUNTER32: "Counter32", TIMETICKS: "Timeticks"}[typ]
        return f"{self.names.get(oid, self.fmt(oid))} = {label}: {text}"

    def get(self, community: str, oid: tuple[int, ...]) -> str | None:
        if not self.auth(community):
            return None                                       # silently dropped, as real agents do
        return self.show(oid, self.mib[oid]) if oid in self.mib else f"{self.fmt(oid)} = noSuchObject"

    def getnext(self, oid: tuple[int, ...]):
        i = bisect.bisect_right(self.keys, oid)
        return self.keys[i] if i < len(self.keys) else None

    def walk(self, community: str, root: tuple[int, ...]) -> list[str]:
        out, cur = [], root
        while self.auth(community):
            cur = self.getnext(cur)
            if cur is None or cur[:len(root)] != root:
                break
            out.append(self.show(cur, self.mib[cur]))
        return out

    def getbulk(self, oid: tuple[int, ...], max_rep: int) -> list[str]:
        out, cur = [], oid
        for _ in range(max_rep):
            cur = self.getnext(cur)
            out.append(self.show(cur, self.mib[cur]) if cur else "endOfMibView")
            if cur is None:
                break
        return out

    def set(self, community: str, oid: tuple[int, ...], typ: int, val) -> str:
        if not self.auth(community, write=True):
            return "(no response: wrong community)"
        if oid not in self.mib:
            return "noCreation"
        entry = self.mib[oid]
        if not entry[2]:
            return "notWritable"
        if entry[0] != typ:
            return "wrongType"
        entry[1] = val
        return "OK -> " + self.show(oid, entry)

    def link_event(self, index: int, status: int) -> None:
        self.mib[(1, 3, 6, 1, 2, 1, 2, 2, 1, 8, index)][1] = status
        word = {1: "up", 2: "down"}[status]
        self.traps.append(f"linkDown/linkUp trap: ifIndex={index} ifOperStatus={status}({word})")


agent = Agent()
def T(text: str) -> tuple[int, ...]:
    """OID text -> tuple of ints."""
    return tuple(int(x) for x in text.split("."))


print("GET with the right community, a wrong one, and a missing object:")
print("  ", agent.get("public", T("1.3.6.1.2.1.1.5.0")))
print("  ", agent.get("public", T("1.3.6.1.2.1.1.5.1")))
print("  ", agent.get("hunter2", T("1.3.6.1.2.1.1.5.0")) or "(no reply at all: wrong community)")
print("\nGETNEXT chain starting before the first object (this is how a WALK works):")
cur = T("1.3.6.1.2.1.1")
for _ in range(3):
    cur = agent.getnext(cur)
    print("  ", agent.show(cur, agent.mib[cur]))
print("\nWALK of the interfaces subtree 1.3.6.1.2.1.2:")
rows = agent.walk("public", T("1.3.6.1.2.1.2"))
for r in rows:
    print("  ", r)
assert len(rows) == 7 and rows[-1].startswith("ifInOctets.2")
print("   (numeric order: ...2.1.2.x, then ...2.1.8.x, then ...2.1.10.x)")
print("\nGETBULK (v2c): 3 successors in ONE request instead of 3 round trips:")
for r in agent.getbulk(T("1.3.6.1.2.1.1.4.0"), 3):
    print("  ", r)
print("\nSET (needs the write community and a writable object of the right type):")
print("   sysName.0 = 'core-rtr' ->", agent.set("private", T("1.3.6.1.2.1.1.5.0"), OCTETS, b"core-rtr"))
print("   sysDescr.0 (read-only)  ->", agent.set("private", T("1.3.6.1.2.1.1.1.0"), OCTETS, b"x"))
print("   sysName.0 with 'public' ->", agent.set("public", T("1.3.6.1.2.1.1.5.0"), OCTETS, b"evil"))
print("   sysName.0 as INTEGER    ->", agent.set("private", T("1.3.6.1.2.1.1.5.0"), INTEGER, 7))
print("\nTrap: interface eth1 goes down; the agent tells the manager unprompted:")
agent.link_event(2, 2)
print("  ", agent.traps[-1])
print("   polling finds out within one poll period; a trap tells within one packet.")
print("Traps recorded by the agent so far:")
for t in agent.traps:
    print("  -", t)
assert agent.auth_failures >= 2
print("check: OK")

# ===== SECTION 5: SYSLOG =====
print("\n===== SECTION 5: SYSLOG =====")
print("Syslog (UDP 514 classic): devices send one-line log messages to a collector.")
print("Message starts with <PRI>, where PRI = facility x 8 + severity.")
SEVERITY = ["Emergency", "Alert", "Critical", "Error", "Warning", "Notice", "Informational", "Debug"]
FACILITY = {0: "kern", 1: "user", 2: "mail", 3: "daemon", 4: "auth", 5: "syslog", 9: "cron",
            10: "authpriv", 16: "local0", 17: "local1"}
print("severity: " + ", ".join(f"{i} {s}" for i, s in enumerate(SEVERITY)))


def decode_pri(message: str) -> tuple[str, str, str]:
    pri_text, _, rest = message[1:].partition(">")
    pri = int(pri_text)
    return FACILITY.get(pri // 8, f"facility{pri // 8}"), SEVERITY[pri % 8], rest


for fac, sev in ((4, 2), (16, 6), (0, 0)):
    print(f"  facility {fac:>2} ({FACILITY[fac]}) x 8 + severity {sev} = PRI {fac * 8 + sev}")
assert 4 * 8 + 2 == 34 and 16 * 8 + 6 == 134
sample = "<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8"
rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind((HOST, 0))
rx.settimeout(2)
tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    tx.sendto(sample.encode(), rx.getsockname())
    data, _ = rx.recvfrom(2048)
finally:
    tx.close()
    rx.close()
facility, severity, text = decode_pri(data.decode())
print(f"\nOne datagram over loopback UDP: {data.decode()!r}")
print(f"  decoded -> facility={facility}, severity={severity}, text={text.strip()!r}")
assert (facility, severity) == ("auth", "Critical")
print("check: OK (PRI 34 = auth.critical)")
print("Syslog over UDP is unauthenticated and can be lost or forged; use TCP+TLS for logs")
print("that matter. Central logging is how you notice attacks and outages.")

# ===== SECTION 6: NTP STRATA, PORTS AND PROTOCOLS, VOIP NUMBERS =====
print("\n===== SECTION 6: NTP STRATA, PORTS AND PROTOCOLS, VOIP NUMBERS =====")
print("NTP strata: 0 reference clock (GPS/atomic) -> 1 -> 2 -> ... 15; 16 = unsynchronised.")
for s, who in ((0, "GPS receiver (not on the network)"), (1, "primary server wired to it"),
               (2, "syncs to stratum 1 (e.g. your office server)"), (3, "your laptop syncs to that")):
    print(f"  stratum {s}: {who}")
TABLE = [
    ("FTP", "20/21", "TCP", "file transfer (data / control)"), ("SSH", "22", "TCP", "secure remote login, SFTP"),
    ("Telnet", "23", "TCP", "remote login, cleartext"), ("SMTP", "25", "TCP", "send mail between servers"),
    ("DNS", "53", "UDP+TCP", "name resolution"), ("DHCP", "67/68", "UDP", "address configuration"),
    ("TFTP", "69", "UDP", "trivial file transfer"), ("Gopher", "70", "TCP", "menu-based documents (WWW predecessor)"),
    ("Finger", "79", "TCP", "who is logged in (historic)"), ("HTTP", "80", "TCP", "web"),
    ("POP3", "110", "TCP", "mail retrieval"), ("NNTP", "119", "TCP", "Usenet news (historic)"),
    ("NTP", "123", "UDP", "time sync"), ("IMAP", "143", "TCP", "mail access"),
    ("SNMP", "161/162", "UDP", "management / traps"), ("LDAP", "389", "TCP (+UDP)", "directory lookup"),
    ("HTTPS", "443", "TCP (QUIC: UDP)", "web over TLS"), ("Syslog", "514", "UDP", "log messages"),
    ("RTSP", "554", "TCP", "control of media streams"), ("SMTP submission", "587", "TCP", "clients send mail"),
    ("LDAPS", "636", "TCP", "LDAP over TLS"), ("IMAPS / POP3S", "993 / 995", "TCP", "mail over TLS"),
    ("RADIUS", "1812/1813", "UDP", "authentication / accounting (AAA)"),
    ("SIP", "5060 (5061 TLS)", "UDP/TCP", "VoIP call signalling"),
    ("RTP / RTCP", "negotiated", "UDP", "voice/video media + feedback"),
]
print(f"\n{'protocol':<17}{'port':<17}{'transport':<17}purpose")
for row in TABLE:
    print(f"{row[0]:<17}{row[1]:<17}{row[2]:<17}{row[3]}")
print("\nLDAP: query a hierarchical directory (cn=alice,ou=staff,dc=example,dc=test) for users,")
print("groups and attributes; bind = log in, search = look up. Used for central logins.")
print("RADIUS: network access login/accounting (Wi-Fi 802.1X, VPN): switch asks RADIUS server.")
print("SIP sets up the call (INVITE/ACK/BYE); SDP inside it describes the media; then RTP")
print("carries the voice over UDP. RTP header = 12 bytes: version, payload type, sequence")
print("number (detect loss/reorder) and timestamp (play-out timing, jitter).")
payload = 64_000 // 8 * 20 // 1000                          # G.711: 64 kbit/s, 20 ms of audio
overhead = 12 + 8 + 20                                      # RTP + UDP + IPv4
pps = 1000 // 20
bps = (payload + overhead) * 8 * pps
print(f"VoIP numbers (G.711 codec, 20 ms packets): payload {payload} B + {overhead} B headers")
print(f"  = {payload + overhead} B per packet, {pps} packets/s -> {bps / 1000:.0f} kbit/s on the IP layer")
assert payload == 160 and bps == 80_000
print("check: OK (64 kbit/s of audio costs 80 kbit/s once RTP/UDP/IP headers are added)")
