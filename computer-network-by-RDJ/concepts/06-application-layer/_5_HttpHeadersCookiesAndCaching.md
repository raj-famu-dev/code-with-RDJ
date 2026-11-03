# `_5_HttpHeadersCookiesAndCaching.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
HTTP headers are the name-value lines that describe a request or response: who is asking, what format the body is in, how long it may be cached, and which session it belongs to. Because HTTP itself is stateless, cookies (a small token the server hands out and the browser returns) add sessions, and caching headers let browsers and proxies reuse earlier responses so the same bytes are not sent twice.

**Important headers.**

| Header | Direction | Meaning |
|---|---|---|
| Host | request | which site (name:port) is wanted; mandatory in HTTP/1.1, enables virtual hosting |
| User-Agent | request | client software description |
| Accept, Accept-Language, Accept-Encoding | request | formats, languages and compressions the client can handle (with optional `q` weights 0 to 1) |
| Content-Type | both | media type and charset of the body, e.g. `text/html; charset=utf-8`, `application/json` |
| Content-Length | both | size of the body in BYTES |
| Cookie | request | cookies the browser returns |
| Set-Cookie | response | create, update or delete a cookie |
| Location | response | target of a redirect (3xx) or of a newly created resource (201) |
| ETag / If-None-Match | response / request | validator for conditional requests |
| Last-Modified / If-Modified-Since | response / request | date-based validator |
| Cache-Control | both | caching rules: `max-age=N`, `no-cache` (must revalidate), `no-store` (never keep), `public`, `private` |
| Vary | response | which request headers the response depends on |
| Allow | response | methods allowed on the resource |

**Cookies and sessions.** On login the server creates a session record and sends `Set-Cookie: sid=<random>; ...`. The browser stores it and sends `Cookie: sid=<random>` with every later request to that site; the server looks up the record. Attributes:
- `Max-Age` or `Expires`: lifetime. Without either it is a session cookie and disappears when the browser closes. `Max-Age=0` deletes it.
- `Path`, `Domain`: which URLs receive it.
- `Secure`: only sent over HTTPS.
- `HttpOnly`: invisible to JavaScript (`document.cookie`), so a cross-site-scripting bug cannot read the session id.
- `SameSite=Strict|Lax|None`: whether it is attached to cross-site requests; limits cross-site request forgery. `None` requires `Secure`.
The session id must be long and unpredictable (generate it with a cryptographic random source); anyone who copies it can impersonate you. Cookies enable personalisation and tracking, which raises privacy issues.

**Web caching and conditional GET.** A cache keeps copies of responses. If the response has `Cache-Control: max-age=60`, the cache may serve it for 60 seconds without contacting the server (a hit with no network). After it expires the cache sends a conditional GET: `If-None-Match: "etag"` (or `If-Modified-Since`). If unchanged the server answers `304 Not Modified` with no body, saving bandwidth; if changed it sends `200` with the new body and a new ETag. `no-store` forbids any caching (private data); `no-cache` allows storing but demands revalidation each time.

**Content negotiation.** A client lists what it accepts with `Accept` and q-values; the server picks the best match (`Content-Type` tells which one it chose) or answers 406 Not Acceptable. `Vary: Accept` tells caches the reply depends on that header.

**Redirects.** A 3xx response with a `Location` header. 301 Moved Permanently and 308 are permanent; 302 and 307 temporary; 303 "see other" (usually after POST). Clients must limit the number of hops because servers can create loops.

**Typical exam questions.** How does a cookie provide a session over a stateless protocol (draw the four steps)? What do HttpOnly, Secure and SameSite do? Explain conditional GET with a diagram; when is a 304 returned? Compute the average delay of a request with a cache hit ratio h. What is the difference between `no-cache` and `no-store`?

## Full Line-by-Line Breakdown

### SECTION 1: REQUEST HEADERS AND Content-Type / Content-Length
The `/headers` route echoes back the `Host`, `User-Agent` and `Accept` headers it received. The client added its own `User-Agent` and `Accept`; `http.client` added `Host` (the port is masked in the output because the OS chooses it). The reply is JSON and says so with `Content-Type`. The program checks that `Content-Length` equals the true body size.

Output from a real run:

```text
===== SECTION 1: REQUEST HEADERS AND Content-Type / Content-Length =====
status: 200
server saw: {'Host': '127.0.0.1:<port chosen by OS>', 'User-Agent': 'RDJ-Client/0.1', 'Accept': 'application/json'}
Content-Type  : application/json
Content-Length equals len(body): True (the number itself depends on the port digits, so it is not printed)
Host tells a server WHICH site is wanted: one IP can host many names (virtual hosts).
Host is mandatory in HTTP/1.1. User-Agent names the client software.
```

### SECTION 2: TRAP - Content-Length COUNTS BYTES, AND CHARSET MATTERS
The string `café ☕` plus a newline has 7 characters but 10 bytes in UTF-8 (`é` is 2 bytes, `☕` is 3). `Content-Length` must be 10. A server that sends `len(text)` (7) would cut the body short. The second half of the trap: bytes only mean something with the right charset. Decoding the UTF-8 bytes as latin-1 produces mojibake (`cafÃ©`). Always declare `charset` in `Content-Type` and decode with it.

Output from a real run:

```text
===== SECTION 2: TRAP - Content-Length COUNTS BYTES, AND CHARSET MATTERS =====
characters: 7, UTF-8 bytes: 10, Content-Length: 10
Content-Type: text/plain; charset=utf-8
decoded with the declared charset (utf-8): 'café ☕\n'
decoded WRONGLY as latin-1               : 'cafÃ© â\x98\x95\n'
check: OK (a length computed with len(str) would be too small and cut the body)
```

### SECTION 3: COOKIES AND SESSIONS
`SimpleCookie` builds the `Set-Cookie` value. The sequence: `/profile` without a cookie gives 401; `/login` creates a session (server side dictionary) and sets `sid`; the client's tiny `Jar` stores it and returns it in a `Cookie` header, so `/profile` now greets alice; `/logout` sends `Max-Age=0` and the jar deletes the cookie. In this demo the token is a counter so the output is repeatable; a real server must use random tokens such as `secrets.token_urlsafe(32)`.

Output from a real run:

```text
===== SECTION 3: COOKIES AND SESSIONS =====
no cookie        -> 401 please log in
login            -> 200 logged in
  Set-Cookie: sid=tok-0001; HttpOnly; Max-Age=3600; Path=/; SameSite=Lax
with the cookie  -> 200 hello alice
  Cookie header sent: {'Cookie': 'sid=tok-0001'}
logout Set-Cookie: sid=""; Max-Age=0; Path=/ (Max-Age=0 deletes it)
jar after logout : {}
Attributes: HttpOnly = JavaScript cannot read it (limits XSS theft);
  Secure = only sent over HTTPS; SameSite=Lax/Strict = not sent on most
  cross-site requests (limits CSRF); Path/Domain = where it applies;
  Max-Age/Expires = lifetime (none = session cookie, gone when browser closes).
The server stores the session; the cookie is just a random key to find it.
```

### SECTION 4: Secure COOKIES ARE WITHHELD ON PLAIN HTTP
`/login-secure` adds the `Secure` attribute. The jar models browser behaviour: it sends the cookie only when the scheme is https. This is why a session cookie without `Secure` is risky on a hotspot: it is sent in clear text over http and can be copied. (We cannot run real HTTPS here, so the https case is a model, labelled as such.)

Output from a real run:

```text
===== SECTION 4: Secure COOKIES ARE WITHHELD ON PLAIN HTTP =====
Set-Cookie: sid=tok-0002; HttpOnly; Max-Age=3600; Path=/; SameSite=Lax; Secure
over http : (cookie NOT sent)
over https: {'Cookie': 'sid=tok-0002'}
Trap: a session cookie without Secure travels in clear text on http and can be
stolen by anyone on the path. Set Secure + HttpOnly + SameSite on session cookies.
```

### SECTION 5: CONDITIONAL GET, ETag, Cache-Control
The ETag is the first 8 hex digits of a SHA-1 of the body (a content fingerprint). First GET: 200 with 40 bytes plus `ETag` and `Cache-Control: max-age=60`. Second GET sends `If-None-Match` with that ETag: the server compares, finds equality and answers `304 Not Modified` with 0 body bytes. Third GET with an old tag gets the full 200 again. `/private` shows `no-store`.

Output from a real run:

```text
===== SECTION 5: CONDITIONAL GET, ETag, Cache-Control =====
1st GET : 200, 40 bytes, ETag="0176912f", Cache-Control=max-age=60
2nd GET with If-None-Match: 304 Not Modified, body bytes=0
3rd GET with an OLD etag  : 200 OK, body bytes=40
server handled 3 requests; 304 saved re-sending the body.
max-age=60: a cache may reuse the copy for 60 s WITHOUT asking; after that it
revalidates with If-None-Match and usually gets a cheap 304.
no-store page: Cache-Control = no-store (never store it)
check: OK
```

### SECTION 6: CONTENT NEGOTIATION
`parse_accept` splits the header into media types with q-values and sorts by q (best first). The server walks that list and answers with the first type it can produce; `*/*` means anything, `image/png` cannot be satisfied so the reply is 406. The line with `text/html;q=0.5, application/json` shows the weight overriding the order written.

Output from a real run:

```text
===== SECTION 6: CONTENT NEGOTIATION =====
parse_accept example: [('application/json', 1.0), ('text/html', 0.5), ('*/*', 0.1)]
  Accept: application/json                       -> 200 application/json   {"msg": "hello"}
  Accept: text/html                              -> 200 text/html          <p>hello</p>
  Accept: text/html;q=0.5, application/json      -> 200 application/json   {"msg": "hello"}
  Accept: image/png                              -> 406 text/plain; charset=utf-8 cannot satisfy Accept
  Accept: */*                                    -> 200 text/plain         hello
406 Not Acceptable = server has nothing the client said it can handle.
Vary: Accept tells caches the reply depends on that request header.
```

### SECTION 7: REDIRECTS (AND A REDIRECT LOOP)
`follow` implements what a browser does: if the status is a redirect, request `Location` next. `/old` (301) and `/temp` (302) both end at `/new`. `/loop1` and `/loop2` point at each other, so the loop would run forever without the hop limit of 5, after which the client gives up.

Output from a real run:

```text
===== SECTION 7: REDIRECTS (AND A REDIRECT LOOP) =====
  /old [301] -> /new [200] | final body: you reached /new
  /temp [302] -> /new [200] | final body: you reached /new
  /loop1 [302] -> /loop2 [302] -> /loop1 [302] -> /loop2 [302] -> /loop1 [302] -> /loop2 [302] | GAVE UP after 5 redirects
301 = moved permanently (caches/browsers may remember it); 302 = temporary.
Clients must cap the number of redirects, or a loop never ends.

server stopped: True
```

## Worked Example
**Problem.** (a) A browser has a cached page with `ETag: "abc"` and `max-age=60`. At t=30 s and t=90 s it needs the page again. What happens? (b) A cache has hit ratio 0.6; a hit costs 10 ms, a miss 210 ms. Average delay? (c) How many bytes is the `Content-Length` of `naïve` encoded in UTF-8?

**Solution.** (a) At t=30 s the copy is fresh, so it is used with no network traffic. At t=90 s it is stale, so the browser sends `If-None-Match: "abc"`; if the page is unchanged the server returns 304 with no body and the browser reuses its copy. (b) 0.6 x 10 + 0.4 x 210 = 6 + 84 = 90 ms. (c) 5 characters but `ï` takes 2 bytes, so 6. The program verified the same kind of byte count for `café ☕` (7 characters, 10 bytes) and the 304 flow.

## Key Rules / Gotchas Recap
- `Content-Length` is a byte count of the encoded body, not the number of characters; declare the charset.
- Cookie = session key; the session data lives on the server.
- Session cookie flags: `Secure; HttpOnly; SameSite=Lax` (or Strict).
- `Max-Age=0` deletes a cookie. No expiry means a session cookie.
- `304 Not Modified` has no body; conditional requests use `If-None-Match` (ETag) or `If-Modified-Since`.
- `no-store` never caches; `no-cache` caches but revalidates.
- Cap redirect hops; 301 is cached aggressively by clients, so use it only for permanent moves.
- Add `Vary` when the response depends on a request header.

## Why This Matters
Session handling and caching are where most real web bugs and vulnerabilities live: stolen cookies, CSRF, stale pages, wrong charset, runaway redirects. Any scraper, API client or AI agent that fetches pages must handle cookies, redirects and conditional requests correctly and politely.
