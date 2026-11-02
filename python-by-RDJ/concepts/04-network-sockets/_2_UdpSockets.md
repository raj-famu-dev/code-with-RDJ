# `_2_UdpSockets.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
UDP is the "fire and forget" transport: there is no connection, each `sendto()` sends one self-contained **datagram** to an address, and each `recvfrom()` returns exactly one datagram along with the sender's address. Unlike TCP's byte stream, UDP preserves message boundaries, but it gives no promise of delivery, ordering or duplicate protection. It is used for DNS, games, video and anything where speed matters more than perfect delivery. All code here runs on loopback only.

## Full Line-by-Line Breakdown

### SECTION 1: a UDP server socket
`SOCK_DGRAM` selects UDP. The server calls `bind()` but there is no `listen()` or `accept()`, because nothing is connected. A background thread handles three requests: `recvfrom(2048)` returns `(data, address)` and `sendto(reply, address)` answers to whoever sent it.

```text
=== SECTION 1: a UDP server socket ===
type: SOCK_DGRAM | bound host: 127.0.0.1
UDP has no listen()/accept(): there is no connection to accept.

```

### SECTION 2: sendto / recvfrom (no connect needed)
The client creates a datagram socket and names the destination on **every** `sendto`. It never calls `connect`. Each reply arrives with the server's address, and the script checks the port matches. The thread is joined and the server socket closed.

```text
=== SECTION 2: sendto / recvfrom (no connect needed) ===
sent b'alpha' -> reply b'ACK:alpha' | from port matches server: True
sent b'beta' -> reply b'ACK:beta' | from port matches server: True
sent b'gamma' -> reply b'ACK:gamma' | from port matches server: True
server thread finished: True

```

### SECTION 3: message boundaries are PRESERVED in UDP
Three separate `sendto` calls produce three separate datagrams, and three `recvfrom` calls return exactly `b"one"`, `b"two"`, `b"three"`. One send equals one receive.

```text
=== SECTION 3: message boundaries are PRESERVED in UDP ===
three sends, three separate receives: [b'one', b'two', b'three']
Each recvfrom() returned exactly one whole datagram.

```

### SECTION 4: contrast with TCP (a stream merges writes)
The same three small sends over TCP arrive as a byte stream: the receiver may see them in one chunk (`b"onetwothree"`) or split in any way. The script only asserts the joined result, because the split is not guaranteed; that missing guarantee is the lesson.

```text
=== SECTION 4: contrast with TCP (a stream merges writes) ===
TCP total bytes received: b'onetwothree'
TCP may deliver these as 1, 2 or 3 chunks; the exact split is NOT guaranteed,
so we only claim the joined bytes. UDP's per-message guarantee is the difference.

```

### SECTION 5: TRAP - a small buffer truncates a datagram
If the buffer passed to `recvfrom` is smaller than the datagram, the extra bytes are **discarded**, not kept for the next call. On this Linux run, `recvfrom(4)` returned `b'0123'` and the next call timed out. Behaviour is platform-specific (Windows raises an error instead), so the code handles both. Use a buffer large enough for your biggest datagram.

```text
=== SECTION 5: TRAP - a small buffer truncates a datagram ===
recvfrom(4) returned: b'0123' <- the rest of the datagram is DISCARDED
second recvfrom -> timeout: the other 6 bytes are gone, not queued

```

### SECTION 6: UDP is unreliable by design
Sending to a port where nothing listens does **not** raise an error on this platform; `sendto` succeeds and the data simply vanishes. The only way to notice is a timeout waiting for a reply, so UDP programs need their own timeouts, retries and sequence numbers. (Some systems may report an ICMP error as `ConnectionRefusedError`, which the code also handles.)

```text
=== SECTION 6: UDP is unreliable by design (no connection, no delivery proof) ===
sendto() to a dead port did NOT raise: UDP does not tell you.
no reply: you need your own timeout/retry logic (or use TCP)

all sockets closed; threads joined
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| UDP socket | `DatagramSocket socket = new DatagramSocket(0, InetAddress.getLoopbackAddress())` | `socket.socket(AF_INET, SOCK_DGRAM)` then `bind` |
| Sending | Build a `DatagramPacket(buf, len, addr, port)` and call `socket.send(packet)` | `sock.sendto(data, (host, port))` |
| Receiving | Allocate `byte[]`, create a `DatagramPacket`, call `socket.receive(packet)`, read `packet.getData()` and `getLength()` | `data, addr = sock.recvfrom(2048)`; both returned directly |
| Same class as TCP? | No: `DatagramSocket` vs `Socket`/`ServerSocket` | Yes: one `socket` class; the type argument chooses UDP or TCP |
| Timeout | `setSoTimeout(ms)` -> `SocketTimeoutException` | `settimeout(s)` -> `socket.timeout` |
| Truncation | Silent cut to the packet's buffer length | Silent on Linux, error on Windows |
| Errors | Checked `IOException` | Unchecked `OSError` family |

## Key Rules / Gotchas Recap

- UDP: no `listen`/`accept`, no connection, an address on every `sendto`.
- One `sendto` equals one `recvfrom`; TCP gives no such guarantee.
- A receive buffer smaller than the datagram loses the remainder.
- Delivery, order and duplicates are not guaranteed; add timeouts and retries yourself.
- Always set a timeout, or `recvfrom` can wait forever.
- Keep datagrams small (well under about 1,400 bytes) to avoid IP fragmentation on real networks.

## Why This Structure Exists
DNS, service discovery, telemetry and real-time media use UDP, and security tools often need to understand its lack of connection state (for example why UDP "port checks" are less certain than TCP). Seeing both transports side by side makes the stream-versus-message distinction concrete.
