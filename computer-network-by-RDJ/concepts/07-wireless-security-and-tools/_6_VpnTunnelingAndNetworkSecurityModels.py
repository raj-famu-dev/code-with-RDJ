# Tags: #Python #ComputerNetworks #Wireless #NetworkSecurity #VpnTunnelingNetworkSecurityModels | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""VPNs, tunnelling and security models: encapsulation and its overhead, GRE vs
IPsec (AH vs ESP, transport vs tunnel mode) with a toy integrity/confidentiality
model, SSL VPN and WireGuard overview, perimeter vs zero trust, defence in
depth, the CIA triad and AAA. The 'cipher' here is a TOY built from hashlib to
show structure; it is NOT real cryptography and must never protect real data."""
import hashlib
import hmac
from dataclasses import dataclass, replace

# ===== SECTION 1: TUNNELLING = ENCAPSULATION AND ITS OVERHEAD =====
print("===== SECTION 1: TUNNELLING = ENCAPSULATION AND ITS OVERHEAD =====")


@dataclass(frozen=True)
class Pkt:
    src: str
    dst: str
    proto: str
    payload: object
    ttl: int = 64


inner = Pkt("10.1.0.5", "10.2.0.9", "TCP", "data from site A to site B")   # private addresses
outer = Pkt("203.0.113.1", "198.51.100.1", "GRE", inner)                    # public gateways
print("inner (original):", inner)
print("outer (tunnel):  ", Pkt(outer.src, outer.dst, outer.proto, "<inner packet>"))
print("The Internet routes on the OUTER header only; the private inner addresses are carried as opaque payload.")
decap = outer.payload
assert decap == inner
print("check: OK (decapsulation at the far gateway returns the original packet)")

MTU = 1500
print("Overhead per scheme (bytes added to each packet):")
GRE_OVERHEAD = 20 + 4          # new outer IPv4 header + basic GRE header
IPIP_OVERHEAD = 20
for name, ov in (("IP-in-IP", IPIP_OVERHEAD), ("GRE (basic header)", GRE_OVERHEAD)):
    print(f"  {name:<20} +{ov} B  -> largest inner packet that fits a {MTU}-byte link: {MTU - ov}")
print(f"TRAP: a full-size {MTU}-byte inner packet no longer fits after adding {GRE_OVERHEAD} B -> it must be fragmented,")
print("      or the sender must learn a smaller MTU (Path MTU Discovery), or the tunnel clamps TCP MSS. Broken PMTUD => stalls.")
assert MTU - GRE_OVERHEAD == 1476

# ===== SECTION 2: IPSEC - AH VS ESP, TRANSPORT VS TUNNEL =====
print("\n===== SECTION 2: IPSEC - AH VS ESP, TRANSPORT VS TUNNEL =====")
print("IPsec = IP protocol suite: AH = IP protocol 51, ESP = IP protocol 50, key exchange IKE on UDP 500 (UDP 4500 for NAT-T).")
print("Feature                  AH                         ESP")
print("Integrity + authenticity yes                        yes (optional but normally used)")
print("Confidentiality          NO                         yes (encryption)")
print("Covers outer IP header   yes (immutable fields)     no (tunnel mode: only the inner packet)")
print("Works through NAT        no (address change breaks) yes, with NAT-T (UDP encapsulation)")
print("Mode          What is protected                              Typical use")
print("Transport     payload only; original IP header stays        host-to-host")
print("Tunnel        whole original packet, NEW outer IP header     gateway-to-gateway site VPN, remote access")


def esp_tunnel_size(inner_len: int, block: int = 16, iv: int = 16, icv: int = 12) -> int:
    """ESP tunnel mode, example suite AES-CBC (16 B IV/block) + HMAC-SHA1-96 (12 B ICV)."""
    padded = inner_len + 2                       # +pad-length byte +next-header byte
    padded += (-padded) % block                  # pad up to a block multiple
    return 20 + 8 + iv + padded + icv            # new IP + (SPI+seq) + IV + encrypted part + ICV


size = esp_tunnel_size(100)
print(f"Example: 100-byte inner packet in ESP tunnel mode (AES-CBC + HMAC-SHA1-96): "
      f"20 + 8 + 16 + 112 + 12 = {size} bytes (overhead {size - 100}).")
assert size == 168
print("check: OK (the 112 = 100 + 2 trailer bytes + 10 padding, a multiple of 16)")

KEY = b"toy-shared-key"


def keystream(key: bytes, n: int) -> bytes:
    out, ctr = b"", 0
    while len(out) < n:
        out += hashlib.sha256(key + ctr.to_bytes(4, "big")).digest()
        ctr += 1
    return out[:n]


def toy_encrypt(data: bytes) -> bytes:           # TOY stream cipher, illustration only
    return bytes(a ^ b for a, b in zip(data, keystream(KEY, len(data))))


def icv(data: bytes) -> bytes:
    return hmac.new(KEY, data, hashlib.sha256).digest()[:12]


def ah_protect(p: Pkt) -> tuple[Pkt, bytes]:
    covered = f"{p.src}|{p.dst}|{p.proto}|{p.payload}".encode()     # TTL is mutable, so excluded
    return p, icv(covered)


def ah_verify(p: Pkt, tag: bytes) -> bool:
    return hmac.compare_digest(ah_protect(p)[1], tag)


pkt = Pkt("10.1.0.5", "10.2.0.9", "TCP", "transfer $100")
_, tag = ah_protect(pkt)
print("AH-like: genuine packet verifies:", ah_verify(pkt, tag))
print("AH-like: payload changed in transit verifies:", ah_verify(replace(pkt, payload="transfer $900"), tag))
print("AH-like: NAT rewrote the source address, verifies:", ah_verify(replace(pkt, src="203.0.113.77"), tag), "<- why AH and NAT clash")
print("AH-like: router decremented TTL, verifies:", ah_verify(replace(pkt, ttl=pkt.ttl - 1), tag), "(mutable field excluded)")
assert ah_verify(pkt, tag) and not ah_verify(replace(pkt, payload="transfer $900"), tag)
assert not ah_verify(replace(pkt, src="203.0.113.77"), tag) and ah_verify(replace(pkt, ttl=1), tag)
ct = toy_encrypt(b"transfer $100")
print("ESP-like (TOY cipher): ciphertext hex =", ct.hex(), "| decrypts back:", toy_encrypt(ct) == b"transfer $100")


def esp_seal(plain: bytes) -> bytes:
    body = toy_encrypt(plain)
    return body + icv(body)                      # encrypt-then-MAC: tag covers the ciphertext


def esp_open(sealed: bytes) -> bytes | None:
    body, tag = sealed[:-12], sealed[-12:]
    return toy_encrypt(body) if hmac.compare_digest(icv(body), tag) else None   # verify BEFORE decrypting


sealed = esp_seal(b"transfer $100")
tampered = bytes([sealed[0] ^ 1]) + sealed[1:]
print("ESP-like open(genuine):", esp_open(sealed), "| open(1 bit flipped):", esp_open(tampered))
assert esp_open(sealed) == b"transfer $100" and esp_open(tampered) is None
print("check: OK (tampering is rejected before any decryption happens)")

# ===== SECTION 3: VPN FAMILIES COMPARED =====
print("\n===== SECTION 3: VPN FAMILIES COMPARED =====")
print("Tech        Layer / transport              Gives                         Notes")
print("GRE         IP protocol 47                 tunnelling only (no crypto)   carries multicast/routing protocols; often paired with IPsec")
print("IPsec       L3: ESP(50)/AH(51), IKE UDP    auth + encryption             site-to-site standard; many options = complex to configure")
print("SSL/TLS VPN L4-7: TCP (often 443)          auth + encryption             passes through most firewalls; portal (clientless) or full tunnel")
print("WireGuard   UDP, own protocol (Noise)      auth + encryption             small codebase, fixed modern primitives (Curve25519,")
print("                                                                         ChaCha20-Poly1305, BLAKE2s), peers identified by public key")
print("Remote-access VPN = one user to a gateway; site-to-site = two networks joined permanently; both extend a private network.")

# ===== SECTION 4: PERIMETER VS ZERO TRUST =====
print("\n===== SECTION 4: PERIMETER VS ZERO TRUST =====")
print("Perimeter ('castle and moat'): inside = trusted. Zero trust: never trust by location; verify every request.")


@dataclass(frozen=True)
class Request:
    user: str
    device_managed: bool
    mfa: bool
    src_net: str          # "internal" or "external"
    resource: str


ACCESS = {"payroll": {"hr"}, "wiki": {"hr", "dev"}}
ROLES = {"alice": "hr", "bob": "dev"}


def perimeter(r: Request) -> bool:
    return r.src_net == "internal"                          # one check, at the door


def zero_trust(r: Request) -> bool:
    role = ROLES.get(r.user)
    return bool(role and role in ACCESS.get(r.resource, set()) and r.device_managed and r.mfa)


cases = [
    ("alice, managed laptop, MFA, internal -> payroll", Request("alice", True, True, "internal", "payroll")),
    ("bob (dev) on a compromised internal PC -> payroll", Request("bob", False, False, "internal", "payroll")),
    ("alice, managed laptop, MFA, from a cafe -> payroll", Request("alice", True, True, "external", "payroll")),
]
print(f"{'case':<54} {'perimeter':<10} zero-trust")
for label, r in cases:
    print(f"{label:<54} {'allow' if perimeter(r) else 'deny':<10} {'allow' if zero_trust(r) else 'deny'}")
assert perimeter(cases[1][1]) and not zero_trust(cases[1][1]) and zero_trust(cases[2][1]) and not perimeter(cases[2][1])
print("check: OK (perimeter lets lateral movement from a compromised inside host through; zero trust does not)")
print("Zero trust building blocks: strong identity, device posture, least privilege, micro-segmentation, continuous logging.")

# ===== SECTION 5: DEFENCE IN DEPTH =====
print("\n===== SECTION 5: DEFENCE IN DEPTH =====")
print("Layers: physical, network (firewall, segmentation), host (patching, EDR), application (input validation), data (encryption), people (training).")
print("Illustration with ASSUMED numbers, not measurements: if each independent layer stops 90% of attempts,")
for n in (1, 2, 3, 4):
    print(f"  {n} layer(s): {0.1 ** n * 100:g}% get through")
print("TRAP: layers are rarely independent (one stolen admin password can defeat several), so real risk falls less than this.")
print("Principles: least privilege, fail secure (default deny), avoid single point of failure, assume breach.")

# ===== SECTION 6: CIA TRIAD AND AAA =====
print("\n===== SECTION 6: CIA TRIAD AND AAA =====")
print("Confidentiality: only authorised parties read data   -> encryption, access control")
print("Integrity:       data is not altered undetected      -> hashes, MACs, signatures")
print("Availability:    service is usable when needed        -> redundancy, DoS defence, backups")
print("AAA: Authentication (who are you?), Authorization (what may you do?), Accounting (what did you do?)")
print("Protocols: RADIUS (UDP 1812/1813), TACACS+ (TCP 49), Diameter (successor to RADIUS).")

USERS: dict[str, tuple[bytes, bytes, str]] = {}
AUDIT: list[str] = []


def register(name: str, password: str, role: str) -> None:
    salt = hashlib.sha256(name.encode()).digest()[:8]       # demo salt; real systems use random per-user salts
    USERS[name] = (salt, hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000), role)


def aaa(name: str, password: str, action: str) -> str:
    rec = USERS.get(name)
    if not rec or not hmac.compare_digest(rec[1], hashlib.pbkdf2_hmac("sha256", password.encode(), rec[0], 100_000)):
        AUDIT.append(f"{name}: login FAILED")
        return "authentication failed"
    allowed = {"admin": {"read", "write"}, "user": {"read"}}[rec[2]]
    AUDIT.append(f"{name}: {action} {'ok' if action in allowed else 'DENIED'}")
    return "authorised" if action in allowed else "authenticated but NOT authorised"


register("alice", "correct horse", "admin")
register("bob", "hunter2", "user")
for who, pw, act in [("alice", "correct horse", "write"), ("bob", "hunter2", "write"), ("bob", "wrong", "read")]:
    print(f"  {who} tries '{act}': {aaa(who, pw, act)}")
print("  accounting log:", AUDIT)
assert AUDIT == ["alice: write ok", "bob: write DENIED", "bob: login FAILED"]
register("carol", "hunter2", "user")      # same password as bob
unsalted = [hashlib.sha256(b"hunter2").hexdigest() for _ in ("bob", "carol")]
print("TRAP: unsalted SHA-256 of bob's and carol's identical password are equal:", unsalted[0] == unsalted[1],
      "-> one cracked hash exposes every user with that password.")
print("      salted PBKDF2 hashes of the same password differ:", USERS["bob"][1] != USERS["carol"][1],
      "(use a per-user random salt and a slow KDF: PBKDF2/bcrypt/scrypt/Argon2)")
assert unsalted[0] == unsalted[1] and USERS["bob"][1] != USERS["carol"][1]
print("check: OK")
