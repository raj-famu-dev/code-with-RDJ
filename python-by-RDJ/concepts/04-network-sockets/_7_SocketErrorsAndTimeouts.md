# `_7_SocketErrorsAndTimeouts.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Network code fails in ways ordinary code does not: the other side may not exist, may stay silent, may close halfway through a message, or may deliver your data in unexpected pieces. This file demonstrates each failure on loopback and the standard fixes: catch `ConnectionRefusedError`, use timeouts, loop on `recv()` until you have all the bytes, add a **length prefix** to frame messages on a byte stream, set `SO_REUSEADDR` so a restarted server can rebind, and shut down gracefully.

## Full Line-by-Line Breakdown

### SECTION 1: ConnectionRefusedError
The script grabs a free port, closes it, then tries to connect to it. Nobody listens, so the operating system refuses and Python raises `ConnectionRefusedError`, a subclass of `OSError`. The machine answered; there was just no program on that port.

```text
=== SECTION 1: ConnectionRefusedError ===
caught: ConnectionRefusedError
is an OSError subclass: True
Meaning: the machine answered, but no program is listening on that port.

```

### SECTION 2: socket.timeout on recv
A server accepts a connection but says nothing. The client sets `settimeout(0.3)` and calls `recv()`, which raises `socket.timeout` after about 0.3 seconds. (In Python 3.10+ `socket.timeout` is simply another name for the built-in `TimeoutError`, which the output confirms.) The elapsed time line is a **measurement** and varies per machine. Without a timeout, `recv()` would wait forever. An `Event` lets the test release the silent server so threads end cleanly.

```text
=== SECTION 2: socket.timeout on recv ===
caught: TimeoutError | socket.timeout is TimeoutError: True
measurement: waited about 0.3 s (limit was 0.3 s; value varies by machine)
TRAP: without settimeout, recv() on a silent peer blocks forever.

```

### SECTION 3: TRAP - recv() returns PARTIAL data
The server sends `HEL`, waits 0.2 s, then sends `LO`. The client asks `recv(5)` and gets only `b'HEL'`, 3 bytes, even though the whole message is 5. `recv(n)` means "at most n bytes". The fix is a loop that keeps reading until the needed count is reached. The 0.2 s gap makes the short read reliable for the demonstration; on real networks short reads happen unpredictably.

```text
=== SECTION 3: TRAP - recv() returns PARTIAL data ===
naive recv(5) returned: b'HEL' | length: 3 (whole message is 5 bytes)
after looping: b'HELLO'
recv(n) means AT MOST n bytes. Loop until you have what you need.

```

### SECTION 4: framing with a length prefix
Since TCP is a byte stream, the receiver needs a way to know where one message ends. A **length prefix** sends a 4-byte big-endian length (`struct.pack(">I", len)`) followed by the payload. `recv_exact(sock, n)` loops until exactly `n` bytes arrive (raising `ConnectionError` if the peer closes early). `recv_msg` reads 4 bytes, decodes the length, then reads that many bytes. Four messages, including an empty one and a 100,000-byte one, round-trip perfectly.

```text
=== SECTION 4: framing with a length prefix ===
messages sent: [5, 0, 23, 100000]
messages received: [5, 0, 23, 100000]
all identical: True
The prefix restores message boundaries on top of TCP's byte stream.

```

### SECTION 5: peer closes early (EOF mid-message)
A misbehaving server promises 50 bytes, sends 10 and closes. `recv()` returns `b""` (EOF) so `recv_exact` raises `ConnectionError("peer closed after 10 of 50 bytes")`. The note about hostile peers matters: always cap the maximum length you accept, or a sender can claim a huge value and make you allocate memory.

```text
=== SECTION 5: peer closes early (EOF mid-message) ===
caught ConnectionError: peer closed after 10 of 50 bytes
recv() == b'' means the peer closed; treat EOF before the full length as an error.
Also: validate the length field. A hostile peer could claim 4 GB; cap it.

```

### SECTION 6: SO_REUSEADDR
Binding a second socket to a port that is in use raises `OSError` (address already in use). `setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)` **before** `bind` allows a restarted server to rebind while old connections linger in the TCP `TIME_WAIT` state. The script is honest that this particular demo had no lingering connection, so the rebind would probably succeed anyway; the option matters after real client traffic. It does not allow two live listeners on the same port on Linux or macOS (Windows semantics differ).

```text
=== SECTION 6: SO_REUSEADDR ===
second bind on an in-use port -> OSError
rebind after close works with SO_REUSEADDR set; flag value: True
Honest note: no connection sat in TIME_WAIT in this demo, so this rebind would
likely succeed even without the flag; the flag matters after real client traffic.
SO_REUSEADDR lets a restarted server rebind while old connections sit in TIME_WAIT.
It does NOT let two live listeners share a port (on Linux/macOS).

```

### SECTION 7: graceful shutdown
The server sends a goodbye, then calls `shutdown(SHUT_WR)`, which sends a "no more data from me" signal while keeping the socket open for reading. The client sees the data and then EOF (`b""`), half-closes its own side, and closes. The server confirms it saw the client's EOF. `shutdown` signals the end of a direction; `close` releases the file descriptor.

```text
=== SECTION 7: graceful shutdown ===
client reads: b'bye'
then EOF from server: True
server log: got: hello
server log: server saw client EOF: True
shutdown(SHUT_WR) signals EOF but keeps the socket readable; close() releases it.

```

### SECTION 8: always close sockets: use `with`
A socket is a context manager; leaving the `with` block closes it, and `fileno()` becomes `-1`. This is the same safety idea as `with open(...)`.

```text
=== SECTION 8: always close sockets: use `with` ===
inside with, fileno >= 0: True
after with, fileno: -1
All threads joined: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Connection refused | `java.net.ConnectException` | `ConnectionRefusedError` |
| Timeout | `SocketTimeoutException` (a checked `IOException`) | `socket.timeout` / `TimeoutError` (unchecked) |
| EOF | `InputStream.read()` returns `-1` | `recv()` returns `b""` |
| Read exactly N bytes | `DataInputStream.readFully(buf)` or `InputStream.readNBytes(n)` | No built-in for sockets; write `recv_exact` (or use `sock.makefile("rb").read(n)`) |
| Length-prefixed messages | `DataOutputStream.writeInt(len)` + `write(bytes)`; `DataInputStream.readInt()` | `struct.pack(">I", n)` + `sendall`, then `recv_exact` |
| Reuse address | `serverSocket.setReuseAddress(true)` (before bind; the default on many platforms) | `setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)` before `bind` |
| Half-close | `shutdownOutput()` / `shutdownInput()` | `shutdown(SHUT_WR)` / `shutdown(SHUT_RD)` |
| Cleanup | try-with-resources | `with socket.socket() as s:` |
| Error model | Checked exceptions force handling | Exceptions are optional; forgetting a timeout or a `recv` loop causes hangs and bugs instead of compile errors |

## Key Rules / Gotchas Recap

- Set a timeout on every socket and catch `socket.timeout`.
- `recv(n)` returns at most `n` bytes; loop until you have them all.
- `b""` from `recv` means the peer closed; treat EOF in mid-message as an error.
- Frame messages on TCP with a length prefix (or a delimiter), and cap the maximum length.
- Set `SO_REUSEADDR` before `bind` for servers that restart.
- Use `shutdown()` to signal end-of-data and `close()` (or `with`) to release the socket.
- Always join threads you start.

## Why This Structure Exists
Production network code spends most of its time on failure handling: slow peers, dropped connections and partial reads. Length-prefixed framing and strict timeouts are the same techniques used in real protocols, and getting them right is what keeps AI agents, API clients and security tools from hanging or crashing on bad network behaviour.
