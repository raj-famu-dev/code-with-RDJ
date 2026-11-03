# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Transport layer services: process-to-process delivery, port numbers (well-known,
registered, dynamic), sockets as IP+port, the 5-tuple, multiplexing and
demultiplexing, connection-oriented vs connectionless. Real loopback demo only
(127.0.0.1, port 0, timeouts, everything closed and joined)."""
import socket
import threading

HOST = "127.0.0.1"


# ===== SECTION 1: PORT NUMBER RANGES =====
print("===== SECTION 1: PORT NUMBER RANGES =====")


def port_class(port: int) -> str:
    """Classify a 16-bit port using the IANA ranges."""
    if not 0 <= port <= 65535:
        raise ValueError(f"port {port} does not fit in 16 bits")
    if port <= 1023:
        return "well-known (system)"
    if port <= 49151:
        return "registered (user)"
    return "dynamic / private / ephemeral"


print("A port is a 16-bit number: 2**16 =", 2 ** 16, "values (0..65535)")
well_known = {20: "FTP data", 21: "FTP control", 22: "SSH", 25: "SMTP", 53: "DNS",
              67: "DHCP server", 68: "DHCP client", 80: "HTTP", 110: "POP3",
              123: "NTP", 143: "IMAP", 443: "HTTPS"}
for p, name in well_known.items():
    print(f"  {p:>5}  {name:<12} -> {port_class(p)}")
for p in (1023, 1024, 3306, 8080, 49151, 49152, 65535):
    print(f"  {p:>5}  {'(boundary)':<12} -> {port_class(p)}")
try:
    port_class(65536)
except ValueError as e:
    print("trap: 65536 is invalid ->", e)
# cross-check with the OS services database (names only; depends on /etc/services)
for name, expected in (("http", 80), ("https", 443), ("smtp", 25)):
    try:
        assert socket.getservbyname(name, "tcp") == expected
        print(f"check: getservbyname({name!r}) == {expected}: OK")
    except OSError:
        print(f"check: services database has no {name!r} entry here (skipped)")


# ===== SECTION 2: PROCESS-TO-PROCESS DELIVERY AND MULTIPLEXING =====
print("\n===== SECTION 2: MULTIPLEXING / DEMULTIPLEXING (SIMULATED) =====")
print("IP gets a packet to the right HOST. The port gets the data to the right PROCESS.")
# A tiny model of what the OS does on receive: look at the destination port,
# then hand the payload to the process that bound that port.
bindings = {53: "dns-server", 80: "web-server", 5000: "my-chat-app"}
incoming = [("10.0.0.7", 40001, 80, "GET /"), ("10.0.0.8", 40002, 53, "A? example.com"),
            ("10.0.0.7", 40003, 5000, "hello"), ("10.0.0.9", 40004, 9999, "anyone?")]
for src_ip, src_port, dst_port, data in incoming:
    owner = bindings.get(dst_port)
    if owner:
        print(f"  {src_ip}:{src_port} -> port {dst_port}: deliver {data!r} to {owner}")
    else:
        print(f"  {src_ip}:{src_port} -> port {dst_port}: nobody bound -> dropped (UDP: ICMP "
              f"port unreachable; TCP: RST)")
print("Multiplexing = sender side: many apps share one IP, each tagged with a source port.")
print("Demultiplexing = receiver side: the destination port picks the process.")


# ===== SECTION 3: REAL LOOPBACK DEMO: OS-ASSIGNED PORTS AND THE 5-TUPLE =====
print("\n===== SECTION 3: REAL LOOPBACK: OS-ASSIGNED PORTS AND THE 5-TUPLE =====")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, 0))  # port 0 = "OS, pick any free port for me"
server.listen(4)
server.settimeout(3)
server_port = server.getsockname()[1]
print("server asked for port 0; OS gave a real port in 1024..65535:", 1024 <= server_port <= 65535)
print("the number varies per run, so it is not printed. Note: the OS ephemeral range is OS-specific")
print("(Linux default 32768-60999) and is NOT the same as IANA's 49152-65535 'dynamic' range.")

accepted: list[tuple[socket.socket, tuple[str, int]]] = []


def accept_two() -> None:
    for _ in range(2):
        accepted.append(server.accept())


t = threading.Thread(target=accept_two)
t.start()
clients = []
for _ in range(2):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.settimeout(3)
    c.connect((HOST, server_port))  # client never binds: OS picks an ephemeral port
    clients.append(c)
t.join(timeout=5)

five_tuples = []
for c in clients:
    laddr, raddr = c.getsockname(), c.getpeername()
    five_tuples.append(("TCP", laddr[0], laddr[1], raddr[0], raddr[1]))
print("client sockets (protocol, src ip, src port, dst ip, dst port):")
for i, ft in enumerate(five_tuples, 1):
    print(f"  client {i}: TCP {ft[1]}:<ephemeral> -> {ft[3]}:<server port>")
print("both clients use the SAME destination (ip, port):", five_tuples[0][3:] == five_tuples[1][3:])
print("but DIFFERENT source ports:", five_tuples[0][2] != five_tuples[1][2])
print("so the two 5-tuples are different:", five_tuples[0] != five_tuples[1])
print("accepted server-side sockets:", len(accepted))
for conn, peer in accepted:
    # server-side connection: local port is the SAME listening port, remote is the client's
    assert conn.getsockname()[1] == server_port
print("each accepted connection keeps local port == listening port: OK")
srv_view = sorted((peer[1]) for _, peer in accepted)
cli_ports = sorted(ft[2] for ft in five_tuples)
print("check: server's view of client ports == clients' own ports:", srv_view == cli_ports)
assert srv_view == cli_ports

# send one line on each connection to prove they are independent streams
for i, c in enumerate(clients):
    c.sendall(f"from client {i}".encode())
received = []
for conn, _ in accepted:
    conn.settimeout(3)
    received.append(conn.recv(100).decode())
print("server received (order may differ by accept order):", sorted(received))
for c in clients:
    c.close()
for conn, _ in accepted:
    conn.close()
server.close()
print("all sockets closed, thread joined")


# ===== SECTION 4: CONNECTION-ORIENTED VS CONNECTIONLESS =====
print("\n===== SECTION 4: CONNECTION-ORIENTED (TCP) VS CONNECTIONLESS (UDP) =====")
u_srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u_srv.bind((HOST, 0))
u_srv.settimeout(3)
u_port = u_srv.getsockname()[1]
u_cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u_cli.settimeout(3)
u_cli.sendto(b"no handshake needed", (HOST, u_port))  # just send
data, addr = u_srv.recvfrom(100)
print("UDP: first packet sent with no connection setup; server got:", data)
print("UDP server identifies the sender only per datagram; sender port is ephemeral:",
      addr[1] != u_port)
# UDP demux uses only (dst ip, dst port); a second sender to the same socket shares it
u_cli2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u_cli2.sendto(b"second sender", (HOST, u_port))
data2, addr2 = u_srv.recvfrom(100)
print("UDP: a second sender reached the SAME server socket:", data2, "; senders differ:",
      addr[1] != addr2[1])
for s in (u_srv, u_cli, u_cli2):
    s.close()

print("""
  feature              TCP (SOCK_STREAM)              UDP (SOCK_DGRAM)
  setup                3-way handshake first          none
  demux key at server  full 5-tuple (one socket       dst ip + dst port only
                       per connection)                (one socket for all senders)
  delivery             reliable, ordered byte stream  best effort datagrams
  boundaries           NOT preserved                  preserved
""")

# trap: a client's ephemeral port is different on every run
print("trap: never hard-code the client's source port; the OS picks a different one each run.")
print("Only the SERVER needs a well-known/agreed port so clients can find it.")
