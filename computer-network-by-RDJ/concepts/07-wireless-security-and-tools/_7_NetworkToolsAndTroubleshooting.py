# Tags: #Python #ComputerNetworks #Wireless #NetworkSecurity #NetworkToolsTroubleshooting | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Network tools and troubleshooting: what ping, traceroute, nslookup/dig,
netstat/ss, ip/ifconfig, arp, curl, nmap and Wireshark each do and which layer
they diagnose; a bottom-up troubleshooting method as a decision-table function;
a TTL/traceroute and ping-statistics model; and our own tiny port-check and
latency-measure built on the socket module against 127.0.0.1 servers that this
script starts itself. Nothing here contacts any outside host."""
import socket
import statistics
import threading
import time

# ===== SECTION 1: THE TOOLBOX AND THE LAYERS =====
print("===== SECTION 1: THE TOOLBOX AND THE LAYERS =====")
TOOLS = [
    ("ip / ifconfig", "1-3", "Is the interface up? What IP, mask, MAC, routes do I have?", "ip addr, ip route (ifconfig is the older tool)"),
    ("arp / ip neigh", "2-3", "Which MAC does this IP on my LAN map to?", "ip neigh"),
    ("ping", "3", "Is the host reachable by ICMP echo, and what is the RTT / loss?", "ping -c 4 <host>"),
    ("traceroute", "3", "Which routers lie on the path, where does it stop?", "traceroute <host> (tracert on Windows)"),
    ("nslookup / dig", "7 (DNS)", "Does the name resolve, to what, via which server?", "dig <name>; nslookup <name>"),
    ("netstat / ss", "4", "Which ports are listening / which connections exist on THIS machine?", "ss -tulpn"),
    ("curl", "7", "Does the application answer? Status code, headers, TLS, timing.", "curl -v <url>"),
    ("nmap", "3-4 (+7)", "Which ports/services are open on a host YOU are authorised to test?", "only on systems you own or have written permission for"),
    ("Wireshark / tcpdump", "2-7", "What exactly is on the wire (packet capture + decode)?", "needs capture privileges, own networks only"),
]
print(f"{'Tool':<20} {'Layer':<9} Question it answers")
for t in TOOLS:
    print(f"{t[0]:<20} {t[1]:<9} {t[2]}")
    print(f"{'':<30} e.g. {t[3]}")
print("This file does not run any of these. It implements the IDEAS (port check, latency, TTL walk) on loopback only.")

# ===== SECTION 2: OWN PORT-CHECK ON LOOPBACK (A MEASUREMENT) =====
print("\n===== SECTION 2: OWN PORT-CHECK ON LOOPBACK (A MEASUREMENT) =====")
LOOPBACK = "127.0.0.1"


def require_loopback(host: str) -> None:
    if host != LOOPBACK:
        raise ValueError(f"refusing to contact {host!r}: this module measures 127.0.0.1 only")


class EchoServer:
    """Tiny TCP echo server (one thread per connection) on 127.0.0.1, port 0 (OS-chosen)."""

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((LOOPBACK, 0))
        self.sock.listen(128)
        self.sock.settimeout(0.2)
        self.port = self.sock.getsockname()[1]
        self.stop = threading.Event()
        self.workers: list[threading.Thread] = []
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self.stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            t = threading.Thread(target=self._serve, args=(conn,), daemon=True)
            t.start()
            self.workers.append(t)

    @staticmethod
    def _serve(conn: socket.socket) -> None:
        with conn:
            conn.settimeout(1.0)
            try:
                while data := conn.recv(1024):
                    conn.sendall(data)
            except (socket.timeout, ConnectionError):
                pass

    def __enter__(self) -> "EchoServer":
        self.thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop.set()
        self.thread.join(timeout=3)
        for w in self.workers:
            w.join(timeout=3)
        self.sock.close()


def port_check(host: str, port: int, timeout: float = 0.5) -> str:
    """'open' if a TCP connect succeeds, 'closed' if refused, 'filtered/timeout' otherwise."""
    require_loopback(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        code = s.connect_ex((host, port))
    if code == 0:
        return "open"
    return "closed" if code in (111, 61, 10061) else "filtered/timeout"   # ECONNREFUSED on Linux/mac/Windows


with EchoServer() as server:
    probe = socket.socket()
    probe.bind((LOOPBACK, 0))
    dead_port = probe.getsockname()[1]
    probe.close()                       # nothing listens here any more
    r_open, r_closed = port_check(LOOPBACK, server.port), port_check(LOOPBACK, dead_port)
    print(f"port_check(127.0.0.1, <our echo server>) -> {r_open}")
    print(f"port_check(127.0.0.1, <a port nobody listens on>) -> {r_closed}")
    assert (r_open, r_closed) == ("open", "closed")
    print("check: OK (a listening port accepts; a closed one answers RST = 'connection refused')")
    try:
        port_check("192.0.2.1", 80)   # documentation address: refused BEFORE any socket is created
    except ValueError as e:
        print("guard works:", e)
    print("A SYN that gets NO answer at all (firewall DROP) shows up as a timeout, which is why 'filtered' differs from 'closed'.")

    # ===== SECTION 3: OWN LATENCY MEASURE (A MEASUREMENT) =====
    print("\n===== SECTION 3: OWN LATENCY MEASURE (A MEASUREMENT) =====")
    N = 20
    connect_ms: list[float] = []
    for _ in range(N):
        t0 = time.perf_counter()
        with socket.create_connection((LOOPBACK, server.port), timeout=1):
            connect_ms.append((time.perf_counter() - t0) * 1000)
    echo_ms: list[float] = []
    with socket.create_connection((LOOPBACK, server.port), timeout=1) as c:
        for i in range(N):
            msg = f"ping {i}".encode()
            t0 = time.perf_counter()
            c.sendall(msg)
            got = c.recv(1024)
            echo_ms.append((time.perf_counter() - t0) * 1000)
            assert got == msg
    assert len(connect_ms) == len(echo_ms) == N and min(connect_ms + echo_ms) > 0
    print(f"{N} TCP connects and {N} echo round trips completed, every echo returned the exact bytes. check: OK")
    print(f"[measurement, varies per run] TCP connect: min={min(connect_ms):.3f} ms median={statistics.median(connect_ms):.3f} ms max={max(connect_ms):.3f} ms")
    print(f"[measurement, varies per run] echo RTT:    min={min(echo_ms):.3f} ms median={statistics.median(echo_ms):.3f} ms max={max(echo_ms):.3f} ms")
    print("These numbers describe this machine's loopback only. They say nothing about real network latency, which is")
    print("dominated by propagation + queuing (module 01). Use min/median, not mean, because one slow outlier skews it.")
print("server stopped, thread joined, sockets closed")

# ===== SECTION 4: NAME RESOLUTION ON 'localhost' ONLY =====
print("\n===== SECTION 4: NAME RESOLUTION ON 'localhost' ONLY =====")


def resolve_local(name: str) -> list[str]:
    if name != "localhost":
        raise ValueError("this demo resolves 'localhost' only (no outside lookups)")
    infos = socket.getaddrinfo(name, None, proto=socket.IPPROTO_TCP)
    return sorted({i[4][0] for i in infos})


addrs = resolve_local("localhost")
print("getaddrinfo('localhost') addresses (set depends on the machine's hosts file):", addrs)
assert "127.0.0.1" in addrs or "::1" in addrs
print("check: OK (localhost maps to the loopback address 127.0.0.1 and/or ::1)")
print("'localhost' is answered from the local hosts file / resolver config, no DNS query leaves the machine.")
print("What dig/nslookup add: ask a chosen DNS server, see record types (A, AAAA, MX, NS, CNAME), TTLs and the answer path.")
print("Diagnostic trick: if ping <IP> works but ping <name> fails, the fault is DNS, not connectivity.")

# ===== SECTION 5: TTL WALK (TRACEROUTE LOGIC) AND PING STATISTICS =====
print("\n===== SECTION 5: TTL WALK (TRACEROUTE LOGIC) AND PING STATISTICS =====")
PATH = ["192.168.1.1 (home router)", "10.20.0.1 (ISP edge)", "172.31.5.2 (backbone)", "203.0.113.9 (destination)"]


def probe(ttl: int, blocked_at: int | None = None) -> str:
    """Each router decrements TTL; the router where it hits 0 drops the packet and sends ICMP Time Exceeded."""
    if blocked_at is not None and ttl >= blocked_at:
        return "* (no reply)"                  # a filter at hop `blocked_at` swallows the probe or the reply
    router = PATH[min(ttl, len(PATH)) - 1]
    return f"{router} reached, ICMP Echo Reply" if ttl >= len(PATH) else f"{router} ICMP Time Exceeded"


print("Made-up path; traceroute sends probes with TTL 1, 2, 3, ... and records who answers:")
for ttl in range(1, 5):
    print(f"  TTL={ttl}: {probe(ttl)}")
print("Same path with the third router silently dropping everything (a filter):")
for ttl in range(1, 5):
    print(f"  TTL={ttl}: {probe(ttl, blocked_at=3)}")
assert probe(1).startswith("192.168.1.1") and probe(4).endswith("Echo Reply")
print("check: OK (a row of '*' shows where the path is filtered, not necessarily where it is broken)")

sample_rtts = [21.4, 20.9, None, 22.1, 20.7, 35.2]       # fixed sample, ms; None = lost
got = [r for r in sample_rtts if r is not None]
loss = 100 * (len(sample_rtts) - len(got)) / len(sample_rtts)
print(f"Sample ping run (fixed example data): sent={len(sample_rtts)} received={len(got)} loss={loss:.1f}% "
      f"min/avg/max = {min(got):.1f}/{sum(got) / len(got):.1f}/{max(got):.1f} ms")
assert abs(loss - 100 / 6) < 1e-9
print("check: OK (1 lost of 6 = 16.7% loss)")

# ===== SECTION 6: BOTTOM-UP TROUBLESHOOTING DECISION TABLE =====
print("\n===== SECTION 6: BOTTOM-UP TROUBLESHOOTING DECISION TABLE =====")
print("Method: define the symptom, work UP from the physical layer, change one thing at a time, document.")
ORDER = ["link_up", "has_ip", "gateway_ping", "ip_ping", "dns_resolves", "port_open", "app_ok"]
DIAGNOSIS = {
    "link_up": ("L1/L2: no link", "check cable/Wi-Fi association, switch port, NIC (ip link)"),
    "has_ip": ("L3: no valid IP configuration", "check DHCP, mask, gateway (ip addr, dhclient logs)"),
    "gateway_ping": ("L2/L3: cannot reach the default gateway", "check ARP (ip neigh), VLAN, gateway device"),
    "ip_ping": ("L3: routing/ISP or ICMP blocked beyond the gateway", "traceroute to see where it stops"),
    "dns_resolves": ("L7 DNS: IP works but the name does not resolve", "check resolver config; dig @server name"),
    "port_open": ("L4: host reachable but the port is closed or filtered", "check the service is listening (ss -tulpn) and firewall rules"),
    "app_ok": ("L7: port open but the application fails", "read the app logs; curl -v for status and headers"),
}


def diagnose(obs: dict[str, bool]) -> tuple[str, str]:
    for key in ORDER:
        if not obs.get(key, False):
            return DIAGNOSIS[key]
    return ("no fault found at these layers", "problem may be intermittent: monitor and capture")


ok = {k: True for k in ORDER}
SCENARIOS = {
    "cable unplugged": {**ok, **{k: False for k in ORDER}},
    "DHCP failed (169.254.x.x)": {**ok, "has_ip": False, "gateway_ping": False, "ip_ping": False, "dns_resolves": False, "port_open": False, "app_ok": False},
    "can ping an IP but not a name": {**ok, "dns_resolves": False, "port_open": False, "app_ok": False},
    "web server process crashed": {**ok, "port_open": False, "app_ok": False},
    "HTTP 500 from the app": {**ok, "app_ok": False},
    "everything passes": ok,
}
for name, obs in SCENARIOS.items():
    layer, action = diagnose(obs)
    print(f"  {name:<34} -> {layer}\n  {'':<34}    next: {action}")
assert diagnose(SCENARIOS["web server process crashed"])[0].startswith("L4")
print("check: OK")
print("TRAP 1: 'ping works but the website does not' = ICMP is allowed but TCP 80/443 is not (or the app is down).")
print("TRAP 2: 'ping fails but the website works' = ICMP is blocked by a firewall; ping is not proof of reachability either way.")
print("Loopback analogue of 'host is up but the port is not': our server port was", r_open, "while a dead port was", r_closed, "- same host, different answers.")
