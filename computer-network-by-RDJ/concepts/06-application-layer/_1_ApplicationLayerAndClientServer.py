# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches the application layer: what it does, client-server vs peer-to-peer vs
hybrid, how to design a tiny application protocol (syntax / semantics / timing),
stateless vs stateful servers, and a working line-based protocol server + client.
Syllabus idea: Application layer principles (chapter 6). Loopback only, port 0.
"""
import socket
import threading

HOST = "127.0.0.1"

# ===== SECTION 1: WHAT THE APPLICATION LAYER IS =====
print("===== SECTION 1: WHAT THE APPLICATION LAYER IS =====")
print("The application layer defines HOW two programs talk: message formats,")
print("message order, and what each message means. It relies on a transport")
print("service (TCP or UDP) and never worries about routing or bits on wire.")
APPS = [  # (protocol, well-known port, transport)
    ("HTTP", 80, "TCP"), ("HTTPS", 443, "TCP"), ("DNS", 53, "UDP (TCP for big)"),
    ("SMTP", 25, "TCP"), ("FTP control", 21, "TCP"), ("SSH", 22, "TCP"),
    ("DHCP server", 67, "UDP"), ("TFTP", 69, "UDP"),
]
print(f"{'protocol':<12}{'port':>6}  transport")
for name, port, transport in APPS:
    print(f"{name:<12}{port:>6}  {transport}")

# ===== SECTION 2: CLIENT-SERVER VS P2P VS HYBRID =====
print("\n===== SECTION 2: CLIENT-SERVER VS P2P VS HYBRID =====")
print("Client-server: one always-on server, many clients that only talk to it.")
print("P2P: any peer can be client and server; no central always-on host.")
print("Hybrid: central directory/index + direct peer transfers (classic Napster idea).")
print(f"{'peers n':>8}{'client-server links':>21}{'full-mesh P2P links':>21}")
for n in (2, 5, 10, 100):
    cs_links = n                  # each client has one connection to the server
    mesh = n * (n - 1) // 2       # every pair connected
    print(f"{n:>8}{cs_links:>21}{mesh:>21}")
assert 10 * 9 // 2 == 45
print("check: OK (10 peers -> 45 mesh links vs 10 client-server links)")

# ===== SECTION 3: DESIGNING A PROTOCOL (SYNTAX / SEMANTICS / TIMING) =====
print("\n===== SECTION 3: DESIGNING A PROTOCOL (SYNTAX / SEMANTICS / TIMING) =====")
print("Our toy protocol, 'MiniKV' (one request per line, ends with \\n):")
print("  syntax    : VERB [key [value...]]   e.g.  SET color blue")
print("  semantics : SET stores, GET reads, DEL removes, AUTH logs in, QUIT ends")
print("  timing    : strictly request -> reply; client waits for the reply")
print("  replies   : '+OK', '+OK <value>', or '-ERR <reason>'")


def parse_request(line: str) -> tuple[str, list[str]]:
    """Syntax check only: split into verb and args, raise ValueError if malformed."""
    parts = line.strip().split(" ", 2)
    verb = parts[0].upper()
    arity = {"SET": 2, "GET": 1, "DEL": 1, "AUTH": 1, "QUIT": 0}
    if verb not in arity:
        raise ValueError(f"unknown verb {verb!r}")
    args = parts[1:]
    if len(args) != arity[verb]:
        raise ValueError(f"{verb} needs {arity[verb]} argument(s), got {len(args)}")
    return verb, args


for text in ("SET color blue", "get color", "SET color", "FLY away", "SET msg hello world"):
    try:
        print(f"  {text!r:<24} -> {parse_request(text)}")
    except ValueError as err:
        print(f"  {text!r:<24} -> syntax error: {err}")

# ===== SECTION 4: STATELESS VS STATEFUL =====
print("\n===== SECTION 4: STATELESS VS STATEFUL =====")
print("Stateless: every request carries everything needed (HTTP without cookies).")
print("Stateful : server remembers the session (FTP login, SMTP dialogue, our AUTH).")


def stateless_handle(request: str, store: dict[str, str]) -> str:
    # Credentials travel in EVERY request: nothing remembered between requests.
    user, _, rest = request.partition("|")
    if user != "alice":
        return "-ERR bad credentials"
    verb, args = parse_request(rest)
    return store_apply(verb, args, store)


def store_apply(verb: str, args: list[str], store: dict[str, str]) -> str:
    if verb == "SET":
        store[args[0]] = args[1]
        return "+OK"
    if verb == "GET":
        return f"+OK {store[args[0]]}" if args[0] in store else "-ERR no such key"
    if verb == "DEL":
        return "+OK" if store.pop(args[0], None) is not None else "-ERR no such key"
    return "-ERR unsupported"


shared: dict[str, str] = {}
print("stateless:", stateless_handle("alice|SET a 1", shared), "|",
      stateless_handle("alice|GET a", shared), "|",
      stateless_handle("mallory|GET a", shared))
print("  + any server instance could answer; easy to scale; bigger requests.")
print("stateful : server keeps 'logged_in' per connection (shown live in Section 5).")
print("  + shorter requests; - state is lost on crash, harder to load-balance.")

# ===== SECTION 5: A WORKING SERVER + CLIENT ON LOOPBACK =====
print("\n===== SECTION 5: A WORKING SERVER + CLIENT ON LOOPBACK =====")


def split_lines(buffer: bytes) -> tuple[list[str], bytes]:
    """Frame a TCP byte stream into newline-terminated messages; keep the rest."""
    *complete, rest = buffer.split(b"\n")
    return [c.decode() for c in complete], rest


class MiniKVServer:
    def __init__(self) -> None:
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((HOST, 0))
        self.listener.listen(1)
        self.listener.settimeout(5)
        self.port: int = self.listener.getsockname()[1]
        self.store: dict[str, str] = {}
        self.thread = threading.Thread(target=self.serve_one_client)

    def serve_one_client(self) -> None:
        conn, _ = self.listener.accept()
        conn.settimeout(5)
        logged_in = False                      # per-connection STATE
        buffer = b""
        with conn:
            while True:
                data = conn.recv(4096)
                if not data:
                    return
                buffer += data
                lines, buffer = split_lines(buffer)
                for line in lines:
                    reply, logged_in, done = self.handle(line, logged_in)
                    conn.sendall((reply + "\n").encode())
                    if done:
                        return

    def handle(self, line: str, logged_in: bool) -> tuple[str, bool, bool]:
        try:
            verb, args = parse_request(line)
        except ValueError as err:
            return f"-ERR {err}", logged_in, False
        if verb == "QUIT":
            return "+OK bye", logged_in, True
        if verb == "AUTH":
            ok = args[0] == "letmein"
            return ("+OK welcome" if ok else "-ERR bad password"), ok, False
        if not logged_in:
            return "-ERR login first", logged_in, False
        return store_apply(verb, args, self.store), logged_in, False


server = MiniKVServer()
server.thread.start()
client = socket.create_connection((HOST, server.port), timeout=5)
reader = client.makefile("r", encoding="utf-8", newline="\n")


def ask(text: str) -> str:
    client.sendall((text + "\n").encode())
    reply = reader.readline().rstrip("\n")
    print(f"  C: {text:<18} S: {reply}")
    return reply


try:
    ask("GET color")                # not logged in yet -> stateful refusal
    ask("AUTH wrong")
    ask("AUTH letmein")
    ask("SET color blue")
    ask("GET color")
    ask("GET size")
    ask("DEL color")
    ask("FLY away")
    ask("QUIT")
finally:
    reader.close()
    client.close()
    server.thread.join(timeout=5)
    server.listener.close()
print("server thread finished:", not server.thread.is_alive())

# ===== SECTION 6: TRAP - TCP HAS NO MESSAGE BOUNDARIES =====
print("\n===== SECTION 6: TRAP - TCP HAS NO MESSAGE BOUNDARIES =====")
print("TCP is a byte stream. One send() is NOT guaranteed to be one recv().")
chunks = [b"GET a\nGET b\n", b"GET c\nGE", b"T d\n"]  # how bytes might arrive
print("naive: treat every recv() chunk as exactly one message:")
for chunk in chunks:
    print("  naive sees", repr(chunk.decode()))
print("  -> merged messages and half messages: broken.")
print("fixed: buffer bytes, cut on the newline delimiter:")
buf = b""
for chunk in chunks:
    msgs, buf = split_lines(buf + chunk)
    print(f"  after {chunk!r:<18} messages={msgs} leftover={buf!r}")
assert buf == b""
print("check: OK (4 messages recovered: a, b, c, d)")
