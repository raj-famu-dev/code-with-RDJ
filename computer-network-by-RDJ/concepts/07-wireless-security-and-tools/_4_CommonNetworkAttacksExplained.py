# Tags: #Python #ComputerNetworks #Wireless #NetworkSecurity #CommonNetworkAttacksExplained | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Common network attacks explained for DEFENDERS: a taxonomy, then three
in-memory simulations each shown with its defence (SYN backlog + SYN cookies,
ARP cache poisoning + static entry / DAI-style validation, a token-bucket rate
limiter), a DNS-cache-poisoning probability model, and session-ID entropy.
No packets are sent, no sockets are opened, no real hosts are involved."""
import hashlib
import hmac
import math
import random
import secrets

# ===== SECTION 1: TAXONOMY =====
print("===== SECTION 1: TAXONOMY =====")
print("Attack             Layer    Breaks (CIA)       Type     Main defence")
TAXONOMY = [
    ("Eavesdropping", "any", "Confidentiality", "passive", "encryption (TLS, WPA2/3, IPsec)"),
    ("Spoofing", "2-4", "Authenticity", "active", "ingress/egress filtering, authentication"),
    ("MITM", "2-7", "Conf. + Integrity", "active", "mutual auth, certificate validation, DAI"),
    ("DoS / DDoS", "3-7", "Availability", "active", "rate limiting, scrubbing, anycast, capacity"),
    ("SYN flood", "4", "Availability", "active", "SYN cookies, bigger backlog, timeouts"),
    ("ARP poisoning", "2", "Conf. + Integrity", "active", "static ARP, Dynamic ARP Inspection, port security"),
    ("DNS cache poison", "7", "Integrity", "active", "random ID + source port, DNSSEC"),
    ("Session hijack", "4-7", "Conf. + Integrity", "active", "unpredictable IDs, TLS, short lifetimes"),
    ("Port scan", "4", "(recon, precursor)", "active", "firewall default deny, detect + rate limit"),
]
for t in TAXONOMY:
    print(f"{t[0]:<18} {t[1]:<8} {t[2]:<18} {t[3]:<8} {t[4]}")
print("Passive = only observes (hard to detect); active = modifies/injects/disrupts. DoS = one source; DDoS = many.")

# ===== SECTION 2: SYN BACKLOG FILLING AND SYN COOKIES (SIMULATION) =====
print("\n===== SECTION 2: SYN BACKLOG FILLING AND SYN COOKIES (SIMULATION) =====")


class BacklogServer:
    """Listener keeping half-open (SYN-RECEIVED) entries in a fixed-size table."""

    def __init__(self, size: int, timeout: int) -> None:
        self.size, self.timeout = size, timeout
        self.half_open: dict[str, int] = {}   # client -> tick when SYN arrived

    def on_syn(self, tick: int, client: str) -> str:
        for c in [c for c, t in self.half_open.items() if tick - t >= self.timeout]:
            del self.half_open[c]
        if len(self.half_open) >= self.size:
            return "DROPPED (backlog full)"
        self.half_open[client] = tick
        return "SYN-ACK sent, entry stored"

    def on_ack(self, client: str) -> bool:
        return self.half_open.pop(client, None) is not None


srv = BacklogServer(size=8, timeout=60)
print("Backlog size 8, entry lifetime 60 ticks. Spoofed sources never answer the SYN-ACK, so entries just sit.")
for i in range(8):
    srv.on_syn(i, f"spoofed-{i}")
print(f"  after 8 spoofed SYNs: half-open table {len(srv.half_open)}/{srv.size}")
print("  legitimate client SYN at tick 9:", srv.on_syn(9, "alice"))
assert srv.on_syn(9, "alice").startswith("DROPPED")
print("  legitimate client SYN at tick 70 (old entries expired):", srv.on_syn(70, "alice"))
print("So the attacker must keep sending; the flood costs the server memory per half-open entry and costs the attacker almost nothing.")
print("check: OK")


class CookieServer:
    """Stores NOTHING on SYN. The ISN is a keyed hash of the connection tuple, so the final ACK proves the client saw the SYN-ACK."""

    def __init__(self, secret: bytes) -> None:
        self.secret = secret

    def cookie(self, client: str, cport: int, slice_no: int) -> int:
        msg = f"{client}|{cport}|{slice_no}".encode()
        return int.from_bytes(hmac.new(self.secret, msg, hashlib.sha256).digest()[:4], "big")

    def on_syn(self, client: str, cport: int, slice_no: int) -> int:
        return self.cookie(client, cport, slice_no)           # no table entry created

    def on_ack(self, client: str, cport: int, ack_no: int, slice_no: int) -> bool:
        return any(ack_no - 1 == self.cookie(client, cport, s) % 2 ** 32 for s in (slice_no, slice_no - 1))


ck = CookieServer(b"server-private-key")
isn = ck.on_syn("alice", 50000, slice_no=10)
print(f"SYN-cookie server: SYN from alice answered with ISN {isn} (derived, not stored). Table size stays 0.")
print("  alice's real ACK (ack = ISN+1):         ", ck.on_ack("alice", 50000, isn + 1, 10))
print("  forged ACK from a host that never saw the SYN-ACK:", ck.on_ack("mallory", 50001, 12345, 10))
assert ck.on_ack("alice", 50000, isn + 1, 10) and not ck.on_ack("mallory", 50001, 12345, 10)
print("check: OK")
print("Real SYN cookies pack a time counter and an encoded MSS into the 32-bit ISN (so some TCP options are lost);")
print("this model keeps only the core idea: state is rebuilt from the returning ACK, so flooding SYNs cannot fill memory.")

# ===== SECTION 3: ARP CACHE POISONING AND ITS DEFENCE (SIMULATION) =====
print("\n===== SECTION 3: ARP CACHE POISONING AND ITS DEFENCE (SIMULATION) =====")
GW_IP, GW_MAC = "192.168.1.1", "aa:aa:aa:aa:aa:01"
BAD_MAC = "02:00:00:00:00:66"


class ArpCache:
    def __init__(self, accept_unsolicited: bool, static: dict[str, str] | None = None) -> None:
        self.table = dict(static or {})
        self.static = set(static or {})
        self.accept_unsolicited = accept_unsolicited

    def on_reply(self, ip: str, mac: str, we_asked: bool) -> None:
        if ip in self.static:
            return                                   # static entries are never overwritten
        if we_asked or self.accept_unsolicited:
            self.table[ip] = mac


victim = ArpCache(accept_unsolicited=True)
victim.on_reply(GW_IP, GW_MAC, we_asked=True)
print("victim learns the gateway normally:    ", victim.table)
victim.on_reply(GW_IP, BAD_MAC, we_asked=False)
print("unsolicited reply claiming the gateway: ", victim.table, "<- traffic for the gateway now goes to the wrong MAC")
assert victim.table[GW_IP] == BAD_MAC
print("Cause: ARP has no authentication; any host on the LAN segment can send a reply and many stacks cache it.")

print("-- Defence 1: static entry on a critical host --")
firm = ArpCache(accept_unsolicited=True, static={GW_IP: GW_MAC})
firm.on_reply(GW_IP, BAD_MAC, we_asked=False)
print("  cache after the same forged reply:", firm.table)
assert firm.table[GW_IP] == GW_MAC

print("-- Defence 2: Dynamic ARP Inspection (switch checks ARP against a trusted IP->MAC binding table) --")
BINDINGS = {GW_IP: ("aa:aa:aa:aa:aa:01", "port1"), "192.168.1.20": ("bb:bb:bb:bb:bb:20", "port2")}


def dai_permits(sender_ip: str, sender_mac: str, ingress_port: str) -> bool:
    entry = BINDINGS.get(sender_ip)   # in real switches, built from DHCP snooping
    return entry == (sender_mac, ingress_port)


print("  genuine gateway reply on port1:  ", dai_permits(GW_IP, GW_MAC, "port1"))
print("  forged reply from port2 host:    ", dai_permits(GW_IP, BAD_MAC, "port2"), "-> switch drops it and can log it")
assert dai_permits(GW_IP, GW_MAC, "port1") and not dai_permits(GW_IP, BAD_MAC, "port2")
print("check: OK")
print("Also: ARP poisoning needs the attacker on the SAME LAN segment, so port security and segmentation reduce exposure.")

# ===== SECTION 4: RATE LIMITER (TOKEN BUCKET) =====
print("\n===== SECTION 4: RATE LIMITER (TOKEN BUCKET) =====")


class TokenBucket:
    def __init__(self, rate_per_tick: float, burst: int) -> None:
        self.rate, self.burst = rate_per_tick, burst
        self.tokens, self.last = float(burst), 0

    def allow(self, tick: int) -> bool:
        self.tokens = min(self.burst, self.tokens + (tick - self.last) * self.rate)
        self.last = tick
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


limiter = TokenBucket(rate_per_tick=2, burst=10)
sent_ok = sum(limiter.allow(0) for _ in range(100))   # one source fires 100 requests in the same tick
print(f"Single source sends 100 requests at once: {sent_ok} allowed (the burst), {100 - sent_ok} refused")
steady = sum(limiter.allow(t) for t in range(1, 11) for _ in range(5))   # 5 requests per tick for 10 ticks
print(f"Then 5 requests/tick for 10 ticks (50 total): {steady} allowed ~ refill rate 2/tick x 10 = 20")
assert sent_ok == 10 and steady == 20
print("check: OK")
buckets: dict[str, TokenBucket] = {}
legit_ok = attack_ok = 0
for src in [f"botnet-{i}" for i in range(200)]:
    b = buckets.setdefault(src, TokenBucket(2, 10))
    attack_ok += sum(b.allow(0) for _ in range(5))
legit = TokenBucket(2, 10)
legit_ok = sum(legit.allow(0) for _ in range(3))
print(f"TRAP: per-source limiting vs DDoS: 200 sources x 5 requests = 1000 offered, {attack_ok} pass (each source stays under its own limit)")
print(f"      legit user still gets {legit_ok}/3, but the SERVER still has to handle {attack_ok} attack requests. Defence: global limits, upstream scrubbing/CDN, capacity.")
print("DoS vs DDoS: one fast source is easy to limit or block; many slow sources need aggregate detection.")

# ===== SECTION 5: DNS CACHE POISONING PROBABILITY MODEL =====
print("\n===== SECTION 5: DNS CACHE POISONING PROBABILITY MODEL =====")
print("A resolver accepts a reply only if it matches the pending query: question, 16-bit transaction ID, (and source port).")


class Resolver:
    def __init__(self, rng: random.Random, randomize_port: bool) -> None:
        self.txid = rng.getrandbits(16)
        self.port = rng.randint(1024, 65535) if randomize_port else 53
        self.cache: dict[str, str] = {}

    def on_reply(self, name: str, txid: int, port: int, ip: str) -> bool:
        if txid == self.txid and port == self.port:
            self.cache[name] = ip
            return True
        return False


rr = Resolver(random.Random(1), randomize_port=True)
accepted = rr.on_reply("www.example", 0, 53, "198.51.100.66")
print("A forged reply with a wrong guess is rejected:", not accepted, "| cache:", rr.cache)
assert not accepted
space_id = 2 ** 16
space_both = 2 ** 16 * (65535 - 1024 + 1)
print(f"Guess space with txid only: {space_id:,} -> one forged reply succeeds with p = 1/{space_id:,}")
print(f"Guess space with txid + random source port: {space_both:,} -> p = 1/{space_both:,} per attempt")
print(f"Extra work factor from port randomisation = {space_both // space_id:,}x. DNSSEC goes further: signatures, not luck.")
print("check: OK")

# ===== SECTION 6: SESSION HIJACKING, MITM AND SESSION-ID STRENGTH =====
print("\n===== SECTION 6: SESSION HIJACKING, MITM AND SESSION-ID STRENGTH =====")
print("Session hijack = taking over an authenticated session by learning or guessing its token (or TCP sequence numbers).")
counter_ids = [f"sess{n:06d}" for n in range(1000, 1004)]
print("Predictable IDs (counter):", counter_ids, "-> guess the next one trivially")
rand_id = secrets.token_hex(16)
print(f"Unpredictable ID: {len(rand_id) * 4} random bits from secrets.token_hex(16) (value not printed)")
assert len(rand_id) == 32
print(f"Search space 2^128 = {2 ** 128:.3e}; brute force is infeasible, so theft (sniffing, XSS) is the realistic risk.")
print("Defences: random ID, TLS everywhere, Secure + HttpOnly cookie flags, rotate ID at login, expire idle sessions.")
print("MITM defence in one line: the client must verify WHO it talks to (certificate chain + hostname), not just encrypt.")
print("check: OK")
