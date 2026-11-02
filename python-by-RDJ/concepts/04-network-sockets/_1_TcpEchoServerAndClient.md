# `_1_TcpEchoServerAndClient.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
TCP is the reliable, ordered, connection-based transport underneath HTTP, SSH and most internet services. A **server** creates a socket, binds it to an address and port, listens, and accepts connections; a **client** creates a socket and connects. After that both sides exchange **bytes** with `sendall()` and `recv()`. This file builds the smallest complete example, an echo server running in a background thread, entirely on the loopback address `127.0.0.1`, so nothing ever leaves your computer.

## Full Line-by-Line Breakdown

Safety conventions used in every networking file here: only `127.0.0.1`, port `0` (the OS chooses a free port, so there are never conflicts), a timeout on every socket, and every thread is joined and every socket closed.

### SECTION 1: the server side (bind, listen)
`socket.socket(AF_INET, SOCK_STREAM)` creates an IPv4 (`AF_INET`) TCP (`SOCK_STREAM`) socket. `settimeout(5)` makes blocking calls raise `socket.timeout` instead of waiting forever. `bind(("127.0.0.1", 0))` attaches the socket to loopback; port `0` asks the OS for any free port, which `getsockname()` then reveals. `listen(1)` turns it into a listening socket with a queue for incoming connections. `echo_once()` runs in a thread: `accept()` blocks until a client connects and returns a **new** socket for that client plus its address, then a loop calls `recv(1024)` and answers with `sendall(data.upper())`. When `recv` returns `b""` the client has closed the connection. The thread records what happened in lists instead of printing, because output from a thread would race with the main thread's output order.

```text
=== SECTION 1: the server side (bind, listen) ===
bound host: 127.0.0.1
port is an OS-chosen ephemeral port (> 1023): True
socket family/type: AF_INET SOCK_STREAM

```

### SECTION 2: the client side (connect, sendall, recv)
The client creates its own socket, `connect()`s to the server's address, sends `b"hello server"` and reads the reply `b"HELLO SERVER"`. Network data is `bytes`, not `str`; `decode("utf-8")` converts it back to text.

```text
=== SECTION 2: the client side (connect, sendall, recv) ===
client connected; peer host: 127.0.0.1
sent   : b'hello server'
reply  : b'HELLO SERVER'
type is bytes, not str: bytes
decoded: HELLO SERVER

```

### SECTION 3: bytes vs str
`"café"` is 4 characters but 5 bytes in UTF-8 (the `é` takes two). `encode()` turns text into bytes before sending, `decode()` turns it back. The server's reply uses `bytes.upper()`, which only changes ASCII letters, so `é` stays lowercase (`CAFé`). Passing a `str` to `sendall` raises `TypeError`.

```text
=== SECTION 3: bytes vs str ===
str  : café | len = 4
bytes: b'caf\xc3\xa9' | len = 5
echoed: CAFé <- bytes.upper() only changes ASCII letters
sendall(str) -> TypeError: a bytes-like object is required, not 'str'
RULE: sockets carry bytes; encode on send, decode on receive.

```

### SECTION 4: clean shutdown
Closing the client makes the server's `recv` return `b""`, so its loop ends and the thread finishes; `join(timeout=5)` waits for it. Then the listening socket is closed; `fileno()` becomes `-1` to show it is closed. The `server events` list shows what the thread saw.

```text
=== SECTION 4: clean shutdown ===
server thread finished: True
server socket closed; fileno = -1 (-1 means closed)
server received: [b'hello server', b'caf\xc3\xa9']
server events: ['accepted a client from host 127.0.0.1', "client closed the connection (recv returned b'')"]

```

### SECTION 5: connecting after the server is gone
With no program listening on the port, `connect()` fails immediately with `ConnectionRefusedError` (an `OSError` subclass): the machine answered, but nobody is listening there. This is how "port closed" appears to a program.

```text
=== SECTION 5: connecting after the server is gone ===
ConnectionRefusedError -> no listener on that port

```

### SECTION 6: TRAP - TCP is a stream, not messages
The client calls `sendall` three times (`one`, `two`, `three`) but TCP does not remember those boundaries; the receiver may get the bytes in one chunk or several. The script therefore only reports the **joined** bytes `onetwothree`. If you need message boundaries, you must add them yourself (a delimiter or a length prefix); see `_7_SocketErrorsAndTimeouts.py`. `socket.create_connection((host, port), timeout=5)` is a convenient helper that creates and connects in one call.

```text
=== SECTION 6: TRAP - TCP is a stream, not messages ===
three sendall() calls, bytes received in total: b'onetwothree'
TCP does not preserve send() boundaries; recv() may merge or split them.
(see _7_SocketErrorsAndTimeouts for length-prefix framing)
threads cleaned up: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Server socket | `new ServerSocket(0, 1, InetAddress.getLoopbackAddress())` | `socket.socket(...)`, `bind(("127.0.0.1", 0))`, `listen(1)` |
| One class or two | `ServerSocket` for servers, `Socket` for clients | **One** `socket` class for both roles |
| Accept | `Socket s = server.accept();` | `conn, addr = server.accept()` |
| Connect | `new Socket("127.0.0.1", port)` | `socket.create_connection(("127.0.0.1", port))` or `socket()` + `connect()` |
| I/O | Streams: `getInputStream().read(buf)`, `getOutputStream().write(...)`, usually wrapped in `BufferedReader` / `PrintWriter` | Direct methods: `recv(n)` returns `bytes`, `sendall(b)` |
| EOF | `read()` returns `-1` | `recv()` returns `b""` |
| Timeout | `setSoTimeout(ms)` throws `SocketTimeoutException` | `settimeout(seconds)` raises `socket.timeout` (an alias of `TimeoutError`) |
| Cleanup | try-with-resources (`Socket` is `AutoCloseable`) | `with socket.socket() as s:` or `close()` |
| Error handling | `IOException` is checked | `OSError` family, unchecked |
| Text | `PrintWriter`/`BufferedReader` handle chars | You `encode()`/`decode()` yourself; sockets only carry bytes |
| Threads | Often `ExecutorService` | `threading.Thread` (or `socketserver`, `asyncio`) |

## Key Rules / Gotchas Recap

- Bind to `127.0.0.1` for experiments; use port `0` and read the real port with `getsockname()`.
- Set a timeout on every socket; blocking calls otherwise wait forever.
- `recv()` returns `b""` when the peer closes; that is not an error.
- Sockets carry bytes; encode and decode text explicitly.
- `send()` may send only part of your data; `sendall()` sends all of it.
- TCP has no message boundaries (see `_7_SocketErrorsAndTimeouts.py`).
- Do not print from worker threads if you need deterministic output.

## Why This Structure Exists
Every networked service, from an LLM API to an agent talking to a tool server, is built on this accept/connect/send/receive cycle. Understanding it at the socket level makes you better at debugging real network problems and is the foundation for security work such as writing test servers and understanding protocols.
