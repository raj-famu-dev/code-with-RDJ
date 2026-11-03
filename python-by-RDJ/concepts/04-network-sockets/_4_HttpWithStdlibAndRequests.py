# Tags: #Python #Networking #Sockets #HttpStdlibRequests | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches HTTP from both sides on loopback only: a tiny JSON server built with
http.server.ThreadingHTTPServer, queried with urllib (stdlib) and requests.
Covers status codes, headers, JSON bodies, POST, errors and timeouts.
"""
import json
import os
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import requests

HOST = "127.0.0.1"
os.environ["NO_PROXY"] = HOST   # never route loopback traffic through an HTTP proxy

print("=== SECTION 1: a small JSON server ===")
ITEMS = {"1": {"id": 1, "name": "keyboard"}, "2": {"id": 2, "name": "mouse"}}

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))   # client needs this to know where body ends
        self.send_header("X-Demo", "rdj")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/items":
            self._send_json(200, list(ITEMS.values()))
        elif self.path.startswith("/items/"):
            item = ITEMS.get(self.path.rsplit("/", 1)[1])
            if item is None:
                self._send_json(404, {"error": "not found"})
            else:
                self._send_json(200, item)
        elif self.path == "/slow":
            threading.Event().wait(1.5)                      # deliberately slower than client timeouts
            self._send_json(200, {"slow": True})
        else:
            self._send_json(404, {"error": "no such route"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"null")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return
        self._send_json(201, {"created": data})

    def log_message(self, format: str, *args: Any) -> None:   # silence per-request stderr logging
        pass

httpd = ThreadingHTTPServer((HOST, 0), Handler)              # port 0 -> OS picks
httpd.daemon_threads = True
port = httpd.server_address[1]
BASE = f"http://{HOST}:{port}"
thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.1})
thread.start()
print("server running on host", HOST, "(port chosen by OS)")

try:
    print("\n=== SECTION 2: urllib (standard library) ===")
    with urllib.request.urlopen(BASE + "/items", timeout=3) as resp:
        print("status:", resp.status, resp.reason)
        print("Content-Type:", resp.headers["Content-Type"])
        print("X-Demo header:", resp.headers.get("X-Demo"))
        raw = resp.read()                                    # bytes
        print("raw body type:", type(raw).__name__)
        print("parsed:", json.loads(raw))

    print("\n=== SECTION 3: urllib raises on 4xx/5xx ===")
    try:
        urllib.request.urlopen(BASE + "/items/99", timeout=3)
    except urllib.error.HTTPError as e:
        print("HTTPError status:", e.code, "| body:", json.loads(e.read()))
        e.close()

    print("\n=== SECTION 4: requests (nicer API) ===")
    r = requests.get(BASE + "/items/1", timeout=3)
    print("status_code:", r.status_code, "| ok:", r.ok)
    print("headers['content-type'] (case-insensitive):", r.headers["content-type"])
    print("r.json():", r.json())
    print("r.text:", r.text)
    r404 = requests.get(BASE + "/items/99", timeout=3)
    print("404 did NOT raise by default; status_code =", r404.status_code, "| ok =", r404.ok)
    try:
        r404.raise_for_status()
    except requests.HTTPError as e:
        print("raise_for_status() ->", type(e).__name__)

    print("\n=== SECTION 5: POST with a JSON body ===")
    rp = requests.post(BASE + "/items", json={"name": "monitor"}, timeout=3)
    print("requests POST:", rp.status_code, rp.json())
    req = urllib.request.Request(
        BASE + "/items",
        data=json.dumps({"name": "webcam"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=3) as resp2:
        print("urllib POST :", resp2.status, json.loads(resp2.read()))
    bad = requests.post(BASE + "/items", data=b"{not json", timeout=3)
    print("malformed body ->", bad.status_code, bad.json())

    print("\n=== SECTION 6: timeouts ===")
    try:
        requests.get(BASE + "/slow", timeout=0.3)            # server takes 1.5 s
    except requests.exceptions.ReadTimeout:
        print("requests: ReadTimeout after 0.3 s (server accepted but answered too slowly)")
    try:
        urllib.request.urlopen(BASE + "/slow", timeout=0.3)
    except (TimeoutError, urllib.error.URLError) as e:
        print("urllib  :", type(e).__name__)
    print("TRAP: requests has NO default timeout. requests.get(url) can hang forever.")
    print("RULE: always pass timeout=...")

    print("\n=== SECTION 7: Session reuses the connection ===")
    with requests.Session() as s:
        s.headers.update({"X-Client": "demo"})
        codes = [s.get(BASE + f"/items/{i}", timeout=3).status_code for i in (1, 2, 3)]
    print("status codes from one Session:", codes)
finally:
    httpd.shutdown()                  # stop serve_forever
    httpd.server_close()              # release the port
    thread.join(timeout=5)

print("\n=== SECTION 8: shutdown ===")
print("server thread finished:", not thread.is_alive())
try:
    requests.get(BASE + "/items", timeout=1)
except requests.exceptions.ConnectionError:
    print("after shutdown: requests.ConnectionError (connection refused)")
