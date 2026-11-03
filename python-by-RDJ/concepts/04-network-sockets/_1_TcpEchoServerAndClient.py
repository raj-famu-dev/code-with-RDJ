# Tags: #Python #Networking #Sockets #TcpEchoServerClient | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches TCP sockets from scratch: bind, listen, accept, connect, sendall,
recv, close. A server runs in a background thread and a client talks to it,
both on loopback (127.0.0.1) only. Port 0 lets the OS pick a free port.
"""
import socket
import threading

HOST = "127.0.0.1"          # loopback: traffic never leaves this machine

print("=== SECTION 1: the server side (bind, listen) ===")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # IPv4 + TCP
server.settimeout(5)                                          # never block forever
server.bind((HOST, 0))                                        # port 0 = OS picks a free port
server.listen(1)                                              # start queueing connections
port = server.getsockname()[1]
print("bound host:", server.getsockname()[0])
print("port is an OS-chosen ephemeral port (> 1023):", port > 1023)
print("socket family/type:", server.family.name, server.type.name)

received_by_server: list[bytes] = []
server_events: list[str] = []      # threads must not print: output order would race with main

def echo_once() -> None:
    conn, addr = server.accept()                              # blocks until a client connects
    with conn:
        conn.settimeout(5)
        server_events.append("accepted a client from host " + addr[0])
        while True:
            data = conn.recv(1024)                            # up to 1024 bytes
            if not data:                                      # b"" means the client closed
                server_events.append("client closed the connection (recv returned b'')")
                break
            received_by_server.append(data)
            conn.sendall(data.upper())                        # reply

t = threading.Thread(target=echo_once, name="echo-server")
t.start()

print("\n=== SECTION 2: the client side (connect, sendall, recv) ===")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(5)
client.connect((HOST, port))
print("client connected; peer host:", client.getpeername()[0])
client.sendall(b"hello server")
reply = client.recv(1024)
print("sent   : b'hello server'")
print("reply  :", reply)
print("type is bytes, not str:", type(reply).__name__)
print("decoded:", reply.decode("utf-8"))

print("\n=== SECTION 3: bytes vs str ===")
msg = "café"
wire = msg.encode("utf-8")
print("str  :", msg, "| len =", len(msg))
print("bytes:", wire, "| len =", len(wire))
client.sendall(wire)
print("echoed:", client.recv(1024).decode("utf-8"), "<- bytes.upper() only changes ASCII letters")
try:
    client.sendall("plain str")                               # TRAP
except TypeError as e:
    print("sendall(str) -> TypeError:", e)
print("RULE: sockets carry bytes; encode on send, decode on receive.")

print("\n=== SECTION 4: clean shutdown ===")
client.close()                                                # server sees recv() == b""
t.join(timeout=5)
print("server thread finished:", not t.is_alive())
server.close()
print("server socket closed; fileno =", server.fileno(), "(-1 means closed)")
print("server received:", received_by_server)
print("server events:", server_events)

print("\n=== SECTION 5: connecting after the server is gone ===")
dead = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dead.settimeout(2)
try:
    dead.connect((HOST, port))                                # nobody listens now
except ConnectionRefusedError as e:
    print("ConnectionRefusedError -> no listener on that port")
finally:
    dead.close()

print("\n=== SECTION 6: TRAP - TCP is a stream, not messages ===")
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.settimeout(5)
srv.bind((HOST, 0))
srv.listen(1)
p2 = srv.getsockname()[1]
chunks: list[bytes] = []

def collect() -> None:
    c, _ = srv.accept()
    with c:
        c.settimeout(5)
        while True:
            d = c.recv(4096)
            if not d:
                break
            chunks.append(d)

t2 = threading.Thread(target=collect)
t2.start()
with socket.create_connection((HOST, p2), timeout=5) as c2:   # connect helper
    c2.sendall(b"one")
    c2.sendall(b"two")
    c2.sendall(b"three")
t2.join(timeout=5)
srv.close()
print("three sendall() calls, bytes received in total:", b"".join(chunks))
print("TCP does not preserve send() boundaries; recv() may merge or split them.")
print("(see _7_SocketErrorsAndTimeouts for length-prefix framing)")
print("threads cleaned up:", not t2.is_alive())
