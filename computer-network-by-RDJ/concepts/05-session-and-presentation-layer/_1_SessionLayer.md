# `_1_SessionLayer.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The session layer (layer 5 of the OSI model) lets two applications open, manage and close a long-running conversation, called a session. It decides who may talk when (dialog control), who may do a critical operation (token management) and where to restart after a failure (synchronization checkpoints). It exists so that a long job, such as a 20-page file transfer, does not have to start from zero when something breaks.

The OSI model has seven layers: Physical, Data Link, Network, Transport, Session, Presentation, Application. Layers 5 and 6 sit above the transport layer. The transport layer moves bytes reliably between two processes; the session layer organises those bytes into a meaningful dialogue.

**Functions of the session layer (exam list)**
- **Dialog control.** Chooses the mode of communication. *Simplex*: one direction only (keyboard to computer). *Half duplex*: both directions but one at a time (walkie-talkie). *Full duplex*: both directions at the same time (telephone).
- **Token management.** Some operations must not be done by both sides at once. A token is passed between the parties and only the holder may perform that operation.
- **Synchronization.** The session layer inserts checkpoints (synchronization points) into the data stream. After a crash only the data after the last confirmed checkpoint is resent. OSI distinguishes major and minor synchronization points: a major point confirms everything before it, a minor point is a lighter marker.
- **Session establishment, maintenance and termination.** Open the session (agree on parameters), keep it alive (keep-alives, activity timers), close it in an orderly way (so no data is lost, unlike an abrupt abort).
- **Authentication and authorization.** Usually done when the session is set up: who are you and what may you do?

**Examples.** Remote Procedure Call (RPC), NetBIOS and SMB sessions (Windows file sharing), database sessions, and web login sessions.

**Why TCP/IP has no session layer.** The TCP/IP model has four layers (Link, Internet, Transport, Application). The OSI session and presentation layers are folded into the application layer. Applications that need session behaviour build it themselves: HTTP is stateless, so web sites use cookies or tokens that carry a session id; TLS has its own session resumption; SMB has its own sessions; databases have their own login sessions.

**Cookie / session-id idea.** HTTP does not remember who you are between requests. After login the server creates a random session id, stores it with your user data, and sends it to your browser as a cookie. The browser sends it back with every request. The id must be unpredictable, because whoever holds the id is treated as you (session hijacking). An alternative is a signed cookie: the server keeps no state and puts the data in the cookie with an HMAC tag so changes are detected.

**Comparison: session layer vs transport layer.**

| | Transport (TCP) | Session |
|---|---|---|
| Unit | segment / byte stream | dialogue / session |
| Recovery | retransmits lost segments | resumes a whole task from a checkpoint |
| Survives a TCP connection drop? | no | can (checkpoint + reconnect) |

**Typical exam questions.** List the functions of the session layer. Explain half vs full duplex. What is a synchronization point and why is it needed? Which TCP/IP layer replaces layers 5 to 7? What is the difference between a connection and a session?

## Full Line-by-Line Breakdown

### SECTION 1: WHAT THE SESSION LAYER DOES
A table of the five functions printed as plain text, plus the note that TCP/IP folds the layer into the application. Nothing is computed; it is the vocabulary you need before the simulations.

```text
===== SECTION 1: WHAT THE SESSION LAYER DOES =====
  Dialog control                 who may talk now: simplex / half duplex / full duplex
  Token management               only the token holder may perform a critical operation
  Synchronization                checkpoints in the stream so a crash resumes, not restarts
  Establish/maintain/terminate   open, keep alive, close gracefully
  Authentication                 usually done at session set-up (who is the user?)
Examples: RPC, NetBIOS/SMB sessions, SQL*Net-style database sessions.
TCP/IP has no separate session layer: layers 5-7 are folded into the
application (HTTP cookies, TLS sessions, SMB sessions are app-level).
```

### SECTION 2: DIALOG CONTROL
The `Dialog` class models the mode. In `half` mode only the current talker (`self.talker`) may send; an attempt by the other side is logged as REJECTED. `turn_over()` passes the turn, as a real session layer does with a token. In `full` mode both sides send at once and nothing is rejected.

```text
===== SECTION 2: DIALOG CONTROL =====
HALF duplex:
   A -> 'question?' ok
   B -> 'interrupting!' REJECTED (not their turn)
   -- turn passes to B
   B -> 'answer' ok
FULL duplex:
   A -> 'hello' ok
   B -> 'hello (at the same time)' ok
```

### SECTION 3: TOKEN MANAGEMENT
`TokenSession` holds a `holder`. `critical_write` succeeds only for the holder. B's first write is denied; after `pass_token("B")` it succeeds and the final value is 99. The point: the token turns "who may do this?" into a rule that does not need guessing.

```text
===== SECTION 3: TOKEN MANAGEMENT =====
A: write 10 done
B: write 99 DENIED (token held by A)
token A -> B
B: write 99 done
final value: 99
```

### SECTION 4: CHECKPOINTS AND RESUME AFTER A CRASH
A 20-page file is sent and the receiver makes a checkpoint every 5 pages. The crash happens after 13 pages, so everything after the last checkpoint (page 10) is lost; `crash()` discards it. Without checkpoints the sender restarts from page 0 and sends 13 + 20 = 33 pages. With checkpoints it resumes from page 10 and sends 13 + 10 = 23 pages. The assertion checks that the receiver ends with pages 0 to 19, each exactly once and in order. The saving is 10 pages here; it grows with the file size.

```text
===== SECTION 4: CHECKPOINTS AND RESUME AFTER A CRASH =====
No checkpoints : sent 13 + 20 = 33 pages for a 20-page file
Crash after 13 pages; last checkpoint = 10; kept pages = 10
With checkpoints: sent 13 + 10 = 23 pages
check: OK (receiver has pages 0..19 exactly once, in order)
```

### SECTION 5: SESSION ESTABLISH / MAINTAIN / TERMINATE
A tiny state machine as a dictionary: `(state, event) -> next state`. A `data` event before `connect` is illegal and ignored; after `close` it is illegal again. This is the same idea as the TCP state machine, one level up.

```text
===== SECTION 5: SESSION ESTABLISH / MAINTAIN / TERMINATE =====
  IDLE         --data--> ILLEGAL (ignored)
  IDLE         --connect--> ESTABLISHED
  ESTABLISHED  --data--> ESTABLISHED
  ESTABLISHED  --keepalive--> ESTABLISHED
  ESTABLISHED  --close--> CLOSED
  CLOSED       --data--> ILLEGAL (ignored)
```

### SECTION 6: COOKIE / SESSION-ID
Trap: `weak_login` hands out sequential ids (1001, 1002). An attacker who is user bob (id 1002) guesses 1001 and becomes alice. Fix: a 128-bit random id (32 hex digits); a random generator seeded with 42 is used here only so the output is repeatable, and the code comment says real servers use `secrets.token_urlsafe()`. Last, a signed cookie: `sign()` appends a truncated HMAC-SHA256 tag; changing `alice` to `admin` makes `verify()` fail because the attacker does not know the key.

```text
===== SECTION 6: COOKIE / SESSION-ID =====
alice got sid=1001, bob got sid=1002
attacker guesses sid=1001 -> hijacks: alice
fixed: 128-bit random id like 30877432... cannot be guessed
signed cookie  : user=alice.7b155415cae83f49 valid: True
forged cookie  : user=admin.7b155415cae83f49 valid: False
```

## Worked Example
**Problem.** A 1000-page document is sent over a session with a checkpoint every 100 pages. The connection crashes while page 457 is being sent (pages 1 to 456 were delivered). How many pages must be resent after the crash, and how many pages are sent in total, compared with having no checkpoints?

1. Checkpoints sit at 100, 200, 300, 400, 500, ... The last checkpoint before the crash is 400.
2. The receiver keeps pages 1 to 400. Pages 401 to 456 (56 pages) were received but are not covered by a checkpoint, so they are discarded.
3. The sender resumes at page 401 and sends 401 to 1000, which is 600 pages.
4. Total sent with checkpoints: 456 (first attempt) + 600 = 1056 pages.
5. Without checkpoints: 456 + 1000 = 1456 pages.
6. Saved: 1456 - 1056 = 400 pages, which is exactly the checkpointed work.

The code in Section 4 follows the same rule with 20 pages and interval 5 (13 + 10 = 23 versus 13 + 20 = 33).

## Key Rules / Gotchas Recap
- Session layer functions: dialog control, token management, synchronization, establish/maintain/terminate, authentication.
- Simplex = one way, half duplex = alternate, full duplex = simultaneous.
- A checkpoint saves only what has been confirmed; data after it is resent.
- TCP/IP has no separate session layer: the application does it (cookies, TLS sessions, SMB, RPC).
- Session ids must be random and long; sequential ids can be guessed and hijacked.
- A signed cookie detects tampering but does not hide its content (it is not encryption).
- A TCP connection and a session are different things: a session can outlive a TCP connection.

## Why This Matters
Every login system, API token, database connection and long file upload depends on session ideas, and weak session ids and cookies are a classic web security hole. Resumable transfers (checkpoints) are how large AI model and dataset downloads survive flaky networks.
