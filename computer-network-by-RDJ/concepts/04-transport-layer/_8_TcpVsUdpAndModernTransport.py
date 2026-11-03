# Tags: #Python #ComputerNetworks #TransportLayer #TcpUdpModernTransport | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TCP vs UDP comparison and when to use which, head-of-line blocking illustrated by a
small simulation, reliability rebuilt on top of UDP (real loopback stop-and-wait), and
overviews of SCTP (multi-streaming, multi-homing) and QUIC (0-RTT, streams, built-in
TLS). SCTP and QUIC are described, not implemented."""
import socket
import threading

HOST = "127.0.0.1"

# ===== SECTION 1: COMPARISON AND WHEN TO USE WHICH =====
print("===== SECTION 1: TCP VS UDP COMPARISON AND CHOOSING =====")
rows = [
    ("connection", "connection-oriented (handshake)", "connectionless"),
    ("reliability", "ACKs + retransmission", "none (best effort)"),
    ("ordering", "in order", "not guaranteed"),
    ("data unit", "byte stream (no boundaries)", "datagrams (boundaries kept)"),
    ("header", "20 to 60 bytes", "8 bytes"),
    ("flow control", "yes (rwnd)", "no"),
    ("congestion control", "yes (cwnd)", "no (app must do it)"),
    ("broadcast/multicast", "no (point to point)", "yes"),
    ("speed/latency", "slower start, extra delay on loss", "fast, no setup"),
    ("typical use", "web, email, file transfer, SSH", "DNS, DHCP, VoIP, games, QUIC"),
]
print(f"{'feature':<20} {'TCP':<36} {'UDP'}")
print("-" * 80)
for f, t, u in rows:
    print(f"{f:<20} {t:<36} {u}")


def choose(needs_reliable: bool, tolerates_loss: bool, small_request_response: bool,
           realtime: bool, multicast: bool) -> str:
    """A teaching heuristic, not a law."""
    if multicast:
        return "UDP (only it supports multicast/broadcast)"
    if realtime and tolerates_loss:
        return "UDP (a retransmitted old packet is useless late)"
    if small_request_response and tolerates_loss:
        return "UDP (one datagram each way beats a handshake)"
    if needs_reliable:
        return "TCP (do not rebuild reliability yourself)"
    return "UDP or QUIC (reliability built by the app/protocol)"


cases = {
    "web page download": (True, False, False, False, False),
    "DNS lookup": (False, True, True, False, False),
    "live voice call": (False, True, False, True, False),
    "bank transfer API": (True, False, True, False, False),
    "IPTV to many viewers": (False, True, False, True, True),
}
print("\nwhen to use which (heuristic):")
for name, args in cases.items():
    print(f"  {name:<22} -> {choose(*args)}")
assert choose(*cases["web page download"]).startswith("TCP")
assert choose(*cases["live voice call"]).startswith("UDP")
print("check: web=TCP, voice=UDP: OK")


# ===== SECTION 2: HEAD-OF-LINE BLOCKING =====
print("\n===== SECTION 2: HEAD-OF-LINE BLOCKING (SIMULATION) =====")
print("Three streams (A, B, C) share one connection. Packets are sent 1 per 10 ms, one-way delay 20 ms.")
SEND_GAP, DELAY = 10, 20
packets = [(i, "ABC"[i % 3]) for i in range(12)]  # packet i belongs to stream A, B or C
LOST = 4  # packet 4 (stream B) is lost on its first transmission
arrive = {i: i * SEND_GAP + DELAY for i, _ in packets}
# the sender learns of the loss about one RTT later and resends; the copy arrives 3 one-way delays after the original send
arrive[LOST] = LOST * SEND_GAP + 3 * DELAY
print(f"packet {LOST} (stream {packets[LOST][1]}) is lost; its retransmission arrives at t={arrive[LOST]} ms "
      f"instead of t={LOST * SEND_GAP + DELAY} ms (model: one extra RTT of 2 x {DELAY} ms)")

# TCP: one ordered byte stream -> a packet is delivered only after ALL earlier packets
tcp_deliver: dict[int, int] = {}
latest = 0
for i, _ in packets:
    latest = max(latest, arrive[i])
    tcp_deliver[i] = latest
# QUIC / SCTP-style: ordering only inside each stream
quic_deliver: dict[int, int] = {}
stream_latest = {"A": 0, "B": 0, "C": 0}
for i, s in packets:
    stream_latest[s] = max(stream_latest[s], arrive[i])
    quic_deliver[i] = stream_latest[s]
print(f"{'pkt':>3} {'strm':>4} {'arrives':>8} {'TCP delivers':>13} {'QUIC delivers':>14} {'TCP extra wait':>15}")
for i, s in packets:
    extra = tcp_deliver[i] - arrive[i]
    print(f"{i:>3} {s:>4} {arrive[i]:>8} {tcp_deliver[i]:>13} {quic_deliver[i]:>14} {extra:>15}")
blocked_tcp = [i for i, _ in packets if tcp_deliver[i] > arrive[i]]
blocked_quic = [i for i, _ in packets if quic_deliver[i] > arrive[i]]
print("packets delayed by the loss: TCP", blocked_tcp, "| QUIC", blocked_quic)
streams_hit_tcp = sorted({packets[i][1] for i in blocked_tcp})
streams_hit_quic = sorted({packets[i][1] for i in blocked_quic})
print("streams hurt: TCP", streams_hit_tcp, "| QUIC", streams_hit_quic)
assert streams_hit_tcp == ["A", "B", "C"] and streams_hit_quic == ["B"]
print("check: TCP stalls every stream; independent streams stall only the stream that lost data: OK")
print("This is why HTTP/2 over TCP still suffers (many streams, one byte stream) and why HTTP/3 uses QUIC.")


# ===== SECTION 3: RELIABILITY REBUILT ON UDP (REAL LOOPBACK) =====
print("\n===== SECTION 3: RELIABILITY ON TOP OF UDP (REAL LOOPBACK, STOP-AND-WAIT) =====")
srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
srv.bind((HOST, 0))
srv.settimeout(0.3)
srv_port = srv.getsockname()[1]
stop = threading.Event()
delivered: list[bytes] = []


def reliable_receiver() -> None:
    dropped_once = False
    expected = 0
    while not stop.is_set():
        try:
            data, addr = srv.recvfrom(2048)
        except socket.timeout:
            continue
        seq, payload = data[0], data[1:]
        if seq == 2 and not dropped_once:
            dropped_once = True  # simulate a network loss of the FIRST copy of seq 2
            continue
        if seq == expected:
            delivered.append(payload)
            expected += 1
        srv.sendto(bytes([seq]), addr)  # ACK (also re-ACKs duplicates)


rt = threading.Thread(target=reliable_receiver)
rt.start()
cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cli.settimeout(0.15)  # retransmission timeout
retransmissions = 0
for seq, msg in enumerate([b"alpha", b"beta", b"gamma", b"delta"]):
    attempts = 0
    while True:
        attempts += 1
        cli.sendto(bytes([seq]) + msg, (HOST, srv_port))
        try:
            ack, _ = cli.recvfrom(16)
            if ack[0] == seq:
                break
        except socket.timeout:
            retransmissions += 1
            print(f"  seq {seq}: timeout -> retransmit (attempt {attempts + 1})")
    print(f"  seq {seq} {msg!r}: acknowledged after {attempts} attempt(s)")
stop.set()
rt.join(timeout=3)
cli.close()
srv.close()
print("receiver got, in order:", delivered)
print("retransmissions needed:", retransmissions)
assert delivered == [b"alpha", b"beta", b"gamma", b"delta"] and retransmissions == 1
print("check: all 4 messages delivered in order despite one dropped datagram: OK")
print("We needed sequence numbers + ACKs + a timer: that is TCP's job rebuilt by hand. Real")
print("protocols over UDP (QUIC, RTP, DNS retry logic) do exactly this, in a smarter way.")
print("Stop-and-wait sends one message per RTT; TCP/QUIC use windows to keep many in flight.")


# ===== SECTION 4: SCTP OVERVIEW =====
print("\n===== SECTION 4: SCTP OVERVIEW (DESCRIBED, NOT IMPLEMENTED) =====")
print("""SCTP (Stream Control Transmission Protocol, IP protocol number 132, now specified in RFC 9260,
which replaced RFC 4960): a transport protocol that mixes ideas from TCP and UDP.

  feature            SCTP                                        compared with
  message oriented   keeps message boundaries                    like UDP, unlike TCP
  reliable           SACK-based retransmission, congestion ctl   like TCP
  multi-streaming    many independent streams in ONE association  a lost message blocks only its
                     (per-stream ordering, optional unordered)    stream: no cross-stream HOL blocking
  multi-homing       an endpoint has SEVERAL IP addresses; a      TCP is tied to one IP pair; if that
                     failed path => traffic moves to another      path dies the connection dies
  setup              4-way handshake with a signed cookie        server keeps no state until the
                     (INIT, INIT-ACK, COOKIE-ECHO, COOKIE-ACK)   cookie returns: resists SYN floods
  term               'association' instead of 'connection'

Used in telecom signalling (SIGTRAN) and WebRTC data channels (SCTP carried inside DTLS over UDP).
Little general deployment on the open Internet because many NATs and firewalls drop unknown protocols.""")


# ===== SECTION 5: QUIC OVERVIEW =====
print("\n===== SECTION 5: QUIC OVERVIEW (DESCRIBED, NOT IMPLEMENTED) =====")
print("""QUIC (RFC 9000; TLS 1.3 integration in RFC 9001; loss recovery in RFC 9002; HTTP/3 in RFC 9114)
runs over UDP but provides reliable, ordered, congestion-controlled streams itself:

  - built-in TLS 1.3: transport and security handshake are combined; almost everything is encrypted
  - independent STREAMS: loss on one stream does not stall others (see Section 2)
  - connection IDs: a connection survives a change of IP/port (Wi-Fi -> mobile data)
  - runs in user space, so it can be updated without an OS upgrade
  - uses UDP because middleboxes block or mangle new IP protocols (SCTP's problem)""")
RTT = 50  # ms, model value
setups = [("TCP + TLS 1.2", 1 + 2), ("TCP + TLS 1.3", 1 + 1), ("QUIC (new server)", 1), ("QUIC 0-RTT (resumed)", 0)]
print(f"round trips BEFORE the first request byte can be sent (model, RTT = {RTT} ms):")
for name, rtts in setups:
    print(f"  {name:<22} {rtts} RTT = {rtts * RTT:>3} ms handshake  (+ {RTT} ms for the response)")
print("0-RTT trap: early data can be replayed by an attacker, so only idempotent requests (a GET")
print("of public data) belong in 0-RTT. Never a payment. The server must apply replay protection.")
print("Typical rule of thumb for modern apps: web = HTTP/3 (QUIC) with fallback to TCP; most")
print("other bulk or transactional traffic = TCP; low-latency datagrams = UDP.")
