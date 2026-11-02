> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# HttpClient (Java 11+)

## Concept

`java.net.http.HttpClient` makes HTTP requests without a library. The roadmap asked for "call a public REST API"; this file instead starts a tiny HTTP server on **this machine's loopback address** (free port, nothing external can connect) and calls that. The client code is exactly what you would use against a real API, only the URL changes, and the program works offline and gives the same output every run.

## Full Line-by-Line Breakdown

**`startServer()`** uses the JDK's built-in `com.sun.net.httpserver.HttpServer` with three endpoints: `/users/1` (JSON), `/echo` (returns what it received, status 201), `/slow` (sleeps 1.5 s).

**Section 1: the client.** Immutable, thread-safe, holds a connection pool: **build one and share it**. Always set `connectTimeout`.

**Section 2: GET.** A request is built with a builder (URL, header, per-request `timeout`); the response has a status, headers and a body whose type comes from the `BodyHandler`:

```
status:       200
content-type: application/json
body:         {"id": 1, "name": "Ada Lovelace", "city": "London"}
parsed name:  Ada Lovelace, city: London
```

The "parser" is a tiny regex for one flat field. For real JSON use Jackson.

**Section 3: POST.** `BodyPublishers.ofString("hello server")`: `POST status 201: server received POST: hello server`.

**Section 4: status codes are not exceptions.** A 404 is a normal response, `send()` does not throw: `missing path -> status 404`. Your code must decide what a non-2xx response means.

**Section 5: timeouts.** The `/slow` endpoint with a 300 ms limit throws `HttpTimeoutException`. Without a timeout a slow server can block your thread for a very long time.

**Section 6: async.** `sendAsync` returns a `CompletableFuture` (see `05` and `08`); three requests in parallel: `[A:200, B:200, C:201]`.

**Section 7: rules.** One shared client; timeouts; check `statusCode()`; handle `IOException` and `InterruptedException`; never put API keys in source (use environment variables); a real API is the same code with another URL.

## Key Rules

1. Build one `HttpClient` and reuse it.
2. Set a connect timeout and a request timeout.
3. Check the status code yourself.
4. Keep secrets out of source code.
5. `server.stop(0)` in `finally`.

## Gotchas Recap

- Forgetting timeouts is the classic production outage.
- `send()` blocks; use `sendAsync` for concurrency.
- Parsing JSON with regex only works for toy data.

## Why This Structure Exists

A local server removes the network from the lesson, so a failure always means your client code and never the Wi-Fi.
