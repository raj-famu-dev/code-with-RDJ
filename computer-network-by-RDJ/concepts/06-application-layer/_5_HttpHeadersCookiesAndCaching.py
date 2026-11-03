# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches HTTP headers (Host, User-Agent, Content-Type/Length), cookies and
sessions (Set-Cookie attributes), conditional GET with ETag/304, Cache-Control,
content negotiation and redirects, each shown against a loopback server.
Syllabus idea: HTTP state (cookies), web caching, content negotiation.
Loopback only (127.0.0.1, port 0).
"""
import hashlib
import http.client
import json
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
FIXED_DATE = "Mon, 01 Jan 2024 00:00:00 GMT"
STATIC_BODY = "Computer networks: cache me if you can.\n".encode()
ETAG = '"' + hashlib.sha1(STATIC_BODY).hexdigest()[:8] + '"'


def parse_accept(header: str) -> list[tuple[str, float]]:
    """'text/html;q=0.5, application/json' -> [('application/json',1.0), ('text/html',0.5)]"""
    items = []
    for part in header.split(","):
        fields = [f.strip() for f in part.split(";")]
        q = 1.0
        for f in fields[1:]:
            if f.startswith("q="):
                q = float(f[2:])
        items.append((fields[0], q))
    return sorted(items, key=lambda x: -x[1])


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args) -> None:
        pass

    def version_string(self) -> str:
        return "RDJ-Demo/1.0"

    def date_time_string(self, timestamp=None) -> str:
        return FIXED_DATE

    def send(self, code: int, body: bytes = b"", ctype: str = "text/plain; charset=utf-8",
             headers: list[tuple[str, str]] | None = None) -> None:
        self.send_response(code)
        for k, v in headers or []:
            self.send_header(k, v)
        if code != 304:
            self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))   # BYTES, not characters
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def session_user(self) -> str | None:
        jar = SimpleCookie(self.headers.get("Cookie", ""))
        sid = jar["sid"].value if "sid" in jar else None
        return self.server.sessions.get(sid)

    def do_GET(self) -> None:
        path, _, query = self.path.partition("?")
        if path == "/headers":
            seen = {h: self.headers.get(h) for h in ("Host", "User-Agent", "Accept")}
            self.send(200, json.dumps(seen).encode(), "application/json")
        elif path == "/cafe":
            self.send(200, "café ☕\n".encode("utf-8"), "text/plain; charset=utf-8")
        elif path in ("/login", "/login-secure"):
            self.server.token_no += 1
            sid = f"tok-{self.server.token_no:04d}"      # demo only; real ids must be random
            self.server.sessions[sid] = "alice"
            c = SimpleCookie()
            c["sid"] = sid
            m = c["sid"]
            m["path"], m["httponly"], m["samesite"], m["max-age"] = "/", True, "Lax", 3600
            if path == "/login-secure":
                m["secure"] = True
            self.send(200, b"logged in\n", headers=[("Set-Cookie", m.OutputString())])
        elif path == "/profile":
            user = self.session_user()
            if user:
                self.send(200, f"hello {user}\n".encode())
            else:
                self.send(401, b"please log in\n")
        elif path == "/logout":
            c = SimpleCookie()
            c["sid"] = ""
            c["sid"]["max-age"], c["sid"]["path"] = 0, "/"
            self.send(200, b"bye\n", headers=[("Set-Cookie", c["sid"].OutputString())])
        elif path == "/static.txt":
            self.server.static_hits += 1
            if self.headers.get("If-None-Match") == ETAG:
                self.send(304, headers=[("ETag", ETAG), ("Cache-Control", "max-age=60")])
            else:
                self.send(200, STATIC_BODY, headers=[("ETag", ETAG), ("Cache-Control", "max-age=60")])
        elif path == "/private":
            self.send(200, b"secret page\n", headers=[("Cache-Control", "no-store")])
        elif path == "/negotiate":
            offers = {"application/json": b'{"msg": "hello"}\n', "text/plain": b"hello\n",
                      "text/html": b"<p>hello</p>\n"}
            for mime, q in parse_accept(self.headers.get("Accept", "*/*")):
                if q > 0 and mime in offers:
                    self.send(200, offers[mime], mime, headers=[("Vary", "Accept")])
                    return
                if mime == "*/*" and q > 0:
                    self.send(200, offers["text/plain"], "text/plain", headers=[("Vary", "Accept")])
                    return
            self.send(406, b"cannot satisfy Accept\n")
        elif path == "/old":
            self.send(301, headers=[("Location", "/new")])
        elif path == "/temp":
            self.send(302, headers=[("Location", "/new")])
        elif path == "/new":
            self.send(200, b"you reached /new\n")
        elif path == "/loop1":
            self.send(302, headers=[("Location", "/loop2")])
        elif path == "/loop2":
            self.send(302, headers=[("Location", "/loop1")])
        else:
            self.send(404, b"not found\n")


srv = ThreadingHTTPServer((HOST, 0), Handler)
srv.sessions, srv.token_no, srv.static_hits = {}, 0, 0
srv.thread = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05})
srv.thread.start()
PORT = srv.server_address[1]


def get(path: str, headers: dict | None = None):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    try:
        conn.request("GET", path, headers=headers or {})
        r = conn.getresponse()
        body = r.read()
        return r.status, r, body
    finally:
        conn.close()


try:
    # ===== SECTION 1: REQUEST HEADERS AND Content-Type / Content-Length =====
    print("===== SECTION 1: REQUEST HEADERS AND Content-Type / Content-Length =====")
    status, r, body = get("/headers", {"User-Agent": "RDJ-Client/0.1", "Accept": "application/json"})
    print("status:", status)
    seen = json.loads(body)
    seen["Host"] = seen["Host"].replace(f":{PORT}", ":<port chosen by OS>")
    print("server saw:", seen)
    print("Content-Type  :", r.getheader("Content-Type"))
    print("Content-Length equals len(body):", int(r.getheader("Content-Length")) == len(body),
          "(the number itself depends on the port digits, so it is not printed)")
    print("Host tells a server WHICH site is wanted: one IP can host many names (virtual hosts).")
    print("Host is mandatory in HTTP/1.1. User-Agent names the client software.")

    # ===== SECTION 2: TRAP - Content-Length COUNTS BYTES, AND CHARSET MATTERS =====
    print("\n===== SECTION 2: TRAP - Content-Length COUNTS BYTES, AND CHARSET MATTERS =====")
    status, r, body = get("/cafe")
    text = "café ☕\n"
    print(f"characters: {len(text)}, UTF-8 bytes: {len(body)}, Content-Length: {r.getheader('Content-Length')}")
    print("Content-Type:", r.getheader("Content-Type"))
    print("decoded with the declared charset (utf-8):", repr(body.decode("utf-8")))
    print("decoded WRONGLY as latin-1               :", repr(body.decode("latin-1")))
    assert len(text) != len(body) and int(r.getheader("Content-Length")) == len(body)
    print("check: OK (a length computed with len(str) would be too small and cut the body)")

    # ===== SECTION 3: COOKIES AND SESSIONS =====
    print("\n===== SECTION 3: COOKIES AND SESSIONS =====")

    class Jar:
        """A tiny browser cookie jar: honours Path, Secure and Max-Age=0."""

        def __init__(self) -> None:
            self.cookies: dict[str, dict] = {}

        def store(self, set_cookie_headers: list[str]) -> None:
            for h in set_cookie_headers:
                c = SimpleCookie()
                c.load(h)
                for name, m in c.items():
                    if m["max-age"] == "0":
                        self.cookies.pop(name, None)
                    else:
                        self.cookies[name] = {"value": m.value, "secure": bool(m["secure"]),
                                              "path": m["path"] or "/"}

        def header_for(self, path: str, https: bool) -> dict:
            pairs = [f"{n}={c['value']}" for n, c in self.cookies.items()
                     if path.startswith(c["path"]) and (https or not c["secure"])]
            return {"Cookie": "; ".join(pairs)} if pairs else {}

    jar = Jar()
    status, r, body = get("/profile")
    print("no cookie        ->", status, body.decode().strip())
    status, r, body = get("/login")
    set_cookie = r.getheader("Set-Cookie")
    print("login            ->", status, body.decode().strip())
    print("  Set-Cookie:", set_cookie)
    jar.store([set_cookie])
    status, r, body = get("/profile", jar.header_for("/profile", https=False))
    print("with the cookie  ->", status, body.decode().strip())
    print("  Cookie header sent:", jar.header_for("/profile", https=False))
    status, r, body = get("/logout", jar.header_for("/logout", https=False))
    print("logout Set-Cookie:", r.getheader("Set-Cookie"), "(Max-Age=0 deletes it)")
    jar.store([r.getheader("Set-Cookie")])
    print("jar after logout :", jar.cookies)
    print("Attributes: HttpOnly = JavaScript cannot read it (limits XSS theft);")
    print("  Secure = only sent over HTTPS; SameSite=Lax/Strict = not sent on most")
    print("  cross-site requests (limits CSRF); Path/Domain = where it applies;")
    print("  Max-Age/Expires = lifetime (none = session cookie, gone when browser closes).")
    print("The server stores the session; the cookie is just a random key to find it.")

    # ===== SECTION 4: Secure COOKIES ARE WITHHELD ON PLAIN HTTP =====
    print("\n===== SECTION 4: Secure COOKIES ARE WITHHELD ON PLAIN HTTP =====")
    status, r, body = get("/login-secure")
    print("Set-Cookie:", r.getheader("Set-Cookie"))
    jar2 = Jar()
    jar2.store([r.getheader("Set-Cookie")])
    print("over http :", jar2.header_for("/profile", https=False) or "(cookie NOT sent)")
    print("over https:", jar2.header_for("/profile", https=True))
    print("Trap: a session cookie without Secure travels in clear text on http and can be")
    print("stolen by anyone on the path. Set Secure + HttpOnly + SameSite on session cookies.")

    # ===== SECTION 5: CONDITIONAL GET, ETag, Cache-Control =====
    print("\n===== SECTION 5: CONDITIONAL GET, ETag, Cache-Control =====")
    status, r, body = get("/static.txt")
    print(f"1st GET : {status}, {len(body)} bytes, ETag={r.getheader('ETag')}, "
          f"Cache-Control={r.getheader('Cache-Control')}")
    etag = r.getheader("ETag")
    status, r, body = get("/static.txt", {"If-None-Match": etag})
    print(f"2nd GET with If-None-Match: {status} {r.reason}, body bytes={len(body)}")
    status, r, body = get("/static.txt", {"If-None-Match": '"stale"'})
    print(f"3rd GET with an OLD etag  : {status} {r.reason}, body bytes={len(body)}")
    print("server handled", srv.static_hits, "requests; 304 saved re-sending the body.")
    print("max-age=60: a cache may reuse the copy for 60 s WITHOUT asking; after that it")
    print("revalidates with If-None-Match and usually gets a cheap 304.")
    status, r, body = get("/private")
    print("no-store page: Cache-Control =", r.getheader("Cache-Control"), "(never store it)")
    assert status == 200
    print("check: OK")

    # ===== SECTION 6: CONTENT NEGOTIATION =====
    print("\n===== SECTION 6: CONTENT NEGOTIATION =====")
    print("parse_accept example:", parse_accept("text/html;q=0.5, application/json, */*;q=0.1"))
    for accept in ("application/json", "text/html", "text/html;q=0.5, application/json",
                   "image/png", "*/*"):
        status, r, body = get("/negotiate", {"Accept": accept})
        print(f"  Accept: {accept:<38} -> {status} {r.getheader('Content-Type') or '':<18} {body.decode().strip()}")
    print("406 Not Acceptable = server has nothing the client said it can handle.")
    print("Vary: Accept tells caches the reply depends on that request header.")

    # ===== SECTION 7: REDIRECTS (AND A REDIRECT LOOP) =====
    print("\n===== SECTION 7: REDIRECTS (AND A REDIRECT LOOP) =====")

    def follow(path: str, max_hops: int = 5) -> None:
        trail = []
        for _ in range(max_hops + 1):
            status, r, body = get(path)
            trail.append(f"{path} [{status}]")
            if status in (301, 302, 303, 307, 308):
                path = r.getheader("Location")
                continue
            print("  " + " -> ".join(trail), "| final body:", body.decode().strip())
            return
        print("  " + " -> ".join(trail), "| GAVE UP after", max_hops, "redirects")

    follow("/old")
    follow("/temp")
    follow("/loop1")
    print("301 = moved permanently (caches/browsers may remember it); 302 = temporary.")
    print("Clients must cap the number of redirects, or a loop never ends.")
finally:
    srv.shutdown()
    srv.server_close()
    srv.thread.join(timeout=5)
print("\nserver stopped:", not srv.thread.is_alive())
