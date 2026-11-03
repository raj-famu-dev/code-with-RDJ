# Tags: #Python #ComputerNetworks #ApplicationLayer #HttpBasics | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches HTTP/1.1 basics: request line, headers, body, methods (safe vs
idempotent), status code classes, URL anatomy (urllib.parse), a loopback server
(http.server), a client (http.client) and a curl-style raw request over a socket.
Syllabus idea: World Wide Web and HTTP. Loopback only (127.0.0.1, port 0).
"""
import http.client
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, quote_plus, urlencode, urlsplit

HOST = "127.0.0.1"
FIXED_DATE = "Mon, 01 Jan 2024 00:00:00 GMT"   # fixed so output is deterministic

# ===== SECTION 1: ANATOMY OF A REQUEST AND A RESPONSE =====
print("===== SECTION 1: ANATOMY OF A REQUEST AND A RESPONSE =====")
print("""request                                   response
-------                                   --------
GET /items/1 HTTP/1.1      <- request line  HTTP/1.1 200 OK            <- status line
Host: www.example.com      <- headers       Content-Type: application/json
Accept: application/json                    Content-Length: 25
                           <- blank line                               <- blank line
(optional body)                             {"id": 1, "name": "book"}  <- body
Lines end with CRLF (\\r\\n). The blank line ends the headers.""")

# ===== SECTION 2: URL ANATOMY =====
print("\n===== SECTION 2: URL ANATOMY =====")
url = "https://alice@www.example.com:8443/shop/books.html?q=net+work&page=2#reviews"
p = urlsplit(url)
print("url      :", url)
for field in ("scheme", "username", "hostname", "port", "path", "query", "fragment"):
    print(f"  {field:<9}: {getattr(p, field)!r}")
print("  query parsed:", parse_qs(p.query))
print("  default ports: http=80, https=443 ->", urlsplit("http://example.com/").port, "(None means default)")
print("  The #fragment is NEVER sent to the server; the browser keeps it.")
value = "rock & roll/100% fun"
print("  quote()      :", quote(value, safe=""))
print("  quote_plus() :", quote_plus(value))
print("  urlencode()  :", urlencode({"q": value, "page": 2}))
assert parse_qs(urlencode({"q": value}))["q"] == [value]
print("check: OK (urlencode then parse_qs round-trips the awkward value)")

# ===== SECTION 3: METHODS AND STATUS CODES =====
print("\n===== SECTION 3: METHODS AND STATUS CODES =====")
METHODS = [  # method, safe, idempotent, typical use
    ("GET", "yes", "yes", "read a resource"),
    ("HEAD", "yes", "yes", "like GET but headers only"),
    ("OPTIONS", "yes", "yes", "ask what is allowed"),
    ("POST", "no", "no", "create / submit / run an action"),
    ("PUT", "no", "yes", "replace a resource at a known URL"),
    ("DELETE", "no", "yes", "remove a resource"),
]
print(f"{'method':<9}{'safe':<6}{'idempotent':<12}use")
for m, s, i, use in METHODS:
    print(f"{m:<9}{s:<6}{i:<12}{use}")
print("safe = no change to server state; idempotent = repeating gives the same final state")
CLASSES = {1: "informational", 2: "success", 3: "redirection", 4: "client error", 5: "server error"}
COMMON = {200: "OK", 201: "Created", 204: "No Content", 301: "Moved Permanently",
          302: "Found", 304: "Not Modified", 400: "Bad Request", 401: "Unauthorized",
          403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed", 411: "Length Required",
          500: "Internal Server Error", 501: "Not Implemented", 503: "Service Unavailable"}
for cls, label in CLASSES.items():
    codes = ", ".join(f"{c} {t}" for c, t in COMMON.items() if c // 100 == cls) or "100 Continue, 101 Switching Protocols"
    print(f"{cls}xx {label:<14}: {codes}")


# ===== SECTION 4: A LOOPBACK SERVER AND AN http.client CLIENT =====
print("\n===== SECTION 4: A LOOPBACK SERVER AND AN http.client CLIENT =====")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args) -> None:  # silence request logging
        pass

    def version_string(self) -> str:
        return "RDJ-Demo/1.0"

    def date_time_string(self, timestamp=None) -> str:
        return FIXED_DATE

    # -- helpers -------------------------------------------------------
    def reply(self, code: int, payload=None, extra: dict | None = None) -> None:
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(code)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        if code != 204:
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD" and body:
            self.wfile.write(body)

    def item_id(self) -> int | None:
        parts = self.path.strip("/").split("/")
        return int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else None

    def read_json(self):
        length = self.headers.get("Content-Length")
        if length is None:
            self.reply(411, {"error": "Content-Length required"})
            return None
        return json.loads(self.rfile.read(int(length)) or b"{}")

    # -- methods -------------------------------------------------------
    def do_GET(self) -> None:
        items = self.server.items
        if self.path == "/items":
            self.reply(200, items)
        elif self.item_id() in items:
            self.reply(200, {"id": self.item_id(), "name": items[self.item_id()]})
        else:
            self.reply(404, {"error": "not found"})

    do_HEAD = do_GET

    def do_POST(self) -> None:
        data = self.read_json()          # ALWAYS consume the body, even if we then refuse
        if data is None:
            return
        if self.path != "/items":
            self.reply(405, {"error": "POST only on /items"}, {"Allow": "GET, PUT, DELETE, HEAD"})
            return
        new_id = self.server.next_id
        self.server.next_id += 1
        self.server.items[new_id] = data.get("name", "?")
        self.reply(201, {"id": new_id}, {"Location": f"/items/{new_id}"})

    def do_PUT(self) -> None:
        item = self.item_id()
        data = self.read_json()
        if item is None or data is None:
            return
        created = item not in self.server.items
        self.server.items[item] = data.get("name", "?")
        self.reply(201 if created else 200, {"id": item, "name": self.server.items[item]})

    def do_DELETE(self) -> None:
        item = self.item_id()
        if item in self.server.items:
            del self.server.items[item]
            self.reply(204)
        else:
            self.reply(404, {"error": "not found"})

    def do_OPTIONS(self) -> None:
        self.reply(204, None, {"Allow": "GET, HEAD, POST, PUT, DELETE, OPTIONS"})


def start_server() -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer((HOST, 0), Handler)
    srv.items = {1: "book", 2: "pen"}
    srv.next_id = 3
    srv.thread = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05})
    srv.thread.start()
    return srv


def call(port: int, method: str, path: str, body: dict | None = None, quiet: bool = False):
    conn = http.client.HTTPConnection(HOST, port, timeout=5)
    try:
        payload = json.dumps(body) if body is not None else None
        headers = {"Content-Type": "application/json"} if payload else {}
        conn.request(method, path, body=payload, headers=headers)
        resp = conn.getresponse()
        data = resp.read().decode()
        if not quiet:
            shown = {h: resp.getheader(h) for h in ("Content-Length", "Location", "Allow") if resp.getheader(h)}
            short = data if len(data) <= 50 else data[:47] + "..."
            print(f"  {method:<7}{path:<10} -> {resp.status} {resp.reason:<18} {shown} body={short!r}")
        return resp.status, data
    finally:
        conn.close()


srv = start_server()
port = srv.server_address[1]
try:
    call(port, "GET", "/items")
    call(port, "GET", "/items/1")
    call(port, "GET", "/items/99")
    call(port, "HEAD", "/items/1")
    call(port, "POST", "/items", {"name": "mug"})
    call(port, "PUT", "/items/1", {"name": "novel"})
    call(port, "DELETE", "/items/2")
    call(port, "OPTIONS", "/items")
    call(port, "POST", "/items/1", {"name": "x"})
    call(port, "PATCH", "/items/1", {"name": "x"})
    print("HEAD returned the same headers as GET (Content-Length 25) but NO body.")

    # ===== SECTION 5: SAFE AND IDEMPOTENT IN PRACTICE =====
    print("\n===== SECTION 5: SAFE AND IDEMPOTENT IN PRACTICE =====")
    srv.items.clear()
    srv.next_id = 1
    for _ in range(2):
        call(port, "POST", "/items", {"name": "pen"}, quiet=True)
    print("POST twice  -> items:", srv.items, "(two NEW resources: not idempotent)")
    srv.items.clear()
    for _ in range(2):
        call(port, "PUT", "/items/7", {"name": "pen"}, quiet=True)
    print("PUT twice   -> items:", srv.items, "(same final state: idempotent)")
    s1, _ = call(port, "DELETE", "/items/7", quiet=True)
    s2, _ = call(port, "DELETE", "/items/7", quiet=True)
    print(f"DELETE twice-> statuses {s1} then {s2}, items: {srv.items}")
    print("Idempotent means the SERVER STATE is the same, not that the status code is.")
    assert srv.items == {}

    # ===== SECTION 6: A CURL-STYLE RAW REQUEST OVER A SOCKET =====
    print("\n===== SECTION 6: A CURL-STYLE RAW REQUEST OVER A SOCKET =====")
    srv.items.update({1: "book"})

    def raw(request: bytes) -> str:
        with socket.create_connection((HOST, port), timeout=5) as s:
            s.sendall(request)
            chunks = []
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        return b"".join(chunks).decode()

    req = b"GET /items/1 HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    print("sent:")
    for line in req.decode().split("\r\n")[:-1]:
        print("  >", repr(line))
    print("received:")
    for line in raw(req).split("\r\n"):
        print("  <", repr(line))
    print("'Connection: close' makes the server close after replying, so recv() sees EOF.")

    # ===== SECTION 7: TRAP - A POST WITH NO Content-Length =====
    print("\n===== SECTION 7: TRAP - A POST WITH NO Content-Length =====")
    body = b'{"name": "lamp"}'
    bad = b"POST /items HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n" + body
    good = (b"POST /items HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n"
            b"Content-Type: application/json\r\nContent-Length: " + str(len(body)).encode()
            + b"\r\n\r\n" + body)
    print("without Content-Length:", raw(bad).split("\r\n")[0])
    print("with    Content-Length:", raw(good).split("\r\n")[0])
    print("The server cannot guess where the body ends on a persistent connection,")
    print("so the length (or chunked encoding) is mandatory for a request body.")
    assert raw(bad).startswith("HTTP/1.1 411") and raw(good).startswith("HTTP/1.1 201")
    print("check: OK")
finally:
    srv.shutdown()
    srv.server_close()
    srv.thread.join(timeout=5)
print("server stopped:", not srv.thread.is_alive())
