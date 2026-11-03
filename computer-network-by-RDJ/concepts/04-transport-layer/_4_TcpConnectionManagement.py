# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP connection management: three-way handshake with ISNs, four-way close,
TIME_WAIT, half-close, RST, simultaneous open, and the RFC state machine as a
transition table with client/server traces. Real loopback demos show the
outcomes through socket calls. SYN flood is explained in text only."""
import random
import socket
import struct
import threading
from dataclasses import dataclass, field

HOST = "127.0.0.1"

# ===== SECTION 1: THE STATE MACHINE AS A TRANSITION TABLE =====
print("===== SECTION 1: THE STATE MACHINE AS A TRANSITION TABLE =====")
# (state, event) -> (segment to send or "-", next state)
# events: app calls "open_passive", "open_active", "close"; segments "rcv SYN" etc; "timeout_2MSL"
TRANSITIONS: dict[tuple[str, str], tuple[str, str]] = {
    ("CLOSED", "open_passive"): ("-", "LISTEN"),
    ("CLOSED", "open_active"): ("SYN", "SYN_SENT"),
    ("LISTEN", "rcv SYN"): ("SYN+ACK", "SYN_RCVD"),
    ("LISTEN", "close"): ("-", "CLOSED"),
    ("SYN_SENT", "rcv SYN+ACK"): ("ACK", "ESTABLISHED"),
    ("SYN_SENT", "rcv SYN"): ("SYN+ACK", "SYN_RCVD"),  # simultaneous open
    ("SYN_SENT", "rcv RST"): ("-", "CLOSED"),
    ("SYN_SENT", "close"): ("-", "CLOSED"),
    ("SYN_RCVD", "rcv ACK"): ("-", "ESTABLISHED"),
    ("SYN_RCVD", "close"): ("FIN", "FIN_WAIT_1"),
    ("ESTABLISHED", "close"): ("FIN", "FIN_WAIT_1"),
    ("ESTABLISHED", "rcv FIN"): ("ACK", "CLOSE_WAIT"),
    ("ESTABLISHED", "rcv RST"): ("-", "CLOSED"),
    ("FIN_WAIT_1", "rcv ACK"): ("-", "FIN_WAIT_2"),
    ("FIN_WAIT_1", "rcv FIN"): ("ACK", "CLOSING"),  # simultaneous close
    ("FIN_WAIT_1", "rcv FIN+ACK"): ("ACK", "TIME_WAIT"),
    ("FIN_WAIT_2", "rcv FIN"): ("ACK", "TIME_WAIT"),
    ("CLOSING", "rcv ACK"): ("-", "TIME_WAIT"),
    ("TIME_WAIT", "timeout_2MSL"): ("-", "CLOSED"),
    ("CLOSE_WAIT", "close"): ("FIN", "LAST_ACK"),
    ("LAST_ACK", "rcv ACK"): ("-", "CLOSED"),
}
STATES = ["CLOSED", "LISTEN", "SYN_SENT", "SYN_RCVD", "ESTABLISHED", "FIN_WAIT_1",
          "FIN_WAIT_2", "CLOSING", "TIME_WAIT", "CLOSE_WAIT", "LAST_ACK"]
print(f"{len(STATES)} states, {len(TRANSITIONS)} transitions modelled (the subset an exam asks about).")
print(f"{'state':<12} {'event':<14} -> {'send':<8} {'next state'}")
for (state, event), (send, nxt) in TRANSITIONS.items():
    print(f"{state:<12} {event:<14} -> {send:<8} {nxt}")
assert all(s in STATES and n in STATES for (s, _), (_, n) in TRANSITIONS.items())
print("check: every state named in the table is a valid state: OK")


@dataclass
class Host:
    name: str
    isn: int
    state: str = "CLOSED"
    seq: int = 0
    log: list[str] = field(default_factory=list)

    def fire(self, event: str) -> str:
        """Apply an event; returns the segment this host must send ('-' if none)."""
        key = (self.state, event)
        if key not in TRANSITIONS:
            raise RuntimeError(f"{self.name}: event {event!r} is illegal in state {self.state}")
        send, nxt = TRANSITIONS[key]
        print(f"    {self.name:<6} {self.state:<12} --[{event}]--> {nxt:<12} sends {send}")
        self.state = nxt
        return send


# ===== SECTION 2: THREE-WAY HANDSHAKE WITH ISNs =====
print("\n===== SECTION 2: THREE-WAY HANDSHAKE WITH ISNs =====")
rng = random.Random(7)  # real OSes use unpredictable ISNs; seeded here for repeatable output
client = Host("client", isn=rng.randrange(2 ** 32))
server = Host("server", isn=rng.randrange(2 ** 32))
print(f"client ISN = {client.isn}, server ISN = {server.isn} (both 32-bit; unpredictable in real OSes)")
server.fire("open_passive")
seg1 = client.fire("open_active")
print(f"  1) client -> server  SYN      seq={client.isn}")
seg2 = server.fire("rcv SYN")
print(f"  2) server -> client  SYN+ACK  seq={server.isn} ack={client.isn + 1}")
seg3 = client.fire("rcv SYN+ACK")
print(f"  3) client -> server  ACK      seq={client.isn + 1} ack={server.isn + 1}")
server.fire("rcv ACK")
assert client.state == server.state == "ESTABLISHED"
print("both ESTABLISHED. SYN and SYN+ACK each consumed one sequence number (the +1).")
print("A first data byte from the client would carry seq =", client.isn + 1)

# trap: events that make no sense in a state
print("\ntrap: an event the table does not allow in that state:")
try:
    Host("stray", isn=0, state="LISTEN").fire("rcv ACK")
except RuntimeError as e:
    print("  ", e, "-> a real TCP answers a stray ACK in LISTEN with RST")


# ===== SECTION 3: FOUR-WAY CLOSE AND TIME_WAIT =====
print("\n===== SECTION 3: FOUR-WAY CLOSE AND TIME_WAIT =====")
print("client closes first (the ACTIVE closer):")
client.fire("close")
print("  1) client -> server  FIN")
server.fire("rcv FIN")
print("  2) server -> client  ACK     (server may still send data: this is a half-close)")
client.fire("rcv ACK")
server.fire("close")
print("  3) server -> client  FIN")
client.fire("rcv FIN")
print("  4) client -> server  ACK")
server.fire("rcv ACK")
print(f"server state: {server.state} (passive closer is done); client state: {client.state}")
client.fire("timeout_2MSL")
print("TIME_WAIT lasts 2 x MSL (Maximum Segment Lifetime). Why it exists:")
print("  a) if the last ACK is lost the peer resends FIN; someone must still be there to re-ACK;")
print("  b) it lets old duplicate segments from this connection die out before the same")
print("     (ip, port, ip, port) 5-tuple is reused. The duration is OS-specific (Linux uses 60 s).")
assert client.state == "CLOSED"

print("\nsimultaneous close (both send FIN at once):")
a, b = Host("A", 1, state="ESTABLISHED"), Host("B", 2, state="ESTABLISHED")
a.fire("close")
b.fire("close")
a.fire("rcv FIN")
b.fire("rcv FIN")
a.fire("rcv ACK")
b.fire("rcv ACK")
print("both pass through CLOSING and TIME_WAIT:", a.state, b.state)

print("\nsimultaneous open (both send SYN at once; rare):")
a, b = Host("A", 1), Host("B", 2)
a.fire("open_active")
b.fire("open_active")
a.fire("rcv SYN")
b.fire("rcv SYN")
a.fire("rcv ACK")
b.fire("rcv ACK")
print("two SYNs crossed, each side moved SYN_SENT -> SYN_RCVD -> ESTABLISHED:", a.state, b.state)

print("\nRST (reset): abrupt abort, no 4-way close, no TIME_WAIT:")
c = Host("peer", 3, state="ESTABLISHED")
c.fire("rcv RST")
print("  ESTABLISHED + RST ->", c.state, "(RST is sent for a segment to a closed port, or to abort)")


# ===== SECTION 4: REAL LOOPBACK HANDSHAKE OUTCOMES =====
print("\n===== SECTION 4: REAL LOOPBACK HANDSHAKE OUTCOMES =====")
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((HOST, 0))
listener.listen(2)
listener.settimeout(3)
port = listener.getsockname()[1]
c1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c1.settimeout(3)
c1.connect((HOST, port))  # returns after the kernel completed SYN, SYN+ACK, ACK
print("connect() returned BEFORE the server called accept(): the kernel finished the handshake")
print("  and parked the connection in the listen backlog (state ESTABLISHED already).")
conn, peer = listener.accept()
print("accept() then just hands the finished connection to the program: peer is loopback:",
      peer[0] == HOST)

# case 2: nobody listening -> RST -> ConnectionRefusedError
closed = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
closed.bind((HOST, 0))
closed_port = closed.getsockname()[1]
closed.close()
c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c2.settimeout(3)
try:
    c2.connect((HOST, closed_port))
except ConnectionRefusedError as e:
    print("connect to a closed port: server OS replied RST to our SYN ->",
          type(e).__name__, "(errno ECONNREFUSED)")
c2.close()

# half-close: shutdown(SHUT_WR) sends FIN but the socket can still read
c1.sendall(b"request: please answer after I finish")
c1.shutdown(socket.SHUT_WR)  # our FIN: "I'm done sending"
conn.settimeout(3)
got = b""
while True:
    chunk = conn.recv(100)
    if not chunk:  # b"" = the peer's FIN arrived (EOF)
        break
    got += chunk
print("server read until EOF (b'' means FIN received):", got)
conn.sendall(b"reply sent after client half-closed")
conn.close()  # server's FIN
reply = b""
while True:
    chunk = c1.recv(100)
    if not chunk:
        break
    reply += chunk
print("client, though half-closed, still received:", reply)
c1.close()

# RST on abort: SO_LINGER with zero timeout makes close() send RST instead of FIN
c3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c3.settimeout(3)
c3.connect((HOST, port))
conn3, _ = listener.accept()
conn3.settimeout(3)
c3.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
c3.close()  # abortive close: RST, no FIN handshake
try:
    data = conn3.recv(10)
    print("peer after abortive close recv returned:", data)
except ConnectionResetError as e:
    print("peer after abortive close got:", type(e).__name__, "(RST received)")
conn3.close()

# TIME_WAIT effect on re-binding the same server port
def server_closes_first(reuse: bool) -> int:
    """Run one connection where the SERVER closes first (so it holds TIME_WAIT); return its port."""
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if reuse:
        sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.bind((HOST, 0))
    sa.listen(1)
    sa.settimeout(3)
    pa = sa.getsockname()[1]
    cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cl.settimeout(3)
    cl.connect((HOST, pa))
    sc, _ = sa.accept()
    sc.close()  # server sends FIN first -> server side ends in TIME_WAIT on port pa
    cl.recv(10)
    cl.close()
    sa.close()
    return pa


p_a = server_closes_first(reuse=False)
trap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    trap.bind((HOST, p_a))
    print("TIME_WAIT trap: rebind without SO_REUSEADDR succeeded (OS-dependent)")
except OSError as e:
    print("TIME_WAIT trap: restarting a server on the same port WITHOUT SO_REUSEADDR failed:", e.strerror)
trap.close()
p_b = server_closes_first(reuse=True)
fix = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fix.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
fix.bind((HOST, p_b))
print("fix: set SO_REUSEADDR on the server socket (before bind); the restart on the same port works.")
fix.close()
listener.close()
print("all sockets closed")


# ===== SECTION 5: SYN FLOOD (CONCEPT ONLY) =====
print("\n===== SECTION 5: SYN FLOOD (CONCEPT ONLY, NOTHING IS SENT) =====")
print("""The server must remember every half-open connection (state SYN_RCVD) for a while.
An attacker who sends a flood of SYNs from forged addresses and never finishes the
handshake can fill that table, so real clients are refused. This is a denial of service.
Defences (described, not implemented here):
  - SYN cookies: encode the connection info into the server's ISN, keep NO state
    until a valid ACK comes back;
  - a larger backlog, shorter half-open timeouts, rate limiting, and upstream filtering.
Nothing in this file sends forged packets; the only traffic is loopback, to our own sockets.""")
