# `_4_TcpConnectionManagement.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
TCP is connection-oriented: before any data flows, the two ends set up shared state (initial sequence numbers, windows, options) with a three-way handshake, and when finished they tear it down with a four-way close. Each end tracks where it is in this life cycle with a finite state machine of about eleven states, defined in RFC 9293.

**Three-way handshake (connection establishment)**
1. Client -> Server: `SYN`, seq = x (client's ISN). Client enters SYN_SENT.
2. Server -> Client: `SYN+ACK`, seq = y (server's ISN), ack = x + 1. Server (which was in LISTEN) enters SYN_RCVD.
3. Client -> Server: `ACK`, seq = x + 1, ack = y + 1. Both ends are ESTABLISHED.

Why three, not two? Each side must (a) announce its own ISN and (b) have it acknowledged; the middle message does both of those for the server in one segment. Two messages would leave the server unsure that the client really received its ISN, and would let delayed duplicate SYNs from old connections create phantom connections. The ISN is chosen unpredictably (not always starting at 0) so that stray old segments are not confused with a new connection and so that off-path attackers cannot guess sequence numbers.

**Four-way close (connection termination).** Each direction is closed independently:
1. Active closer sends `FIN` (FIN_WAIT_1).
2. Passive side sends `ACK` (CLOSE_WAIT). The active side moves to FIN_WAIT_2. The passive side may still send data.
3. Passive side, when finished, sends `FIN` (LAST_ACK).
4. Active side sends `ACK` and enters TIME_WAIT; the passive side closes on receiving it.

It is four segments because the two directions close separately. Sometimes the passive side's ACK and FIN are combined in one segment (three segments).

**TIME_WAIT.** After the last ACK, the active closer waits 2 x MSL (Maximum Segment Lifetime) before releasing the connection. Reasons: the last ACK may be lost and the peer will retransmit its FIN, and delayed duplicates from this connection must expire before the same 5-tuple is reused. The length is OS-specific (Linux: 60 seconds). Practical consequence: a server that closes first and is restarted immediately may fail to bind its port with "Address already in use" unless it sets `SO_REUSEADDR`.

**Half-close.** `shutdown(SHUT_WR)` sends a FIN but keeps the receiving direction open. It means "I have no more data to send, but I am still listening". It is how a client signals the end of a request and still reads the full reply.

**RST (reset).** An immediate abort. Sent when a segment arrives for a port nobody listens on (connection refused), when a connection is not recognised, or when an application aborts deliberately. No handshake, no TIME_WAIT. The peer sees "connection reset".

**Simultaneous open and close.** If both ends send SYN at the same time, each goes SYN_SENT to SYN_RCVD to ESTABLISHED: two segments crossing, still one connection. If both send FIN at once, each goes FIN_WAIT_1 to CLOSING to TIME_WAIT.

**The state machine in brief**

| State | Meaning |
|---|---|
| CLOSED | No connection |
| LISTEN | Server waiting for a SYN |
| SYN_SENT | Client sent SYN, waiting for SYN+ACK |
| SYN_RCVD | Server got SYN, sent SYN+ACK, waiting for ACK |
| ESTABLISHED | Data transfer |
| FIN_WAIT_1 / FIN_WAIT_2 | Active closer: sent FIN / got ACK of FIN |
| CLOSE_WAIT | Passive closer: got FIN, waiting for its application to close |
| LAST_ACK | Passive closer sent its FIN, waiting for the final ACK |
| CLOSING | Both sent FIN simultaneously |
| TIME_WAIT | Waiting 2 x MSL |

**SYN flood (concept only).** A server must keep state for every half-open connection in SYN_RCVD. An attacker who sends many SYNs from forged source addresses and never completes the handshake can exhaust that table, so legitimate clients are refused: a denial of service. Defences: SYN cookies (encode the needed information in the server's ISN so no state is stored until a valid final ACK returns), larger backlogs with shorter half-open timeouts, rate limiting and network-level filtering. This file explains the idea only and sends nothing forged.

**Typical exam questions:** draw the three-way handshake with sequence and acknowledgement numbers; draw the four-way close; explain TIME_WAIT; why does a connection need an ISN; what is a half-open connection; which side ends in TIME_WAIT; draw the state diagram path of a client and a server.

## Full Line-by-Line Breakdown

### SECTION 1: THE STATE MACHINE AS A TRANSITION TABLE
`TRANSITIONS` is a dictionary from `(state, event)` to `(segment to send, next state)`. This is the entire protocol logic for connection management, and it has no `if` chains: a missing key means the event is illegal in that state. The table models 21 transitions (the subset that exams cover; the full RFC adds timeouts and retransmissions). An assertion checks that every state mentioned is a known state. The `Host.fire` method looks up the transition, prints it and moves the state, raising `RuntimeError` for an illegal event.

Output from a real run:

```text
===== SECTION 1: THE STATE MACHINE AS A TRANSITION TABLE =====
11 states, 21 transitions modelled (the subset an exam asks about).
state        event          -> send     next state
CLOSED       open_passive   -> -        LISTEN
CLOSED       open_active    -> SYN      SYN_SENT
LISTEN       rcv SYN        -> SYN+ACK  SYN_RCVD
LISTEN       close          -> -        CLOSED
SYN_SENT     rcv SYN+ACK    -> ACK      ESTABLISHED
SYN_SENT     rcv SYN        -> SYN+ACK  SYN_RCVD
SYN_SENT     rcv RST        -> -        CLOSED
SYN_SENT     close          -> -        CLOSED
SYN_RCVD     rcv ACK        -> -        ESTABLISHED
SYN_RCVD     close          -> FIN      FIN_WAIT_1
ESTABLISHED  close          -> FIN      FIN_WAIT_1
ESTABLISHED  rcv FIN        -> ACK      CLOSE_WAIT
ESTABLISHED  rcv RST        -> -        CLOSED
FIN_WAIT_1   rcv ACK        -> -        FIN_WAIT_2
FIN_WAIT_1   rcv FIN        -> ACK      CLOSING
FIN_WAIT_1   rcv FIN+ACK    -> ACK      TIME_WAIT
FIN_WAIT_2   rcv FIN        -> ACK      TIME_WAIT
CLOSING      rcv ACK        -> -        TIME_WAIT
TIME_WAIT    timeout_2MSL   -> -        CLOSED
CLOSE_WAIT   close          -> FIN      LAST_ACK
LAST_ACK     rcv ACK        -> -        CLOSED
check: every state named in the table is a valid state: OK
```

### SECTION 2: THREE-WAY HANDSHAKE WITH ISNs
Two `Host` objects get seeded random 32-bit ISNs (seeded only so the output repeats; real operating systems pick unpredictable values). The server starts with a passive open (LISTEN), the client with an active open. The trace prints each state change and the segment sent, then the on-the-wire summary with sequence and acknowledgement numbers: the SYN carries x = 647892279, the SYN+ACK carries y and ack x+1, the final ACK carries seq x+1 and ack y+1. The first data byte would use seq x+1, because the SYN consumed one number. The trap feeds an ACK to a host in LISTEN: the table has no such transition, so it raises. A real TCP replies to a stray ACK with RST.

Output from a real run:

```text
===== SECTION 2: THREE-WAY HANDSHAKE WITH ISNs =====
client ISN = 647892279, server ISN = 2795742288 (both 32-bit; unpredictable in real OSes)
    server CLOSED       --[open_passive]--> LISTEN       sends -
    client CLOSED       --[open_active]--> SYN_SENT     sends SYN
  1) client -> server  SYN      seq=647892279
    server LISTEN       --[rcv SYN]--> SYN_RCVD     sends SYN+ACK
  2) server -> client  SYN+ACK  seq=2795742288 ack=647892280
    client SYN_SENT     --[rcv SYN+ACK]--> ESTABLISHED  sends ACK
  3) client -> server  ACK      seq=647892280 ack=2795742289
    server SYN_RCVD     --[rcv ACK]--> ESTABLISHED  sends -
both ESTABLISHED. SYN and SYN+ACK each consumed one sequence number (the +1).
A first data byte from the client would carry seq = 647892280

trap: an event the table does not allow in that state:
   stray: event 'rcv ACK' is illegal in state LISTEN -> a real TCP answers a stray ACK in LISTEN with RST
```

### SECTION 3: FOUR-WAY CLOSE AND TIME_WAIT
The client closes first. The trace shows the four segments and the states: ESTABLISHED to FIN_WAIT_1 to FIN_WAIT_2 to TIME_WAIT for the client (the active closer), and ESTABLISHED to CLOSE_WAIT to LAST_ACK to CLOSED for the server (the passive closer). Notice that the server is CLOSED while the client is still in TIME_WAIT, so the active closer carries the cost. Then a `timeout_2MSL` event releases the client. The next three traces show simultaneous close (CLOSING appears), simultaneous open (two crossing SYNs), and RST, which jumps straight to CLOSED. In the simultaneous open each side's reply to the other's SYN is a SYN+ACK in the real protocol; the table collapses the follow-up into one `rcv ACK` event for brevity.

Output from a real run:

```text
===== SECTION 3: FOUR-WAY CLOSE AND TIME_WAIT =====
client closes first (the ACTIVE closer):
    client ESTABLISHED  --[close]--> FIN_WAIT_1   sends FIN
  1) client -> server  FIN
    server ESTABLISHED  --[rcv FIN]--> CLOSE_WAIT   sends ACK
  2) server -> client  ACK     (server may still send data: this is a half-close)
    client FIN_WAIT_1   --[rcv ACK]--> FIN_WAIT_2   sends -
    server CLOSE_WAIT   --[close]--> LAST_ACK     sends FIN
  3) server -> client  FIN
    client FIN_WAIT_2   --[rcv FIN]--> TIME_WAIT    sends ACK
  4) client -> server  ACK
    server LAST_ACK     --[rcv ACK]--> CLOSED       sends -
server state: CLOSED (passive closer is done); client state: TIME_WAIT
    client TIME_WAIT    --[timeout_2MSL]--> CLOSED       sends -
TIME_WAIT lasts 2 x MSL (Maximum Segment Lifetime). Why it exists:
  a) if the last ACK is lost the peer resends FIN; someone must still be there to re-ACK;
  b) it lets old duplicate segments from this connection die out before the same
     (ip, port, ip, port) 5-tuple is reused. The duration is OS-specific (Linux uses 60 s).

simultaneous close (both send FIN at once):
    A      ESTABLISHED  --[close]--> FIN_WAIT_1   sends FIN
    B      ESTABLISHED  --[close]--> FIN_WAIT_1   sends FIN
    A      FIN_WAIT_1   --[rcv FIN]--> CLOSING      sends ACK
    B      FIN_WAIT_1   --[rcv FIN]--> CLOSING      sends ACK
    A      CLOSING      --[rcv ACK]--> TIME_WAIT    sends -
    B      CLOSING      --[rcv ACK]--> TIME_WAIT    sends -
both pass through CLOSING and TIME_WAIT: TIME_WAIT TIME_WAIT

simultaneous open (both send SYN at once; rare):
    A      CLOSED       --[open_active]--> SYN_SENT     sends SYN
    B      CLOSED       --[open_active]--> SYN_SENT     sends SYN
    A      SYN_SENT     --[rcv SYN]--> SYN_RCVD     sends SYN+ACK
    B      SYN_SENT     --[rcv SYN]--> SYN_RCVD     sends SYN+ACK
    A      SYN_RCVD     --[rcv ACK]--> ESTABLISHED  sends -
    B      SYN_RCVD     --[rcv ACK]--> ESTABLISHED  sends -
two SYNs crossed, each side moved SYN_SENT -> SYN_RCVD -> ESTABLISHED: ESTABLISHED ESTABLISHED

RST (reset): abrupt abort, no 4-way close, no TIME_WAIT:
    peer   ESTABLISHED  --[rcv RST]--> CLOSED       sends -
  ESTABLISHED + RST -> CLOSED (RST is sent for a segment to a closed port, or to abort)
```

### SECTION 4: REAL LOOPBACK HANDSHAKE OUTCOMES
Now the real kernel. `connect()` returns before `accept()` was even called, because the operating system completes the handshake itself and queues the finished connection in the listen backlog; `accept()` only collects it. A connect to a port that was just freed makes the OS answer the SYN with RST, which Python raises as `ConnectionRefusedError`. The half-close demo is the useful one: the client sends a request, calls `shutdown(SHUT_WR)` (its FIN), the server reads until `recv` returns `b""` (end of stream means FIN arrived), then replies, and the half-closed client still reads the reply. For RST, setting `SO_LINGER` with a zero timeout makes `close()` abort with RST instead of FIN, and the peer sees `ConnectionResetError`. Finally the TIME_WAIT trap: a server that closes first holds the port in TIME_WAIT, so restarting it on the same port fails with "Address already in use" unless `SO_REUSEADDR` was set (before the bind, on the server socket). All sockets are closed.

Output from a real run:

```text
===== SECTION 4: REAL LOOPBACK HANDSHAKE OUTCOMES =====
connect() returned BEFORE the server called accept(): the kernel finished the handshake
  and parked the connection in the listen backlog (state ESTABLISHED already).
accept() then just hands the finished connection to the program: peer is loopback: True
connect to a closed port: server OS replied RST to our SYN -> ConnectionRefusedError (errno ECONNREFUSED)
server read until EOF (b'' means FIN received): b'request: please answer after I finish'
client, though half-closed, still received: b'reply sent after client half-closed'
peer after abortive close got: ConnectionResetError (RST received)
TIME_WAIT trap: restarting a server on the same port WITHOUT SO_REUSEADDR failed: Address already in use
fix: set SO_REUSEADDR on the server socket (before bind); the restart on the same port works.
all sockets closed
```

### SECTION 5: SYN FLOOD (CONCEPT ONLY, NOTHING IS SENT)
A printed explanation of the attack and the defences, matching the concept notes above. No packets are forged; no code here could run it.

Output from a real run:

```text
===== SECTION 5: SYN FLOOD (CONCEPT ONLY, NOTHING IS SENT) =====
The server must remember every half-open connection (state SYN_RCVD) for a while.
An attacker who sends a flood of SYNs from forged addresses and never finishes the
handshake can fill that table, so real clients are refused. This is a denial of service.
Defences (described, not implemented here):
  - SYN cookies: encode the connection info into the server's ISN, keep NO state
    until a valid ACK comes back;
  - a larger backlog, shorter half-open timeouts, rate limiting, and upstream filtering.
Nothing in this file sends forged packets; the only traffic is loopback, to our own sockets.
```

## Worked Example
**Problem.** Client ISN = 100, server ISN = 300. The client sends 200 bytes after the handshake, the server replies with 50 bytes, then the client closes first. Give every segment with flags, seq and ack, and the final states.

**Solution.**
1. `SYN` seq=100. Client: SYN_SENT.
2. `SYN+ACK` seq=300, ack=101. Server: SYN_RCVD.
3. `ACK` seq=101, ack=301. Both ESTABLISHED.
4. Client data: seq=101, 200 bytes (covers 101 to 300). Server ACK: ack=301 (and its own seq 301).
5. Server data: seq=301, 50 bytes. Client ACK: seq=301, ack=351.
6. Client `FIN` seq=301, ack=351 (FIN consumes one number, so next is 302). Client: FIN_WAIT_1.
7. Server `ACK` ack=302. Server: CLOSE_WAIT. Client: FIN_WAIT_2.
8. Server `FIN` seq=351, ack=302. Server: LAST_ACK.
9. Client `ACK` ack=352. Client: TIME_WAIT for 2 x MSL. Server: CLOSED.

Sections 2 and 3 of the code print exactly this pattern of states and sequence numbers (with different ISNs).

## Key Rules / Gotchas Recap
- SYN and FIN each consume one sequence number; a pure ACK consumes none.
- Handshake: SYN, SYN+ACK, ACK. Close: FIN, ACK, FIN, ACK.
- The ACK in the handshake is x+1 and y+1, not x and y.
- The active closer (first to send FIN) ends up in TIME_WAIT, not the server by default.
- TIME_WAIT is 2 x MSL; the value is OS-specific.
- `recv` returning `b""` means the peer's FIN arrived (end of stream), not an error.
- `connect()` can succeed before the server calls `accept()`.
- Closed port: RST, "connection refused". A reset mid-connection: "connection reset by peer".
- Servers must set `SO_REUSEADDR` before `bind` so a restart does not hit TIME_WAIT.
- SYN flood: half-open state exhaustion; SYN cookies are the standard defence.

## Why This Matters
Reading `ss -tan` or Wireshark output means recognising these states: a pile of CLOSE_WAIT sockets means your code forgot to `close()`, a pile of SYN_RCVD may mean a SYN flood, and "Address already in use" after a restart is TIME_WAIT. Knowing the state machine turns those from mysteries into one-minute diagnoses, and it is the heart of any load balancer or connection pool.
