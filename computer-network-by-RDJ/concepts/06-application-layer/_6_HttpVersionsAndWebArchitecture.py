# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches HTTP/1.0 vs 1.1 vs 2 vs 3 (persistent connections, pipelining,
multiplexing, header compression, QUIC), a head-of-line blocking simulation,
proxies / reverse proxies / load balancers / CDNs, a web-cache hit-ratio
simulation and REST with a small JSON API on loopback.
Syllabus idea: Web architecture, HTTP evolution, caching, REST.
Loopback only (127.0.0.1, port 0). Simulations use abstract time units.
"""
import http.client
import json
import math
import random
import threading
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"

# ===== SECTION 1: HTTP/1.0 VS HTTP/1.1 - COUNTING ROUND TRIPS =====
print("===== SECTION 1: HTTP/1.0 VS HTTP/1.1 - COUNTING ROUND TRIPS =====")
print("Page = 1 base HTML + 10 images (11 objects). RTT = 100 ms. Object transmission")
print("time is ignored so only round trips are counted (textbook model).")
RTT, IMAGES = 100, 10
objects = 1 + IMAGES
parallel = 5
models = {
    "HTTP/1.0 non-persistent, serial": objects * 2,                   # 1 RTT TCP + 1 RTT req/resp each
    f"HTTP/1.0 non-persistent, {parallel} parallel": 2 + 2 * math.ceil(IMAGES / parallel),
    "HTTP/1.1 persistent, no pipelining": 1 + objects,                # 1 handshake + 1 RTT per object
    "HTTP/1.1 persistent + pipelining": 1 + 1 + 1,                    # handshake, base, all images together
}
print(f"{'model':<40}{'RTTs':>6}{'time':>9}")
for name, rtts in models.items():
    print(f"{name:<40}{rtts:>6}{rtts * RTT:>7} ms")
assert models["HTTP/1.0 non-persistent, serial"] == 22 and models["HTTP/1.1 persistent + pipelining"] == 3
print("check: OK (22 / 6 / 12 / 3 round trips)")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self) -> None:
        super().setup()
        with self.server.lock:
            self.server.connections += 1          # one per accepted TCP connection

    def log_message(self, format: str, *args) -> None:
        pass

    def send_json(self, code: int, payload=None, headers: dict | None = None) -> None:
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(code)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        if code != 204:
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def book_id(self) -> int | None:
        parts = self.path.strip("/").split("/")
        return int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else None

    def do_GET(self) -> None:
        books = self.server.books
        if self.path == "/ping":
            self.send_json(200, {"pong": True})
        elif self.path == "/api/books":
            self.send_json(200, [{"id": i, **b} for i, b in sorted(books.items())])
        elif self.book_id() in books:
            i = self.book_id()
            self.send_json(200, {"id": i, **books[i], "links": {"self": f"/api/books/{i}",
                                                                 "collection": "/api/books"}})
        else:
            self.send_json(404, {"error": "no such book"})

    def do_POST(self) -> None:
        data = self.body()
        if self.path != "/api/books":
            self.send_json(405, {"error": "POST to the collection"}, {"Allow": "GET, PUT, DELETE"})
        elif "title" not in data:
            self.send_json(400, {"error": "title is required"})
        else:
            i = self.server.next_id
            self.server.next_id += 1
            self.server.books[i] = {"title": data["title"], "year": data.get("year")}
            self.send_json(201, {"id": i}, {"Location": f"/api/books/{i}"})

    def do_PUT(self) -> None:
        data = self.body()
        i = self.book_id()
        if i is None:
            self.send_json(404, {"error": "no such book"})
        else:
            self.server.books[i] = {"title": data.get("title", ""), "year": data.get("year")}
            self.send_json(200, {"id": i, **self.server.books[i]})

    def do_DELETE(self) -> None:
        i = self.book_id()
        if self.server.books.pop(i, None) is None:
            self.send_json(404, {"error": "no such book"})
        else:
            self.send_json(204)


srv = ThreadingHTTPServer((HOST, 0), Handler)
srv.lock = threading.Lock()
srv.connections = 0
srv.books = {1: {"title": "Networks", "year": 2020}}
srv.next_id = 2
srv.thread = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05})
srv.thread.start()
PORT = srv.server_address[1]

try:
    print("\nReal measurement on loopback: 5 requests, count TCP connections the server accepted.")
    before = srv.connections
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)      # HTTP/1.1 keeps it open
    for _ in range(5):
        conn.request("GET", "/ping")
        conn.getresponse().read()
    conn.close()
    persistent = srv.connections - before
    before = srv.connections
    for _ in range(5):
        c = http.client.HTTPConnection(HOST, PORT, timeout=5)
        c.request("GET", "/ping", headers={"Connection": "close"})   # HTTP/1.0 style
        c.getresponse().read()
        c.close()
    non_persistent = srv.connections - before
    print(f"persistent connection     : {persistent} TCP connection for 5 requests")
    print(f"one connection per request: {non_persistent} TCP connections for 5 requests")
    assert persistent == 1 and non_persistent == 5
    print("check: OK (each extra connection costs a handshake, and TCP slow start restarts)")

    # ===== SECTION 2: HTTP/2 AND HTTP/3 =====
    print("\n===== SECTION 2: HTTP/2 AND HTTP/3 =====")
    print(f"{'':<14}{'HTTP/1.1':<18}{'HTTP/2':<20}{'HTTP/3'}")
    rows = [
        ("RFC", "9112", "9113", "9114 (+ QUIC 9000)"),
        ("format", "text", "binary frames", "binary frames"),
        ("transport", "TCP", "TCP (+TLS)", "QUIC over UDP"),
        ("concurrency", "1 req at a time", "many streams", "many streams"),
        ("headers", "repeated text", "HPACK compressed", "QPACK compressed"),
        ("HOL blocking", "yes (app)", "TCP level only", "per stream only"),
        ("encryption", "optional", "usual (browsers)", "always (TLS 1.3)"),
    ]
    for r in rows:
        print(f"{r[0]:<14}{r[1]:<18}{r[2]:<20}{r[3]}")
    print("HTTP/2 server push: the server could send resources before they were requested.")
    print("It proved hard to use well; Chrome removed support in 2022 and it is rarely used,")
    print("so treat it as a historical feature, not a performance tool.")

    print("\nRound trips before the client can send its first request:")
    for name, n in (("TCP only (plain http)", 1), ("TCP + TLS 1.2", 3), ("TCP + TLS 1.3", 2),
                    ("QUIC (HTTP/3), first visit", 1), ("QUIC with 0-RTT resumption", 0)):
        print(f"  {name:<30}{n} RTT = {n * RTT} ms at RTT {RTT} ms")

    print("\nToy header compression (NOT real HPACK; shows the idea of a dynamic table):")
    headers = {"host": "api.example.test", "user-agent": "RDJ-Client/0.1 (Linux)",
               "accept": "application/json", "cookie": "sid=tok-0001"}
    plain_total = sum(len(k) + len(v) + 4 for k, v in headers.items())   # "k: v\r\n"
    seen: dict[tuple[str, str], int] = {}
    compressed_total = 0
    for req in range(1, 6):
        size = 0
        for k, v in headers.items():
            if (k, v) in seen:
                size += 1                                                  # 1-byte table index
            else:
                size += len(k) + len(v) + 2
                seen[(k, v)] = len(seen)
        compressed_total += size
        print(f"  request {req}: text headers {plain_total} bytes, toy-compressed {size} bytes")
    print(f"  five requests: {5 * plain_total} bytes vs {compressed_total} bytes")

    # ===== SECTION 3: HEAD-OF-LINE BLOCKING SIMULATION =====
    print("\n===== SECTION 3: HEAD-OF-LINE BLOCKING SIMULATION =====")
    print("3 responses A (6 packets), B (2), C (2). One packet is sent per time unit.")
    print("Loss: packet A2 is lost; recovery costs 10 extra units (abstract RTO).")
    SIZES = {"A": 6, "B": 2, "C": 2}
    PENALTY = 10

    def serial_order() -> list[tuple[str, int]]:
        return [(s, i) for s, n in SIZES.items() for i in range(1, n + 1)]

    def round_robin_order() -> list[tuple[str, int]]:
        out, pending = [], {s: 1 for s in SIZES}
        while any(pending[s] <= SIZES[s] for s in SIZES):
            for s in SIZES:
                if pending[s] <= SIZES[s]:
                    out.append((s, pending[s]))
                    pending[s] += 1
        return out

    def finish_times(order, lost, ordered_scope: str) -> dict[str, int]:
        """ordered_scope 'connection' = TCP (one in-order byte stream),
        'stream' = QUIC (in order per stream only)."""
        delivered: dict[tuple[str, int], int] = {}
        last_conn = 0
        last_stream: dict[str, int] = {}
        for slot, (s, i) in enumerate(order, 1):
            arrival = slot + (PENALTY if (s, i) == lost else 0)
            if ordered_scope == "connection":
                last_conn = max(last_conn, arrival)
                delivered[(s, i)] = last_conn
            else:
                last_stream[s] = max(last_stream.get(s, 0), arrival)
                delivered[(s, i)] = last_stream[s]
        return {s: max(t for (st, _), t in delivered.items() if st == s) for s in SIZES}

    cases = [("HTTP/1.1 one TCP conn, in order", serial_order(), "connection"),
             ("HTTP/2 multiplexed over TCP", round_robin_order(), "connection"),
             ("HTTP/3 multiplexed over QUIC", round_robin_order(), "stream")]
    print(f"{'':<34}{'no loss (A,B,C)':<20}{'A2 lost (A,B,C)'}")
    results = {}
    for name, order, scope in cases:
        ok = finish_times(order, None, scope)
        bad = finish_times(order, ("A", 2), scope)
        results[name] = (ok, bad)
        print(f"{name:<34}{str(tuple(ok.values())):<20}{tuple(bad.values())}")
    h1, h2, h3 = (results[c[0]] for c in cases)
    assert h1[0]["B"] > h2[0]["B"], "multiplexing lets short B finish before big A"
    assert h3[1]["B"] == h3[0]["B"] and h2[1]["B"] > h2[0]["B"]
    print("Read it: (1) without loss, HTTP/1.1 makes B wait for all of A (app-level HOL);")
    print("(2) HTTP/2 fixes that by interleaving, but one lost TCP packet stalls ALL streams;")
    print("(3) QUIC delays only the stream that lost the packet (B and C unaffected).")
    print("check: OK")

    # ===== SECTION 4: PROXIES, REVERSE PROXIES, LOAD BALANCERS, CDNs =====
    print("\n===== SECTION 4: PROXIES, REVERSE PROXIES, LOAD BALANCERS, CDNs =====")
    print("""  forward proxy (client side)        reverse proxy / load balancer (server side)
  browser -> [proxy] -> Internet     Internet -> [reverse proxy] -> app1
  (cache, filter, hide client IP)                               \\-> app2   (spread load, TLS, cache)
  CDN: many reverse-proxy caches near users, copies of popular content ("edge")""")
    backends = ["app1", "app2", "app3"]
    print("Round-robin vs hash-by-client (sticky) for 8 requests:")
    clients = ["alice", "bob", "alice", "carol", "alice", "bob", "dave", "alice"]
    rr = [backends[i % 3] for i in range(len(clients))]
    # stable hash (sum of character codes), NOT Python's randomised hash()
    sticky = [backends[sum(map(ord, c)) % 3] for c in clients]
    print(f"  {'client':<8}{'round-robin':<13}sticky")
    for c, a, b in zip(clients, rr, sticky):
        print(f"  {c:<8}{a:<13}{b}")
    assert len({b for c, b in zip(clients, sticky) if c == "alice"}) == 1
    print("  Sticky keeps one client on one backend (useful when sessions live in memory).")
    print("  Round-robin balances evenly but the same client may hit different servers.")

    # ===== SECTION 5: WEB CACHE HIT-RATIO SIMULATION =====
    print("\n===== SECTION 5: WEB CACHE HIT-RATIO SIMULATION =====")
    rng = random.Random(42)
    catalog = 200
    weights = [1 / (rank + 1) for rank in range(catalog)]        # Zipf-like popularity
    requests = rng.choices(range(catalog), weights=weights, k=20000)
    HIT_MS, MISS_MS = 10, 210
    print(f"20000 requests over {catalog} objects, popularity ~ 1/rank (seed 42). LRU cache.")
    print(f"hit costs {HIT_MS} ms, miss costs {MISS_MS} ms. avg = h*{HIT_MS} + (1-h)*{MISS_MS}")
    print(f"{'cache size':>11}{'hit ratio':>11}{'avg delay':>11}")
    for size in (0, 5, 20, 50, 100):
        cache: OrderedDict[int, None] = OrderedDict()
        hits = 0
        for obj in requests:
            if obj in cache:
                hits += 1
                cache.move_to_end(obj)
            elif size:
                cache[obj] = None
                if len(cache) > size:
                    cache.popitem(last=False)
        h = hits / len(requests)
        print(f"{size:>11}{h:>11.3f}{h * HIT_MS + (1 - h) * MISS_MS:>8.1f} ms")
    print("These numbers come from this synthetic workload only; real traffic differs.")

    # ===== SECTION 6: REST PRINCIPLES AND A JSON API =====
    print("\n===== SECTION 6: REST PRINCIPLES AND A JSON API =====")
    print("REST constraints: client-server, stateless requests, cacheable responses,")
    print("uniform interface (resources named by URL, standard methods, representations")
    print("like JSON, links), layered system (proxies/CDNs), optional code on demand.")

    def api(method: str, path: str, body: dict | None = None) -> None:
        c = http.client.HTTPConnection(HOST, PORT, timeout=5)
        try:
            c.request(method, path, body=json.dumps(body) if body is not None else None,
                      headers={"Content-Type": "application/json"} if body is not None else {})
            r = c.getresponse()
            data = r.read().decode()
            loc = f" Location={r.getheader('Location')}" if r.getheader("Location") else ""
            print(f"  {method:<7}{path:<16}-> {r.status} {r.reason}{loc} {data}")
        finally:
            c.close()

    api("GET", "/api/books")
    api("POST", "/api/books", {"title": "TCP/IP Illustrated", "year": 1994})
    api("POST", "/api/books", {"year": 2000})
    api("GET", "/api/books/2")
    api("PUT", "/api/books/2", {"title": "TCP/IP Illustrated, Vol. 1", "year": 2011})
    api("DELETE", "/api/books/1")
    api("DELETE", "/api/books/1")
    api("GET", "/api/books")
    print("Nouns in URLs (/api/books/2), verbs are the HTTP methods, codes carry the result.")
finally:
    srv.shutdown()
    srv.server_close()
    srv.thread.join(timeout=5)
print("\nserver stopped:", not srv.thread.is_alive())
