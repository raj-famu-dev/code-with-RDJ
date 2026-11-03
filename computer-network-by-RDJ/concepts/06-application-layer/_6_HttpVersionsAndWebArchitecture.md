# `_6_HttpVersionsAndWebArchitecture.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
HTTP has been revised several times to make pages load faster over the same Internet: HTTP/1.0 opened a new TCP connection for every object, HTTP/1.1 reused connections, HTTP/2 multiplexed many requests over one connection, and HTTP/3 moved the whole thing onto QUIC (over UDP) to avoid TCP's weaknesses. Around the protocol sits web architecture: proxies, load balancers and content delivery networks (CDNs) that cache and distribute traffic, and REST, the design style for web APIs.

**HTTP/1.0 vs 1.1.** In HTTP/1.0 (non-persistent) every request needs a new TCP connection: 1 RTT for the handshake plus 1 RTT for the request and response, so each object costs 2 RTT plus transmission time. HTTP/1.1 made connections persistent by default (the server leaves it open; `Connection: close` ends it), mandated the `Host` header, added chunked transfer and more caching controls. Browsers also open several parallel connections (often about 6 per host). Pipelining lets a client send several requests without waiting for replies, but responses must return in order, so one slow response blocks the rest (head-of-line blocking at the application level). Pipelining proved buggy with proxies and is switched off in browsers.

Textbook formulae for a page with 1 base file and m objects (ignoring transmission time):
- non-persistent, serial: 2(m + 1) RTT;
- non-persistent with k parallel connections: 2 RTT for the base + 2 x ceil(m / k) RTT;
- persistent without pipelining: 1 RTT handshake + (m + 1) RTT;
- persistent with pipelining: 1 handshake + 1 (base) + 1 (all objects) = 3 RTT.

**HTTP/2 (RFC 9113).** Binary framing instead of text; one TCP connection carries many independent streams, so many requests and responses are interleaved (multiplexing); HPACK (RFC 7541) compresses repeated headers using static and dynamic tables; stream priorities exist. It fixes application-level head-of-line blocking but all streams still share one TCP byte stream, so one lost packet stalls every stream until it is retransmitted (TCP-level head-of-line blocking). Server push (the server sending resources unasked) was part of the design but proved hard to benefit from; Chrome removed support in 2022 and it is rarely used.

**HTTP/3 (RFC 9114) over QUIC (RFC 9000).** QUIC runs over UDP and builds in its own reliability, congestion control and TLS 1.3 encryption. Streams are independent: a lost packet delays only the stream it belongs to. The handshake is faster (1 RTT for a new connection and possibly 0 RTT when resuming), and a connection survives a change of IP address (connection migration, useful on phones). Header compression is QPACK (RFC 9204). Some networks block or throttle UDP, so clients fall back to HTTP/2.

**Intermediaries.**
- Forward proxy: sits near the client; caches, filters and can hide the client address.
- Reverse proxy: sits in front of servers; terminates TLS, caches, compresses and forwards to back-ends.
- Load balancer: spreads requests over several servers (round-robin, least connections, hashing for stickiness) and removes unhealthy ones.
- CDN: a global network of reverse-proxy caches near users; popular content is served from the edge, lowering latency and origin load.
Layering these is exactly what REST's "layered system" constraint allows.

**Web caching and hit ratio.** With hit ratio h, hit time T_hit and miss time T_miss, the average delay is h x T_hit + (1 - h) x T_miss. Hit ratio rises with cache size, but with diminishing returns because popularity is skewed (a few objects get most requests, a Zipf-like distribution).

**REST (Representational State Transfer).** An architectural style for web APIs: resources identified by URLs (nouns, `/api/books/2`), manipulated through the standard HTTP methods, exchanged as representations (usually JSON), stateless requests (each carries all it needs, so any server can answer and caches work), cacheable responses, a uniform interface (including links between resources, called HATEOAS) and a layered system. Proper status codes (201 + `Location` on create, 204 on delete, 404, 400) are part of the contract.

**Typical exam questions.** Compute the time to fetch a page under non-persistent, persistent and pipelined HTTP. Compare HTTP/1.1, HTTP/2 and HTTP/3. What is head-of-line blocking and which versions have which kind? What does a reverse proxy do? Average delay with cache hit ratio. What makes an API RESTful?

## Full Line-by-Line Breakdown

### SECTION 1: HTTP/1.0 VS HTTP/1.1 - COUNTING ROUND TRIPS
The table is computed with the formulae above: 11 objects, 5 parallel connections, 100 ms RTT. The assertions check the textbook values 22 and 3 RTT. Then a REAL measurement: a loopback server counts TCP connections in `setup`, which runs once per accepted connection. Five requests through one `HTTPConnection` use 1 connection (HTTP/1.1 persistence). Five requests each sent with `Connection: close` use 5 connections. Only counts are claimed, not timings, because loopback has almost no latency.

Output from a real run:

```text
===== SECTION 1: HTTP/1.0 VS HTTP/1.1 - COUNTING ROUND TRIPS =====
Page = 1 base HTML + 10 images (11 objects). RTT = 100 ms. Object transmission
time is ignored so only round trips are counted (textbook model).
model                                     RTTs     time
HTTP/1.0 non-persistent, serial             22   2200 ms
HTTP/1.0 non-persistent, 5 parallel          6    600 ms
HTTP/1.1 persistent, no pipelining          12   1200 ms
HTTP/1.1 persistent + pipelining             3    300 ms
check: OK (22 / 6 / 12 / 3 round trips)

Real measurement on loopback: 5 requests, count TCP connections the server accepted.
persistent connection     : 1 TCP connection for 5 requests
one connection per request: 5 TCP connections for 5 requests
check: OK (each extra connection costs a handshake, and TCP slow start restarts)
```

### SECTION 2: HTTP/2 AND HTTP/3
A comparison table of the three versions (RFC numbers are correct as of RFC 9110-series from 2022), a note on server push, and a table of round trips before the first request can be sent (TCP 1, TCP + TLS 1.2 3, TCP + TLS 1.3 2, QUIC 1, QUIC resumption 0). The last part is a TOY header-compression demo: it remembers `(name, value)` pairs it has sent and replaces repeats with a 1-byte index. It is not HPACK, only the same idea of a shared dynamic table; five requests drop from 540 to 116 bytes.

Output from a real run:

```text
===== SECTION 2: HTTP/2 AND HTTP/3 =====
              HTTP/1.1          HTTP/2              HTTP/3
RFC           9112              9113                9114 (+ QUIC 9000)
format        text              binary frames       binary frames
transport     TCP               TCP (+TLS)          QUIC over UDP
concurrency   1 req at a time   many streams        many streams
headers       repeated text     HPACK compressed    QPACK compressed
HOL blocking  yes (app)         TCP level only      per stream only
encryption    optional          usual (browsers)    always (TLS 1.3)
HTTP/2 server push: the server could send resources before they were requested.
It proved hard to use well; Chrome removed support in 2022 and it is rarely used,
so treat it as a historical feature, not a performance tool.

Round trips before the client can send its first request:
  TCP only (plain http)         1 RTT = 100 ms at RTT 100 ms
  TCP + TLS 1.2                 3 RTT = 300 ms at RTT 100 ms
  TCP + TLS 1.3                 2 RTT = 200 ms at RTT 100 ms
  QUIC (HTTP/3), first visit    1 RTT = 100 ms at RTT 100 ms
  QUIC with 0-RTT resumption    0 RTT = 0 ms at RTT 100 ms

Toy header compression (NOT real HPACK; shows the idea of a dynamic table):
  request 1: text headers 108 bytes, toy-compressed 100 bytes
  request 2: text headers 108 bytes, toy-compressed 4 bytes
  request 3: text headers 108 bytes, toy-compressed 4 bytes
  request 4: text headers 108 bytes, toy-compressed 4 bytes
  request 5: text headers 108 bytes, toy-compressed 4 bytes
  five requests: 540 bytes vs 116 bytes
```

### SECTION 3: HEAD-OF-LINE BLOCKING SIMULATION
Three responses A (6 packets), B (2) and C (2) share one path that sends one packet per time unit. `serial_order` is HTTP/1.1 (A fully, then B, then C); `round_robin_order` interleaves (HTTP/2 and 3). `finish_times` computes when each response completes. Loss: packet A2 arrives 10 units late (the retransmission). Two delivery rules: "connection" (TCP) delivers strictly in order across the whole connection, so any late packet holds back every later packet of every stream; "stream" (QUIC) keeps order only inside a stream.

Reading the table: with no loss, HTTP/1.1 finishes (A, B, C) at (6, 8, 10), so small B waits behind big A, while multiplexing gives (10, 5, 6): B and C finish early. With A2 lost, HTTP/2 over TCP drags everything to 14 (B and C did nothing wrong), while QUIC keeps B and C at 5 and 6 and only A suffers. This is a model with abstract time units, not a benchmark of any real implementation.

Output from a real run:

```text
===== SECTION 3: HEAD-OF-LINE BLOCKING SIMULATION =====
3 responses A (6 packets), B (2), C (2). One packet is sent per time unit.
Loss: packet A2 is lost; recovery costs 10 extra units (abstract RTO).
                                  no loss (A,B,C)     A2 lost (A,B,C)
HTTP/1.1 one TCP conn, in order   (6, 8, 10)          (12, 12, 12)
HTTP/2 multiplexed over TCP       (10, 5, 6)          (14, 14, 14)
HTTP/3 multiplexed over QUIC      (10, 5, 6)          (14, 5, 6)
Read it: (1) without loss, HTTP/1.1 makes B wait for all of A (app-level HOL);
(2) HTTP/2 fixes that by interleaving, but one lost TCP packet stalls ALL streams;
(3) QUIC delays only the stream that lost the packet (B and C unaffected).
check: OK
```

### SECTION 4: PROXIES, REVERSE PROXIES, LOAD BALANCERS, CDNs
An ASCII picture of the two proxy placements and a comparison of two balancing policies for eight requests: round-robin simply rotates over app1..app3, so alice reaches different servers; the sticky policy hashes the client name (with a stable sum of character codes, because Python's built-in `hash()` of strings changes between runs) so alice always reaches app1. Sticky is useful when session data lives in a server's memory; the better design is to keep sessions in a shared store.

Output from a real run:

```text
===== SECTION 4: PROXIES, REVERSE PROXIES, LOAD BALANCERS, CDNs =====
  forward proxy (client side)        reverse proxy / load balancer (server side)
  browser -> [proxy] -> Internet     Internet -> [reverse proxy] -> app1
  (cache, filter, hide client IP)                               \-> app2   (spread load, TLS, cache)
  CDN: many reverse-proxy caches near users, copies of popular content ("edge")
Round-robin vs hash-by-client (sticky) for 8 requests:
  client  round-robin  sticky
  alice   app1         app1
  bob     app2         app2
  alice   app3         app1
  carol   app1         app2
  alice   app2         app1
  bob     app3         app2
  dave    app1         app3
  alice   app2         app1
  Sticky keeps one client on one backend (useful when sessions live in memory).
  Round-robin balances evenly but the same client may hit different servers.
```

### SECTION 5: WEB CACHE HIT-RATIO SIMULATION
20000 requests drawn with `random.Random(42)` over 200 objects with weights 1/rank (a few hot objects, a long tail). An LRU cache (an `OrderedDict`; most recent at the end, evict from the front) of different sizes processes the same request list. The hit ratio grows with cache size: caching only 5 of 200 objects already serves about one request in five, and half the catalogue gives about 83 percent. Average delay is computed with the formula. These are results of this synthetic workload, not claims about real web traffic.

Output from a real run:

```text
===== SECTION 5: WEB CACHE HIT-RATIO SIMULATION =====
20000 requests over 200 objects, popularity ~ 1/rank (seed 42). LRU cache.
hit costs 10 ms, miss costs 210 ms. avg = h*10 + (1-h)*210
 cache size  hit ratio  avg delay
          0      0.000   210.0 ms
          5      0.194   171.3 ms
         20      0.462   117.5 ms
         50      0.665    76.9 ms
        100      0.827    44.6 ms
These numbers come from this synthetic workload only; real traffic differs.
```

### SECTION 6: REST PRINCIPLES AND A JSON API
The same loopback server exposes `/api/books`. The client sequence: list; create a book (201 plus `Location: /api/books/2`); create without a title (400); read the book (the JSON includes `links`, the hypermedia part); replace it with PUT; delete book 1 (204, no body); delete it again (404); list the final state. Each request is self-contained, so the server keeps no session for the client: that is REST's statelessness.

Output from a real run:

```text
===== SECTION 6: REST PRINCIPLES AND A JSON API =====
REST constraints: client-server, stateless requests, cacheable responses,
uniform interface (resources named by URL, standard methods, representations
like JSON, links), layered system (proxies/CDNs), optional code on demand.
  GET    /api/books      -> 200 OK [{"id": 1, "title": "Networks", "year": 2020}]
  POST   /api/books      -> 201 Created Location=/api/books/2 {"id": 2}
  POST   /api/books      -> 400 Bad Request {"error": "title is required"}
  GET    /api/books/2    -> 200 OK {"id": 2, "title": "TCP/IP Illustrated", "year": 1994, "links": {"self": "/api/books/2", "collection": "/api/books"}}
  PUT    /api/books/2    -> 200 OK {"id": 2, "title": "TCP/IP Illustrated, Vol. 1", "year": 2011}
  DELETE /api/books/1    -> 204 No Content 
  DELETE /api/books/1    -> 404 Not Found {"error": "no such book"}
  GET    /api/books      -> 200 OK [{"id": 2, "title": "TCP/IP Illustrated, Vol. 1", "year": 2011}]
Nouns in URLs (/api/books/2), verbs are the HTTP methods, codes carry the result.

server stopped: True
```

## Worked Example
**Problem.** A page has 1 HTML file and 8 images. RTT = 50 ms. Find the load time (ignore transmission time) for (a) non-persistent HTTP with no parallelism, (b) non-persistent with 4 parallel connections for the images, (c) persistent HTTP without pipelining, (d) persistent with pipelining. Also, a cache has hit ratio 0.7, hit time 5 ms, miss time 105 ms: average delay?

**Solution.** (a) 9 objects x 2 RTT = 18 RTT = 900 ms. (b) base 2 RTT + 2 x ceil(8/4) = 2 + 4 = 6 RTT = 300 ms. (c) 1 + 9 = 10 RTT = 500 ms. (d) 1 + 1 + 1 = 3 RTT = 150 ms. Cache: 0.7 x 5 + 0.3 x 105 = 3.5 + 31.5 = 35 ms. The same formulae in the code gave 22, 6, 12 and 3 RTT for 11 objects and 5 parallel connections.

## Key Rules / Gotchas Recap
- Non-persistent: 2 RTT per object (TCP handshake + request); persistent: handshake once.
- HTTP/1.1 head-of-line blocking is per connection at the application level; HTTP/2 has it at the TCP level; HTTP/3 (QUIC) only per stream.
- HTTP/2 is binary, multiplexed, HPACK; HTTP/3 is HTTP over QUIC over UDP, encrypted with TLS 1.3.
- Server push is effectively dead; do not rely on it.
- Average delay = h x T_hit + (1 - h) x T_miss.
- Forward proxy serves clients; reverse proxy and load balancer serve servers; a CDN is many reverse-proxy caches.
- REST: nouns in URLs, verbs are HTTP methods, stateless, proper status codes.
- Never use Python's `hash()` for stickiness across restarts (it is randomised per process).

## Why This Matters
Latency work (connection reuse, CDN, caching, HTTP/2 or 3) is a big part of making APIs and model-serving endpoints feel fast, and load balancers and reverse proxies are standard in every deployment. REST design is the everyday format of services you will build and call.
