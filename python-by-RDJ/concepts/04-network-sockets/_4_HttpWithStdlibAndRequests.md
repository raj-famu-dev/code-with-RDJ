# `_4_HttpWithStdlibAndRequests.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
HTTP is a text protocol on top of TCP: a client sends a request (method, path, headers, optional body) and the server answers with a status code, headers and a body, very often JSON. This file starts a tiny JSON API on loopback using `http.server.ThreadingHTTPServer`, then calls it two ways: `urllib` from the standard library and the popular third-party `requests` library. You see status codes, headers, JSON, POST bodies, error handling and timeouts without touching the internet.

## Full Line-by-Line Breakdown

The script sets `NO_PROXY=127.0.0.1` so local requests never go through a proxy, binds to port `0`, and stops the server in a `finally` block so it always shuts down.

### SECTION 1: a small JSON server
`Handler` subclasses `BaseHTTPRequestHandler`; methods named `do_GET` and `do_POST` handle those HTTP methods. `_send_json` writes the status line (`send_response`), headers (`Content-Type`, `Content-Length`, a custom `X-Demo`), a blank line (`end_headers`) and the body bytes (`wfile.write`). Routes: `/items` returns a list, `/items/<id>` returns one item or a 404, `/slow` waits 1.5 s to test timeouts, and POST echoes parsed JSON with status 201 (or 400 for invalid JSON). `log_message` is overridden to silence the default request log. `ThreadingHTTPServer` handles each request in its own thread; `serve_forever` runs in a background thread.

```text
=== SECTION 1: a small JSON server ===
server running on host 127.0.0.1 (port chosen by OS)

```

### SECTION 2: urllib (standard library)
`urllib.request.urlopen(url, timeout=3)` returns a response usable in `with`. `resp.status` and `resp.reason` give `200 OK`, `resp.headers` holds headers (looked up case-insensitively), and `resp.read()` returns **bytes** that you decode with `json.loads`.

```text
=== SECTION 2: urllib (standard library) ===
status: 200 OK
Content-Type: application/json
X-Demo header: rdj
raw body type: bytes
parsed: [{'id': 1, 'name': 'keyboard'}, {'id': 2, 'name': 'mouse'}]

```

### SECTION 3: urllib raises on 4xx/5xx
For error statuses `urlopen` raises `urllib.error.HTTPError`, which still has the status (`e.code`) and a readable body, so you can parse the server's JSON error message.

```text
=== SECTION 3: urllib raises on 4xx/5xx ===
HTTPError status: 404 | body: {'error': 'not found'}

```

### SECTION 4: requests (nicer API)
`requests.get(url, timeout=3)` returns a `Response` with `status_code`, `ok`, `headers` (case-insensitive), `.text` and `.json()`. By default `requests` does **not** raise on 404; you inspect `ok` or call `raise_for_status()`, which raises `requests.HTTPError`. This is the opposite default from urllib.

```text
=== SECTION 4: requests (nicer API) ===
status_code: 200 | ok: True
headers['content-type'] (case-insensitive): application/json
r.json(): {'id': 1, 'name': 'keyboard'}
r.text: {"id": 1, "name": "keyboard"}
404 did NOT raise by default; status_code = 404 | ok = False
raise_for_status() -> HTTPError

```

### SECTION 5: POST with a JSON body
`requests.post(url, json={...})` serialises the dict and sets the `Content-Type` header for you. With urllib you build a `Request` object, encode the JSON to bytes, set the header and specify `method="POST"` yourself. Sending malformed JSON makes the server answer 400.

```text
=== SECTION 5: POST with a JSON body ===
requests POST: 201 {'created': {'name': 'monitor'}}
urllib POST : 201 {'created': {'name': 'webcam'}}
malformed body -> 400 {'error': 'invalid JSON'}

```

### SECTION 6: timeouts
The `/slow` endpoint takes 1.5 seconds, longer than the 0.3 s limit. `requests` raises `ReadTimeout`; urllib raises a `TimeoutError`-type error. The trap: **`requests` has no default timeout**, so a call without `timeout=` can hang forever on a stalled server. Always pass one.

```text
=== SECTION 6: timeouts ===
requests: ReadTimeout after 0.3 s (server accepted but answered too slowly)
urllib  : TimeoutError
TRAP: requests has NO default timeout. requests.get(url) can hang forever.
RULE: always pass timeout=...

```

### SECTION 7: Session reuses the connection
A `requests.Session` keeps cookies and default headers and reuses the underlying TCP connection (keep-alive), which is faster than opening a new connection for every request. The third call returns 404 because item 3 does not exist.

```text
=== SECTION 7: Session reuses the connection ===
status codes from one Session: [200, 200, 404]

```

### SECTION 8: shutdown
`httpd.shutdown()` stops `serve_forever`, `server_close()` closes the socket, and the thread is joined. A later request is refused (`requests.ConnectionError`), proving the server is down.

```text
=== SECTION 8: shutdown ===
server thread finished: True
after shutdown: requests.ConnectionError (connection refused)
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Built-in HTTP client | `java.net.http.HttpClient` (Java 11+); older `HttpURLConnection` | `urllib.request` (basic) or third-party `requests` |
| Send a GET | `client.send(HttpRequest.newBuilder(uri).build(), BodyHandlers.ofString())` | `requests.get(url, timeout=3)` |
| Status | `response.statusCode()` | `response.status_code` |
| JSON body | Needs Jackson/Gson to parse | `response.json()` (built in) |
| Error statuses | No exception; you check `statusCode()` | `requests`: no exception unless `raise_for_status()`; `urllib`: raises `HTTPError` |
| Timeouts | `HttpRequest.timeout(Duration)`, `connectTimeout` on the client | `timeout=` argument (none by default in `requests`) |
| Built-in test server | `com.sun.net.httpserver.HttpServer` | `http.server.ThreadingHTTPServer` |
| Production servers | Spring Boot (RDJ's strength), Jetty, Tomcat | FastAPI, Flask, Django (FastAPI is one of RDJ's 12-month targets); `http.server` is for demos only, not production |
| Connection reuse | `HttpClient` reuses connections automatically | Use a `requests.Session` explicitly |

## Key Rules / Gotchas Recap

- Always pass `timeout=` to `requests` calls.
- `requests` does not raise on 4xx/5xx; use `raise_for_status()` or check `ok`.
- `urllib` raises `HTTPError` on 4xx/5xx; the exception also holds the body.
- Bodies are `bytes`; use `.json()` / `.text` (requests) or `json.loads(raw)` (urllib).
- Set `Content-Length` when writing a response by hand.
- `http.server` is a learning tool; use a real framework for production.
- Only talk to servers you own; here that means `127.0.0.1`.

## Why This Structure Exists
AI engineers call model APIs, and agents call tools, over HTTP all day; knowing status codes, headers and timeouts is what separates scripts that fail silently from ones you can trust. Building the server yourself shows what frameworks like FastAPI hide, and a local test server is how you test HTTP clients without internet access.
