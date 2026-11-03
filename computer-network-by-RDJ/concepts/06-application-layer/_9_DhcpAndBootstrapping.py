# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches DHCP: the DORA exchange, the packed message format (struct), lease
timers T1/T2, relay agents, APIPA fallback, an in-memory DHCP server with an
address pool and lease expiry, starvation and rogue-server attacks with their
defences (port security, DHCP snooping), plus BOOTP and NTP overviews.
Everything is an IN-MEMORY SIMULATION: no sockets, no real network traffic.
Syllabus idea: DHCP / bootstrapping (application layer, UDP ports 67 and 68).
"""
import ipaddress
import random
import struct

MAGIC = bytes.fromhex("63825363")
MSG = {1: "DISCOVER", 2: "OFFER", 3: "REQUEST", 4: "DECLINE", 5: "ACK", 6: "NAK",
       7: "RELEASE", 8: "INFORM"}
OPT = {1: "subnet mask", 3: "router", 6: "DNS", 50: "requested IP", 51: "lease time",
       53: "message type", 54: "server id", 61: "client id", 255: "end"}
HEADER = struct.Struct("!BBBBIHH4s4s4s4s16s64s128s")


def mac_bytes(mac: str) -> bytes:
    return bytes(int(x, 16) for x in mac.split(":"))


def mac_str(raw: bytes) -> str:
    return ":".join(f"{b:02x}" for b in raw)


def ip4(text: str) -> bytes:
    return ipaddress.IPv4Address(text).packed


def pack_dhcp(op: int, xid: int, mac: str, msg_type: int, ciaddr: str = "0.0.0.0",
              yiaddr: str = "0.0.0.0", siaddr: str = "0.0.0.0", giaddr: str = "0.0.0.0",
              flags: int = 0, options: list[tuple[int, bytes]] | None = None) -> bytes:
    fixed = HEADER.pack(op, 1, 6, 0, xid, 0, flags, ip4(ciaddr), ip4(yiaddr), ip4(siaddr),
                        ip4(giaddr), mac_bytes(mac).ljust(16, b"\x00"), b"", b"")
    body = bytes([53, 1, msg_type])
    for code, val in options or []:
        body += bytes([code, len(val)]) + val
    return fixed + MAGIC + body + b"\xff"


def parse_dhcp(data: bytes) -> dict:
    op, htype, hlen, hops, xid, secs, flags, ci, yi, si, gi, chaddr, _, _ = HEADER.unpack(data[:236])
    assert data[236:240] == MAGIC, "missing magic cookie"
    opts, pos = {}, 240
    while data[pos] != 255:
        code, length = data[pos], data[pos + 1]
        opts[code] = data[pos + 2: pos + 2 + length]
        pos += 2 + length
    return {"op": op, "xid": xid, "flags": flags, "ciaddr": str(ipaddress.IPv4Address(ci)),
            "yiaddr": str(ipaddress.IPv4Address(yi)), "siaddr": str(ipaddress.IPv4Address(si)),
            "giaddr": str(ipaddress.IPv4Address(gi)), "mac": mac_str(chaddr[:hlen]),
            "type": opts[53][0], "options": opts}


def opt_ip(code: int, text: str) -> tuple[int, bytes]:
    return code, ip4(text)


def describe(d: dict) -> str:
    extra = []
    if 51 in d["options"]:
        extra.append(f"lease={struct.unpack('!I', d['options'][51])[0]}s")
    if 3 in d["options"]:
        extra.append(f"router={ipaddress.IPv4Address(d['options'][3])}")
    if 50 in d["options"]:
        extra.append(f"wants={ipaddress.IPv4Address(d['options'][50])}")
    return (f"{MSG[d['type']]:<8} xid={d['xid']:#010x} yiaddr={d['yiaddr']:<14} "
            f"ciaddr={d['ciaddr']:<14} {' '.join(extra)}")


# ===== SECTION 1: WHY DHCP AND THE DORA EXCHANGE =====
print("===== SECTION 1: WHY DHCP AND THE DORA EXCHANGE =====")
print("A new host knows only its MAC address. It needs an IP, a mask, a default router and")
print("a DNS server. DHCP (RFC 2131) hands these out automatically from a pool, for a LEASE.")
print("""  client (0.0.0.0)                              server
     | --- DISCOVER (broadcast 255.255.255.255) --> |   D: "is there a DHCP server?"
     | <-- OFFER   (yiaddr = proposed address) ---- |   O: "you may have 192.168.1.100"
     | --- REQUEST (broadcast, names the server) -> |   R: "I accept that offer"
     | <-- ACK     (lease time, mask, router, DNS) - |   A: "it is yours for N seconds"
  UDP: client port 68, server port 67. Broadcast because the client has no IP yet.""")
print("Why is REQUEST broadcast? So OTHER DHCP servers that made offers learn they lost.")
print("Other messages: DECLINE (address in use), NAK (server refuses), RELEASE, INFORM.")

# ===== SECTION 2: THE MESSAGE FORMAT PACKED WITH struct =====
print("\n===== SECTION 2: THE MESSAGE FORMAT PACKED WITH struct =====")
fields = [("op", 1, "1 request, 2 reply"), ("htype", 1, "1 = Ethernet"), ("hlen", 1, "6 (MAC length)"),
          ("hops", 1, "relay hop count"), ("xid", 4, "transaction id"), ("secs", 2, "seconds elapsed"),
          ("flags", 2, "bit 15 = broadcast reply"), ("ciaddr", 4, "client IP (renewing)"),
          ("yiaddr", 4, "'your' IP (offered)"), ("siaddr", 4, "next server"),
          ("giaddr", 4, "relay agent IP"), ("chaddr", 16, "client hardware address"),
          ("sname", 64, "server name (unused)"), ("file", 128, "boot file name")]
print(f"{'field':<8}{'bytes':>6}  meaning")
for name, size, meaning in fields:
    print(f"{name:<8}{size:>6}  {meaning}")
total = sum(f[1] for f in fields)
print(f"fixed part = {total} bytes, + 4-byte magic cookie 63 82 53 63, then options (TLV)")
assert total == HEADER.size == 236
discover = pack_dhcp(1, 0xA1B2C3D4, "02:00:00:00:00:01", 1, flags=0x8000,
                     options=[(61, b"\x01" + mac_bytes("02:00:00:00:00:01"))])
print(f"\nDISCOVER packed: {len(discover)} bytes. First 28 bytes in hex:")
print("  ", discover[:28].hex(" "))
print("   op=01 htype=01 hlen=06 hops=00 | xid=a1b2c3d4 | secs=0000 flags=8000 | ciaddr=0.0.0.0 ...")
print("   options start at byte 240:", discover[240:].hex(" "))
print("   = 53 (msg type) len 1 value 01 (DISCOVER) | 61 (client id) len 7 ... | ff (end)")
parsed = parse_dhcp(discover)
assert parsed["xid"] == 0xA1B2C3D4 and parsed["mac"] == "02:00:00:00:00:01" and parsed["type"] == 1
print("check: OK (parse(pack(x)) gives back xid, MAC and message type)")

# ===== SECTION 3: AN IN-MEMORY DHCP SERVER =====
print("\n===== SECTION 3: AN IN-MEMORY DHCP SERVER =====")


class Scope:
    def __init__(self, network: str, first: int, last: int, router: str, lease: int = 3600) -> None:
        self.net = ipaddress.ip_network(network)
        hosts = list(self.net.hosts())
        self.pool = [str(h) for h in hosts[first - 1:last]]
        self.router, self.lease = router, lease
        self.leases: dict[str, tuple[str, int]] = {}     # mac -> (ip, expiry time)
        self.pending: dict[str, str] = {}                # mac -> offered ip (not yet ACKed)

    def reclaim(self, now: int) -> list[str]:
        gone = [m for m, (_, exp) in self.leases.items() if exp <= now]
        freed = [self.leases.pop(m)[0] for m in gone]
        return freed

    def free(self) -> list[str]:
        taken = {ip for ip, _ in self.leases.values()} | set(self.pending.values())
        return [ip for ip in self.pool if ip not in taken]


class DhcpServer:
    def __init__(self, server_ip: str, scopes: list[Scope]) -> None:
        self.ip, self.scopes = server_ip, scopes

    def scope_for(self, giaddr: str) -> Scope | None:
        if giaddr == "0.0.0.0":
            return self.scopes[0]
        for s in self.scopes:
            if ipaddress.ip_address(giaddr) in s.net:
                return s
        return None

    def reply(self, d: dict, scope: Scope, msg_type: int, yiaddr: str = "0.0.0.0") -> bytes:
        opts = [(54, ip4(self.ip))]
        if msg_type != 6:
            opts += [(51, struct.pack("!I", scope.lease)), (1, scope.net.netmask.packed),
                     opt_ip(3, scope.router), opt_ip(6, scope.router)]
        return pack_dhcp(2, d["xid"], d["mac"], msg_type, yiaddr=yiaddr, siaddr=self.ip,
                         giaddr=d["giaddr"], flags=d["flags"], options=opts)

    def handle(self, data: bytes, now: int) -> bytes | None:
        d = parse_dhcp(data)
        scope = self.scope_for(d["giaddr"])
        if scope is None:
            return None
        scope.reclaim(now)
        mac = d["mac"]
        if d["type"] == 1:                                           # DISCOVER
            current = scope.leases.get(mac)
            want = d["options"].get(50)
            free = scope.free()
            if current:
                ip = current[0]
            elif want and str(ipaddress.IPv4Address(want)) in free:
                ip = str(ipaddress.IPv4Address(want))
            elif free:
                ip = free[0]
            else:
                return None                                          # pool exhausted: silence
            scope.pending[mac] = ip
            return self.reply(d, scope, 2, ip)
        if d["type"] == 3:                                           # REQUEST
            sid = d["options"].get(54)
            if sid is not None and str(ipaddress.IPv4Address(sid)) != self.ip:
                scope.pending.pop(mac, None)                         # client chose another server
                return None
            asked = d["options"].get(50)
            ip = str(ipaddress.IPv4Address(asked)) if asked else d["ciaddr"]
            ok = scope.pending.get(mac) == ip or scope.leases.get(mac, (None,))[0] == ip
            if not ok:
                return self.reply(d, scope, 6)                       # NAK
            scope.pending.pop(mac, None)
            scope.leases[mac] = (ip, now + scope.lease)
            return self.reply(d, scope, 5, ip)
        if d["type"] == 7:                                           # RELEASE
            scope.leases.pop(mac, None)
        return None


def lease_table(server: DhcpServer, now: int) -> str:
    s = server.scopes[0]
    rows = [f"{m[-2:]}->{ip} (expires {exp})" for m, (ip, exp) in sorted(s.leases.items())]
    return f"t={now}: free={len(s.free())} leases=[{', '.join(rows)}]"


rng = random.Random(2024)
srv = DhcpServer("192.168.1.1", [Scope("192.168.1.0/24", 100, 102, "192.168.1.1")])
print("Pool 192.168.1.100-102 (3 addresses), lease 3600 s, simulated clock.\n")


def dora(mac: str, now: int, xid: int | None = None, verbose: bool = True) -> str | None:
    xid = xid if xid is not None else rng.getrandbits(32)
    disc = pack_dhcp(1, xid, mac, 1, flags=0x8000)
    if verbose:
        print("  D ", describe(parse_dhcp(disc)), f"[{mac[-2:]}] 0.0.0.0 -> 255.255.255.255")
    offer = srv.handle(disc, now)
    if offer is None:
        print("  (no OFFER: the pool is exhausted, the client keeps retrying)")
        return None
    o = parse_dhcp(offer)
    if verbose:
        print("  O ", describe(o))
    req = pack_dhcp(1, xid, mac, 3, flags=0x8000,
                    options=[opt_ip(50, o["yiaddr"]), (54, o["options"][54])])
    if verbose:
        print("  R ", describe(parse_dhcp(req)))
    ack = parse_dhcp(srv.handle(req, now))
    if verbose:
        print("  A ", describe(ack))
    return ack["yiaddr"]


macs = [f"02:00:00:00:00:{n:02x}" for n in range(1, 6)]
print("Client A:")
ip_a = dora(macs[0], 0)
print("Client B:")
ip_b = dora(macs[1], 0, verbose=False)
print("  B got", ip_b)
print("Client C:")
ip_c = dora(macs[2], 0, verbose=False)
print("  C got", ip_c)
print("Client D (pool is full):")
assert dora(macs[3], 0) is None
print(lease_table(srv, 0))
assert (ip_a, ip_b, ip_c) == ("192.168.1.100", "192.168.1.101", "192.168.1.102")

print("\nRenewal: at T1 = 1800 s client A unicasts REQUEST with ciaddr set (no new DORA):")
renew = pack_dhcp(1, 0x1111, macs[0], 3, ciaddr=ip_a)
print("  R ", describe(parse_dhcp(renew)))
print("  A ", describe(parse_dhcp(srv.handle(renew, 1800))))
print(lease_table(srv, 1800))
print("\nt=3601: B and C never renewed, so their leases ended; D tries again:")
ip_d = dora(macs[3], 3601, verbose=False)
print("  D got", ip_d, "(a reclaimed address) |", lease_table(srv, 3601))
assert ip_d == "192.168.1.101"
print("A releases politely (DHCPRELEASE, no reply):")
srv.handle(pack_dhcp(1, 0x2222, macs[0], 7, ciaddr=ip_a), 3700)
print(" ", lease_table(srv, 3700))

# ===== SECTION 4: TRAP - REPLIES ARE BROADCAST; MATCH THE xid =====
print("\n===== SECTION 4: TRAP - REPLIES ARE BROADCAST; MATCH THE xid =====")
srv = DhcpServer("192.168.1.1", [Scope("192.168.1.0/24", 100, 110, "192.168.1.1")])
xa, xb = 0x0000AAAA, 0x0000BBBB
disc_a = pack_dhcp(1, xa, macs[0], 1, flags=0x8000)
disc_b = pack_dhcp(1, xb, macs[1], 1, flags=0x8000)
replies = [srv.handle(disc_b, 0), srv.handle(disc_a, 0)]       # B's offer reaches the wire first
print("Both clients broadcast DISCOVER together. Offers (broadcast) arrive in this order:")
for r in replies:
    print("  ", describe(parse_dhcp(r)), "for", parse_dhcp(r)["mac"][-2:])
naive = parse_dhcp(replies[0])
print(f"naive client A takes the FIRST offer -> {naive['yiaddr']} (that was meant for B!)")
good = [parse_dhcp(r) for r in replies if parse_dhcp(r)["xid"] == xa and parse_dhcp(r)["mac"] == macs[0]][0]
print(f"correct client A filters on xid and chaddr -> {good['yiaddr']}")
assert naive["yiaddr"] != good["yiaddr"]
print("check: OK (xid + chaddr identify which reply belongs to which client)")

# ===== SECTION 5: LEASE TIMERS, REBINDING AND APIPA =====
print("\n===== SECTION 5: LEASE TIMERS, REBINDING AND APIPA =====")
print("T1 = 50% of lease: renew with the SAME server (unicast).")
print("T2 = 87.5% of lease: if no answer, REBIND: broadcast to ANY server.")
print("End of lease: stop using the address, restart DORA.")
for lease in (3600, 8 * 3600, 86400):
    t1, t2 = lease * 0.5, lease * 0.875
    print(f"  lease {lease:>6} s ({lease / 3600:>5.2f} h): T1={t1:>8.0f} s ({t1 / 3600:.2f} h)"
          f"  T2={t2:>8.0f} s ({t2 / 3600:.3f} h)")
assert 8 * 3600 * 0.5 == 14400 and 8 * 3600 * 0.875 == 25200
print("check: OK (8 h lease -> T1 = 4 h, T2 = 7 h)")
print("\nTimeline when the server dies right after the ACK (lease 3600 s):")
events = [(0, "ACK received, address in use"), (1800, "T1: unicast renew -> no reply"),
          (3150, "T2: broadcast rebind -> no reply"), (3600, "lease expired: drop the address")]
for t, what in events:
    print(f"  t={t:>4} s  {what}")
rng2 = random.Random(7)
apipa = f"169.254.{rng2.randint(1, 254)}.{rng2.randint(0, 255)}"
print(f"Fallback (APIPA / IPv4 link-local, RFC 3927): self-assign {apipa}/16 from 169.254.0.0/16,")
print("first probing with ARP to check nobody uses it. Works only on the local link: no")
print("router, no Internet. Seeing 169.254.x.x on a PC means 'DHCP failed'.")
assert ipaddress.ip_address(apipa) in ipaddress.ip_network("169.254.0.0/16")

# ===== SECTION 6: RELAY AGENT =====
print("\n===== SECTION 6: RELAY AGENT =====")
print("Broadcasts do not cross routers. A relay agent (usually the router) receives the")
print("broadcast on each subnet and forwards it by UNICAST to the DHCP server, writing its")
print("own interface address into giaddr. The server uses giaddr to pick the right scope.")
srv = DhcpServer("10.0.0.5", [Scope("10.0.0.0/24", 50, 60, "10.0.0.1"),
                              Scope("10.0.2.0/24", 100, 110, "10.0.2.1"),
                              Scope("10.0.3.0/24", 100, 110, "10.0.3.1")])
for giaddr, mac in (("0.0.0.0", macs[0]), ("10.0.2.1", macs[1]), ("10.0.3.1", macs[2])):
    req = pack_dhcp(1, 0x3333, mac, 1, giaddr=giaddr, flags=0x8000)
    o = parse_dhcp(srv.handle(req, 0))
    print(f"  DISCOVER with giaddr={giaddr:<9} -> OFFER {o['yiaddr']:<10} router={ipaddress.IPv4Address(o['options'][3])}")
print("One server, three subnets. Without a relay you would need a server on every subnet.")

# ===== SECTION 7: STARVATION, ROGUE SERVER AND DHCP SNOOPING =====
print("\n===== SECTION 7: STARVATION, ROGUE SERVER AND DHCP SNOOPING =====")
print("(An in-memory model of the attack AND the defence. No real network is touched.)")


class Switch:
    def __init__(self, port_security_max: int | None, snooping: bool) -> None:
        self.max_macs, self.snooping = port_security_max, snooping
        self.macs: dict[str, set[str]] = {}
        self.trusted = {"uplink"}

    def allow_frame(self, port: str, src_mac: str) -> bool:      # port security
        seen = self.macs.setdefault(port, set())
        if src_mac in seen:
            return True
        if self.max_macs is not None and len(seen) >= self.max_macs:
            return False
        seen.add(src_mac)
        return True

    def allow_server_reply(self, port: str) -> bool:             # DHCP snooping
        return (not self.snooping) or port in self.trusted


def starvation(defended: bool) -> tuple[int, str | None]:
    server = DhcpServer("192.168.1.1", [Scope("192.168.1.0/24", 100, 109, "192.168.1.1")])
    sw = Switch(3 if defended else None, snooping=defended)
    atk = random.Random(99)
    got = 0
    for i in range(40):                                          # attacker spoofs 40 MACs
        fake = ":".join(f"{atk.randrange(256):02x}" for _ in range(6))
        if not sw.allow_frame("port-attacker", fake):
            continue
        d = pack_dhcp(1, i, fake, 1, flags=0x8000)
        o = server.handle(d, 0)
        if o:
            ob = parse_dhcp(o)
            r = pack_dhcp(1, i, fake, 3, options=[opt_ip(50, ob["yiaddr"]), (54, ob["options"][54])])
            server.handle(r, 0)
            got += 1
    legit = None
    if sw.allow_frame("port-legit", macs[4]):
        o = server.handle(pack_dhcp(1, 777, macs[4], 1, flags=0x8000), 0)
        legit = parse_dhcp(o)["yiaddr"] if o else None
    return got, legit


for label, defended in (("no defence", False), ("port security (max 3 MACs/port)", True)):
    got, legit = starvation(defended)
    print(f"  starvation, {label:<32}: attacker holds {got:>2}/10 addresses; legit client gets {legit}")
assert starvation(False)[1] is None and starvation(True)[1] is not None
print("check: OK (undefended pool is drained; with port security the legit client is served)")


def rogue(snooping: bool) -> str:
    sw = Switch(None, snooping)
    legit = DhcpServer("192.168.1.1", [Scope("192.168.1.0/24", 100, 110, "192.168.1.1")])
    evil = DhcpServer("192.168.1.66", [Scope("192.168.1.0/24", 200, 210, "192.168.1.66")])
    disc = pack_dhcp(1, 0x4444, macs[0], 1, flags=0x8000)
    offers = []
    for port, server in (("rogue-port", evil), ("uplink", legit)):   # the rogue answers first
        o = server.handle(disc, 0)
        if o and sw.allow_server_reply(port):
            offers.append(parse_dhcp(o))
    first = offers[0]
    return f"offer accepted from {ipaddress.IPv4Address(first['options'][54])}, router {ipaddress.IPv4Address(first['options'][3])}"


print("Rogue DHCP server (it answers first and names ITSELF as the gateway -> traffic hijack):")
print("  without snooping:", rogue(False))
print("  with snooping   :", rogue(True), "(OFFER/ACK from an untrusted port is dropped)")
assert "192.168.1.66" in rogue(False) and "192.168.1.1," in rogue(True) + ","
print("check: OK")
print("Defences: DHCP snooping (trusted ports only for servers; builds a binding table that")
print("also feeds dynamic ARP inspection), port security, rate limits, 802.1X.")

# ===== SECTION 8: BOOTP AND NTP OVERVIEW =====
print("\n===== SECTION 8: BOOTP AND NTP OVERVIEW =====")
print("BOOTP (RFC 951): the ancestor of DHCP, same ports 67/68 and the SAME packet layout")
print("(that is why DHCP's first 236 bytes above are 'BOOTP'). Static MAC->IP table, no")
print("leases, no pool; used by diskless machines to learn their IP and boot file.")
print("DHCP = BOOTP + dynamic pools + leases + options.")
print("\nNTP (UDP port 123) keeps clocks in step. Stratum 0 = reference clock (GPS, atomic),")
print("stratum 1 = servers wired to it, stratum 2 = clients of stratum 1, and so on.")
t0, t1_, t2_, t3 = 100.000, 100.130, 100.134, 100.044          # one request/response
offset = ((t1_ - t0) + (t2_ - t3)) / 2
delay = (t3 - t0) - (t2_ - t1_)
print(f"Example timestamps (s): t0 client send={t0}, t1 server recv={t1_}, "
      f"t2 server send={t2_}, t3 client recv={t3}")
print(f"  offset = ((t1-t0)+(t2-t3))/2 = {offset:.3f} s  (client clock is {abs(offset) * 1000:.0f} ms behind)")
print(f"  delay  = (t3-t0)-(t2-t1)     = {delay * 1000:.0f} ms round trip on the network")
assert abs(offset - 0.110) < 1e-9 and abs(delay - 0.040) < 1e-9
print("check: OK (offset 0.110 s, delay 0.040 s)")
