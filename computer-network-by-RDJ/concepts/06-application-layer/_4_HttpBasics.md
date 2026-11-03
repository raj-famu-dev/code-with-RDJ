# `_4_HttpBasics.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
HTTP (HyperText Transfer Protocol) is the request-response protocol of the World Wide Web: a client sends a text request naming a resource and a method, and the server replies with a status code, headers and usually a body. It exists so that any browser or program can fetch or change resources on any server using one shared, simple, human-readable format. It runs over TCP (port 80, or port 443 when wrapped in TLS as HTTPS).

**Message format (HTTP/1.1, RFC 9110/9112).** A request is: a request line `METHOD target HTTP-version`, header lines `Name: value`, an empty line, then an optional body. A response is: a status line `HTTP-version code reason`, header lines, an empty line and an optional body. Lines end with CRLF (`\r\n`). The message body length is given by `Content-Length` (bytes) or by `Transfer-Encoding: chunked`. HTTP is stateless: each request stands alone (cookies, covered next, add state).

**URL anatomy.** `scheme://userinfo@host:port/path?query#fragment`. The scheme picks the protocol, host and port say where to connect (default 80 for http, 443 for https), the path names the resource, the query carries parameters (`key=value&key=value`) and the fragment (after `#`) is used only by the browser and is never sent to the server. Special characters are percent-encoded (`%20` for a space, `%26` for `&`); in form-style query strings a space may be written `+`.

**Methods.**

| Method | Safe | Idempotent | Typical use |
|---|---|---|---|
| GET | yes | yes | retrieve a resource |
| HEAD | yes | yes | retrieve headers only |
| OPTIONS | yes | yes | discover allowed methods |
| POST | no | no | create a resource or run an action; a repeat may create a second one |
| PUT | no | yes | replace the resource at the URL (create if absent) |
| DELETE | no | yes | remove the resource |

Safe means the request is not supposed to change server state. Idempotent means that sending it once or many times leaves the server in the same final state (the response code may differ: the second DELETE returns 404). Browsers retry or prefetch GET freely, which is why a GET must never delete anything.

**Status codes.**

| Class | Meaning | Examples |
|---|---|---|
| 1xx | informational | 100 Continue, 101 Switching Protocols |
| 2xx | success | 200 OK, 201 Created, 204 No Content |
| 3xx | redirection | 301 Moved Permanently, 302 Found, 304 Not Modified |
| 4xx | client error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed |
| 5xx | server error | 500 Internal Server Error, 501 Not Implemented, 503 Service Unavailable |

401 means "you are not authenticated", 403 means "I know who you are and you may not". 404 means no such resource; 405 means the resource exists but not for that method (the reply should carry an `Allow` header); 501 means the server does not know the method at all.

**Typical exam questions.** Draw an HTTP request and response with their fields. Differentiate GET and POST, and PUT and POST. What is the difference between safe and idempotent? Explain the meaning of 200, 301, 304, 404, 500. Why is HTTP called stateless? What is in a URL?

## Full Line-by-Line Breakdown

### SECTION 1: ANATOMY OF A REQUEST AND A RESPONSE
A side-by-side ASCII drawing of a request and a response with the request line, headers, the blank separator line and the body. `{"id": 1, "name": "book"}` is 25 characters, which is why `Content-Length: 25` appears.

Output from a real run:

```text
===== SECTION 1: ANATOMY OF A REQUEST AND A RESPONSE =====
request                                   response
-------                                   --------
GET /items/1 HTTP/1.1      <- request line  HTTP/1.1 200 OK            <- status line
Host: www.example.com      <- headers       Content-Type: application/json
Accept: application/json                    Content-Length: 25
                           <- blank line                               <- blank line
(optional body)                             {"id": 1, "name": "book"}  <- body
Lines end with CRLF (\r\n). The blank line ends the headers.
```

### SECTION 2: URL ANATOMY
`urlsplit` cuts a URL into scheme, user, host, port, path, query and fragment. `parse_qs` decodes the query into a dict of lists (a key can repeat; `+` becomes a space). A URL without a port gives `None`, meaning use the scheme default. The three encoders differ: `quote` encodes a space as `%20`, `quote_plus` as `+`, and `urlencode` builds a whole query string (it uses plus style). The awkward value `rock & roll/100% fun` contains `&`, `/` and `%`, which would break the URL if left raw (for example `&` would start a new parameter). The assertion proves the round trip.

Output from a real run:

```text
===== SECTION 2: URL ANATOMY =====
url      : https://alice@www.example.com:8443/shop/books.html?q=net+work&page=2#reviews
  scheme   : 'https'
  username : 'alice'
  hostname : 'www.example.com'
  port     : 8443
  path     : '/shop/books.html'
  query    : 'q=net+work&page=2'
  fragment : 'reviews'
  query parsed: {'q': ['net work'], 'page': ['2']}
  default ports: http=80, https=443 -> None (None means default)
  The #fragment is NEVER sent to the server; the browser keeps it.
  quote()      : rock%20%26%20roll%2F100%25%20fun
  quote_plus() : rock+%26+roll%2F100%25+fun
  urlencode()  : q=rock+%26+roll%2F100%25+fun&page=2
check: OK (urlencode then parse_qs round-trips the awkward value)
```

### SECTION 3: METHODS AND STATUS CODES
Two lookup tables printed from Python data: the six methods with safe/idempotent flags and the five status classes with common examples.

Output from a real run:

```text
===== SECTION 3: METHODS AND STATUS CODES =====
method   safe  idempotent  use
GET      yes   yes         read a resource
HEAD     yes   yes         like GET but headers only
OPTIONS  yes   yes         ask what is allowed
POST     no    no          create / submit / run an action
PUT      no    yes         replace a resource at a known URL
DELETE   no    yes         remove a resource
safe = no change to server state; idempotent = repeating gives the same final state
1xx informational : 100 Continue, 101 Switching Protocols
2xx success       : 200 OK, 201 Created, 204 No Content
3xx redirection   : 301 Moved Permanently, 302 Found, 304 Not Modified
4xx client error  : 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 411 Length Required
5xx server error  : 500 Internal Server Error, 501 Not Implemented, 503 Service Unavailable
```

### SECTION 4: A LOOPBACK SERVER AND AN http.client CLIENT
`Handler` subclasses `BaseHTTPRequestHandler`; a method `do_GET`, `do_POST` and so on is called for each HTTP method. `protocol_version = "HTTP/1.1"` turns on persistent connections, which means every reply must have a correct `Content-Length` (or the client cannot know where the body ends). `date_time_string` and `version_string` are overridden only so the output is identical on every run. The server holds a small in-memory item table and runs in a thread on `127.0.0.1` port 0; `shutdown`, `server_close` and `join` stop it.

Reading the output: GET returns 200 with JSON. A missing item returns 404. HEAD has the same headers as GET (including `Content-Length: 25`) but no body. POST creates item 3 and answers `201 Created` with a `Location` header. PUT replaces item 1. DELETE returns `204 No Content` (a 204 has no body). OPTIONS lists allowed methods in `Allow`. POST on `/items/1` gets `405` with an `Allow` header. `PATCH` has no `do_PATCH`, so the library answers `501`.

A subtle point is in `do_POST`: it reads the request body BEFORE deciding to refuse with 405. If a server answers an error without consuming the body on a persistent connection, the unread body bytes are interpreted as the start of the NEXT request, which produced a confusing "Bad HTTP/0.9 request" error when this file was first written. Always drain the body.

Output from a real run:

```text
===== SECTION 4: A LOOPBACK SERVER AND AN http.client CLIENT =====
  GET    /items     -> 200 OK                 {'Content-Length': '25'} body='{"1": "book", "2": "pen"}'
  GET    /items/1   -> 200 OK                 {'Content-Length': '25'} body='{"id": 1, "name": "book"}'
  GET    /items/99  -> 404 Not Found          {'Content-Length': '22'} body='{"error": "not found"}'
  HEAD   /items/1   -> 200 OK                 {'Content-Length': '25'} body=''
  POST   /items     -> 201 Created            {'Content-Length': '9', 'Location': '/items/3'} body='{"id": 3}'
  PUT    /items/1   -> 200 OK                 {'Content-Length': '26'} body='{"id": 1, "name": "novel"}'
  DELETE /items/2   -> 204 No Content         {} body=''
  OPTIONS/items     -> 204 No Content         {'Allow': 'GET, HEAD, POST, PUT, DELETE, OPTIONS'} body=''
  POST   /items/1   -> 405 Method Not Allowed {'Content-Length': '32', 'Allow': 'GET, PUT, DELETE, HEAD'} body='{"error": "POST only on /items"}'
  PATCH  /items/1   -> 501 Unsupported method ('PATCH') {'Content-Length': '358'} body='<!DOCTYPE HTML>\n<html lang="en">\n    <head>\n   ...'
HEAD returned the same headers as GET (Content-Length 25) but NO body.
```

### SECTION 5: SAFE AND IDEMPOTENT IN PRACTICE
Runs the same call twice and inspects the server's table. Two POSTs create two items (not idempotent). Two PUTs to `/items/7` leave exactly one item (idempotent). Two DELETEs return `204` then `404` but leave the same final state (empty), which shows that idempotent refers to state, not status.

Output from a real run:

```text
===== SECTION 5: SAFE AND IDEMPOTENT IN PRACTICE =====
POST twice  -> items: {1: 'pen', 2: 'pen'} (two NEW resources: not idempotent)
PUT twice   -> items: {7: 'pen'} (same final state: idempotent)
DELETE twice-> statuses 204 then 404, items: {}
Idempotent means the SERVER STATE is the same, not that the status code is.
```

### SECTION 6: A CURL-STYLE RAW REQUEST OVER A SOCKET
Everything HTTP does is just bytes on TCP. We open a socket, send the exact request text with `\r\n` line endings, and read until the server closes (`Connection: close`). Each line is printed with `repr` so the CRLFs and blank line are visible. This is what `curl -v` shows you.

Output from a real run:

```text
===== SECTION 6: A CURL-STYLE RAW REQUEST OVER A SOCKET =====
sent:
  > 'GET /items/1 HTTP/1.1'
  > 'Host: localhost'
  > 'Connection: close'
  > ''
received:
  < 'HTTP/1.1 200 OK'
  < 'Server: RDJ-Demo/1.0'
  < 'Date: Mon, 01 Jan 2024 00:00:00 GMT'
  < 'Content-Type: application/json'
  < 'Content-Length: 25'
  < ''
  < '{"id": 1, "name": "book"}'
'Connection: close' makes the server close after replying, so recv() sees EOF.
```

### SECTION 7: TRAP - A POST WITH NO Content-Length
We send the same JSON body twice by hand. Without `Content-Length` the server cannot know how many body bytes to read, so our handler answers `411 Length Required`. With the header it works (`201 Created`). Other correct options are `Transfer-Encoding: chunked`. `http.client` and `curl` add the header automatically, which is why you rarely see this bug until you write raw requests.

Output from a real run:

```text
===== SECTION 7: TRAP - A POST WITH NO Content-Length =====
without Content-Length: HTTP/1.1 411 Length Required
with    Content-Length: HTTP/1.1 201 Created
The server cannot guess where the body ends on a persistent connection,
so the length (or chunked encoding) is mandatory for a request body.
check: OK
server stopped: True
```

## Worked Example
**Problem.** Given `http://www.example.com:8080/a/b.php?x=1&y=two%20words#top`, (a) name each URL part, (b) say what the server receives on its request line and Host header, (c) the client sent `DELETE /items/7` twice; what are likely status codes, and is DELETE idempotent?

**Solution.** (a) scheme `http`, host `www.example.com`, port 8080, path `/a/b.php`, query `x=1&y=two%20words` (decoded: x=1, y="two words"), fragment `top`. (b) The request line is `GET /a/b.php?x=1&y=two%20words HTTP/1.1` and the header is `Host: www.example.com:8080`; the fragment `top` is not sent. (c) First call 204 (or 200), second 404. DELETE is idempotent because the end state (item gone) is the same. The same logic was confirmed in Section 5 (`204` then `404`).

## Key Rules / Gotchas Recap
- Request = line + headers + blank line + body; response = status line + headers + blank line + body; lines end with CRLF.
- GET/HEAD/OPTIONS are safe; GET/HEAD/OPTIONS/PUT/DELETE are idempotent; POST is neither.
- 2xx success, 3xx redirect, 4xx client's fault, 5xx server's fault. 401 = not authenticated, 403 = not allowed.
- `Content-Length` must be exact on a keep-alive connection; always read the whole request body even when you reject it.
- The fragment never reaches the server; percent-encode special characters in queries.
- 405 needs an `Allow` header; 204 has no body; HEAD has headers but no body.

## Why This Matters
Every REST API, webhook and model-serving endpoint speaks this protocol; debugging with a raw request or `curl -v` is a daily skill. Many web vulnerabilities (request smuggling, injection through unencoded URL parts) come from parsers that disagree about where one message ends or how a URL is decoded.
