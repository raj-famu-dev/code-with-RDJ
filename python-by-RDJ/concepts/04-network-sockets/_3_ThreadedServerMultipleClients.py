# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches a thread-per-client TCP server: handle several clients at once,
a thread-safe counter (and the race it prevents), and a clean shutdown.
Loopback only (127.0.0.1), port 0, timeouts everywhere, all threads joined.
"""
import socket
import threading

HOST = "127.0.0.1"
NUM_CLIENTS = 5

print("=== SECTION 1: why one thread is not enough ===")
print("accept() blocks. A single-threaded server serves ONE client at a time;")
print("everyone else waits in the listen backlog. One thread per client fixes that.")

print("\n=== SECTION 2: a thread-safe counter ===")
class Counter:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:                  # only one thread inside at a time
            self._value += 1
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

class UnsafeCounter:
    """Deliberately has no lock; shown only to explain the risk."""
    def __init__(self) -> None:
        self.value = 0

    def increment(self) -> None:
        current = self.value              # read
        self.value = current + 1          # write (another thread may have written in between)

def hammer(counter, times: int) -> None:
    for _ in range(times):
        counter.increment()

safe = Counter()
threads = [threading.Thread(target=hammer, args=(safe, 20_000)) for _ in range(4)]
for th in threads:
    th.start()
for th in threads:
    th.join()
print("safe counter after 4 threads x 20000:", safe.value, "(always exactly 80000)")
print("UnsafeCounter has a read-modify-write gap; whether it loses updates depends on")
print("timing and Python version, so we do not run it and claim a number. The lock")
print("removes the question entirely.")

print("\n=== SECTION 3: the threaded server ===")
class ThreadedServer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, 0))
        self.sock.listen(8)
        self.sock.settimeout(0.2)         # short timeout so the loop can notice shutdown
        self.port: int = self.sock.getsockname()[1]
        self.stop_event = threading.Event()
        self.requests = Counter()
        self.workers: list[threading.Thread] = []
        self.acceptor = threading.Thread(target=self._accept_loop, name="acceptor")

    def start(self) -> None:
        self.acceptor.start()

    def _accept_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                conn, _addr = self.sock.accept()
            except socket.timeout:
                continue                  # loop again, re-check stop_event
            except OSError:
                break                     # socket closed during shutdown
            w = threading.Thread(target=self._handle, args=(conn,))
            self.workers.append(w)
            w.start()                     # one thread per client

    def _handle(self, conn: socket.socket) -> None:
        with conn:
            conn.settimeout(3)
            try:
                data = conn.recv(1024)
                n = self.requests.increment()
                conn.sendall(data + b" #" + str(n).encode())
            except (socket.timeout, OSError):
                pass

    def shutdown(self) -> None:
        self.stop_event.set()             # 1. ask the loop to stop
        self.acceptor.join(timeout=5)     # 2. wait for the acceptor
        for w in self.workers:
            w.join(timeout=5)             # 3. wait for every worker
        self.sock.close()                 # 4. release the port

server = ThreadedServer()
server.start()
print("server started on host", HOST, "(port chosen by OS)")

print("\n=== SECTION 4: many clients at once ===")
replies: dict[int, bytes] = {}
replies_lock = threading.Lock()

def client(i: int) -> None:
    with socket.create_connection((HOST, server.port), timeout=3) as s:
        s.sendall(f"client{i}".encode())
        r = s.recv(1024)
    with replies_lock:
        replies[i] = r

clients = [threading.Thread(target=client, args=(i,)) for i in range(NUM_CLIENTS)]
for c in clients:
    c.start()
for c in clients:
    c.join(timeout=5)

print("replies received:", len(replies), "of", NUM_CLIENTS)
for i in sorted(replies):
    prefix = replies[i].rsplit(b" #", 1)[0]
    print(f"  client{i} got echo prefix:", prefix)
numbers = sorted(int(r.rsplit(b'#', 1)[1]) for r in replies.values())
print("request numbers handed out (order of arrival varies, set does not):", numbers)
print("server-side counter:", server.requests.value)

print("\n=== SECTION 5: clean shutdown ===")
server.shutdown()
print("acceptor alive:", server.acceptor.is_alive())
print("any worker alive:", any(w.is_alive() for w in server.workers))
print("worker threads created:", len(server.workers))
print("socket closed (fileno -1):", server.sock.fileno() == -1)
try:
    socket.create_connection((HOST, server.port), timeout=1)
except ConnectionRefusedError:
    print("new connections now refused: server is really down")

print("\n=== SECTION 6: the output-order trap ===")
print("Replies arrive in nondeterministic order, so this script sorts before printing.")
print("Never print from many threads and expect a stable order.")
