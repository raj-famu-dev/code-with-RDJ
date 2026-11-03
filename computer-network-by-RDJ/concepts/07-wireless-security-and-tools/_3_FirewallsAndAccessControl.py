# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Firewalls and access control: firewall types, ACL rule matching with
first-match-wins and default deny, the rule-order trap, a stateful connection
table, an application-layer (proxy-style) filter, DMZ zone policy and an
IDS-vs-IPS comparison. All traffic is made-up data evaluated in memory."""
import ipaddress
from dataclasses import dataclass

# ===== SECTION 1: FIREWALL TYPES =====
print("===== SECTION 1: FIREWALL TYPES =====")
print("Type                  Looks at                               Remembers?   Strength / weakness")
print("Packet filter         L3/L4 headers (IP, proto, port)        no           fast, simple; blind to context and payload")
print("Stateful inspection   headers + connection state             yes (table)  allows only replies to inside-initiated flows")
print("Proxy / application   full L7 content (HTTP, FTP, SMTP ...)  yes           deepest checks, breaks the client-server link in two; slower")
print("Next-gen (NGFW)       app identification, users, IPS         yes          a marketing name for stateful + L7 + IPS features")
print("Placement: a firewall enforces policy at a boundary between zones of different trust (inside / DMZ / outside).")

# ===== SECTION 2: ACL RULE MATCHING - FIRST MATCH WINS =====
print("\n===== SECTION 2: ACL RULE MATCHING - FIRST MATCH WINS =====")


@dataclass(frozen=True)
class Packet:
    src: str
    dst: str
    proto: str
    dport: int


@dataclass(frozen=True)
class Rule:
    action: str          # "permit" or "deny"
    proto: str           # "tcp", "udp", "icmp" or "any"
    src: str             # CIDR or "any"
    dst: str             # CIDR or "any"
    dport: str           # port number as text, or "any"

    def matches(self, p: Packet) -> bool:
        def in_net(addr: str, net: str) -> bool:
            return net == "any" or ipaddress.ip_address(addr) in ipaddress.ip_network(net)
        return ((self.proto in ("any", p.proto)) and in_net(p.src, self.src) and in_net(p.dst, self.dst)
                and (self.dport == "any" or int(self.dport) == p.dport))


def evaluate(rules: list[Rule], p: Packet) -> tuple[str, str]:
    for i, r in enumerate(rules, 1):
        if r.matches(p):
            return r.action, f"rule {i}"
    return "deny", "implicit default deny"


ACL = [
    Rule("deny", "any", "198.51.100.0/24", "any", "any"),     # known-bad network
    Rule("permit", "tcp", "any", "192.0.2.10/32", "443"),      # public HTTPS server
    Rule("permit", "tcp", "10.0.0.0/8", "any", "22"),          # internal admins may SSH out
    Rule("permit", "icmp", "10.0.0.0/8", "any", "any"),        # internal ping
]
PACKETS = [
    Packet("203.0.113.9", "192.0.2.10", "tcp", 443),
    Packet("198.51.100.7", "192.0.2.10", "tcp", 443),
    Packet("203.0.113.9", "192.0.2.10", "tcp", 23),
    Packet("10.1.2.3", "203.0.113.50", "tcp", 22),
    Packet("10.1.2.3", "203.0.113.50", "icmp", 0),
    Packet("172.16.0.5", "192.0.2.10", "udp", 53),
]
print("ACL (top to bottom):")
for i, r in enumerate(ACL, 1):
    print(f"  {i}. {r.action:<6} {r.proto:<4} src={r.src:<16} dst={r.dst:<14} dport={r.dport}")
print("  (implicit last rule: deny any any)")
EXPECT = ["permit", "deny", "deny", "permit", "permit", "deny"]
got = []
for p in PACKETS:
    action, why = evaluate(ACL, p)
    got.append(action)
    print(f"  {p.src:>13} -> {p.dst:<13} {p.proto:<4}/{p.dport:<4} => {action.upper():<6} ({why})")
assert got == EXPECT
print("check: OK (verdicts match the hand-worked answers)")

print("-- TRAP: rule order. Put the permit for the server above the deny for the bad network --")
BAD_ACL = [ACL[1], ACL[0], ACL[2], ACL[3]]
evil = Packet("198.51.100.7", "192.0.2.10", "tcp", 443)
print("  packet from the bad network, correct ACL:  ", evaluate(ACL, evil))
print("  packet from the bad network, wrong order:  ", evaluate(BAD_ACL, evil), "<- the deny is shadowed, never reached")
print("Rule: most specific first, broadest last; always end with deny; review for shadowed rules.")
assert evaluate(ACL, evil)[0] == "deny" and evaluate(BAD_ACL, evil)[0] == "permit"
print("check: OK")

# ===== SECTION 3: STATEFUL CONNECTION TABLE =====
print("\n===== SECTION 3: STATEFUL CONNECTION TABLE =====")
INSIDE = ipaddress.ip_network("10.0.0.0/8")


class StatefulFirewall:
    def __init__(self, idle_timeout: int) -> None:
        self.table: dict[tuple[str, int, str, int], int] = {}   # flow -> last-seen tick
        self.idle_timeout = idle_timeout

    def handle(self, tick: int, src: str, sport: int, dst: str, dport: int) -> str:
        for k in [k for k, seen in self.table.items() if tick - seen > self.idle_timeout]:
            del self.table[k]                                   # age out idle entries
        outbound = ipaddress.ip_address(src) in INSIDE
        if outbound:
            self.table[(src, sport, dst, dport)] = tick         # create/refresh
            return "PERMIT (new outbound flow, entry added)"
        if (dst, dport, src, sport) in self.table:              # reply matches reversed tuple
            self.table[(dst, dport, src, sport)] = tick
            return "PERMIT (reply to an inside-initiated flow)"
        return "DROP   (no matching entry: unsolicited inbound)"


fw = StatefulFirewall(idle_timeout=30)
events = [
    (0, "10.0.0.5", 50000, "203.0.113.80", 80),
    (1, "203.0.113.80", 80, "10.0.0.5", 50000),   # genuine reply
    (2, "203.0.113.99", 80, "10.0.0.5", 50000),   # wrong source host
    (3, "203.0.113.80", 4444, "10.0.0.5", 50000), # wrong source port
    (4, "203.0.113.80", 80, "10.0.0.5", 50001),   # wrong destination port
    (60, "203.0.113.80", 80, "10.0.0.5", 50000),  # reply after 59 idle ticks
]
verdicts = []
for ev in events:
    v = fw.handle(*ev)
    verdicts.append(v.split()[0])
    print(f"  t={ev[0]:>2} {ev[1]}:{ev[2]} -> {ev[3]}:{ev[4]}  {v}")
assert verdicts == ["PERMIT", "PERMIT", "DROP", "DROP", "DROP", "DROP"]
print("check: OK")
print("A STATELESS packet filter must allow all inbound high ports (to catch replies), which also admits unsolicited")
print("packets to those ports. Stateful needs only 'outbound allowed' and remembers who spoke first. UDP 'state' is a")
print("timeout guess because UDP has no handshake; TCP state can also track SYN/FIN.")

# ===== SECTION 4: APPLICATION-LAYER (PROXY-STYLE) FILTERING =====
print("\n===== SECTION 4: APPLICATION-LAYER (PROXY-STYLE) FILTERING =====")
ALLOWED_METHODS = {"GET", "HEAD"}
ALLOWED_HOSTS = {"intranet.example", "docs.example"}


def http_policy(raw: str) -> str:
    request_line, *headers = raw.split("\r\n")
    parts = request_line.split(" ")
    if len(parts) != 3:
        return "BLOCK malformed request line"
    method, path, _version = parts
    host = next((h.split(":", 1)[1].strip() for h in headers if h.lower().startswith("host:")), "")
    if method not in ALLOWED_METHODS:
        return f"BLOCK method {method} not allowed"
    if host not in ALLOWED_HOSTS:
        return f"BLOCK host '{host}' not on the allow list"
    if ".." in path:
        return "BLOCK path traversal pattern"
    return "ALLOW"


for raw in ["GET /index.html HTTP/1.1\r\nHost: docs.example",
            "POST /upload HTTP/1.1\r\nHost: docs.example",
            "GET /../../etc/passwd HTTP/1.1\r\nHost: intranet.example",
            "GET / HTTP/1.1\r\nHost: unknown.example",
            "GARBAGE"]:
    print(f"  {raw.splitlines()[0]:<45} -> {http_policy(raw)}")
print("A packet filter sees only 'TCP to port 80/443' and cannot make any of these distinctions.")
print("Cost: a proxy terminates the connection and opens a second one, so it must understand each protocol, and")
print("encrypted traffic (TLS) hides the content unless the proxy decrypts it (which brings its own risks).")

# ===== SECTION 5: DMZ AND ZONE POLICY =====
print("\n===== SECTION 5: DMZ AND ZONE POLICY =====")
print("Internet --[FW]-- DMZ (public web/mail/DNS servers)")
print("             |")
print("            LAN (users, databases)")
POLICY = {  # (from_zone, to_zone) -> allowed destination ports (None = nothing)
    ("internet", "dmz"): {80, 443, 25},
    ("internet", "lan"): set(),
    ("dmz", "lan"): {5432},        # only the web app's database port, an explicit hole
    ("dmz", "internet"): {53},
    ("lan", "dmz"): {22, 80, 443},
    ("lan", "internet"): {80, 443, 53},
}


def zone_allows(src: str, dst: str, port: int) -> bool:
    return port in POLICY.get((src, dst), set())     # missing pair == default deny


tests = [("internet", "dmz", 443, True), ("internet", "lan", 443, False), ("internet", "dmz", 22, False),
         ("dmz", "lan", 22, False), ("dmz", "lan", 5432, True), ("lan", "internet", 443, True)]
for s, d, port, want in tests:
    got_ok = zone_allows(s, d, port)
    assert got_ok == want
    print(f"  {s:>8} -> {d:<8} port {port:<5} {'ALLOW' if got_ok else 'DENY '}")
print("check: OK")
print("Idea: if the web server in the DMZ is compromised, the attacker still faces a second firewall rule set before")
print("reaching the LAN. Without a DMZ, public servers would sit inside, or be exposed outside with no protection.")

# ===== SECTION 6: IDS VS IPS =====
print("\n===== SECTION 6: IDS VS IPS =====")
SIGNATURES = {"/etc/passwd": "path-traversal signature", "' OR 1=1": "SQL-injection-style signature"}
log = [("203.0.113.20", 80, "GET /index"), ("203.0.113.21", 80, "GET /a?q=' OR 1=1"),
       ("203.0.113.22", 80, "GET /../../etc/passwd"), ("203.0.113.20", 80, "GET /about")]


def inspect(payload: str) -> str | None:
    return next((name for sig, name in SIGNATURES.items() if sig in payload), None)


for mode in ("IDS (passive, copy of traffic)", "IPS (inline, can drop)"):
    print(f"-- {mode} --")
    for src, port, payload in log:
        hit = inspect(payload)
        if hit is None:
            print(f"  {src:<13} {payload:<24} pass")
        elif mode.startswith("IDS"):
            print(f"  {src:<13} {payload:<24} ALERT ({hit}); packet was already delivered")
        else:
            print(f"  {src:<13} {payload:<24} DROPPED ({hit})")

print("-- Anomaly (behaviour) rule: many distinct destination ports from one source in a short window --")
conn_log = [("203.0.113.30", p) for p in range(1, 41)] + [("203.0.113.40", p) for p in (80, 443, 80, 443, 443)]


def scan_like(entries: list[tuple[str, int]], threshold: int) -> list[str]:
    ports: dict[str, set[int]] = {}
    for src, port in entries:
        ports.setdefault(src, set()).add(port)
    return sorted(s for s, ps in ports.items() if len(ps) >= threshold)


print("  threshold 20 distinct ports ->", scan_like(conn_log, 20))
print("  threshold 2  distinct ports ->", scan_like(conn_log, 2), "<- TRAP: a normal web client flagged (false positive)")
assert scan_like(conn_log, 20) == ["203.0.113.30"]
print("check: OK")
print("IDS: detects and alerts, no effect on traffic, so a miss is only a missed alert. IPS: acts, so a false positive")
print("blocks real users and it is a point of failure. Signature = known bad; anomaly = unusual, more false alarms.")
