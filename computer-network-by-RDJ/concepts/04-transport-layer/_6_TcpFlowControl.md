# `_6_TcpFlowControl.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Flow control stops a fast sender from overwhelming a slow receiver. In TCP the receiver tells the sender, in every segment's 16-bit window field, how many more bytes it has room for (the receive window, `rwnd`), and the sender promises never to have more unacknowledged data in flight than that.

**The receive window.** The receiver has a buffer of `RcvBuffer` bytes. Data that has arrived but that the application has not yet read sits in it. So:

`rwnd = RcvBuffer - (LastByteRcvd - LastByteRead)`

The sender keeps `LastByteSent - LastByteAcked <= rwnd`. The amount it may still send is the **usable window** = `rwnd - bytes in flight`. As ACKs arrive and the receiving application reads data, the window edges slide to the right: this is the **sliding window**. TCP's window is measured in bytes (not packets). The real sending limit is `min(rwnd, cwnd)`, where `cwnd` is the congestion window from topic 7. Flow control protects the receiver; congestion control protects the network.

**Zero window and window probes.** If the application stops reading, the buffer fills and the receiver advertises `rwnd = 0`. The sender must stop sending data. But if the later "window is open again" update is lost, both sides would wait forever. So the sender runs a **persist timer** and sends tiny **window probes** (typically 1 byte) now and then; each probe forces the receiver to answer with its current window.

**Silly window syndrome (SWS).** If a slow application frees a few bytes at a time and the receiver keeps advertising each sliver ("window = 100"), the sender dutifully sends 100-byte segments carrying 40 bytes of IP and TCP headers each: terribly inefficient, and it never recovers. Cures:
- Receiver side (Clark's solution): do not advertise a window increase until at least `min(MSS, RcvBuffer / 2)` bytes are free; advertise 0 until then.
- Sender side: do not send a small segment unless it is all the data left; wait until you can send a full MSS (or half the receiver's maximum window).

**Nagle's algorithm (RFC 896).** The sender-side SWS cure for applications that write tiny pieces: if there is unacknowledged data in flight, hold small writes in the buffer and send them as one segment when the ACK arrives (or when a full MSS has accumulated). One small packet in flight at a time. It helps keystroke-style traffic, reducing header overhead.

**Delayed ACK (RFC 1122).** The receiver waits a short time (up to 500 ms is allowed by the RFC; common values are 40 to 200 ms) before sending a pure ACK, hoping to piggyback it on data going back, and ACKs at least every second full-sized segment. Fewer pure ACKs on the wire.

**The interaction.** In a *write-write-read* pattern (send a small header, then a small body, then wait for the reply) Nagle holds the second write until the first is ACKed, while the receiver delays that ACK because it has no reply to piggyback on yet and is waiting for more data. Each side waits on the other until the delayed-ACK timer fires: an artificial stall of tens to hundreds of milliseconds. Fixes: write the request with a single `send` (best), or disable Nagle with the `TCP_NODELAY` socket option for latency-sensitive request/response traffic.

**Window scaling.** The 16-bit field limits the window to 65535 bytes; the window-scale option (negotiated in the SYN) multiplies it up to about 1 GiB so that fast long-delay links can be filled (see topic 3).

**Typical exam questions:** compute rwnd given buffer, LastByteRcvd and LastByteRead; compute how many bytes the sender may still send; what does `rwnd = 0` mean and how does the sender recover; explain silly window syndrome and both fixes; explain Nagle's algorithm; why does a small write after a small write stall (Nagle vs delayed ACK); difference between flow control and congestion control.

## Full Line-by-Line Breakdown

### SECTION 1: THE RECEIVER WINDOW FORMULA
Plain arithmetic with the formula: buffer 4000, 3000 bytes received, 1200 read, so 1800 bytes are waiting and `rwnd = 4000 - 1800 = 2200`. The sender has sent 3000 and had 2000 acknowledged, so 1000 bytes are in flight and the usable window is `2200 - 1000 = 1200`. Two asserts lock the hand answers. The trap line reminds you that rwnd is the *free* space, not the buffer size and not the unread amount, which is the usual exam slip.

Output from a real run:

```text
===== SECTION 1: THE RECEIVER WINDOW FORMULA =====
rwnd = RcvBuffer - (LastByteRcvd - LastByteRead)   i.e. the FREE space in the receive buffer
sender rule: LastByteSent - LastByteAcked <= rwnd   (never have more unacked data than rwnd)
example: buffer 4000, received up to byte 3000, app has read up to 1200
  unread = 1800, rwnd = 4000 - 1800 = 2200
sender: sent up to 3000, acked up to 2000 -> in flight 1000
  usable window = rwnd - in flight = 2200 - 1000 = 1200 more bytes may be sent
check: hand arithmetic (rwnd 2200, usable 1200): OK
flow control protects the RECEIVER's buffer; congestion control (topic 7) protects the NETWORK.
effective sending limit = min(rwnd, cwnd).
trap: rwnd is in BYTES and is the free space, not the buffer size and not the unread amount.
```

### SECTION 2: SLIDING WINDOW, SLOW READER, ZERO WINDOW
The loop models one round as one RTT. Each round the sender sends as much as the window it last saw allows (split into MSS-sized segments), the data lands in the receiver's buffer, the application reads whatever its `reads` list says for that round, and the new window is the free space. The application reads 1500, 0, 0, 0, 2000, then 4000 per round. Round 1 uses the full 4000 window but only 1500 is drained, so the next window is 1500. In round 2 the sender fills that 1500 (1000 + 500) while the app reads nothing, so the window closes to 0. Rounds 3 to 5 show the zero window: no data, only a 1-byte probe each round. At the end of round 5 the app finally reads 2000 and the window reopens to 2000; round 6 sends 2000, and round 7 finishes the transfer. The assert confirms all 10000 bytes were delivered with no overflow because the sender never exceeded the advertised window. Note that the sender's average throughput is bounded by how fast the application reads.

Output from a real run:

```text
===== SECTION 2: SLIDING WINDOW, SLOW READER, ZERO WINDOW =====
buffer 4000, MSS 1000, 10000 bytes to send; 1 round = 1 RTT; window = free buffer space
rnd rwnd seen sender sends                 unread app reads new rwnd
  1      4000 4000 B = 1000+1000+1000+1000   4000      1500     1500
  2      1500 1500 B = 1000+500              4000         0        0
  3         0 ZERO WINDOW: 1-byte probe      4000         0        0
  4         0 ZERO WINDOW: 1-byte probe      4000         0        0
  5         0 ZERO WINDOW: 1-byte probe      4000      2000     2000
  6      2000 2000 B = 1000+1000             4000      4000     4000
  7      4000 2500 B = 1000+1000+500         2500      2500     4000
sent 10000 of 10000 bytes in 7 rounds
What happened:
  round 1: full 4000-byte window used; the app only drained 1500, so the window shrank to 1500.
  round 2: sender fills the 1500 it is allowed; the app is stalled, so the window becomes 0.
  rounds 3-5: zero window -> sender STOPS sending data and only sends 1-byte probes.
  The probe is driven by the persist timer: without it a lost 'window reopened' update would
  leave both sides waiting forever (deadlock).
  end of round 5: the app wakes up and reads; the receiver sends a window update (2000); the sender resumes.
The sender never exceeded rwnd, so the receiver buffer never overflowed: that IS flow control.
```

### SECTION 3: SILLY WINDOW SYNDROME (TRAP AND FIX)
`transfer` starts with a full 4000-byte buffer and an app that reads only 100 bytes per round, then sends 8000 bytes. Naive behaviour: after the first burst the receiver advertises 100, then 100, then 100 again, so after four full segments the sender emits 40 runt segments of 100 bytes: 44 segments, efficiency 8000 / (8000 + 40 x 44) = 82.0% (40 bytes of IP+TCP header per segment, no options). With the fix the receiver advertises 0 until at least `min(MSS, buffer/2)` = 1000 bytes are free and the sender waits for a full segment: 8 full segments, 96.2% efficient. The efficiency numbers are computed from the simulated segment sizes, not claimed from elsewhere. The cost of the fix is a short wait, but the data rate cannot exceed the app's read rate anyway.

Output from a real run:

```text
===== SECTION 3: SILLY WINDOW SYNDROME (TRAP AND FIX) =====
NAIVE (silly window): 44 segments, 40 runts (< 1000 B), efficiency = 8000/(8000+40x44) = 82.0%
FIXED (Clark + sender rule): 8 segments, 0 runts (< 1000 B), efficiency = 8000/(8000+40x8) = 96.2%
naive: the app frees 100 bytes, the receiver says 'window = 100', the sender obliges with a
100-byte segment carrying 40 bytes of headers. Repeated forever = a silly window.
fixes: receiver does not advertise until free space >= min(MSS, buffer/2) (Clark);
       sender does not send until it can fill an MSS or half the max window (or has nothing more).
(the sender-side fix is the same idea as Nagle's algorithm, next section)
```

### SECTION 4: NAGLE'S ALGORITHM VS DELAYED ACK (MODEL)
A small timeline model with an assumed one-way delay of 5 ms and an assumed delayed-ACK timer of 200 ms (assumptions, labelled in the output; real stacks differ). With Nagle on, write #1 (10 bytes) goes at once; write #2 (90 bytes) is held because data is unacknowledged; the server receives 10 bytes, has nothing to reply with, and delays its ACK for 200 ms; only then does the body get sent. Total 220 ms. With `TCP_NODELAY` both writes leave at once and the reply arrives in 10 ms. The assert confirms the extra 210 ms is the delayed-ACK timer plus one extra round trip. The last lines create an unconnected socket, read `TCP_NODELAY` (default 0, meaning Nagle is active), set it to 1 and read it back. This is the real API call, shown without opening a connection or claiming a real-world timing.

Output from a real run:

```text
===== SECTION 4: NAGLE'S ALGORITHM VS DELAYED ACK (MODEL) =====
Nagle: if unacked data is in flight, buffer new small writes until an ACK arrives
       or a full MSS has accumulated. Goal: stop streams of 1-byte segments (telnet).
Delayed ACK: the receiver waits (assumed below: 200 ms; real values vary by OS) hoping to
       piggyback the ACK on response data, or ACKs at once on every second full segment.
  --- TCP_NODELAY = False ---
  t=  0 ms  app write #1 (10 B header) -> sent immediately (nothing in flight)
  t=  0 ms  app write #2 (90 B body) -> HELD by Nagle (unacked data in flight, segment is small)
  t=  5 ms  server got 10 B; has nothing to send yet -> delays its ACK
  t=205 ms  delayed-ACK timer fires, ACK sent
  t=210 ms  client gets ACK, Nagle releases the 90 B body
  t=215 ms  server has the full request, replies
  t=220 ms  client receives reply -> request latency 220 ms
  --- TCP_NODELAY = True ---
  t=  0 ms  app write #1 (10 B header) -> sent immediately (nothing in flight)
  t=  0 ms  app write #2 (90 B body) -> sent immediately (Nagle disabled)
  t=  5 ms  server has the full request, replies
  t= 10 ms  client receives reply -> request latency 10 ms
model result: 220 ms vs 10 ms, a stall of 210 ms caused ONLY by the clash
check: extra delay = delayed-ACK timer + one extra round trip (ACK back, body out): OK
Fixes: send the request with ONE write (join header+body: sendall(header+body)), or set
TCP_NODELAY for latency-sensitive request/response code. Keep Nagle for bulk streams.
real socket: TCP_NODELAY default = 0
after setsockopt(TCP_NODELAY, 1) = 1
(0 = Nagle ON by default; no connection is opened for this demo)
```

## Worked Example
**Problem.** Receiver buffer 5000 bytes. The sender has sent bytes up to 4000, but only the first 2500 have reached the receiver (the other 1500 are still on the wire); the sender has received the ACK for 2500. The application has read up to byte 1500. (a) What rwnd is in that ACK? (b) How many more bytes may the sender send? (c) The in-flight 1500 bytes now arrive and the app reads 2000 more bytes; what is the new rwnd?

**Solution.**
1. Unread = received minus read = 2500 - 1500 = 1000. `rwnd = 5000 - 1000 = 4000`.
2. In flight = LastByteSent - LastByteAcked = 4000 - 2500 = 1500. Usable = 4000 - 1500 = 2500 bytes.
3. After the 1500 bytes arrive: received = 4000, unread = 4000 - 1500 = 2500. The app reads 2000 more: unread = 500; new `rwnd = 5000 - 500 = 4500`.

Section 1 of the code does the same style of calculation with different numbers (buffer 4000, 3000 received, 1200 read gives rwnd 2200 and usable 1200).

**Silly window check.** With buffer 5000 and MSS 1460 the receiver should not advertise a reopened window until free space reaches min(1460, 2500) = 1460 bytes.

## Key Rules / Gotchas Recap
- `rwnd` = free buffer space, in bytes, carried in every ACK.
- The sender may have at most rwnd unacknowledged bytes; usable = rwnd - in flight.
- Real limit is min(rwnd, cwnd).
- rwnd = 0 means stop; the sender probes with the persist timer so a lost update cannot deadlock the connection.
- Silly window: receiver should advertise 0 until free space >= min(MSS, buffer/2); sender should not send runts.
- Nagle: one unacknowledged small segment at a time. Delayed ACK: wait to piggyback the ACK. Together they can stall write-write-read traffic.
- Prefer one `send` for a whole request; use `TCP_NODELAY` for interactive request/response code.
- 16-bit window = 65535; window scaling raises it.

## Why This Matters
Mysterious 40 ms to 200 ms latency in an RPC or model-serving call is very often Nagle plus delayed ACK, and a stalled consumer filling the receive buffer is the usual reason a streaming producer "hangs" (zero window). Back-pressure in real systems, from sockets up through message queues, is the same idea as `rwnd`.
