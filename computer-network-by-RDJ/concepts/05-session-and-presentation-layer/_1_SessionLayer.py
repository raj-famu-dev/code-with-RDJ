# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""OSI Session layer (layer 5): dialog control (half/full duplex), token
management, synchronization checkpoints, session establish/maintain/terminate,
and the cookie / session-id idea that TCP/IP applications use instead."""
from __future__ import annotations

import hashlib
import hmac
import random


# ===== SECTION 1: WHAT THE SESSION LAYER DOES =====
print("===== SECTION 1: WHAT THE SESSION LAYER DOES =====")
functions = [
    ("Dialog control", "who may talk now: simplex / half duplex / full duplex"),
    ("Token management", "only the token holder may perform a critical operation"),
    ("Synchronization", "checkpoints in the stream so a crash resumes, not restarts"),
    ("Establish/maintain/terminate", "open, keep alive, close gracefully"),
    ("Authentication", "usually done at session set-up (who is the user?)"),
]
for name, text in functions:
    print(f"  {name:<30} {text}")
print("Examples: RPC, NetBIOS/SMB sessions, SQL*Net-style database sessions.")
print("TCP/IP has no separate session layer: layers 5-7 are folded into the")
print("application (HTTP cookies, TLS sessions, SMB sessions are app-level).")


# ===== SECTION 2: DIALOG CONTROL (HALF VS FULL DUPLEX) =====
print("\n===== SECTION 2: DIALOG CONTROL =====")


class Dialog:
    """Tiny model of dialog control. Half duplex = one talker at a time."""

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.talker = "A"  # in half duplex only this side may send
        self.log: list[str] = []

    def send(self, who: str, msg: str) -> bool:
        if self.mode == "half" and who != self.talker:
            self.log.append(f"{who} -> '{msg}' REJECTED (not their turn)")
            return False
        self.log.append(f"{who} -> '{msg}' ok")
        return True

    def turn_over(self) -> None:
        self.talker = "B" if self.talker == "A" else "A"
        self.log.append(f"-- turn passes to {self.talker}")


half = Dialog("half")
half.send("A", "question?")
half.send("B", "interrupting!")   # not allowed
half.turn_over()
half.send("B", "answer")
full = Dialog("full")
full.send("A", "hello")
full.send("B", "hello (at the same time)")
print("HALF duplex:")
for line in half.log:
    print("  ", line)
print("FULL duplex:")
for line in full.log:
    print("  ", line)


# ===== SECTION 3: TOKEN MANAGEMENT =====
print("\n===== SECTION 3: TOKEN MANAGEMENT =====")


class TokenSession:
    """Only the token holder may do the critical operation (e.g. write)."""

    def __init__(self) -> None:
        self.holder = "A"
        self.value = 0

    def critical_write(self, who: str, v: int) -> str:
        if who != self.holder:
            return f"{who}: write {v} DENIED (token held by {self.holder})"
        self.value = v
        return f"{who}: write {v} done"

    def pass_token(self, to: str) -> str:
        old, self.holder = self.holder, to
        return f"token {old} -> {to}"


ts = TokenSession()
print(ts.critical_write("A", 10))
print(ts.critical_write("B", 99))
print(ts.pass_token("B"))
print(ts.critical_write("B", 99))
print("final value:", ts.value)


# ===== SECTION 4: SYNCHRONIZATION CHECKPOINTS AND CRASH RESUME =====
print("\n===== SECTION 4: CHECKPOINTS AND RESUME AFTER A CRASH =====")
PAGES = 20
INTERVAL = 5  # checkpoint every 5 pages


class Receiver:
    def __init__(self) -> None:
        self.received: list[int] = []
        self.checkpoint = 0  # pages up to here are safely stored

    def accept(self, page: int) -> None:
        self.received.append(page)
        if len(self.received) % INTERVAL == 0:
            self.checkpoint = len(self.received)

    def crash(self) -> None:
        # Everything after the last checkpoint is lost.
        self.received = self.received[: self.checkpoint]


def transfer(rx: Receiver, start: int, crash_after: int | None) -> int:
    """Send pages start..PAGES-1; returns number of pages sent this attempt."""
    sent = 0
    for page in range(start, PAGES):
        rx.accept(page)
        sent += 1
        if crash_after is not None and sent == crash_after:
            rx.crash()
            return sent
    return sent


# Without checkpoints: crash at page 13 means start again from page 0.
rx1 = Receiver()
a = transfer(rx1, 0, 13)
rx1.received.clear()
b = transfer(rx1, 0, None)
print(f"No checkpoints : sent {a} + {b} = {a + b} pages for a {PAGES}-page file")

# With checkpoints: crash at page 13, resume from the last checkpoint (10).
rx2 = Receiver()
a = transfer(rx2, 0, 13)
resume_from = rx2.checkpoint
print(f"Crash after 13 pages; last checkpoint = {resume_from}; "
      f"kept pages = {len(rx2.received)}")
b = transfer(rx2, resume_from, None)
print(f"With checkpoints: sent {a} + {b} = {a + b} pages")
assert rx2.received == list(range(PAGES))
print("check: OK (receiver has pages 0..19 exactly once, in order)")


# ===== SECTION 5: SESSION LIFECYCLE STATE MACHINE =====
print("\n===== SECTION 5: SESSION ESTABLISH / MAINTAIN / TERMINATE =====")
TRANSITIONS = {
    ("IDLE", "connect"): "ESTABLISHED",
    ("ESTABLISHED", "data"): "ESTABLISHED",
    ("ESTABLISHED", "keepalive"): "ESTABLISHED",
    ("ESTABLISHED", "close"): "CLOSED",
}
state = "IDLE"
for event in ["data", "connect", "data", "keepalive", "close", "data"]:
    nxt = TRANSITIONS.get((state, event))
    if nxt is None:
        print(f"  {state:<12} --{event}--> ILLEGAL (ignored)")
    else:
        print(f"  {state:<12} --{event}--> {nxt}")
        state = nxt


# ===== SECTION 6: COOKIE / SESSION-ID IDEA (TRAP: GUESSABLE IDS) =====
print("\n===== SECTION 6: COOKIE / SESSION-ID =====")
# HTTP is stateless; the server hands out an id and the client sends it back.
store: dict[str, str] = {}


def weak_login(user: str, counter: list[int]) -> str:
    counter[0] += 1
    sid = str(counter[0])  # TRAP: sequential, guessable
    store[sid] = user
    return sid


ctr = [1000]
alice = weak_login("alice", ctr)
bob = weak_login("bob", ctr)
print(f"alice got sid={alice}, bob got sid={bob}")
print(f"attacker guesses sid={int(bob) - 1} -> hijacks:", store.get(str(int(bob) - 1)))

rng = random.Random(42)  # seeded ONLY to keep this demo deterministic.
# Real servers use secrets.token_urlsafe(), never a seeded PRNG.
strong = "".join(rng.choice("0123456789abcdef") for _ in range(32))
store[strong] = "carol"
print(f"fixed: 128-bit random id like {strong[:8]}... cannot be guessed")

# Signed cookie: tamper-evident client-side state (HMAC-SHA256).
key = b"demo-server-secret"


def sign(data: str) -> str:
    return data + "." + hmac.new(key, data.encode(), hashlib.sha256).hexdigest()[:16]


def verify(cookie: str) -> bool:
    data, _, tag = cookie.rpartition(".")
    return hmac.compare_digest(sign(data), cookie) and bool(tag)


c = sign("user=alice")
print("signed cookie  :", c, "valid:", verify(c))
forged = c.replace("alice", "admin")
print("forged cookie  :", forged, "valid:", verify(forged))
