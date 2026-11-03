# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""NAT and PAT simulated in memory: static NAT, dynamic NAT with a pool,
PAT (overload) with a port translation table, inbound handling, port
exhaustion, and why NAT breaks end-to-end addressing. No real packets."""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class Packet:
    src: str
    sport: int
    dst: str
    dport: int
    data: str = ""

    def __str__(self) -> str:
        return f"{self.src}:{self.sport} -> {self.dst}:{self.dport}"


# ===== SECTION 1: PRIVATE VS PUBLIC =====
print("===== SECTION 1: PRIVATE VS PUBLIC =====")
RFC1918 = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
for a in ["192.168.1.10", "10.0.0.5", "172.16.4.4", "172.32.4.4", "203.0.113.5", "8.8.8.8"]:
    ip = ipaddress.IPv4Address(a)
    note = "documentation range, used below as a stand-in for public addresses" if ip in ipaddress.ip_network("203.0.113.0/24") else ""
    print(f"{a:14} RFC1918 private={any(ip in n for n in RFC1918)!s:5} {note}")
print("Private (RFC 1918) addresses are reused by millions of networks, so they are NOT unique")
print("and routers on the Internet drop them. NAT swaps them for a public address at the border.")
print("Simulation below uses 203.0.113.0/24 (RFC 5737 documentation) as the 'public' side.")


# ===== SECTION 2: STATIC AND DYNAMIC NAT =====
print("\n===== SECTION 2: STATIC AND DYNAMIC NAT =====")


class Nat:
    """Basic NAT: one private address <-> one public address (ports unchanged)."""

    def __init__(self, pool: list[str], static: dict[str, str] | None = None) -> None:
        self.free = list(pool)
        self.map: dict[str, str] = dict(static or {})     # private -> public
        self.reverse = {v: k for k, v in self.map.items()}

    def outbound(self, p: Packet) -> Packet | None:
        if p.src not in self.map:
            if not self.free:
                return None                                # pool exhausted: no translation
            pub = self.free.pop(0)
            self.map[p.src], self.reverse[pub] = pub, p.src
        return Packet(self.map[p.src], p.sport, p.dst, p.dport, p.data)

    def inbound(self, p: Packet) -> Packet | None:
        if p.dst not in self.reverse:
            return None
        return Packet(p.src, p.sport, self.reverse[p.dst], p.dport, p.data)


nat = Nat(["203.0.113.11", "203.0.113.12"], static={"192.168.1.100": "203.0.113.10"})
print("static : 192.168.1.100 <-> 203.0.113.10 (web server reachable from outside at a fixed address)")
print("dynamic: pool = 203.0.113.11, 203.0.113.12 (first come, first served)")
for host in ["192.168.1.100", "192.168.1.21", "192.168.1.22", "192.168.1.23"]:
    out = nat.outbound(Packet(host, 5000, "198.51.100.9", 80))
    print(f"  {host:14} -> {out if out else 'DROPPED (pool exhausted: only 2 dynamic addresses for 3 hosts)'}")
reply = nat.inbound(Packet("198.51.100.9", 80, "203.0.113.11", 5000))
print("  reply to 203.0.113.11 is delivered to", reply.dst if reply else None)
assert reply and reply.dst == "192.168.1.21"
unsol = nat.inbound(Packet("198.51.100.9", 80, "203.0.113.99", 5000))
print("  unknown public address 203.0.113.99 ->", "dropped" if unsol is None else unsol)
print("check: OK")
print("Static NAT = 1:1 permanent; dynamic NAT = 1:1 temporary from a pool. Both need as many")
print("public addresses as simultaneous inside hosts, so they do NOT save addresses.")


# ===== SECTION 3: PAT (OVERLOAD) =====
print("\n===== SECTION 3: PAT / NAT OVERLOAD WITH PORT TABLE =====")


class Pat:
    def __init__(self, public_ip: str, port_lo: int = 1024, port_hi: int = 1030) -> None:
        self.public_ip = public_ip
        self.lo, self.hi = port_lo, port_hi
        self.next_port = port_lo
        self.table: dict[tuple[str, int, str, int], int] = {}      # (priv ip, priv port, dst, dport) -> public port
        self.back: dict[tuple[int, str, int], tuple[str, int]] = {}  # (public port, remote ip, remote port) -> (priv ip, priv port)

    def outbound(self, p: Packet) -> Packet | None:
        key = (p.src, p.sport, p.dst, p.dport)
        if key not in self.table:
            if self.next_port > self.hi:
                return None                                       # no ports left
            self.table[key] = self.next_port
            self.back[(self.next_port, p.dst, p.dport)] = (p.src, p.sport)
            self.next_port += 1
        return Packet(self.public_ip, self.table[key], p.dst, p.dport, p.data)

    def inbound(self, p: Packet) -> Packet | None:
        if p.dst != self.public_ip:
            return None
        hit = self.back.get((p.dport, p.src, p.sport))
        if hit is None:
            return None                                           # unsolicited: no mapping -> drop
        return Packet(p.src, p.sport, hit[0], hit[1], p.data)


pat = Pat("203.0.113.1")
flows = [Packet("192.168.1.10", 51000, "198.51.100.9", 80),
         Packet("192.168.1.11", 51000, "198.51.100.9", 80),      # SAME private port, different host
         Packet("192.168.1.10", 51001, "198.51.100.9", 443),
         Packet("192.168.1.12", 40000, "198.51.100.77", 53)]
print(f"{'inside (private)':24} {'outside (after PAT)':26}")
for f in flows:
    o = pat.outbound(f)
    print(f"{f.src + ':' + str(f.sport):24} {o.src + ':' + str(o.sport):26} to {f.dst}:{f.dport}")
print("\nNAT translation table (what the router stores):")
print(f"{'inside local':22} {'inside global':20} {'outside'}")
for (ip, port, d, dp), pub in pat.table.items():
    print(f"{ip + ':' + str(port):22} {pat.public_ip + ':' + str(pub):20} {d}:{dp}")
assert len({pub for pub in pat.table.values()}) == len(pat.table)
print("\nOne public IP, many hosts: the PORT number tells replies apart.")
rep = pat.inbound(Packet("198.51.100.9", 80, "203.0.113.1", 1025))
print("reply 198.51.100.9:80 -> 203.0.113.1:1025 is translated back to", f"{rep.dst}:{rep.dport}" if rep else None)
assert rep and (rep.dst, rep.dport) == ("192.168.1.11", 51000)
unsol = pat.inbound(Packet("203.0.113.200", 4444, "203.0.113.1", 1025))
print("unsolicited packet from 203.0.113.200:4444 to port 1025 ->", "dropped (no matching entry)" if unsol is None else unsol)
assert unsol is None
print("check: OK")


# ===== SECTION 4: PORT EXHAUSTION TRAP =====
print("\n===== SECTION 4: TRAP - PORT EXHAUSTION =====")
small = Pat("203.0.113.1", 1024, 1026)           # only 3 ports to make it visible
results = []
for i in range(5):
    r = small.outbound(Packet(f"192.168.1.{10 + i}", 50000, "198.51.100.9", 80))
    results.append(r.sport if r else None)
print("5 hosts, 3 usable ports ->", results, "(None = no free port, new flow is dropped)")
print("Real PAT has tens of thousands of ports per public address, but busy sites")
print("(carrier-grade NAT) can run out; fix = more public addresses in the pool or timeouts that")
print("free idle entries.")
assert results.count(None) == 2


# ===== SECTION 5: WHY NAT BREAKS END-TO-END =====
print("\n===== SECTION 5: ADVANTAGES, DISADVANTAGES, END-TO-END =====")
inside = Packet("192.168.1.10", 51000, "198.51.100.9", 21, data="PORT 192,168,1,10,200,10")
out = Pat("203.0.113.1").outbound(inside)
print("A protocol that writes its address INSIDE the payload (e.g. active FTP):")
print("  header after PAT:", out)
print("  payload still says:", repr(out.data), "-> the server would try to connect to a private address")
print("  Fix: an ALG (application-layer gateway) that rewrites payloads, or protocols avoiding embedded addresses.")
print("Advantages: saves public IPv4 addresses, hides internal addressing, easy ISP changes, basic")
print("  'unsolicited inbound drop' behaviour (this is a side effect, NOT a security feature by design).")
print("Disadvantages: breaks end-to-end principle, inbound connections need port forwarding,")
print("  complicates P2P/VoIP/IPsec AH, adds state and latency, per-flow logging needed for audit.")
print("IPv6: with 2^128 addresses every host can have a public address, so NAT is not needed for")
print("  address conservation (NAT66 and NAT64 exist for special cases).")
