# `scanner.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A TCP connect scanner tries to open a connection to each port on a host; if the connection succeeds, something is listening there. Doing this one port at a time is slow because most waits are idle time, so a thread pool runs many attempts at once. Because scanning other people's machines is illegal, this version refuses every target that is not loopback or private space, before it creates a single socket.

## Full Line-by-Line Breakdown

### Header, imports and constants
- Line 1 is the authorship line; the triple-quoted docstring states the purpose and the legal limit.
- `from __future__ import annotations` lets type hints like `list[int]` and `dict | None` be written freely.
- `MAX_PORTS = 2048`, `MAX_THREADS = 100`, `MAX_TIMEOUT = 5.0` are hard caps. `BANNER_BYTES = 128` and `BANNER_TIMEOUT = 0.3` control banner reading.
- `ALLOWED_NETWORKS` is the whitelist: `127.0.0.0/8`, `::1/128`, `10/8`, `172.16/12`, `192.168/16`, written explicitly rather than using `ip.is_private`, which admits more ranges.

### `ScanError`
A small exception for bad input or refusal. `main` catches it, prints `error: ...` to stderr and returns 2.

### `parse_ports(spec)`
Splits on commas; each part is `N` or `LO-HI`. It rejects empty items, non-numbers, backwards ranges, ports outside 1-65535, and totals above 2048. A `set` removes duplicates and `sorted` returns a list. The early size check inside the loop stops a huge range like `1-65535` from being expanded into memory first. `from None` hides the confusing chained `ValueError`.

### `is_allowed(ip)`
Unwraps IPv4-mapped IPv6 (`::ffff:8.8.8.8` becomes `8.8.8.8`) so it cannot be used to sneak past the check, then tests membership in each whitelisted network of the same IP version.

### `resolve_and_check(target)`
The safety gate. An IP literal is parsed locally with `ipaddress.ip_address` (no DNS). Otherwise `getaddrinfo` resolves the name and **every** returned address must be allowed. It returns the checked IP string, and the scan connects to that IP, never the name, so DNS cannot change the answer later. No socket is created in this function for a literal.

### `grab_banner(sock)`
Sets a 0.3 s timeout and calls `recv(128)`. Silent servers time out and give `""`. Bytes are decoded with `errors="replace"` so garbage becomes `�` instead of crashing, then stripped.

### `scan_port(ip, port, timeout, banner)`
Picks IPv4 or IPv6, creates a socket, sets the timeout, and calls `connect_ex`, which returns an error number (0 = success) instead of raising. If open it returns `{"port", "banner"}`; else `None`. `finally: sock.close()` always releases the socket.

### `scan(...)`
`ThreadPoolExecutor(max_workers=threads)` with `pool.map` runs `scan_port` for each port. The `with` block waits for all workers. Results that are not `None` are sorted by port.

### `build_parser()` and `main(argv)`
`argparse` defines the flags. `main` validates timeout and threads, parses ports, runs the safety gate, and only then calls `scan`. Taking `argv` as a parameter makes `main` testable. Output is text or `json.dumps`. The final `sys.exit(main())` turns the return value into the process exit code.

### Real run (own local servers, OS-assigned ports)
```text
banner server: 48219 silent server: 55599 closed port: 39541

$ python3 scanner.py --ports 48219,55599,39541 --timeout 0.5
Scanning 127.0.0.1 (127.0.0.1): 3 ports, 50 threads, timeout 0.5s
  48219/tcp open  banner: 'SSH-2.0-DemoServer'
  55599/tcp open
2 open, 1 closed/filtered (elapsed 0.302s, a measurement)
exit code: 0

$ python3 scanner.py --ports 48219,55599,39541 --timeout 0.5 --json
{
  "target": "127.0.0.1",
  "resolved": "127.0.0.1",
  "ports_scanned": 3,
  "open": [
    {
      "port": 48219,
      "banner": "SSH-2.0-DemoServer"
    },
    {
      "port": 55599,
      "banner": ""
    }
  ],
  "elapsed_seconds": 0.302
}
exit code: 0

$ python3 scanner.py --ports 48219,55599,39541 --timeout 0.5 --target 8.8.8.8
error: REFUSED: '8.8.8.8' -> 8.8.8.8 is not loopback or private (127.0.0.0/8, ::1, 10/8, 172.16/12, 192.168/16). Only scan machines you own. There is no override.
exit code: 2
```
Why: the banner server sends text on connect, so it is captured; the silent server accepts but says nothing, so its banner is empty; the closed port refuses the connection, so it is not listed. The 8.8.8.8 run never reaches the network.

## Key Differences From Java
| Java | Python |
|---|---|
| `new Socket()` + `socket.connect(new InetSocketAddress(ip, port), timeoutMs)` throws `SocketTimeoutException`/`ConnectException` | `sock.connect_ex((ip, port))` returns 0 or an errno; no exception for a refused port (a `socket.timeout` still applies to `recv`) |
| `ExecutorService pool = Executors.newFixedThreadPool(n)`; submit `Callable`s, collect `Future`s, `shutdown()` | `with ThreadPoolExecutor(max_workers=n) as pool:` and `pool.map(...)`; the `with` block replaces `shutdown()`/`awaitTermination` |
| try-with-resources closes the `Socket` | `try/finally: sock.close()` (a socket also works in a `with` block) |
| `InetAddress.getByName` then checks like `isLoopbackAddress()`/`isSiteLocalAddress()` | `ipaddress` module with explicit network membership |
| `new String(bytes, UTF_8)` silently substitutes bad bytes | `bytes.decode("utf-8", errors="replace")`, explicit |
| Threads run in parallel across cores | CPython threads share the GIL, but this work is I/O waiting, so threads help a lot |
| `public static void main(String[] args)` | `if __name__ == "__main__": sys.exit(main())` |

## Key Rules / Gotchas Recap
- Validate the target BEFORE creating any socket; connect to the checked IP, not the hostname.
- Judge `::ffff:a.b.c.d` as the IPv4 address.
- `connect_ex` returns an error code instead of raising; 0 means open.
- Always close sockets (`finally`) and set timeouts; cap threads, ports and timeout.
- Banner grabbing here is passive; silent or wait-for-client servers show `""`.
- Closed and firewalled ports look the same to a connect scan.
- Ownership of a private IP cannot be checked by code; scan only what is yours.

## Why This Structure Exists
Security tooling must be safe by construction: a whitelist gate, hard caps and no override flag mean a typo cannot turn a practice tool into an attack. The same pattern (thread pool, timeouts, structured JSON output) is used in automation and in testing LLM-backed services you own.
