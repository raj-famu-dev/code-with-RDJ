# Tags: #Python #Networking #Sockets #SocketErrorsTimeouts | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches the failure modes of sockets on loopback: ConnectionRefusedError,
timeouts, partial recv() and how a length prefix fixes it, SO_REUSEADDR, and
graceful shutdown. 127.0.0.1 only, port 0, every socket has a timeout.
"""
import socket
import struct
import threading
import time

HOST = "127.0.0.1"

print("=== SECTION 1: ConnectionRefusedError ===")
probe = socket.socket()
probe.bind((HOST, 0))
free_port = probe.getsockname()[1]
probe.close()                                       # nothing listens on free_port now
try:
    socket.create_connection((HOST, free_port), timeout=1)
except ConnectionRefusedError as e:
    print("caught:", type(e).__name__)
    print("is an OSError subclass:", isinstance(e, OSError))
print("Meaning: the machine answered, but no program is listening on that port.")

print("\n=== SECTION 2: socket.timeout on recv ===")
srv = socket.socket()
srv.settimeout(3)
srv.bind((HOST, 0))
srv.listen(1)
port = srv.getsockname()[1]
release = threading.Event()

def silent_server() -> None:
    conn, _ = srv.accept()
    with conn:
        release.wait(timeout=5)                     # accept, then say nothing

t = threading.Thread(target=silent_server)
t.start()
c = socket.create_connection((HOST, port), timeout=2)
c.settimeout(0.3)
start = time.monotonic()
try:
    c.recv(10)
except socket.timeout as e:
    waited = time.monotonic() - start
    print("caught:", type(e).__name__, "| socket.timeout is TimeoutError:", socket.timeout is TimeoutError)
    print(f"measurement: waited about {waited:.1f} s (limit was 0.3 s; value varies by machine)")
release.set()
c.close()
t.join(timeout=5)
srv.close()
print("TRAP: without settimeout, recv() on a silent peer blocks forever.")

print("\n=== SECTION 3: TRAP - recv() returns PARTIAL data ===")
srv = socket.socket()
srv.settimeout(3)
srv.bind((HOST, 0))
srv.listen(1)
port = srv.getsockname()[1]

def slow_sender() -> None:
    conn, _ = srv.accept()
    with conn:
        conn.sendall(b"HEL")                        # message arrives in two pieces
        time.sleep(0.2)
        conn.sendall(b"LO")

t = threading.Thread(target=slow_sender)
t.start()
c = socket.create_connection((HOST, port), timeout=3)
first = c.recv(5)                                   # asked for 5; the 0.2 s gap makes a short read near-certain
print("naive recv(5) returned:", first, "| length:", len(first), "(whole message is 5 bytes)")
rest = b""
while len(first + rest) < 5:                        # keep reading until we have it all
    rest += c.recv(5 - len(first + rest))
print("after looping:", first + rest)
c.close()
t.join(timeout=5)
srv.close()
print("recv(n) means AT MOST n bytes. Loop until you have what you need.")

print("\n=== SECTION 4: framing with a length prefix ===")
def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"peer closed after {len(buf)} of {n} bytes")
        buf.extend(chunk)
    return bytes(buf)

def send_msg(sock: socket.socket, payload: bytes) -> None:
    sock.sendall(struct.pack(">I", len(payload)) + payload)     # 4-byte big-endian length

def recv_msg(sock: socket.socket) -> bytes:
    (length,) = struct.unpack(">I", recv_exact(sock, 4))
    return recv_exact(sock, length)

srv = socket.socket()
srv.settimeout(3)
srv.bind((HOST, 0))
srv.listen(1)
port = srv.getsockname()[1]
messages = [b"first", b"", b"third message is longer", b"x" * 100_000]

def framed_sender() -> None:
    conn, _ = srv.accept()
    with conn:
        conn.settimeout(5)
        for m in messages:
            send_msg(conn, m)

t = threading.Thread(target=framed_sender)
t.start()
c = socket.create_connection((HOST, port), timeout=5)
got = [recv_msg(c) for _ in messages]
c.close()
t.join(timeout=5)
srv.close()
print("messages sent:", [len(m) for m in messages])
print("messages received:", [len(g) for g in got])
print("all identical:", got == messages)
print("The prefix restores message boundaries on top of TCP's byte stream.")

print("\n=== SECTION 5: peer closes early (EOF mid-message) ===")
srv = socket.socket()
srv.settimeout(3)
srv.bind((HOST, 0))
srv.listen(1)
port = srv.getsockname()[1]

def liar() -> None:
    conn, _ = srv.accept()
    with conn:
        conn.sendall(struct.pack(">I", 50) + b"only-ten-b")   # promises 50, sends 10, closes

t = threading.Thread(target=liar)
t.start()
c = socket.create_connection((HOST, port), timeout=3)
try:
    recv_msg(c)
except ConnectionError as e:
    print("caught ConnectionError:", e)
c.close()
t.join(timeout=5)
srv.close()
print("recv() == b'' means the peer closed; treat EOF before the full length as an error.")
print("Also: validate the length field. A hostile peer could claim 4 GB; cap it.")

print("\n=== SECTION 6: SO_REUSEADDR ===")
a = socket.socket()
a.bind((HOST, 0))
fixed_port = a.getsockname()[1]
a.listen(1)
b = socket.socket()
try:
    b.bind((HOST, fixed_port))                      # second bind to a port in use
except OSError as e:
    print("second bind on an in-use port ->", type(e).__name__)
b.close()
a.close()
r = socket.socket()
r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # must be set BEFORE bind
r.bind((HOST, fixed_port))
print("rebind after close works with SO_REUSEADDR set; flag value:",
      r.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) != 0)
r.close()
print("Honest note: no connection sat in TIME_WAIT in this demo, so this rebind would")
print("likely succeed even without the flag; the flag matters after real client traffic.")
print("SO_REUSEADDR lets a restarted server rebind while old connections sit in TIME_WAIT.")
print("It does NOT let two live listeners share a port (on Linux/macOS).")

print("\n=== SECTION 7: graceful shutdown ===")
srv = socket.socket()
srv.settimeout(3)
srv.bind((HOST, 0))
srv.listen(1)
port = srv.getsockname()[1]
log: list[str] = []

def polite_server() -> None:
    conn, _ = srv.accept()
    with conn:
        conn.settimeout(3)
        log.append("got: " + conn.recv(100).decode())
        conn.sendall(b"bye")
        conn.shutdown(socket.SHUT_WR)               # "I'm done sending", FIN goes out
        log.append("server saw client EOF: " + str(conn.recv(100) == b""))

t = threading.Thread(target=polite_server)
t.start()
c = socket.create_connection((HOST, port), timeout=3)
c.sendall(b"hello")
print("client reads:", c.recv(100))
print("then EOF from server:", c.recv(100) == b"")
c.shutdown(socket.SHUT_WR)                          # half-close our side too
c.close()
t.join(timeout=5)
srv.close()
for line in log:
    print("server log:", line)
print("shutdown(SHUT_WR) signals EOF but keeps the socket readable; close() releases it.")

print("\n=== SECTION 8: always close sockets: use `with` ===")
with socket.socket() as s:
    s.settimeout(1)
    print("inside with, fileno >= 0:", s.fileno() >= 0)
print("after with, fileno:", s.fileno())
print("All threads joined:", not t.is_alive())
