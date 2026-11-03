# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP flow control: receiver window (rwnd), byte-based sliding window, zero window
and window probes, silly window syndrome (trap and fix), Nagle's algorithm and its
clash with delayed ACK. A simulator with a slow reader; loopback only for one
TCP_NODELAY socket-option demo."""
import socket

HEADER = 40  # 20 bytes IP + 20 bytes TCP, no options (used for overhead arithmetic)

# ===== SECTION 1: THE RECEIVER WINDOW FORMULA =====
print("===== SECTION 1: THE RECEIVER WINDOW FORMULA =====")
print("rwnd = RcvBuffer - (LastByteRcvd - LastByteRead)   i.e. the FREE space in the receive buffer")
print("sender rule: LastByteSent - LastByteAcked <= rwnd   (never have more unacked data than rwnd)")
rcv_buffer = 4000
last_rcvd, last_read = 3000, 1200
rwnd = rcv_buffer - (last_rcvd - last_read)
print(f"example: buffer {rcv_buffer}, received up to byte {last_rcvd}, app has read up to {last_read}")
print(f"  unread = {last_rcvd - last_read}, rwnd = {rcv_buffer} - {last_rcvd - last_read} = {rwnd}")
last_sent, last_acked = 3000, 2000
inflight = last_sent - last_acked
print(f"sender: sent up to {last_sent}, acked up to {last_acked} -> in flight {inflight}")
print(f"  usable window = rwnd - in flight = {rwnd} - {inflight} = {rwnd - inflight} more bytes may be sent")
assert rwnd == 2200 and rwnd - inflight == 1200
print("check: hand arithmetic (rwnd 2200, usable 1200): OK")
print("flow control protects the RECEIVER's buffer; congestion control (topic 7) protects the NETWORK.")
print("effective sending limit = min(rwnd, cwnd).")
print("trap: rwnd is in BYTES and is the free space, not the buffer size and not the unread amount.")


# ===== SECTION 2: SLIDING WINDOW WITH A SLOW READER AND ZERO WINDOW =====
print("\n===== SECTION 2: SLIDING WINDOW, SLOW READER, ZERO WINDOW =====")
MSS = 1000
BUF = 4000
TOTAL = 10000
# bytes the application reads in each round (1 round = 1 RTT); zeros = the app is stalled
reads = [1500, 0, 0, 0, 2000, 4000, 4000, 4000, 4000, 4000]
sent = unread = 0
advertised = BUF
print(f"buffer {BUF}, MSS {MSS}, {TOTAL} bytes to send; 1 round = 1 RTT; window = free buffer space")
print(f"{'rnd':>3} {'rwnd seen':>9} {'sender sends':<28} {'unread':>6} {'app reads':>9} {'new rwnd':>8}")
r = 0
while sent < TOTAL and r < len(reads):
    seen = advertised
    if seen == 0:
        action = "ZERO WINDOW: 1-byte probe"
        unread_after_arrival = unread  # the probe byte is not accepted: no space
        n = 0
    else:
        n = min(seen, TOTAL - sent)
        segs = [min(MSS, n - i) for i in range(0, n, MSS)]
        action = f"{n} B = {'+'.join(map(str, segs))}"
        sent += n
        unread += n
        unread_after_arrival = unread
    rd = min(unread, reads[r])
    unread -= rd
    advertised = BUF - unread
    r += 1
    print(f"{r:>3} {seen:>9} {action:<28} {unread_after_arrival:>6} {rd:>9} {advertised:>8}")
print(f"sent {sent} of {TOTAL} bytes in {r} rounds")
assert sent == TOTAL
print("What happened:")
print("  round 1: full 4000-byte window used; the app only drained 1500, so the window shrank to 1500.")
print("  round 2: sender fills the 1500 it is allowed; the app is stalled, so the window becomes 0.")
print("  rounds 3-5: zero window -> sender STOPS sending data and only sends 1-byte probes.")
print("  The probe is driven by the persist timer: without it a lost 'window reopened' update would")
print("  leave both sides waiting forever (deadlock).")
print("  end of round 5: the app wakes up and reads; the receiver sends a window update (2000); the sender resumes.")
print("The sender never exceeded rwnd, so the receiver buffer never overflowed: that IS flow control.")


# ===== SECTION 3: SILLY WINDOW SYNDROME (TRAP AND FIX) =====
print("\n===== SECTION 3: SILLY WINDOW SYNDROME (TRAP AND FIX) =====")


def transfer(total: int, buf: int, mss: int, read_per_round: int, fix: bool) -> tuple[list[int], int]:
    """Full buffer at the start; the app drains read_per_round per round.
    fix=True: receiver advertises 0 until free >= min(mss, buf/2); sender never sends a runt."""
    unread, sent, advertised = 0, 0, buf
    sizes: list[int] = []
    rounds = 0
    while sent < total and rounds < 500:
        rounds += 1
        n = min(advertised, total - sent)
        if fix and n < min(mss, total - sent):
            n = 0  # sender-side rule: wait rather than send a tiny segment
        for i in range(0, n, mss):
            sizes.append(min(mss, n - i))
        sent += n
        unread += n
        unread -= min(unread, read_per_round if rounds > 1 else 0)
        free = buf - unread
        advertised = free
        if fix and free < min(mss, buf // 2):
            advertised = 0  # receiver-side rule: do not advertise a sliver
    return sizes, rounds


for label, fix in (("NAIVE (silly window)", False), ("FIXED (Clark + sender rule)", True)):
    sizes, rounds = transfer(8000, 4000, 1000, 100, fix)
    payload = sum(sizes)
    eff = payload / (payload + HEADER * len(sizes))
    small = sum(1 for s in sizes if s < 1000)
    print(f"{label}: {len(sizes)} segments, {small} runts (< 1000 B), "
          f"efficiency = {payload}/({payload}+{HEADER}x{len(sizes)}) = {eff:.1%}")
print("naive: the app frees 100 bytes, the receiver says 'window = 100', the sender obliges with a")
print("100-byte segment carrying 40 bytes of headers. Repeated forever = a silly window.")
print("fixes: receiver does not advertise until free space >= min(MSS, buffer/2) (Clark);")
print("       sender does not send until it can fill an MSS or half the max window (or has nothing more).")
print("(the sender-side fix is the same idea as Nagle's algorithm, next section)")


# ===== SECTION 4: NAGLE'S ALGORITHM AND DELAYED ACK =====
print("\n===== SECTION 4: NAGLE'S ALGORITHM VS DELAYED ACK (MODEL) =====")
print("Nagle: if unacked data is in flight, buffer new small writes until an ACK arrives")
print("       or a full MSS has accumulated. Goal: stop streams of 1-byte segments (telnet).")
print("Delayed ACK: the receiver waits (assumed below: 200 ms; real values vary by OS) hoping to")
print("       piggyback the ACK on response data, or ACKs at once on every second full segment.")
RTT_HALF = 5       # ms one way (model)
DELAYED_ACK = 200  # ms (assumed for the model)


def request_latency(nodelay: bool) -> int:
    """App writes a 10-byte header, then a 90-byte body, then waits for the reply (write-write-read)."""
    t = 0
    print(f"  --- TCP_NODELAY = {nodelay} ---")
    print(f"  t={t:>3} ms  app write #1 (10 B header) -> sent immediately (nothing in flight)")
    first_arrives = t + RTT_HALF
    print(f"  t={t:>3} ms  app write #2 (90 B body)", end="")
    if nodelay:
        print(" -> sent immediately (Nagle disabled)")
        second_arrives = t + RTT_HALF
        reply_sent = second_arrives
        print(f"  t={second_arrives:>3} ms  server has the full request, replies")
    else:
        print(" -> HELD by Nagle (unacked data in flight, segment is small)")
        ack_at = first_arrives + DELAYED_ACK
        print(f"  t={first_arrives:>3} ms  server got 10 B; has nothing to send yet -> delays its ACK")
        print(f"  t={ack_at:>3} ms  delayed-ACK timer fires, ACK sent")
        release = ack_at + RTT_HALF
        print(f"  t={release:>3} ms  client gets ACK, Nagle releases the 90 B body")
        second_arrives = release + RTT_HALF
        reply_sent = second_arrives
        print(f"  t={second_arrives:>3} ms  server has the full request, replies")
    done = reply_sent + RTT_HALF
    print(f"  t={done:>3} ms  client receives reply -> request latency {done} ms")
    return done


slow = request_latency(nodelay=False)
fast = request_latency(nodelay=True)
print(f"model result: {slow} ms vs {fast} ms, a stall of {slow - fast} ms caused ONLY by the clash")
assert slow - fast == DELAYED_ACK + 2 * RTT_HALF
print("check: extra delay = delayed-ACK timer + one extra round trip (ACK back, body out): OK")
print("Fixes: send the request with ONE write (join header+body: sendall(header+body)), or set")
print("TCP_NODELAY for latency-sensitive request/response code. Keep Nagle for bulk streams.")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print("real socket: TCP_NODELAY default =", s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY))
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print("after setsockopt(TCP_NODELAY, 1) =", s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY))
finally:
    s.close()
print("(0 = Nagle ON by default; no connection is opened for this demo)")
