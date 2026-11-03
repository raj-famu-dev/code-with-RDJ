# `_9_SocketProgramming.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A socket is the programming interface to the transport layer: a handle your program uses to send and receive data over TCP or UDP. The BSD (Berkeley) sockets API, created in the 1980s and still the basis of every operating system's networking, turns the protocol machinery of the previous topics into a handful of function calls.

**TCP server and client call sequence**

| Step | Server | Client |
|---|---|---|
| 1 | `socket()` creates an endpoint (`AF_INET` = IPv4, `SOCK_STREAM` = TCP) | `socket()` |
| 2 | `bind(ip, port)` attaches a local address (port 0 = OS chooses) | normally no bind: the OS assigns an ephemeral port on connect |
| 3 | `listen(backlog)` makes it a passive socket; the OS now completes handshakes | |
| 4 | `accept()` blocks, then returns a **new** socket for one client | `connect(ip, port)` starts the three-way handshake |
| 5 | `recv()` / `send()` exchange data | `send()` / `recv()` |
| 6 | `close()` sends FIN | `close()` |

The listening socket keeps listening; each `accept()` gives a separate connected socket identified by its 5-tuple (topic 1). UDP is simpler: `socket(SOCK_DGRAM)`, `bind` for a receiver, then `sendto` / `recvfrom`, with no listen, accept or connect.

**`recv` and `send` do not match message boundaries.** `recv(n)` returns *at most* n bytes: whatever the OS has queued, which may be less than a whole message, or pieces of two messages. `recv` returning `b""` means the peer closed the connection (EOF). `send(data)` may accept only part of the data; `sendall` loops until everything is queued. So every real protocol over TCP needs **framing**, a rule for where one message ends:
- **Length prefix:** send a fixed-size length field first (for example 4 bytes, big-endian), then exactly that many bytes. Works for binary data. Always cap the length you will accept.
- **Delimiter:** end each message with a special byte such as a newline (used by many text protocols). Needs escaping if the payload can contain the delimiter.
- **Fixed size:** every message has the same length. Simple, wasteful.

**Handling many clients**
- **Iterative:** one client at a time. Others wait in the backlog.
- **Thread (or process) per client:** simple; each blocking call only blocks its own thread. Costs memory and context switches, and needs locks for shared state.
- **Event loop with `select`/`epoll`/`selectors`:** one thread asks the OS which sockets are ready and handles those. Sockets are non-blocking. Scales to thousands of connections. `asyncio` is a friendlier version of this.

**Blocking, timeouts, non-blocking.** By default calls block forever. `settimeout(t)` makes a call raise `socket.timeout` if nothing happens in `t` seconds: use it always. `setblocking(False)` makes calls return or raise `BlockingIOError` immediately, which you only want together with a selector.

**Good habits:** set `SO_REUSEADDR` before `bind` on servers; close every socket (use `with` or `try/finally`); set timeouts; validate lengths from the network; join your threads; and prefer bind to `127.0.0.1` for local services (binding `0.0.0.0` exposes them to the whole network).

**Typical exam questions:** list the socket calls on the server and client in order; what does `listen`'s backlog mean; why does `accept` return a new socket; what is the difference between `send` and `sendall`; how do you delimit messages over TCP; what is the difference between iterative and concurrent servers; blocking vs non-blocking I/O.

## Full Line-by-Line Breakdown

### SECTION 1: THE BSD SOCKET CALLS IN ORDER
Draws the call sequence, then runs it for real on loopback. `bind((HOST, 0))` gets an OS-chosen port; `listen(5)` starts accepting handshakes; a helper thread calls `accept` while the main thread calls `connect`. The check that `conn.getsockname() == listener.getsockname()` while `conn is not listener` shows that `accept` returned a different socket sharing the same local port. Data goes both ways, then the client closes and the server's `recv` returns `b''`, which is how TCP signals end of stream. Everything is closed.

Output from a real run:

```text
===== SECTION 1: THE BSD SOCKET CALLS IN ORDER =====
  SERVER                              CLIENT
  socket()   create endpoint          socket()   create endpoint
  bind()     attach local ip:port     (no bind: OS picks an ephemeral port)
  listen()   mark as passive, backlog
  accept()   wait; returns NEW socket connect()  3-way handshake (SYN, SYN+ACK, ACK)
  recv()/send()  <------- data ------->  send()/recv()
  close()    send FIN                 close()
1. socket() + bind(('127.0.0.1', 0)) + listen(5): bound to a loopback port chosen by the OS: True
2. connect() returned and accept() returned a DIFFERENT socket for this connection: True
3. server recv: b'hello server'
4. client recv: b'hello client'
5. after client close(), server recv returns b'' (EOF): b''
6. close() on all three sockets (listener, accepted, client). Always close: use try/finally or with.
Python note: socket objects support `with`, which closes them for you.
```

### SECTION 2: TRAP: recv() MAY RETURN PARTIAL DATA
A sender thread sends the first 4 bytes of a 10-byte message, pauses 0.15 s, then sends the remaining 6 and later a 5000-byte block. The client's `recv(10)` returns only `b'0123'`: that is the trap. `recv_exact(sock, n)` loops, asking for the remaining `n - len(buf)` bytes each time, and treats an empty read as an error (peer closed before the full message). The second experiment reads 5000 bytes with `recv(1000)` and checks that it needed at least five calls and that no chunk exceeded 1000 bytes. The final read shows `b''` at end of stream. `TCP_NODELAY` is set on the sender only so the first four bytes leave immediately (see topic 6).

Output from a real run:

```text
===== SECTION 2: TRAP: recv() MAY RETURN PARTIAL DATA =====
message is 10 bytes; recv(10) returned: b'0123' (4 bytes, not 10!)
TRAP: recv(n) returns AT MOST n bytes, whatever is available. Never assume it is a whole message.
fix: recv_exact loop collected the rest: b'456789' -> full message: b'0123456789'
reading 5000 bytes with recv(1000) needed at least 5 calls: True, every chunk <= 1000: True
end of stream: recv returns b'': b''
The same is true for send(): it may accept only part of the data. sendall() loops for you.
```

### SECTION 3: LENGTH-PREFIXED MESSAGE PROTOCOL
The framing layer: `LEN = struct.Struct("!I")` is a 4-byte unsigned big-endian length, `send_msg` writes length + payload with one `sendall`, and `recv_msg` reads exactly 4 header bytes, validates the length against `MAX_MSG`, then reads exactly that many payload bytes. First the delimiter pitfall is shown on `b'line1\nline2'`, which would be cut into two messages. Then a real echo thread round-trips five messages, including an empty one, all 256 byte values, and 100,000 bytes. A message sent one byte per `send` still arrives as one message, and two messages written in a single `send` are read as two, which proves the framing is independent of how TCP chops the stream. The last trap hands `recv_msg` a header that claims 4,000,000,000 bytes (through a tiny fake object, so no network is needed): the limit check rejects it before any allocation.

Output from a real run:

```text
===== SECTION 3: LENGTH-PREFIXED MESSAGE PROTOCOL =====
wire format: [4-byte big-endian length][payload]. Example for b'hi': 00 00 00 02 68 69
Why not a newline delimiter? Payloads may contain newlines:
  delimiter split of b'line1\nline2' -> [b'line1', b'line2'] (two messages: WRONG)
  length-prefixed keeps it as ONE message of 11 bytes.
round trip of [2, 0, 11, 256, 100000] byte messages (incl. empty and binary): True
a message dribbled one byte per send is still read as one message: b'slow but safe'
two messages in one send are read as two: b'one' b'two'
hostile header claiming 4 GB is rejected: message length 4000000000 exceeds limit 1000000
TRAP: skipping the MAX_MSG check lets one malicious 4-byte header make you allocate gigabytes.
```

### SECTION 4: THREADED MULTI-CLIENT ECHO SERVER
`EchoServer` binds `127.0.0.1` port 0 with a 0.2 s accept timeout so the acceptor thread can see the `stop` event. Each accepted connection gets a worker thread. A worker waits for readability with `select` in 0.2 s slices (so it can notice shutdown while idle), then sets a 2 s timeout for the message itself, so a client that stalls mid-message cannot hold the thread forever. `QUIT` gets `BYE`; everything else is returned in upper case. Counters guarded by a `Lock` record how many clients were active at once. Four client threads connect, wait on a `threading.Barrier` so all four are connected at the same moment (which is why the server's maximum concurrency is exactly 4), exchange three messages and quit. Each client's replies are checked against what it sent. `shutdown()` sets the flag, joins the acceptor, closes the listening socket, and joins every worker; the final assert confirms no threads are left and 12 messages were echoed.

Output from a real run:

```text
===== SECTION 4: THREADED MULTI-CLIENT ECHO SERVER =====
server started on an OS-chosen loopback port; acceptor thread + one worker thread per client
  client 0 got: ['CLIENT 0 MSG 0', 'CLIENT 0 MSG 1', 'CLIENT 0 MSG 2', 'BYE']
  client 1 got: ['CLIENT 1 MSG 0', 'CLIENT 1 MSG 1', 'CLIENT 1 MSG 2', 'BYE']
  client 2 got: ['CLIENT 2 MSG 0', 'CLIENT 2 MSG 1', 'CLIENT 2 MSG 2', 'BYE']
  client 3 got: ['CLIENT 3 MSG 0', 'CLIENT 3 MSG 1', 'CLIENT 3 MSG 2', 'BYE']
check: every client received only its own uppercase replies, then BYE: OK
server saw 4 clients connected at the same time (barrier forced 4): True
messages echoed: 12
clean shutdown: stop flag set, acceptor joined, listening socket closed, workers joined;
threads still alive: 0
Design notes: SO_REUSEADDR set, port 0, short accept timeout so the loop can stop,
select() before each message so idle workers can stop, and a per-message timeout so a
stalled client cannot hold a thread forever (a slowloris-style resource hog).
```

### SECTION 5: BLOCKING VS NON-BLOCKING VS SELECTORS
A comparison table, then two tiny experiments on a throwaway connection: with `settimeout(0.2)` an empty `recv` raises `socket.timeout` after 0.2 s; with `setblocking(False)` it raises `BlockingIOError` at once. The main demo is a single-threaded event loop using `selectors.DefaultSelector`: the listening socket and each accepted connection are registered for read events, and `select(timeout=0.1)` returns only sockets that are ready. Three clients connect and send; the one loop thread accepts all of them and echoes in upper case. The program records the thread identifiers that handled events and asserts there was exactly one. Note that the loop uses `send` for a tiny reply; a production server must handle partial sends by buffering. The stop flag, join, and closing of the selector and sockets finish the run cleanly.

Output from a real run:

```text
===== SECTION 5: BLOCKING VS NON-BLOCKING VS SELECTORS =====
  mode                call behaviour                        scales by
  blocking            recv/accept wait until ready          one thread per connection (simple;
                                                            threads cost memory)
  timeout             blocking, but raises socket.timeout   same, but can give up (use this by default)
  non-blocking        returns at once or raises             you must poll...
                      BlockingIOError
  selectors/epoll     ONE thread asks the OS 'which sockets  event loop; thousands of connections
                      are ready?' then handles only those    (asyncio is built on this idea)
timeout mode: recv with no data raised socket.timeout after 0.2 s (TimeoutError in 3.10+)
non-blocking mode: recv with no data raised BlockingIOError immediately (no waiting)
selector server replies: ['HELLO FROM 0', 'HELLO FROM 1', 'HELLO FROM 2']
3 clients served by 1 thread (the event loop); echoes: 3
check: one thread, three concurrent connections: OK
Python's asyncio, Node.js, nginx and most modern servers are event loops like this.
Rule of thumb: threads for simplicity and small scale; selectors/asyncio when connections
number in the thousands and mostly idle.
```

## Worked Example
**Problem.** Design the protocol and receive code for a client that sends the messages `"HI"` (2 bytes) and `"GOODBYE"` (7 bytes) one right after the other over TCP. The receiver calls `recv(1024)` once and gets 17 bytes. Using a 4-byte length prefix, show the 17 bytes, and explain how the receiver recovers the two messages.

**Solution.**
1. Message 1 on the wire: `00 00 00 02` + `48 49` = 6 bytes. Message 2: `00 00 00 07` + `47 4f 4f 44 42 59 45` = 11 bytes. Total 6 + 11 = 17 bytes, in one `recv` (TCP merged them).
2. The receiver reads the first 4 bytes: length = 2. It takes the next 2 bytes: `HI`.
3. Next 4 bytes: length = 7; next 7 bytes: `GOODBYE`.
4. If instead `recv` had returned only 9 bytes, the loop would decode `HI` (6 bytes), find only 3 of message 2's 4 header bytes, and call `recv` again for the missing 1 byte and then the payload: the same code works for any chunking because it always asks for exactly the number of bytes it still needs.

Section 3 of the code performs exactly this on real sockets, including the case of two messages in one `send` and a message dribbled one byte at a time.

## Key Rules / Gotchas Recap
- Server order: `socket`, `bind`, `listen`, `accept`, `recv`/`send`, `close`. Client order: `socket`, `connect`, `send`/`recv`, `close`.
- `accept` returns a new socket; the listening socket stays open.
- `recv(n)` returns at most n bytes; `b""` means the peer closed. Loop with a `recv_exact` helper.
- `send` may be partial; use `sendall`.
- TCP has no message boundaries: add framing (length prefix is the safest for binary data) and cap the length.
- Always `settimeout`, set `SO_REUSEADDR` on servers, and close/join everything.
- Bind to 127.0.0.1 for local services; port 0 for tests.
- Shared counters across threads need a lock.
- Non-blocking sockets only make sense with a selector or event loop.

## Why This Matters
Every client library, web server and model-serving endpoint is built on these calls, and "it works on my machine but hangs in production" is usually a missing timeout, a half-read message or a leaked socket. A length-prefixed protocol is the same idea gRPC, Redis-style protocols and most binary RPC systems use, and writing one by hand once makes their behaviour and failure modes predictable.
