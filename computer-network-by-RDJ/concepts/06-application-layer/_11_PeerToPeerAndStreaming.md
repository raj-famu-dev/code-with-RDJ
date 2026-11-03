# `_11_PeerToPeerAndStreaming.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
In a peer-to-peer (P2P) application every participant is both a client and a server: peers download from and upload to each other, so capacity grows with the number of users instead of overloading one server. This file covers P2P file distribution (BitTorrent: pieces, trackers, the Kademlia DHT), the formulas that show why P2P scales, multimedia streaming (RTP/RTSP and adaptive bitrate over HTTP) and WebSockets, the bidirectional channel behind live web apps.

**P2P architecture.** There is no (or minimal) always-on server. Peers find each other, either through a directory (a tracker or index server: a hybrid design) or through a distributed structure such as a DHT (a structured overlay). The overlay network is the logical graph of peers over the Internet. Advantages: scalability, no single point of failure, cost spread over users. Disadvantages: churn (peers join and leave), free riding, harder security and management, untrusted data.

**BitTorrent.** A file is split into equal pieces (chunks). A small metainfo (`.torrent`) file holds the file name, size, piece length, the SHA-1 hash of every piece (v2 uses SHA-256) and the tracker address; a magnet link carries the hash that identifies the torrent so the metainfo can be fetched from peers. All peers sharing a torrent form a swarm: seeders have the whole file, leechers are still downloading. A tracker returns a list of peers; the peer then connects to some of them and exchanges messages saying which pieces each has. Policies: rarest first (request the piece with fewest copies in the swarm) keeps the file complete and balanced; tit-for-tat choking (upload to the peers that give you the best download rates, plus one random "optimistic unchoke" to try newcomers) rewards contribution. Every received piece is checked against its hash before being accepted and re-shared.

**Kademlia DHT.** A distributed hash table stores (key, value) pairs across many nodes without a central server; in BitTorrent a key is a torrent's info-hash and values are peer addresses. Node ids and keys are numbers (160 bits in BitTorrent). The distance between two ids is their XOR interpreted as an integer: symmetric, zero only for identical ids, and ids with a long common prefix are close. Each node keeps k-buckets: for each bit position i, up to k contacts whose distance from it lies in [2^i, 2^(i+1)). To look up a key, a node asks the closest nodes it knows for nodes even closer to the key, repeating until no closer node appears; each step halves the remaining distance, so the cost is O(log N) messages. The value is stored on the k nodes closest to the key.

**Distribution time (Kurose-style).** Server upload rate u_s, N peers, file size F, peer upload u_i, slowest peer download d_min.
- Client-server: D_cs >= max( N F / u_s , F / d_min ). The server must send N copies, so the time grows linearly with N.
- P2P: D_p2p >= max( F / u_s , F / d_min , N F / (u_s + sum of u_i) ). The total upload capacity grows with N, so the third term stays small.
These are lower bounds; they are achievable with a good scheduler.

**Streaming.** Stored audio/video is played while it downloads; a playout buffer hides jitter, and the stream must be reachable within tight delay limits only for interactive uses (calls: about 150 ms one way is the usual comfort limit; stored video tolerates seconds). RTP (over UDP) carries media with sequence numbers and timestamps; RTCP carries quality reports; RTSP (TCP 554) is the remote control with SETUP, PLAY, PAUSE and TEARDOWN. Modern video on demand mostly uses HTTP-based adaptive bitrate streaming (HLS with `.m3u8` playlists, MPEG-DASH with `.mpd` manifests): the video is cut into segments of a few seconds, each encoded at several bitrates; the player downloads each segment at the bitrate it thinks the connection can sustain. Advantages: works through firewalls and CDNs, no special server, adapts to changing bandwidth; cost: some delay (live streams are tens of seconds behind unless tuned) and lower quality when the link is poor.

**WebSocket (RFC 6455).** HTTP is request-response; WebSocket gives a persistent, full-duplex connection over a single TCP connection for chat, games and live feeds. It starts as an HTTP/1.1 request with `Upgrade: websocket`, `Connection: Upgrade`, `Sec-WebSocket-Key` (a random base64 value) and `Sec-WebSocket-Version: 13`. The server replies `101 Switching Protocols` with `Sec-WebSocket-Accept` = base64( SHA-1( key + the fixed GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11` ) ). After that both sides exchange frames: byte 0 holds FIN and a 4-bit opcode (1 text, 2 binary, 8 close, 9 ping, 10 pong); byte 1 holds the MASK bit and a 7-bit length (126 means a 16-bit length follows, 127 a 64-bit length). Frames from the client are masked with a random 4-byte key (XOR), frames from the server are not. The handshake proof is not security: use `wss://` (WebSocket over TLS).

**Typical exam questions.** Compare client-server and P2P; compute the distribution time for both with given rates; explain how BitTorrent works (tracker, swarm, rarest first, tit-for-tat); how does a DHT find a key; what is adaptive streaming; why does RTP use UDP; what is the WebSocket handshake.

## Full Line-by-Line Breakdown

### SECTION 1: P2P ARCHITECTURE AND BITTORRENT VOCABULARY
Two small drawings (star versus mesh) and a glossary of torrent, piece, swarm, tracker, DHT, rarest first and tit-for-tat, followed by the weak points of P2P.

Output from a real run:

```text
===== SECTION 1: P2P ARCHITECTURE AND BITTORRENT VOCABULARY =====
  client-server                         peer-to-peer (BitTorrent swarm)
      S                                   P1 <-> P2
    / | \                                  ^ \   / ^
  C1 C2 C3   (all load on S)              v   \ /  v
                                          P3 <-> P4   (every peer also uploads)
  torrent / metainfo small file: file name, size, piece length, SHA-1 hash of EVERY piece, tracker URL
  piece (chunk)      fixed-size slice of the file (typically 256 KiB to a few MiB); the unit of exchange
  swarm              all peers sharing one torrent;  seeder = has the whole file, leecher = still downloading
  tracker            server that lists the peers of a torrent (it never holds the file itself)
  DHT                distributed hash table (Kademlia): finds peers with NO tracker, spread over all peers
  rarest first       ask first for the piece with the fewest copies in the swarm, so no piece disappears
  tit-for-tat        upload more to peers that upload to you (choking/unchoking), discourages free riders
P2P is scalable: each new peer brings upload capacity as well as demand.
Weak points: peers come and go (churn), free riders, legal and trust issues, no
central control. Always verify the data you receive (Section 4).
```

### SECTION 2: HOW LONG DOES DISTRIBUTION TAKE? (FORMULAS)
`d_client_server` and `d_p2p` implement the two formulas. The parameters are F = 15 Gbit (1.875 GB), u_s = 30 Mbit/s, d_min = 2 Mbit/s and a peer upload of 300 kbit/s. Results in hours: with 10 peers both are limited by the slowest download link (F / d_min = 7500 s = 2.08 h), so P2P gains nothing. With 100 peers the server needs 13.89 h but the swarm 6.94 h. At 1000 peers it is 138.89 h against 12.63 h, and at 10 000 peers 1388.89 h against 13.75 h: the client-server time grows tenfold with every tenfold N, while the P2P time flattens toward F / u_peer. The assertions compare the code with hand arithmetic: 1000 x 15e9 / 30e6 = 500 000 s and 15e12 / 330e6 = 45 454.5 s.

Output from a real run:

```text
===== SECTION 2: HOW LONG DOES DISTRIBUTION TAKE? (FORMULAS) =====
F = file size (bits), N = peers, u_s = server upload rate, u_i = peer upload rate,
d_min = slowest peer download rate.
  client-server: D_cs >= max( N*F / u_s ,  F / d_min )
  P2P          : D_p2p >= max( F / u_s ,  F / d_min ,  N*F / (u_s + sum(u_i)) )

Worked example: F = 15 Gbit (1.875 GB), u_s = 30 Mbit/s, d_min = 2 Mbit/s, u = 300 kbit/s
     N   client-server (h)     P2P (h)
    10                2.08        2.08
   100               13.89        6.94
  1000              138.89       12.63
 10000             1388.89       13.75
check: OK (N=1000: 500000 s vs 45454.5 s by hand; N=10 both limited by d_min = 7500 s)
Client-server time grows LINEARLY with N; P2P time levels off near F/u as N grows,
because every new peer adds upload capacity. For small N the slowest download link wins.
```

### SECTION 3: A BITTORRENT-STYLE SWARM SIMULATION
A round-based model: 1 seed and 7 leechers, 16 pieces, each peer uploads at most 1 piece and downloads at most 1 piece per round. `run_swarm(p2p=False)` lets only the seed upload (client-server), giving exactly 16 x 7 = 112 rounds. In P2P mode each uploader (seed first, then the other peers in a seeded random order) chooses the neediest receiver that still lacks something it holds, then sends the rarest piece among those (the piece with the fewest copies, `copies[p]`). The progress bars show leechers' pieces growing faster and faster as peers start to upload to each other; all finish in 20 rounds against 112. This is a toy model with equal rates and no churn or choking, so the number 20 is a property of this model only.

Output from a real run:

```text
===== SECTION 3: A BITTORRENT-STYLE SWARM SIMULATION =====
1 seed + 7 leechers, 16 pieces. Each round every peer may upload 1 piece
and download 1 piece. Rounds until every leecher has everything (seeded, repeatable).
P2P swarm progress:
  round   4:  13/112 pieces held by leechers |###                           |
  round   8:  39/112 pieces held by leechers |##########                    |
  round  12:  63/112 pieces held by leechers |################              |
  round  16:  90/112 pieces held by leechers |########################      |
  round  20: 112/112 pieces held by leechers |##############################|
rounds needed: client-server (seed uploads alone) = 112, P2P swarm = 20
check: OK (client-server must be 16 x 7 = 112 rounds; the swarm is much faster)
Rarest-first matters: if the only copy of a piece leaves, nobody can finish.
```

### SECTION 4: TRAP - NEVER TRUST A PIECE WITHOUT ITS HASH
A 10 000-byte pseudo-random file is cut into 1024-byte pieces (10 pieces, the last has 784 bytes) and the SHA-1 of every piece is stored, as the metainfo would. One piece is damaged in transit. A client that accepts everything ends up with a wrong file without noticing. A client that hashes each piece detects piece 3 and re-requests it from another peer. The hash list must come from a trusted source, otherwise an attacker can supply matching hashes for poisoned data.

Output from a real run:

```text
===== SECTION 4: TRAP - NEVER TRUST A PIECE WITHOUT ITS HASH =====
file 10000 bytes, piece length 1024 -> 10 pieces (last is 784 bytes)
first 3 piece hashes (from the metainfo): ['eef045c0cf...', '44910a75f7...', '9259ec1846...']
peer sent piece 3 with one byte damaged (all 8 bits inverted).
naive client (no check) accepts every piece; is the assembled file correct? False
verifying client finds corrupt pieces: [3] -> re-download them from another peer
check: OK (a single damaged byte changes the whole SHA-1, so the bad piece is caught)
BitTorrent v1 uses SHA-1 per piece; v2 uses SHA-256. The hash list is the trust anchor,
so it must come from a source you trust (the .torrent or magnet link).
```

### SECTION 5: DHT AND KADEMLIA XOR DISTANCE
First the 4-bit examples: 1011 XOR 1010 = 1 (close), 1011 XOR 0011 = 8 (far). Then 200 nodes with random 16-bit ids; each node keeps up to k = 4 contacts for each bit position (bucket index = position of the highest differing bit), so each node knows only 21 to 32 of the other 199 nodes. `lookup` starts with the k closest contacts the initiator knows, queries up to alpha = 3 of the closest unqueried nodes at a time, merges their answers and stops when all of the k closest are queried. Each RPC is counted. In this simulation all 200 random lookups found the true closest node, with mean 6.8 and maximum 10 RPCs, close to log2(200) = 7.6. These figures come from this simulated network, with idealised random buckets and no failures.

Output from a real run:

```text
===== SECTION 5: DHT AND KADEMLIA XOR DISTANCE =====
Kademlia gives every node and every key a number (here 16 bits). The DISTANCE between
two ids is their bitwise XOR read as a number: nodes sharing a long prefix are close.
  d(1011,1010) =  1 (share 3 leading bits -> very close)
  d(1011,0011) =  8 (differ in the first bit -> far)
  symmetric: d(a,b)==d(b,a): True;  d(a,a) = 0;  for one target every node has a different distance

200 nodes, k=4 contacts per bucket (one bucket per bit position): a node knows only 21..32 of the other 199
A lookup asks the closest known nodes for even closer ones until nobody knows better:
  start=0011011100110001 key=0100001011000110 -> found 0100001001010011 (correct), 7 RPCs
  start=0110010010100111 key=1111001010110111 -> found 1111001001010001 (correct), 9 RPCs
  start=1100101000101010 key=0010000110001100 -> found 0010000001010111 (correct), 9 RPCs
  start=1100010110111000 key=0000011010111101 -> found 0000011001011111 (correct), 7 RPCs
over 200 lookups in THIS simulation: 200 found the true closest node, mean RPCs = 6.8, max = 10
log2(200) = 7.6: lookup cost grows with the LOGARITHM of the network size,
not with its size. Peers for a torrent are stored on the nodes closest to its info-hash.
```

### SECTION 6: STREAMING AND ADAPTIVE BITRATE
Text on stored, live and interactive media, RTSP/RTP/RTCP, and adaptive streaming. The model: 12 segments of 4 s, a bitrate ladder of 300, 750, 1500 and 3000 kbit/s, and a hand-written throughput trace that dips below 1 Mbit/s in the middle. For each segment: download time = 4 s x bitrate / throughput; the playout buffer (seconds of video ready) is reduced by the download time and increased by 4 s; if the download takes longer than the buffer holds, the player stalls for the difference. The fixed 3000 kbit/s player stalls for 77.9 s in total. The adaptive player picks the highest bitrate not above 80 percent of the last measured throughput (and the lowest when the buffer is under one segment); it never stalls, at an average of 938 kbit/s. The trace is invented for the demonstration.

Output from a real run:

```text
===== SECTION 6: STREAMING AND ADAPTIVE BITRATE =====
Stored video (YouTube-style) vs live vs interactive (VoIP/video call): the tighter the
delay limit, the less buffering is possible. A playout buffer hides network jitter.
RTSP (TCP 554) = remote control (SETUP/PLAY/PAUSE); RTP over UDP = the media itself;
RTCP = quality feedback. Most video on demand today instead uses plain HTTP:
  video is cut into short SEGMENTS (here 4 s), each encoded at several bitrates;
  a manifest lists them (HLS: .m3u8 playlist, DASH: .mpd XML); the PLAYER picks the
  bitrate for every segment from measured throughput = adaptive bitrate (ABR).
  Because it is HTTP, CDNs and caches work, and no special server is needed.

Bitrate ladder [300, 750, 1500, 3000] kbit/s; link throughput per segment (kbit/s):
   [2800, 2600, 2000, 900, 500, 400, 700, 1200, 2500, 3200, 3500, 3000]
policy         startup(s)  stalled(s)  avg kbit/s   chosen bitrates
fixed 3000            4.3        77.9        3000   [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000]
adaptive              0.4         0.0         938   [300, 1500, 1500, 1500, 300, 300, 300, 300, 750, 1500, 1500, 1500]
check: OK (adaptive stalls less, at the price of lower quality when the link is poor)
Rule used: pick the highest bitrate <= 0.8 x last measured throughput, lowest when the
buffer is under one segment. Real players use buffer-based and hybrid algorithms; this
is a model with a made-up throughput trace, not a measurement of any service.
```

### SECTION 7: WEBSOCKETS
`accept_key` computes the handshake value with `hashlib.sha1` and `base64`, and it equals the RFC 6455 sample (`s3pPLMBiTxaQ9kYGzzhZRbK+xOo=` for key `dGhlIHNhbXBsZSBub25jZQ==`). `encode_frame` builds frames: header byte `0x80 | opcode` (FIN=1), the length (1, 3 or 9 bytes, with the mask bit), and for client frames the 4-byte mask key followed by the payload XOR the key. The two frames for text `Hello` equal the RFC's examples (`81 05 48 65 6c 6c 6f` and `81 85 37 fa 21 3d 7f 9f 4d 51 58`). A 200-byte payload needs the 2-byte length form (`7e 00 c8`). The loopback demo: a thread accepts a connection, parses the HTTP Upgrade request, answers `101 Switching Protocols` with the computed accept value, reads a masked frame, echoes it and answers the close frame. The client verifies the accept value itself. To make the output repeatable, the demo uses the RFC sample key and mask (a real client uses random ones).

Output from a real run:

```text
===== SECTION 7: WEBSOCKETS =====
WebSocket (RFC 6455): a full-duplex message channel over ONE TCP connection, started with
an HTTP/1.1 Upgrade request, then both sides can send at any time (chat, live data).
accept = base64( SHA-1( client key + GUID ) )
client key : dGhlIHNhbXBsZSBub25jZQ==
GUID       : 258EAFA5-E914-47DA-95CA-C5AB0DC85B11
computed   : s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
RFC sample : s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
check: OK (matches the RFC 6455 section 1.3 example)
The accept value only proves the server understood WebSocket (not a confused HTTP server);
it is NOT authentication or encryption. Use wss:// (TLS) for that.

frame bytes for text 'Hello' (opcode 1, FIN=1):
  unmasked (server -> client): 81 05 48 65 6c 6c 6f
  masked   (client -> server): 81 85 37 fa 21 3d 7f 9f 4d 51 58  <- mask key 37 fa 21 3d
check: OK (both match the examples in RFC 6455 section 5.7)
Header: byte0 = FIN + opcode (1 text, 2 binary, 8 close, 9 ping, 10 pong);
byte1 = MASK bit + length (<126 direct, 126 -> next 2 bytes, 127 -> next 8 bytes).
Client frames MUST be masked (a defence against cache-poisoning proxies); server frames are not.
200-byte payload header: 81 7e 00 c8 (81 7e 00 c8: length 200 in 2 bytes)

loopback handshake:
  client sent: GET /chat HTTP/1.1 + Upgrade: websocket + Sec-WebSocket-Key
  server said : HTTP/1.1 101 Switching Protocols
   Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
  client received frame: opcode=1 payload=b'echo: Hello'
  server closed with opcode 8 (8 = close)
  server got: GET /chat HTTP/1.1 | Upgrade=websocket | key=dGhlIHNhbXBsZSBub25jZQ==
  server frame: opcode=1 payload=b'Hello'
check: OK (handshake verified by the client, message echoed, clean close)
thread finished: True
```

## Worked Example
**Problem.** A 1 GB file (8 Gbit) is distributed from a server with u_s = 20 Mbit/s. Every peer can upload u = 1 Mbit/s and download at least d_min = 4 Mbit/s. Compute the minimum time for N = 50 peers with (a) client-server, (b) P2P. Also: what is the XOR distance between node ids 0110 and 0011, and which of 0111 and 1110 is closer to 0110?

**Solution.** (a) N F / u_s = 50 x 8000 Mbit / 20 Mbit/s = 20 000 s; F / d_min = 2000 s; D_cs = max = 20 000 s (5.56 h). (b) F / u_s = 400 s; F / d_min = 2000 s; N F / (u_s + N u) = 400 000 / (20 + 50) = 5714.3 s; D_p2p = max = 5714.3 s (1.59 h). XOR: 0110 XOR 0011 = 0101 = 5. Distance of 0111 to 0110 is 0001 = 1; of 1110 to 0110 is 1000 = 8, so 0111 is closer (only the last bit differs). The same formulas are checked by assertions in Section 2 and the XOR examples are in Section 5.

## Key Rules / Gotchas Recap
- Client-server time grows with N; P2P time is limited by total upload capacity, so it flattens.
- Always the maximum of the terms; for small N the slowest peer's download rate dominates.
- BitTorrent: pieces, per-piece SHA-1, tracker/DHT for finding peers, rarest first, tit-for-tat.
- Verify every piece with its hash; never trust data from a peer.
- Kademlia distance = XOR of ids; lookups take O(log N) steps.
- Adaptive streaming = short segments, several bitrates, manifest, the player decides.
- RTP/UDP for real-time media, RTSP for control; HTTP segments for video on demand.
- WebSocket accept = base64(SHA-1(key + GUID)); client frames are masked; use wss:// for security.

## Why This Matters
Peer-to-peer and DHT ideas appear in distributed systems (model weight and dataset distribution, service discovery, blockchains), and adaptive streaming is how almost all video reaches users. WebSockets carry the streaming responses of many chat and AI applications, so being able to read the handshake and frames helps when debugging them. Hash-checking untrusted pieces is the same integrity habit needed in any supply chain.
