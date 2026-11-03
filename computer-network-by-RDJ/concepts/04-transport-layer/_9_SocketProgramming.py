# Tags: #Python #ComputerNetworks #TransportLayer #SocketProgramming | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""BSD socket programming with TCP: socket/bind/listen/accept/connect/send/recv/close,
the partial-recv trap, length-prefixed framing, a threaded multi-client echo server
with timeouts and clean shutdown, and a selectors-based single-thread server.
Loopback only: 127.0.0.1, port 0, timeouts everywhere, all threads joined."""
import select
import selectors
import socket
import struct
import threading
import time

HOST = "127.0.0.1"

# ===== SECTION 1: THE BSD SOCKET CALLS IN ORDER =====
print("===== SECTION 1: THE BSD SOCKET CALLS IN ORDER =====")
print("""  SERVER                              CLIENT
  socket()   create endpoint          socket()   create endpoint
  bind()     attach local ip:port     (no bind: OS picks an ephemeral port)
  listen()   mark as passive, backlog
  accept()   wait; returns NEW socket connect()  3-way handshake (SYN, SYN+ACK, ACK)
  recv()/send()  <------- data ------->  send()/recv()
  close()    send FIN                 close()""")
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IPv4, SOCK_STREAM = TCP
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((HOST, 0))
listener.listen(5)
listener.settimeout(3)
port = listener.getsockname()[1]
print("1. socket() + bind(('127.0.0.1', 0)) + listen(5): bound to a loopback port chosen by the OS:",
      port > 0)
holder: dict[str, socket.socket] = {}
t = threading.Thread(target=lambda: holder.update(conn=listener.accept()[0]))
t.start()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(3)
client.connect((HOST, port))
t.join(timeout=5)
conn = holder["conn"]
conn.settimeout(3)
print("2. connect() returned and accept() returned a DIFFERENT socket for this connection:",
      conn is not listener and conn.getsockname() == listener.getsockname())
client.sendall(b"hello server")
print("3. server recv:", conn.recv(100))
conn.sendall(b"hello client")
print("4. client recv:", client.recv(100))
client.close()
print("5. after client close(), server recv returns b'' (EOF):", conn.recv(100))
conn.close()
listener.close()
print("6. close() on all three sockets (listener, accepted, client). Always close: use try/finally or with.")
print("Python note: socket objects support `with`, which closes them for you.")


# ===== SECTION 2: TRAP: recv() MAY RETURN PARTIAL DATA =====
print("\n===== SECTION 2: TRAP: recv() MAY RETURN PARTIAL DATA =====")


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Loop until exactly n bytes arrive. b'' from recv means the peer closed."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"peer closed after {len(buf)} of {n} bytes")
        buf += chunk
    return bytes(buf)


srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind((HOST, 0))
srv.listen(1)
srv.settimeout(3)
sport = srv.getsockname()[1]
results: dict[str, object] = {}


def slow_sender() -> None:
    c, _ = srv.accept()
    c.settimeout(3)
    c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # push each send out immediately
    c.sendall(b"0123")      # first 4 bytes of a 10-byte message...
    time.sleep(0.15)        # ...the rest comes later
    c.sendall(b"456789")
    time.sleep(0.15)
    c.sendall(b"X" * 5000)  # a 5000-byte block for the second experiment
    c.close()


th = threading.Thread(target=slow_sender)
th.start()
rc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rc.settimeout(3)
rc.connect((HOST, sport))
first = rc.recv(10)
print("message is 10 bytes; recv(10) returned:", first, f"({len(first)} bytes, not 10!)")
print("TRAP: recv(n) returns AT MOST n bytes, whatever is available. Never assume it is a whole message.")
rest = recv_exact(rc, 10 - len(first))
print("fix: recv_exact loop collected the rest:", rest, "-> full message:", first + rest)
assert first + rest == b"0123456789" and len(first) < 10
time.sleep(0.4)  # let the 5000 bytes arrive
calls, got = 0, 0
while got < 5000:
    chunk = rc.recv(1000)
    assert 0 < len(chunk) <= 1000
    calls += 1
    got += len(chunk)
print(f"reading 5000 bytes with recv(1000) needed at least 5 calls: {calls >= 5}, every chunk <= 1000: True")
print("end of stream: recv returns b'':", rc.recv(10))
rc.close()
th.join(timeout=5)
srv.close()
print("The same is true for send(): it may accept only part of the data. sendall() loops for you.")


# ===== SECTION 3: LENGTH-PREFIXED MESSAGES (FRAMING) =====
print("\n===== SECTION 3: LENGTH-PREFIXED MESSAGE PROTOCOL =====")
LEN = struct.Struct("!I")  # 4-byte unsigned big-endian length
MAX_MSG = 1_000_000


def send_msg(sock: socket.socket, payload: bytes) -> None:
    sock.sendall(LEN.pack(len(payload)) + payload)


def recv_msg(sock: socket.socket) -> bytes:
    (n,) = LEN.unpack(recv_exact(sock, LEN.size))
    if n > MAX_MSG:  # never trust a length from the network
        raise ValueError(f"message length {n} exceeds limit {MAX_MSG}")
    return recv_exact(sock, n)


print("wire format: [4-byte big-endian length][payload]. Example for b'hi':", (LEN.pack(2) + b"hi").hex(" "))
print("Why not a newline delimiter? Payloads may contain newlines:")
payload_nl = b"line1\nline2"
print("  delimiter split of", payload_nl, "->", payload_nl.split(b"\n"), "(two messages: WRONG)")
print("  length-prefixed keeps it as ONE message of", len(payload_nl), "bytes.")

a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
a.bind((HOST, 0))
a.listen(1)
a.settimeout(3)
a_port = a.getsockname()[1]
echoed: list[bytes] = []


def framed_echo() -> None:
    c, _ = a.accept()
    c.settimeout(3)
    try:
        while True:
            try:
                m = recv_msg(c)
            except ConnectionError:
                break
            send_msg(c, m)
    finally:
        c.close()


th = threading.Thread(target=framed_echo)
th.start()
fc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fc.settimeout(3)
fc.connect((HOST, a_port))
tests = [b"hi", b"", payload_nl, bytes(range(256)), b"B" * 100_000]
for m in tests:
    send_msg(fc, m)
for m in tests:
    echoed.append(recv_msg(fc))
print("round trip of", [len(m) for m in tests], "byte messages (incl. empty and binary):", echoed == tests)
assert echoed == tests
# dribble test: send one message one byte at a time; framing still works
dribble = b"slow but safe"
wire = LEN.pack(len(dribble)) + dribble
for i in range(len(wire)):
    fc.sendall(wire[i:i + 1])
print("a message dribbled one byte per send is still read as one message:", recv_msg(fc))
# two messages written back-to-back in ONE send are still read as two
fc.sendall(LEN.pack(3) + b"one" + LEN.pack(3) + b"two")
print("two messages in one send are read as two:", recv_msg(fc), recv_msg(fc))
fc.shutdown(socket.SHUT_WR)
fc.close()
th.join(timeout=5)
a.close()
# hostile length
bogus = LEN.pack(4_000_000_000) + b"x"


class _Fake:
    def __init__(self, data: bytes) -> None:
        self.data = bytearray(data)

    def recv(self, n: int) -> bytes:
        out, self.data = bytes(self.data[:n]), self.data[n:]
        return out


try:
    recv_msg(_Fake(bogus))  # type: ignore[arg-type]
except ValueError as e:
    print("hostile header claiming 4 GB is rejected:", e)
print("TRAP: skipping the MAX_MSG check lets one malicious 4-byte header make you allocate gigabytes.")


# ===== SECTION 4: THREADED MULTI-CLIENT ECHO SERVER =====
print("\n===== SECTION 4: THREADED MULTI-CLIENT ECHO SERVER =====")


class EchoServer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, 0))
        self.sock.listen(8)
        self.sock.settimeout(0.2)  # so the accept loop can notice the stop flag
        self.port = self.sock.getsockname()[1]
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.active = 0
        self.max_active = 0
        self.served = 0
        self.workers: list[threading.Thread] = []
        self.acceptor = threading.Thread(target=self._accept_loop, name="acceptor")

    def start(self) -> None:
        self.acceptor.start()

    def _accept_loop(self) -> None:
        while not self.stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            w = threading.Thread(target=self._handle, args=(conn,))
            self.workers.append(w)
            w.start()

    def _handle(self, conn: socket.socket) -> None:
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            with conn:
                while not self.stop.is_set():
                    ready, _, _ = select.select([conn], [], [], 0.2)  # idle wait, shutdown-aware
                    if not ready:
                        continue
                    conn.settimeout(2)  # a message that starts must finish within 2 s
                    try:
                        msg = recv_msg(conn)
                    except (ConnectionError, socket.timeout, ValueError):
                        break
                    if msg == b"QUIT":
                        send_msg(conn, b"BYE")
                        break
                    send_msg(conn, msg.upper())
                    with self.lock:
                        self.served += 1
        finally:
            with self.lock:
                self.active -= 1

    def shutdown(self) -> None:
        self.stop.set()
        self.acceptor.join(timeout=5)
        self.sock.close()
        for w in self.workers:
            w.join(timeout=5)


server = EchoServer()
server.start()
print("server started on an OS-chosen loopback port; acceptor thread + one worker thread per client")
all_connected = threading.Barrier(4, timeout=5)
replies: dict[int, list[str]] = {}


def run_client(i: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.settimeout(3)
        c.connect((HOST, server.port))
        all_connected.wait()  # make sure all 4 are connected at the same time
        out = []
        for j in range(3):
            send_msg(c, f"client {i} msg {j}".encode())
            out.append(recv_msg(c).decode())
        send_msg(c, b"QUIT")
        out.append(recv_msg(c).decode())
        replies[i] = out


clients_t = [threading.Thread(target=run_client, args=(i,)) for i in range(4)]
for ct in clients_t:
    ct.start()
for ct in clients_t:
    ct.join(timeout=10)
for i in sorted(replies):
    print(f"  client {i} got: {replies[i]}")
assert all(replies[i][:3] == [f"CLIENT {i} MSG {j}" for j in range(3)] and replies[i][3] == "BYE" for i in range(4))
time.sleep(0.3)  # let workers finish their cleanup
print("check: every client received only its own uppercase replies, then BYE: OK")
print("server saw", server.max_active, "clients connected at the same time (barrier forced 4):",
      server.max_active == 4)
print("messages echoed:", server.served)
server.shutdown()
alive = [w for w in server.workers if w.is_alive()] + ([server.acceptor] if server.acceptor.is_alive() else [])
print("clean shutdown: stop flag set, acceptor joined, listening socket closed, workers joined;")
print("threads still alive:", len(alive))
assert not alive and server.served == 12
print("Design notes: SO_REUSEADDR set, port 0, short accept timeout so the loop can stop,")
print("select() before each message so idle workers can stop, and a per-message timeout so a")
print("stalled client cannot hold a thread forever (a slowloris-style resource hog).")


# ===== SECTION 5: BLOCKING VS NON-BLOCKING VS SELECTORS =====
print("\n===== SECTION 5: BLOCKING VS NON-BLOCKING VS SELECTORS =====")
print("""  mode                call behaviour                        scales by
  blocking            recv/accept wait until ready          one thread per connection (simple;
                                                            threads cost memory)
  timeout             blocking, but raises socket.timeout   same, but can give up (use this by default)
  non-blocking        returns at once or raises             you must poll...
                      BlockingIOError
  selectors/epoll     ONE thread asks the OS 'which sockets  event loop; thousands of connections
                      are ready?' then handles only those    (asyncio is built on this idea)""")
tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tmp.bind((HOST, 0))
tmp.listen(1)
tmp.settimeout(3)
tc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tc.connect((HOST, tmp.getsockname()[1]))
ts, _ = tmp.accept()
tc.settimeout(0.2)
try:
    tc.recv(10)
except socket.timeout:
    print("timeout mode: recv with no data raised socket.timeout after 0.2 s (TimeoutError in 3.10+)")
tc.setblocking(False)
try:
    tc.recv(10)
except BlockingIOError:
    print("non-blocking mode: recv with no data raised BlockingIOError immediately (no waiting)")
for s_ in (tc, ts, tmp):
    s_.close()

sel_stop = threading.Event()
sel = selectors.DefaultSelector()
sel_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sel_listener.bind((HOST, 0))
sel_listener.listen(8)
sel_listener.setblocking(False)
sel_port = sel_listener.getsockname()[1]
sel.register(sel_listener, selectors.EVENT_READ, data="listener")
thread_ids: set[int] = set()
served_by_sel = [0]


def event_loop() -> None:
    while not sel_stop.is_set():
        for key, _ in sel.select(timeout=0.1):
            thread_ids.add(threading.get_ident())
            if key.data == "listener":
                c, _ = sel_listener.accept()
                c.setblocking(False)
                sel.register(c, selectors.EVENT_READ, data="conn")
            else:
                c = key.fileobj
                try:
                    data = c.recv(1024)
                except BlockingIOError:
                    continue
                if data:
                    c.send(data.upper())  # tiny reply; a real server would buffer unsent bytes
                    served_by_sel[0] += 1
                else:
                    sel.unregister(c)
                    c.close()
    for key in list(sel.get_map().values()):
        if key.data == "conn":
            sel.unregister(key.fileobj)
            key.fileobj.close()


loop_t = threading.Thread(target=event_loop)
loop_t.start()
conns = []
for _ in range(3):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.settimeout(3)
    c.connect((HOST, sel_port))
    conns.append(c)
for i, c in enumerate(conns):
    c.sendall(f"hello from {i}".encode())
print("selector server replies:", [c.recv(100).decode() for c in conns])
for c in conns:
    c.close()
time.sleep(0.3)
sel_stop.set()
loop_t.join(timeout=5)
sel.unregister(sel_listener)
sel_listener.close()
sel.close()
print("3 clients served by", len(thread_ids), "thread (the event loop); echoes:", served_by_sel[0])
assert len(thread_ids) == 1 and served_by_sel[0] == 3
print("check: one thread, three concurrent connections: OK")
print("Python's asyncio, Node.js, nginx and most modern servers are event loops like this.")
print("Rule of thumb: threads for simplicity and small scale; selectors/asyncio when connections")
print("number in the thousands and mostly idle.")
