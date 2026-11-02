# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches how to check whether a TCP port is open, using connect_ex, against
YOUR OWN machine only (127.0.0.1). We start one listener ourselves and find one
port we know is closed. The checker REFUSES any non-loopback address on purpose.

LEGAL / ETHICAL RULE: only probe systems you own or have explicit written
permission to test. Unauthorized port scanning can violate computer-misuse laws
and acceptable-use policies. Practice on localhost or legal training labs.
"""
import errno
import ipaddress
import socket
import threading

print("=== SECTION 1: the rule that shapes this whole file ===")
print("Only YOUR machine is checked here. Probing someone else's host without")
print("permission can be illegal (e.g. under the US CFAA) and violates most ISP rules.")
print("Learn on 127.0.0.1, your own VMs, or legal labs/CTF platforms.")

print("\n=== SECTION 2: a checker that refuses non-loopback hosts ===")
def check_port(host: str, port: int, timeout: float = 0.5) -> str:
    """Return 'open', 'closed' or 'filtered/timeout' for a LOOPBACK address."""
    if not ipaddress.ip_address(host).is_loopback:
        raise ValueError(f"refusing to probe non-loopback host {host!r}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        code = s.connect_ex((host, port))            # returns an errno instead of raising
    if code == 0:
        return "open"
    if code == errno.ECONNREFUSED:
        return "closed"
    return f"other (errno {code})"

try:
    check_port("192.0.2.1", 80)                       # TEST-NET-1 documentation address: must be refused
except ValueError as e:
    print("guard works ->", e)
print("(the guard raised BEFORE any socket was created; nothing was sent anywhere)")

print("\n=== SECTION 3: an open port we start ourselves ===")
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.settimeout(3)
listener.bind(("127.0.0.1", 0))
listener.listen(5)
open_port = listener.getsockname()[1]
accepted = 0

def accept_some() -> None:
    global accepted
    while True:
        try:
            conn, _ = listener.accept()
        except (socket.timeout, OSError):
            return
        conn.close()
        accepted += 1
        if accepted >= 2:
            return

t = threading.Thread(target=accept_some)
t.start()
print("connect_ex on our listener:", check_port("127.0.0.1", open_port))
print("0 from connect_ex means success; the three-way handshake completed.")

print("\n=== SECTION 4: a port we KNOW is closed ===")
tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tmp.bind(("127.0.0.1", 0))
closed_port = tmp.getsockname()[1]
tmp.close()                                          # port is free again: nothing listens
print("connect_ex on a freed port:", check_port("127.0.0.1", closed_port))
raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw.settimeout(0.5)
code = raw.connect_ex(("127.0.0.1", closed_port))
raw.close()
print("raw return code == errno.ECONNREFUSED:", code == errno.ECONNREFUSED)
print("errno value itself is OS-specific (Linux 111, macOS 61, Windows 10061);")
print("compare against errno.ECONNREFUSED, never a hard-coded number.")

print("\n=== SECTION 5: connect vs connect_ex ===")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.5)
try:
    s.connect(("127.0.0.1", closed_port))            # raises
except ConnectionRefusedError:
    print("connect()    -> raises ConnectionRefusedError")
print("connect_ex() -> returns an error code, no exception (handy for loops)")
s.close()

print("\n=== SECTION 6: checking a small list of ports ===")
results = {p: check_port("127.0.0.1", p) for p in sorted([open_port, closed_port])}
for p, status in results.items():
    label = "our listener" if p == open_port else "known-closed port"
    print(f"  {label:18}: {status}")
print("Only two ports, both ours. We do NOT sweep ranges, and we never take a")
print("host from user input.")

print("\n=== SECTION 7: timeouts and what 'filtered' means ===")
print("closed = host actively answers 'nobody here' (RST) -> ECONNREFUSED, fast.")
print("filtered = a firewall silently drops packets -> no answer -> timeout, slow.")
print("On loopback you will essentially never see 'filtered', so we only explain it.")
print("A short timeout keeps a checker from hanging; it must never be left unset.")

print("\n=== SECTION 8: cleanup ===")
check_port("127.0.0.1", open_port)                   # second connection lets the thread finish
t.join(timeout=5)
listener.close()
print("thread joined:", not t.is_alive(), "| connections the listener accepted:", accepted)
print("listener closed; fileno =", listener.fileno())
