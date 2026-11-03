# `_7_LoopbackSocketsPosix.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A socket is an operating-system handle for network communication. With POSIX sockets you create one with `socket()`, a server then `bind`s, `listen`s and `accept`s, and a client `connect`s; both sides use `send` / `recv` and finally `close`. TCP is a stream of bytes, not a series of messages, so you need loops for partial reads and writes. This file runs a TCP echo server and client in one process on 127.0.0.1 only (the loopback interface; nothing leaves your machine), using port 0 so the OS picks a free port. Compile with `-pthread`.

## Full Line-by-Line Breakdown

### SECTION 1: LISTEN ON PORT 0 AND LEARN THE PORT
`make_listener()` creates a TCP socket (`AF_INET`, `SOCK_STREAM`), binds it to `INADDR_LOOPBACK` (127.0.0.1) with port 0, and calls `listen`. Binding to loopback means only programs on this machine can connect. Port 0 asks the OS for any free port, and `getsockname()` returns the port that was actually assigned, so there is no hard-coded port and no clash with other programs. The actual number differs each run, so the program prints only that it is nonzero. An `Fd` RAII class wraps the descriptor so `close()` is called exactly once, on every exit path. The echo server then runs on a second thread of this same process via `std::async`.

Output from a real run:

```text
===== SECTION 1: LISTEN ON PORT 0 AND LEARN THE PORT =====
bound to 127.0.0.1 with port 0; the OS chose a port; getsockname says it is nonzero: true
(the actual port number differs every run, so it is not printed)
```

### SECTION 2: ECHO ROUND TRIP
The client connects to the learned port and sends three messages. The server thread `recv`s whatever bytes arrive and `send`s the same bytes back. Because TCP gives no message boundaries, the client reads back exactly `msg.size()` bytes with `recv_exact()`, which loops until the count is reached. `send_all()` loops because `send` may accept fewer bytes than requested, and uses `MSG_NOSIGNAL` so a closed peer gives an error instead of killing the process with SIGPIPE. When done, `shutdown(fd, SHUT_WR)` says "I will send no more" (a half-close); the server sees `recv` return 0 (end of stream), finishes, and closes its side, which makes the client's `recv_until_eof()` see EOF too.

Output from a real run:

```text
===== SECTION 2: ECHO ROUND TRIP =====
sent "hello" -> echoed "hello" matches: true
sent "second message" -> echoed "second message" matches: true
sent "RDJ" -> echoed "RDJ" matches: true
after shutdown(SHUT_WR), recv returns EOF: true
```

### SECTION 3: TCP IS A BYTE STREAM, NOT MESSAGES
The client does three separate `send`s of "AAAA", "BBBB", "CCCC" and then reads one continuous stream back: 12 bytes `AAAABBBBCCCC`. The data is the same, but no promise says one `recv` returns one `send`; the three writes could arrive merged or split. (This is why the demo reads until EOF instead of counting messages, which keeps the output deterministic.) Real protocols add a length prefix or a delimiter. After the second connection ends, the server thread returns and `server_result.get()` gives an empty error string, which confirms both connections were served without errors.

Output from a real run:

```text
===== SECTION 3: TCP IS A BYTE STREAM, NOT MESSAGES =====
3 sends of 4 bytes came back as a stream of 12 bytes: AAAABBBBCCCC
TRAP: one recv() is NOT one send(). Message boundaries are not preserved, so real protocols add a
      length prefix or a delimiter, and loops like recv_exact() / send_all() handle partial reads and writes.
echo server finished both connections; error: ""
```

### SECTION 4: RECEIVE TIMEOUT WITH SO_RCVTIMEO
A second listener is created, and the client connects to it. The kernel completes the TCP handshake from the listen backlog even though nobody calls `accept`, and the silent "server" never sends. `setsockopt(SOL_SOCKET, SO_RCVTIMEO, 150 ms)` sets a receive timeout, so `recv` gives up with `-1` and `errno` of `EAGAIN` / `EWOULDBLOCK` instead of blocking forever. This is how you stop one dead peer from freezing a thread. (The timeout is 150 ms, but the program prints only whether the error was the timeout, not any measured time.)

Output from a real run:

```text
===== SECTION 4: RECEIVE TIMEOUT WITH SO_RCVTIMEO =====
recv() on a silent peer with a 150 ms timeout returned -1 with EAGAIN/EWOULDBLOCK: true
(without SO_RCVTIMEO this recv() would block forever)
```

### SECTION 5: CONNECTION REFUSED AND close()
A listener is created and immediately closed, leaving a port where nothing listens. Connecting to it on loopback fails with `ECONNREFUSED`; `strerror` gives `Connection refused`. The closing note repeats the difference: `close(fd)` releases the descriptor, while `shutdown(fd, how)` ends one or both directions but leaves the descriptor open (so you can still read the remaining data after `SHUT_WR`). TRAPS: leaking descriptors (the `Fd` class prevents it), and SIGPIPE when writing to a socket the peer closed (avoided with `MSG_NOSIGNAL`).

Output from a real run:

```text
===== SECTION 5: CONNECTION REFUSED AND close() =====
connecting to a closed loopback port failed: connect: Connection refused
close(fd) releases the descriptor; shutdown(fd, how) ends one or both directions but keeps the fd open.
TRAP: forgetting close() leaks descriptors (a process only gets a limited number); the Fd class prevents it.
TRAP: writing to a socket the peer already closed raises SIGPIPE and kills the process; MSG_NOSIGNAL turns it into an EPIPE error.
```

## Key Differences From Java
| Java (`java.net`) | Python (`socket`) | C++ (POSIX) |
|---|---|---|
| `new ServerSocket(0, 50, InetAddress.getLoopbackAddress())`; `getLocalPort()` | `s.bind(("127.0.0.1", 0)); s.getsockname()[1]` | `bind()` with `sin_port = 0`; `getsockname()` |
| `serverSocket.accept()` returns a `Socket` | `conn, addr = s.accept()` | `accept()` returns an `int` descriptor |
| `socket.setSoTimeout(150)`; throws `SocketTimeoutException` | `s.settimeout(0.15)`; raises `socket.timeout` | `SO_RCVTIMEO`; `recv` returns -1 with `EAGAIN` |
| `socket.shutdownOutput()` | `s.shutdown(socket.SHUT_WR)` | `shutdown(fd, SHUT_WR)` |
| try-with-resources closes the socket. | `with socket.socket() as s:` closes it. | Your RAII class (`Fd`) must call `close()`; nothing does it for you. |
| `InputStream.read` returns -1 at EOF; exceptions on errors. | `recv` returns `b""` at EOF; exceptions on errors. | `recv` returns 0 at EOF and -1 on error with `errno`; no exceptions, you check every call. |
| `sendall` equivalent: `OutputStream.write` writes everything. | `s.sendall(data)` | You must loop yourself (`send_all`). |

C++ has no standard networking library yet; POSIX sockets are the platform API (Windows uses Winsock, with differences). Higher-level libraries (Boost.Asio, etc.) wrap this.

## Key Rules / Gotchas Recap
- Bind to 127.0.0.1 for local-only demos and tests; port 0 plus `getsockname()` avoids hard-coded ports.
- TCP is a byte stream: `recv` may return fewer bytes than sent or merge messages; loop and frame your data.
- `send` can write fewer bytes than asked; loop (`send_all`).
- `recv` returns 0 for orderly close, -1 for an error (check `errno`).
- Always handle `EINTR` and set timeouts so a silent peer cannot block you forever.
- Close every descriptor (use RAII); `shutdown` for a half-close, `close` to release.
- Use `MSG_NOSIGNAL` (or ignore SIGPIPE) when writing to sockets.
- Only run network demos against machines and ports you own.

## Why This Structure Exists
Servers for AI models and tools are network programs, and security tooling (scanners, proxies, protocol tests) speaks sockets directly. Knowing partial reads, timeouts, descriptor lifetime and byte-stream framing is the foundation under every web framework and is exactly where network-facing bugs appear. Keeping the demo on loopback means you learn it safely, on a machine and port you control.
