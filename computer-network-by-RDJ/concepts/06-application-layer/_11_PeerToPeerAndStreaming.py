# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches peer-to-peer file distribution (BitTorrent chunks, rarest-first, hash
checks, DHT / Kademlia XOR distance), the client-server vs P2P time formulas,
streaming (RTP/RTSP, adaptive bitrate DASH/HLS idea) and the WebSocket handshake
(Sec-WebSocket-Accept, RFC 6455). Simulations are in memory; the WebSocket demo
uses a loopback server written here (127.0.0.1, port 0).
Syllabus idea: P2P applications, multimedia streaming, WebSockets.
"""
import base64
import hashlib
import math
import random
import socket
import threading

HOST = "127.0.0.1"

# ===== SECTION 1: P2P ARCHITECTURE AND BITTORRENT VOCABULARY =====
print("===== SECTION 1: P2P ARCHITECTURE AND BITTORRENT VOCABULARY =====")
print("""  client-server                         peer-to-peer (BitTorrent swarm)
      S                                   P1 <-> P2
    / | \\                                  ^ \\   / ^
  C1 C2 C3   (all load on S)              v   \\ /  v
                                          P3 <-> P4   (every peer also uploads)""")
for term, meaning in [
    ("torrent / metainfo", "small file: file name, size, piece length, SHA-1 hash of EVERY piece, tracker URL"),
    ("piece (chunk)", "fixed-size slice of the file (typically 256 KiB to a few MiB); the unit of exchange"),
    ("swarm", "all peers sharing one torrent;  seeder = has the whole file, leecher = still downloading"),
    ("tracker", "server that lists the peers of a torrent (it never holds the file itself)"),
    ("DHT", "distributed hash table (Kademlia): finds peers with NO tracker, spread over all peers"),
    ("rarest first", "ask first for the piece with the fewest copies in the swarm, so no piece disappears"),
    ("tit-for-tat", "upload more to peers that upload to you (choking/unchoking), discourages free riders")]:
    print(f"  {term:<19}{meaning}")
print("P2P is scalable: each new peer brings upload capacity as well as demand.")
print("Weak points: peers come and go (churn), free riders, legal and trust issues, no")
print("central control. Always verify the data you receive (Section 4).")

# ===== SECTION 2: HOW LONG DOES DISTRIBUTION TAKE? (FORMULAS) =====
print("\n===== SECTION 2: HOW LONG DOES DISTRIBUTION TAKE? (FORMULAS) =====")
print("F = file size (bits), N = peers, u_s = server upload rate, u_i = peer upload rate,")
print("d_min = slowest peer download rate.")
print("  client-server: D_cs >= max( N*F / u_s ,  F / d_min )")
print("  P2P          : D_p2p >= max( F / u_s ,  F / d_min ,  N*F / (u_s + sum(u_i)) )")
F, U_S, D_MIN, U = 15e9, 30e6, 2e6, 300e3          # 15 Gbit, 30 Mbit/s, 2 Mbit/s, 300 kbit/s


def d_client_server(n: int) -> float:
    return max(n * F / U_S, F / D_MIN)


def d_p2p(n: int) -> float:
    return max(F / U_S, F / D_MIN, n * F / (U_S + n * U))


print(f"\nWorked example: F = 15 Gbit (1.875 GB), u_s = 30 Mbit/s, d_min = 2 Mbit/s, u = 300 kbit/s")
print(f"{'N':>6}{'client-server (h)':>20}{'P2P (h)':>12}")
for n in (10, 100, 1000, 10000):
    print(f"{n:>6}{d_client_server(n) / 3600:>20.2f}{d_p2p(n) / 3600:>12.2f}")
assert d_client_server(1000) == 1000 * 15e9 / 30e6 == 500_000          # hand: 5e5 s
assert abs(d_p2p(1000) - 15e12 / 330e6) < 1e-6 and abs(d_p2p(1000) - 45454.545) < 1e-2
assert d_client_server(10) == 7500 and d_p2p(10) == 7500                # both limited by d_min
print("check: OK (N=1000: 500000 s vs 45454.5 s by hand; N=10 both limited by d_min = 7500 s)")
print("Client-server time grows LINEARLY with N; P2P time levels off near F/u as N grows,")
print("because every new peer adds upload capacity. For small N the slowest download link wins.")

# ===== SECTION 3: A BITTORRENT-STYLE SWARM SIMULATION =====
print("\n===== SECTION 3: A BITTORRENT-STYLE SWARM SIMULATION =====")
PIECES, LEECHERS = 16, 7
print(f"1 seed + {LEECHERS} leechers, {PIECES} pieces. Each round every peer may upload 1 piece")
print("and download 1 piece. Rounds until every leecher has everything (seeded, repeatable).")


def run_swarm(p2p: bool, verbose: bool = False) -> int:
    rng = random.Random(5)
    have = [set(range(PIECES))] + [set() for _ in range(LEECHERS)]        # peer 0 = seed
    rounds = 0
    while any(len(h) < PIECES for h in have):
        rounds += 1
        copies = [sum(p in h for h in have) for p in range(PIECES)]
        order = list(range(len(have)))
        rng.shuffle(order)
        if 0 in order:
            order.remove(0)
            order.insert(0, 0)                                           # seed picks first
        receiving: set[int] = set()
        moves = []
        for up in order:
            if not p2p and up != 0:
                continue                                                 # only the server uploads
            best = None
            for rx in range(1, len(have)):
                need = have[up] - have[rx]
                if rx in receiving or not need:
                    continue
                if best is None or len(have[rx]) < len(have[best[0]]):
                    best = (rx, need)
            if best:
                rx, need = best
                piece = min(need, key=lambda p: (copies[p], p))          # rarest first
                moves.append((rx, piece))
                receiving.add(rx)
        for rx, piece in moves:
            have[rx].add(piece)
        if verbose and (rounds % 4 == 0 or all(len(h) == PIECES for h in have)):
            done = sum(len(h) for h in have[1:])
            bar = "#" * (done * 30 // (PIECES * LEECHERS))
            print(f"  round {rounds:>3}: {done:>3}/{PIECES * LEECHERS} pieces held by leechers |{bar:<30}|")
    return rounds


print("P2P swarm progress:")
r_p2p = run_swarm(True, verbose=True)
r_cs = run_swarm(False)
print(f"rounds needed: client-server (seed uploads alone) = {r_cs}, P2P swarm = {r_p2p}")
assert r_cs == PIECES * LEECHERS == 112 and r_p2p < r_cs // 3
print(f"check: OK (client-server must be {PIECES} x {LEECHERS} = 112 rounds; the swarm is much faster)")
print("Rarest-first matters: if the only copy of a piece leaves, nobody can finish.")

# ===== SECTION 4: TRAP - NEVER TRUST A PIECE WITHOUT ITS HASH =====
print("\n===== SECTION 4: TRAP - NEVER TRUST A PIECE WITHOUT ITS HASH =====")
rng = random.Random(1)
blob = bytes(rng.randrange(256) for _ in range(10_000))
PLEN = 1024
pieces = [blob[i:i + PLEN] for i in range(0, len(blob), PLEN)]
hashes = [hashlib.sha1(p).hexdigest() for p in pieces]           # these live in the .torrent
print(f"file {len(blob)} bytes, piece length {PLEN} -> {len(pieces)} pieces (last is {len(pieces[-1])} bytes)")
print("first 3 piece hashes (from the metainfo):", [h[:10] + "..." for h in hashes[:3]])
received = list(pieces)
received[3] = bytes([received[3][0] ^ 0xFF]) + received[3][1:]    # a peer sends a damaged piece
print("peer sent piece 3 with one byte damaged (all 8 bits inverted).")
print("naive client (no check) accepts every piece; is the assembled file correct?", b"".join(received) == blob)
bad = [i for i, p in enumerate(received) if hashlib.sha1(p).hexdigest() != hashes[i]]
print("verifying client finds corrupt pieces:", bad, "-> re-download them from another peer")
received[3] = pieces[3]
assert not [i for i, p in enumerate(received) if hashlib.sha1(p).hexdigest() != hashes[i]]
assert b"".join(received) == blob
print("check: OK (a single damaged byte changes the whole SHA-1, so the bad piece is caught)")
print("BitTorrent v1 uses SHA-1 per piece; v2 uses SHA-256. The hash list is the trust anchor,")
print("so it must come from a source you trust (the .torrent or magnet link).")

# ===== SECTION 5: DHT AND KADEMLIA XOR DISTANCE =====
print("\n===== SECTION 5: DHT AND KADEMLIA XOR DISTANCE =====")
print("Kademlia gives every node and every key a number (here 16 bits). The DISTANCE between")
print("two ids is their bitwise XOR read as a number: nodes sharing a long prefix are close.")
a, b, c = 0b1011, 0b1010, 0b0011
print(f"  d(1011,1010) = {a ^ b:>2} (share 3 leading bits -> very close)")
print(f"  d(1011,0011) = {a ^ c:>2} (differ in the first bit -> far)")
print(f"  symmetric: d(a,b)==d(b,a): {a ^ b == b ^ a};  d(a,a) = {a ^ a};  for one target every node has a different distance")
assert a ^ b == 1 and a ^ c == 8
BITS, K, ALPHA, NODES = 16, 4, 3, 200
rng = random.Random(11)
node_ids = sorted(rng.sample(range(2 ** BITS), NODES))
table: dict[int, list[int]] = {}
for n in node_ids:
    buckets: dict[int, list[int]] = {}
    for m in node_ids:
        if m != n:
            buckets.setdefault((n ^ m).bit_length() - 1, []).append(m)   # bucket = highest differing bit
    table[n] = [x for i in sorted(buckets) for x in rng.sample(buckets[i], min(K, len(buckets[i])))]
sizes = [len(t) for t in table.values()]
print(f"\n{NODES} nodes, k={K} contacts per bucket (one bucket per bit position): a node knows only"
      f" {min(sizes)}..{max(sizes)} of the other {NODES - 1}")


def closest_known(node: int, target: int) -> list[int]:
    return sorted(table[node] + [node], key=lambda m: m ^ target)[:K]


def lookup(start: int, target: int) -> tuple[int, int]:
    short = closest_known(start, target)
    queried: set[int] = set()
    rpcs = 0
    while True:
        todo = [n for n in sorted(short, key=lambda m: m ^ target) if n not in queried][:ALPHA]
        if not todo:
            return min(short, key=lambda m: m ^ target), rpcs
        for n in todo:
            queried.add(n)
            rpcs += 1
            short = sorted(set(short) | set(closest_known(n, target)), key=lambda m: m ^ target)[:K]


print("A lookup asks the closest known nodes for even closer ones until nobody knows better:")
rng2 = random.Random(3)
hits, hop_list = 0, []
for i in range(200):
    start, target = rng2.choice(node_ids), rng2.randrange(2 ** BITS)
    found, rpcs = lookup(start, target)
    truth = min(node_ids, key=lambda m: m ^ target)
    hits += found == truth
    hop_list.append(rpcs)
    if i < 4:
        print(f"  start={start:016b} key={target:016b} -> found {found:016b} "
              f"({'correct' if found == truth else 'NOT the closest'}), {rpcs} RPCs")
print(f"over 200 lookups in THIS simulation: {hits} found the true closest node,"
      f" mean RPCs = {sum(hop_list) / len(hop_list):.1f}, max = {max(hop_list)}")
print(f"log2({NODES}) = {math.log2(NODES):.1f}: lookup cost grows with the LOGARITHM of the network size,")
print("not with its size. Peers for a torrent are stored on the nodes closest to its info-hash.")
assert max(hop_list) < 60 and hits >= 150

# ===== SECTION 6: STREAMING AND ADAPTIVE BITRATE =====
print("\n===== SECTION 6: STREAMING AND ADAPTIVE BITRATE =====")
print("Stored video (YouTube-style) vs live vs interactive (VoIP/video call): the tighter the")
print("delay limit, the less buffering is possible. A playout buffer hides network jitter.")
print("RTSP (TCP 554) = remote control (SETUP/PLAY/PAUSE); RTP over UDP = the media itself;")
print("RTCP = quality feedback. Most video on demand today instead uses plain HTTP:")
print("  video is cut into short SEGMENTS (here 4 s), each encoded at several bitrates;")
print("  a manifest lists them (HLS: .m3u8 playlist, DASH: .mpd XML); the PLAYER picks the")
print("  bitrate for every segment from measured throughput = adaptive bitrate (ABR).")
print("  Because it is HTTP, CDNs and caches work, and no special server is needed.")
LADDER = [300, 750, 1500, 3000]                                   # kbit/s
SEG = 4                                                           # seconds of video per segment
trace = [2800, 2600, 2000, 900, 500, 400, 700, 1200, 2500, 3200, 3500, 3000]   # kbit/s per segment


def play(policy: str) -> tuple[float, float, float, list[int]]:
    buffer, stall, startup, chosen = 0.0, 0.0, 0.0, []
    est = LADDER[0]
    for i, tput in enumerate(trace):
        if policy == "fixed 3000":
            rate = 3000
        else:
            ok = [r for r in LADDER if r <= 0.8 * est]
            rate = ok[-1] if ok and i > 0 else LADDER[0]
            if buffer < SEG and i > 0:
                rate = LADDER[0]                                  # nearly empty buffer: be safe
        dl = SEG * rate / tput                                    # seconds to download the segment
        if i == 0:
            startup, buffer = dl, float(SEG)
        else:
            stall += max(0.0, dl - buffer)
            buffer = max(0.0, buffer - dl) + SEG
        est = tput
        chosen.append(rate)
    return startup, stall, sum(chosen) / len(chosen), chosen


print(f"\nBitrate ladder {LADDER} kbit/s; link throughput per segment (kbit/s):")
print("  ", trace)
print(f"{'policy':<14}{'startup(s)':>11}{'stalled(s)':>12}{'avg kbit/s':>12}   chosen bitrates")
results = {}
for pol in ("fixed 3000", "adaptive"):
    st, stall, avg, chosen = play(pol)
    results[pol] = (st, stall, avg)
    print(f"{pol:<14}{st:>11.1f}{stall:>12.1f}{avg:>12.0f}   {chosen}")
assert results["adaptive"][1] < results["fixed 3000"][1]
print("check: OK (adaptive stalls less, at the price of lower quality when the link is poor)")
print("Rule used: pick the highest bitrate <= 0.8 x last measured throughput, lowest when the")
print("buffer is under one segment. Real players use buffer-based and hybrid algorithms; this")
print("is a model with a made-up throughput trace, not a measurement of any service.")

# ===== SECTION 7: WEBSOCKETS =====
print("\n===== SECTION 7: WEBSOCKETS =====")
print("WebSocket (RFC 6455): a full-duplex message channel over ONE TCP connection, started with")
print("an HTTP/1.1 Upgrade request, then both sides can send at any time (chat, live data).")
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"                     # fixed by the RFC


def accept_key(client_key: str) -> str:
    return base64.b64encode(hashlib.sha1((client_key + GUID).encode()).digest()).decode()


RFC_KEY, RFC_ACCEPT = "dGhlIHNhbXBsZSBub25jZQ==", "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
print("accept = base64( SHA-1( client key + GUID ) )")
print("client key :", RFC_KEY)
print("GUID       :", GUID)
print("computed   :", accept_key(RFC_KEY))
print("RFC sample :", RFC_ACCEPT)
assert accept_key(RFC_KEY) == RFC_ACCEPT
print("check: OK (matches the RFC 6455 section 1.3 example)")
print("The accept value only proves the server understood WebSocket (not a confused HTTP server);")
print("it is NOT authentication or encryption. Use wss:// (TLS) for that.")


def encode_frame(payload: bytes, opcode: int = 1, mask_key: bytes | None = None) -> bytes:
    n = len(payload)
    mbit = 0x80 if mask_key else 0
    if n < 126:
        head = bytes([0x80 | opcode, mbit | n])
    elif n < 65536:
        head = bytes([0x80 | opcode, mbit | 126]) + n.to_bytes(2, "big")
    else:
        head = bytes([0x80 | opcode, mbit | 127]) + n.to_bytes(8, "big")
    if mask_key:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
        return head + mask_key + payload
    return head + payload


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("closed early")
        buf += chunk
    return buf


def read_frame(sock: socket.socket) -> tuple[int, bytes]:
    b0, b1 = recv_exact(sock, 2)
    n = b1 & 0x7F
    if n == 126:
        n = int.from_bytes(recv_exact(sock, 2), "big")
    elif n == 127:
        n = int.from_bytes(recv_exact(sock, 8), "big")
    key = recv_exact(sock, 4) if b1 & 0x80 else None
    data = recv_exact(sock, n)
    if key:
        data = bytes(b ^ key[i % 4] for i, b in enumerate(data))
    return b0 & 0x0F, data


masked = encode_frame(b"Hello", mask_key=bytes.fromhex("37fa213d"))
unmasked = encode_frame(b"Hello")
print("\nframe bytes for text 'Hello' (opcode 1, FIN=1):")
print("  unmasked (server -> client):", unmasked.hex(" "))
print("  masked   (client -> server):", masked.hex(" "), " <- mask key 37 fa 21 3d")
assert unmasked == bytes.fromhex("810548656c6c6f")
assert masked == bytes.fromhex("818537fa213d7f9f4d5158")                 # RFC 6455 section 5.7
print("check: OK (both match the examples in RFC 6455 section 5.7)")
print("Header: byte0 = FIN + opcode (1 text, 2 binary, 8 close, 9 ping, 10 pong);")
print("byte1 = MASK bit + length (<126 direct, 126 -> next 2 bytes, 127 -> next 8 bytes).")
print("Client frames MUST be masked (a defence against cache-poisoning proxies); server frames are not.")
print("200-byte payload header:", encode_frame(b"x" * 200)[:4].hex(" "), "(81 7e 00 c8: length 200 in 2 bytes)")


def ws_server(listener: socket.socket, log: list[str]) -> None:
    conn, _ = listener.accept()
    conn.settimeout(5)
    with conn:
        request = b""
        while b"\r\n\r\n" not in request:
            request += conn.recv(1024)
        lines = request.decode().split("\r\n")
        hdr = {l.split(":", 1)[0].lower(): l.split(":", 1)[1].strip() for l in lines[1:] if ":" in l}
        log.append(f"server got: {lines[0]} | Upgrade={hdr['upgrade']} | key={hdr['sec-websocket-key']}")
        conn.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                      "Connection: Upgrade\r\nSec-WebSocket-Accept: "
                      + accept_key(hdr["sec-websocket-key"]) + "\r\n\r\n").encode())
        opcode, data = read_frame(conn)
        log.append(f"server frame: opcode={opcode} payload={data!r}")
        conn.sendall(encode_frame(b"echo: " + data))
        opcode, _ = read_frame(conn)                               # client's close frame
        if opcode == 8:
            conn.sendall(encode_frame(b"", opcode=8))


listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind((HOST, 0))
listener.listen(1)
listener.settimeout(5)
log: list[str] = []
th = threading.Thread(target=ws_server, args=(listener, log))
th.start()
try:
    with socket.create_connection(listener.getsockname(), timeout=5) as cs:
        cs.sendall(("GET /chat HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n"
                    "Connection: Upgrade\r\nSec-WebSocket-Key: " + RFC_KEY + "\r\n"
                    "Sec-WebSocket-Version: 13\r\n\r\n").encode())
        reply = b""
        while b"\r\n\r\n" not in reply:
            reply += cs.recv(1024)
        status = reply.decode().split("\r\n")[0]
        got = [l for l in reply.decode().split("\r\n") if l.lower().startswith("sec-websocket-accept")][0]
        print("\nloopback handshake:")
        print("  client sent: GET /chat HTTP/1.1 + Upgrade: websocket + Sec-WebSocket-Key")
        print("  server said :", status)
        print("  ", got)
        assert status.endswith("101 Switching Protocols") and got.split(": ")[1] == RFC_ACCEPT
        cs.sendall(encode_frame(b"Hello", mask_key=bytes.fromhex("37fa213d")))
        opcode, data = read_frame(cs)
        print(f"  client received frame: opcode={opcode} payload={data!r}")
        cs.sendall(encode_frame(b"", opcode=8, mask_key=bytes.fromhex("00000000")))
        opcode, _ = read_frame(cs)
        print(f"  server closed with opcode {opcode} (8 = close)")
finally:
    th.join(timeout=5)
    listener.close()
for line in log:
    print(" ", line)
assert data == b"echo: Hello"
print("check: OK (handshake verified by the client, message echoed, clean close)")
print("thread finished:", not th.is_alive())
