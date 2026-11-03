# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Network types and uses: PAN/LAN/MAN/WAN, internet vs intranet vs extranet,
client-server vs peer-to-peer (with a loopback demo and the textbook
distribution-time formulas), and unicast/broadcast/multicast/anycast delivery.
Implements the 'Introduction: types, goals, applications' part of the syllabus."""
import socket
import threading


# ===== SECTION 1: PAN / LAN / MAN / WAN =====
print("===== SECTION 1: PAN / LAN / MAN / WAN =====")

# (name, typical scale, example) - scales are rules of thumb, not standards.
SCALES = [
    ("PAN", 10, "Bluetooth earbuds, phone <-> smartwatch (about 10 m)"),
    ("LAN", 1_000, "home Wi-Fi, one office floor or campus lab (up to ~1 km)"),
    ("MAN", 50_000, "cable-TV/fibre ring across a city (up to ~50 km)"),
    ("WAN", 10_000_000, "the Internet, a bank's links between countries"),
]


def classify(distance_m: float) -> str:
    """Return the smallest network class whose rule-of-thumb reach covers distance_m."""
    for name, reach, _ in SCALES:
        if distance_m <= reach:
            return name
    return "WAN"


print(f"{'type':<5}{'reach (m)':>12}  example")
for name, reach, example in SCALES:
    print(f"{name:<5}{reach:>12,}  {example}")
for label, d in [("laptop to mouse", 1), ("lab of 40 PCs", 120),
                 ("two campuses in one city", 12_000), ("Florida to Tokyo", 11_000_000)]:
    print(f"classify({d:>10,} m) -> {classify(d):<4} ({label})")
assert [classify(d) for d in (1, 120, 12_000, 11_000_000)] == ["PAN", "LAN", "MAN", "WAN"]
print("check: OK")


# ===== SECTION 2: INTERNET vs INTRANET vs EXTRANET =====
print("\n===== SECTION 2: INTERNET vs INTRANET vs EXTRANET =====")


def access_kind(owner_staff: bool, partner: bool, public: bool) -> str:
    """Who may use a service decides the label, not the technology."""
    if public:
        return "Internet (anyone)"
    if partner:
        return "Extranet (staff + approved outside partners)"
    if owner_staff:
        return "Intranet (organisation's own staff only)"
    return "No access"


services = [
    ("public website", False, False, True),
    ("HR payroll portal", True, False, False),
    ("supplier order portal", True, True, False),
    ("random visitor to payroll", False, False, False),
]
for name, staff, partner, public in services:
    print(f"{name:<28} -> {access_kind(staff, partner, public)}")
print("Trap: 'internet' (lowercase) = any interconnected networks; 'Internet' = the one global TCP/IP network.")


# ===== SECTION 3: CLIENT-SERVER vs PEER-TO-PEER =====
print("\n===== SECTION 3: CLIENT-SERVER vs PEER-TO-PEER =====")


def loopback_client_server() -> str:
    """A server thread answers one client, both on 127.0.0.1 (port 0 = OS picks)."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.settimeout(5)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]
    result: list[str] = []

    def serve() -> None:
        conn, _ = srv.accept()
        with conn:
            conn.settimeout(5)
            request = conn.recv(100).decode()
            conn.sendall(f"SERVER REPLY to '{request}'".encode())

    t = threading.Thread(target=serve)
    t.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
        cli.settimeout(5)
        cli.connect(("127.0.0.1", port))
        cli.sendall(b"GET page")
        result.append(cli.recv(100).decode())
    t.join()
    srv.close()
    return result[0]


print("loopback exchange:", loopback_client_server())

# Kurose-Ross file-distribution model: F bits to N peers.
# us = server upload rate, d_min = slowest peer download, u_i = peer upload.
F = 15 * 8 * 10**9      # 15 GB file expressed in bits (decimal GB)
u_s = 30e6              # server uploads at 30 Mbps
u_peer = 2e6            # each peer uploads at 2 Mbps
d_min = 2e6             # slowest peer downloads at 2 Mbps


def d_client_server(n: int) -> float:
    return max(n * F / u_s, F / d_min)


def d_p2p(n: int) -> float:
    return max(F / u_s, F / d_min, n * F / (u_s + n * u_peer))


print(f"{'peers N':>8}{'client-server (h)':>20}{'peer-to-peer (h)':>20}")
for n in (10, 100, 1000):
    print(f"{n:>8}{d_client_server(n) / 3600:>20.1f}{d_p2p(n) / 3600:>20.1f}")
print("Client-server time grows linearly with N; P2P stays near the F/d_min floor because peers add upload capacity.")
assert d_client_server(1000) > 50 * d_p2p(1000)
print("check: OK")


# ===== SECTION 4: UNICAST / BROADCAST / MULTICAST / ANYCAST =====
print("\n===== SECTION 4: UNICAST / BROADCAST / MULTICAST / ANYCAST =====")

# A tiny network: node -> distance (hops) from the sender "S".
hops = {"A": 1, "B": 2, "C": 3, "D": 3, "E": 4, "F": 5}
groups = {"video-group": {"B", "D", "F"}, "dns-anycast": {"C", "E", "F"}}


def unicast(dst: str) -> set[str]:
    return {dst}


def broadcast() -> set[str]:
    return set(hops)


def multicast(group: str) -> set[str]:
    return set(groups[group])


def anycast(group: str) -> set[str]:
    """Deliver to exactly ONE member: the nearest (fewest hops, ties by name)."""
    return {min(groups[group], key=lambda n: (hops[n], n))}


cases = [
    ("unicast to D (1-to-1)", unicast("D")),
    ("broadcast (1-to-all)", broadcast()),
    ("multicast video-group (1-to-many members)", multicast("video-group")),
    ("anycast dns-anycast (1-to-nearest-one)", anycast("dns-anycast")),
]
for label, receivers in cases:
    print(f"{label:<44} -> receivers={sorted(receivers)} ({len(receivers)} of {len(hops)})")
print("Trap: anycast looks like multicast (a group address) but delivers to ONE member only.")
assert anycast("dns-anycast") == {"C"} and len(multicast("video-group")) == 3
print("check: OK")


# ===== SECTION 5: WORKED EXAMPLE =====
print("\n===== SECTION 5: WORKED EXAMPLE =====")
# Q: A file of 6 GB is sent to 50 clients from a server uploading 100 Mbps.
# How long does client-server need, ignoring client download limits?
size_bits = 6 * 8 * 10**9
t = 50 * size_bits / 100e6
print(f"total bits the server must upload = 50 x {size_bits:,} = {50 * size_bits:,}")
print(f"time = {50 * size_bits:,} / 100,000,000 = {t:,.0f} s = {t / 60:.0f} min = {t / 3600:.2f} h")
assert t == 24000
print("check: OK")
