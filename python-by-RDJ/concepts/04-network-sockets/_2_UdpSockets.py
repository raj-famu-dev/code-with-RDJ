# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches UDP sockets: SOCK_DGRAM, sendto/recvfrom, no connection, and the key
contrast with TCP: UDP keeps message boundaries, TCP is a byte stream.
Loopback only (127.0.0.1), port 0, timeouts everywhere, threads joined.
"""
import socket
import threading

HOST = "127.0.0.1"

print("=== SECTION 1: a UDP server socket ===")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # DGRAM = datagram = UDP
server.settimeout(3)
server.bind((HOST, 0))                                       # no listen(), no accept()
port = server.getsockname()[1]
print("type:", server.type.name, "| bound host:", server.getsockname()[0])
print("UDP has no listen()/accept(): there is no connection to accept.")

def echo_n(count: int) -> None:
    for _ in range(count):
        data, addr = server.recvfrom(2048)                   # data AND who sent it
        server.sendto(b"ACK:" + data, addr)                  # reply to that address

t = threading.Thread(target=echo_n, args=(3,))
t.start()

print("\n=== SECTION 2: sendto / recvfrom (no connect needed) ===")
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(3)
for word in [b"alpha", b"beta", b"gamma"]:
    client.sendto(word, (HOST, port))                        # address given on every send
    reply, addr = client.recvfrom(2048)
    print("sent", word, "-> reply", reply, "| from port matches server:", addr[1] == port)
t.join(timeout=5)
print("server thread finished:", not t.is_alive())
server.close()

print("\n=== SECTION 3: message boundaries are PRESERVED in UDP ===")
rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.settimeout(3)
rx.bind((HOST, 0))
rx_addr = rx.getsockname()
tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for part in [b"one", b"two", b"three"]:
    tx.sendto(part, rx_addr)
got = [rx.recvfrom(2048)[0] for _ in range(3)]               # one recvfrom == one datagram
print("three sends, three separate receives:", got)
print("Each recvfrom() returned exactly one whole datagram.")

print("\n=== SECTION 4: contrast with TCP (a stream merges writes) ===")
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.settimeout(3)
lsock.bind((HOST, 0))
lsock.listen(1)
holder: list[bytes] = []

def tcp_reader() -> None:
    c, _ = lsock.accept()
    with c:
        c.settimeout(3)
        while True:
            d = c.recv(4096)
            if not d:
                break
            holder.append(d)

tt = threading.Thread(target=tcp_reader)
tt.start()
with socket.create_connection(lsock.getsockname(), timeout=3) as cs:
    for part in [b"one", b"two", b"three"]:
        cs.sendall(part)
tt.join(timeout=5)
lsock.close()
print("TCP total bytes received:", b"".join(holder))
print("TCP may deliver these as 1, 2 or 3 chunks; the exact split is NOT guaranteed,")
print("so we only claim the joined bytes. UDP's per-message guarantee is the difference.")

print("\n=== SECTION 5: TRAP - a small buffer truncates a datagram ===")
tx.sendto(b"0123456789", rx_addr)
try:
    chunk = rx.recvfrom(4)[0]                                # buffer smaller than datagram
    print("recvfrom(4) returned:", chunk, "<- the rest of the datagram is DISCARDED")
except OSError as e:
    print("platform raised", type(e).__name__)
rx.settimeout(0.3)
try:
    rx.recvfrom(2048)
except socket.timeout:
    print("second recvfrom -> timeout: the other 6 bytes are gone, not queued")

print("\n=== SECTION 6: UDP is unreliable by design (no connection, no delivery proof) ===")
lonely = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lonely.settimeout(0.3)
spare = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
spare.bind((HOST, 0))
dead_addr = spare.getsockname()
spare.close()                                                # nobody listens there now
lonely.sendto(b"hello?", dead_addr)                          # sendto succeeds regardless
print("sendto() to a dead port did NOT raise: UDP does not tell you.")
try:
    lonely.recvfrom(1024)
except socket.timeout:
    print("no reply: you need your own timeout/retry logic (or use TCP)")
except ConnectionRefusedError:
    print("some OSes surface an ICMP 'port unreachable' as ConnectionRefusedError")

for s in (client, rx, tx, lonely):
    s.close()
print("\nall sockets closed; threads joined")
