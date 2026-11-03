# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches remote file transfer and remote login: FTP (separate control and data
connections, active vs passive mode, commands and reply codes), TFTP (UDP,
512-byte blocks, stop-and-wait with retransmission), Telnet vs SSH (cleartext vs
encrypted, Diffie-Hellman idea) and SFTP vs FTPS. Everything runs on loopback
against servers written in this file (127.0.0.1, port 0, timeouts, joined threads).
Syllabus idea: FTP, TFTP, Telnet, SSH.
"""
import re
import socket
import socketserver
import struct
import threading

HOST = "127.0.0.1"
CRLF = "\r\n"
FILES = {"/README.txt": b"Welcome to the RDJ mini FTP server.\n",
         "/pub/notes.txt": b"Control connection: commands. Data connection: bytes.\n",
         "/pub/big.bin": bytes(range(256)) * 4}            # 1024 bytes


def mask(line: str) -> str:
    """Hide OS-chosen port numbers so the output is identical on every run."""
    line = re.sub(r"\(127,0,0,1,\d+,\d+\)", "(127,0,0,1,P1,P2)", line)
    return re.sub(r"PORT 127,0,0,1,\d+,\d+", "PORT 127,0,0,1,P1,P2", line)


# ===== SECTION 1: FTP IDEAS =====
print("===== SECTION 1: FTP IDEAS =====")
print("""  client                                   server
  ctrl port N  ----- control connection ----- port 21   (commands + replies, text)
  data port    ----- data connection    ----- port 20 (active) or a server-chosen port (passive)
  The control connection lives for the whole session ("out-of-band" control).
  A NEW data connection is opened for each file transfer or directory listing.""")
print("ACTIVE mode : client says PORT h1,h2,h3,h4,p1,p2; the SERVER connects to the client.")
print("PASSIVE mode: client says PASV; the server opens a port and tells it; the CLIENT")
print("              connects. Passive works through client-side firewalls/NAT, so it is")
print("              the usual choice today. Port number = p1 x 256 + p2.")
print("FTP is stateful (login, current directory) and sends passwords in CLEARTEXT.")
print("Anonymous FTP: user 'anonymous', password = any e-mail-like string, read-only files.")
print("Reply codes: 1xx preliminary, 2xx done, 3xx need more, 4xx temporary error, 5xx error.")
print("  220 ready, 331 need password, 230 logged in, 257 path, 227 passive mode, 150 opening")
print("  data connection, 226 transfer complete, 530 not logged in, 550 file unavailable, 221 bye")
assert 19 * 256 + 137 == 5001
print("check: OK (p1=19, p2=137 -> port 19*256+137 = 5001)")


class FtpHandler(socketserver.StreamRequestHandler):
    timeout = 5

    def say(self, line: str) -> None:
        self.transcript.append("S: " + line)
        self.wfile.write((line + CRLF).encode())

    def list_dir(self, cwd: str) -> bytes:
        base = "/" if cwd == "/" else cwd + "/"
        names = set()
        for path in FILES:
            if path.startswith(base):
                head = path[len(base):].split("/")
                names.add(head[0] + ("/" if len(head) > 1 else ""))
        return ("".join(n + CRLF for n in sorted(names))).encode()

    def open_data(self, pasv, port_addr) -> socket.socket | None:
        try:
            if pasv is not None:
                conn, _ = pasv.accept()
                return conn
            if port_addr is not None:
                return socket.create_connection(port_addr, timeout=5)
        except OSError:
            return None
        return None

    def handle(self) -> None:
        self.transcript: list[str] = []
        user, authed, cwd = None, False, "/"
        pasv: socket.socket | None = None
        port_addr: tuple[str, int] | None = None
        self.say("220 RDJ mini FTP ready")
        try:
            while True:
                raw = self.rfile.readline(500)
                if not raw:
                    return
                line = raw.decode("utf-8", "replace").rstrip("\r\n")
                self.transcript.append("C: " + line)
                cmd, _, arg = line.partition(" ")
                cmd = cmd.upper()
                if cmd == "USER":
                    user = arg
                    self.say("331 password please" if arg != "anonymous"
                             else "331 anonymous ok, send e-mail as password")
                elif cmd == "PASS":
                    if user == "anonymous" or (user == "student" and arg == "pa55word"):
                        authed = True
                        self.say("230 logged in")
                    else:
                        self.say("530 login incorrect")
                elif cmd == "QUIT":
                    self.say("221 bye")
                    with self.server.lock:
                        self.server.sessions.append(list(self.transcript))
                    return
                elif not authed:
                    self.say("530 please log in first")
                elif cmd == "PWD":
                    self.say(f'257 "{cwd}" is the current directory')
                elif cmd == "CWD":
                    target = arg if arg.startswith("/") else (cwd.rstrip("/") + "/" + arg)
                    if any(p.startswith(target.rstrip("/") + "/") for p in FILES) or target == "/":
                        cwd = target.rstrip("/") or "/"
                        self.say("250 directory changed")
                    else:
                        self.say("550 no such directory")
                elif cmd == "PASV":
                    if pasv:
                        pasv.close()
                    pasv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pasv.bind((HOST, 0))
                    pasv.listen(1)
                    pasv.settimeout(5)
                    p = pasv.getsockname()[1]
                    port_addr = None
                    self.say(f"227 Entering Passive Mode (127,0,0,1,{p >> 8},{p & 255})")
                elif cmd == "PORT":
                    try:
                        h1, h2, h3, h4, p1, p2 = (int(x) for x in arg.split(","))
                        ip = f"{h1}.{h2}.{h3}.{h4}"
                        if ip != self.client_address[0]:
                            self.say("504 PORT address must be the client's own (bounce protection)")
                            continue
                        port_addr = (ip, p1 * 256 + p2)
                        if pasv:
                            pasv.close()
                            pasv = None
                        self.say("200 PORT ok")
                    except ValueError:
                        self.say("501 bad PORT syntax")
                elif cmd in ("LIST", "RETR"):
                    if cmd == "RETR":
                        path = arg if arg.startswith("/") else cwd.rstrip("/") + "/" + arg
                        if path not in FILES:
                            self.say("550 file unavailable")
                            continue
                        payload = FILES[path]
                    else:
                        payload = self.list_dir(cwd)
                    if pasv is None and port_addr is None:
                        self.say("425 use PORT or PASV first")
                        continue
                    self.say("150 opening data connection")
                    data = self.open_data(pasv, port_addr)
                    if pasv:
                        pasv.close()
                    pasv, port_addr = None, None
                    if data is None:
                        self.say("425 cannot open data connection")
                        continue
                    with data:
                        data.sendall(payload)
                    self.say("226 transfer complete")
                else:
                    self.say("502 command not implemented")
        finally:
            if pasv:
                pasv.close()


class FtpClient:
    def __init__(self, port: int) -> None:
        self.sock = socket.create_connection((HOST, port), timeout=5)
        self.f = self.sock.makefile("rwb")
        self.read_reply()

    def read_reply(self, show: bool = True) -> str:
        line = self.f.readline().decode().rstrip()
        if show:
            print("   S:", mask(line))
        return line

    def cmd(self, text: str, show: bool = True) -> str:
        self.f.write((text + CRLF).encode())
        self.f.flush()
        if show:
            print("   C:", mask(text))
        return self.read_reply(show)

    def close(self) -> None:
        self.f.close()
        self.sock.close()


def read_all(sock: socket.socket) -> bytes:
    chunks = []
    while True:
        c = sock.recv(4096)
        if not c:
            return b"".join(chunks)
        chunks.append(c)


# ===== SECTION 2: A MINI FTP SERVER - PASSIVE MODE SESSION =====
print("\n===== SECTION 2: A MINI FTP SERVER - PASSIVE MODE SESSION =====")
ftp = socketserver.ThreadingTCPServer((HOST, 0), FtpHandler)
ftp.lock, ftp.sessions = threading.Lock(), []
ftp_thread = threading.Thread(target=ftp.serve_forever, kwargs={"poll_interval": 0.05})
ftp_thread.start()
FTP_PORT = ftp.server_address[1]
try:
    c = FtpClient(FTP_PORT)
    c.cmd("LIST")                                    # not logged in yet
    c.cmd("USER student")
    c.cmd("PASS wrong")
    c.cmd("PASS pa55word")
    c.cmd("PWD")
    c.cmd("CWD pub")
    reply = c.cmd("PASV")
    m = re.search(r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", reply)
    port = int(m.group(5)) * 256 + int(m.group(6))
    data = socket.create_connection((m.group(1) + "." + m.group(2) + "." + m.group(3) + "." + m.group(4), port), timeout=5)
    c.f.write(b"LIST\r\n")
    c.f.flush()
    print("   C: LIST")
    c.read_reply()
    listing = read_all(data).decode()
    data.close()
    c.read_reply()
    print("   data connection carried:", listing.split(CRLF)[:-1])
    reply = c.cmd("PASV", show=False)
    m = re.search(r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", reply)
    data = socket.create_connection((HOST, int(m.group(5)) * 256 + int(m.group(6))), timeout=5)
    c.f.write(b"RETR notes.txt\r\n")
    c.f.flush()
    print("   C: PASV / RETR notes.txt")
    c.read_reply()
    body = read_all(data)
    data.close()
    c.read_reply()
    print("   downloaded:", body)
    assert body == FILES["/pub/notes.txt"]
    c.cmd("QUIT")
    c.close()
    print("check: OK (file bytes equal the server's copy; control and data were separate sockets)")

    # ===== SECTION 3: ACTIVE MODE AND THE PORT-BOUNCE CHECK =====
    print("\n===== SECTION 3: ACTIVE MODE AND THE PORT-BOUNCE CHECK =====")
    c = FtpClient(FTP_PORT)
    c.cmd("USER anonymous")
    c.cmd("PASS rdj@example.test")
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((HOST, 0))
    listener.listen(1)
    listener.settimeout(5)
    p = listener.getsockname()[1]
    try:
        c.cmd(f"PORT 127,0,0,1,{p >> 8},{p & 255}")
        c.f.write(b"RETR README.txt\r\n")
        c.f.flush()
        print("   C: RETR README.txt")
        c.read_reply()                               # 150: server is now connecting TO US
        conn, peer = listener.accept()
        body = read_all(conn)
        conn.close()
        c.read_reply()
        print("   active mode: the SERVER opened the data connection; we received:", body)
        assert body == FILES["/README.txt"]
    finally:
        listener.close()
    print("Trap (FTP bounce): a malicious client could say PORT <victim ip>,<victim port>")
    print("and make the server connect to a third machine. Defence: refuse any PORT whose")
    print("address is not the client's own address.")
    c.cmd("PORT 10,0,0,5,0,80")
    c.cmd("RETR nothing.txt")
    c.cmd("QUIT")
    c.close()
    print("check: OK (active transfer worked; bounce attempt refused with 504)")

    # ===== SECTION 4: WHAT A CAPTURE WOULD SHOW - CLEARTEXT =====
    print("\n===== SECTION 4: WHAT A CAPTURE WOULD SHOW - CLEARTEXT =====")
    print("Server-side log of the first session (this is what anyone on the path sees):")
    for line in ftp.sessions[0][:9]:
        print("   ", line)
    print("The password 'pa55word' (a demo value) travels as readable text. The same holds")
    print("for Telnet and for the files themselves. FTPS wraps FTP in TLS; SFTP is a")
    print("different protocol that runs inside SSH (port 22). They are NOT the same thing.")
finally:
    ftp.shutdown()
    ftp.server_close()
    ftp_thread.join(timeout=5)

# ===== SECTION 5: TFTP - UDP, 512-BYTE BLOCKS, STOP-AND-WAIT =====
print("\n===== SECTION 5: TFTP - UDP, 512-BYTE BLOCKS, STOP-AND-WAIT =====")
print("TFTP (port 69/UDP): no login, no directories, tiny; used for network boot and")
print("router config files. Opcodes: 1 RRQ, 2 WRQ, 3 DATA, 4 ACK, 5 ERROR.")
print("Each DATA block carries up to 512 bytes. A block shorter than 512 ENDS the file.")
print("Stop-and-wait: send block n, wait for ACK n, only then send n+1; on timeout resend.")
print(f"{'file size':>10}{'DATA blocks':>13}  (last block is shorter than 512, maybe empty)")
for size in (0, 100, 511, 512, 513, 1024):
    print(f"{size:>10}{size // 512 + 1:>13}")
BLOCK = 512
TFTP_FILES = {"hello.txt": b"hello from tftp\n", "two_blocks.bin": bytes(range(256)) * 4,
              "exact512.bin": b"x" * 512}


class TftpServer:
    def __init__(self, lose: set[tuple[str, int]]) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST, 0))
        self.sock.settimeout(0.2)
        self.port: int = self.sock.getsockname()[1]
        self.lose = set(lose)                       # (file, block) whose FIRST send is "lost"
        self.retransmits = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run)

    def run(self) -> None:
        while not self.stop.is_set():
            try:
                pkt, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                continue
            if struct.unpack("!H", pkt[:2])[0] == 1:             # RRQ
                name = pkt[2:].split(b"\x00")[0].decode()
                self.send_file(name, addr)

    def send_file(self, name: str, addr) -> None:
        t = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # new socket = new TID (port)
        t.bind((HOST, 0))
        t.settimeout(0.3)
        try:
            if name not in TFTP_FILES:
                t.sendto(struct.pack("!HH", 5, 1) + b"File not found\x00", addr)
                return
            data = TFTP_FILES[name]
            n = 1
            while True:
                chunk = data[(n - 1) * BLOCK: n * BLOCK]
                pkt = struct.pack("!HH", 3, n) + chunk
                for attempt in range(5):
                    if (name, n) in self.lose:                   # simulate a lost datagram
                        self.lose.discard((name, n))
                    else:
                        t.sendto(pkt, addr)
                    try:
                        ack, _ = t.recvfrom(1024)
                    except socket.timeout:
                        self.retransmits += 1
                        continue
                    if struct.unpack("!HH", ack[:4]) == (4, n):
                        break
                else:
                    return                                       # give up
                if len(chunk) < BLOCK:
                    return
                n += 1
        finally:
            t.close()

    def close(self) -> None:
        self.stop.set()
        self.thread.join(timeout=5)
        self.sock.close()


def tftp_get(server_port: int, name: str) -> tuple[bytes | None, list[int], int | None]:
    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c.settimeout(3)
    blocks: list[int] = []
    out = b""
    tid = None
    try:
        c.sendto(struct.pack("!H", 1) + name.encode() + b"\x00octet\x00", (HOST, server_port))
        while True:
            pkt, addr = c.recvfrom(1024)
            op, num = struct.unpack("!HH", pkt[:4])
            if op == 5:
                return None, blocks, num
            if tid is None:
                tid = addr[1]
            if addr[1] != tid or op != 3:
                continue
            c.sendto(struct.pack("!HH", 4, num), addr)
            if num == (blocks[-1] if blocks else 0) + 1:        # new block (ignore duplicates)
                out += pkt[4:]
                blocks.append(num)
            if len(pkt) - 4 < BLOCK:
                return out, blocks, None
    finally:
        c.close()


tftp = TftpServer(lose={("two_blocks.bin", 2)})
tftp.thread.start()
try:
    print("\nDownloads from the loopback TFTP server (block 2 of two_blocks.bin is 'lost' once):")
    for name in ("hello.txt", "exact512.bin", "two_blocks.bin", "nope.txt"):
        got, blocks, err = tftp_get(tftp.port, name)
        if err is not None:
            print(f"  {name:<16} -> ERROR code {err} (1 = file not found)")
            continue
        print(f"  {name:<16} -> {len(got):>4} bytes in blocks {blocks}  correct={got == TFTP_FILES[name]}")
        assert got == TFTP_FILES[name]
    print("exact512.bin is exactly 512 bytes, so block 2 is EMPTY: that is how the receiver")
    print("knows the file ended. (A 513-byte file needs block 2 with 1 byte.)")
    print("server retransmissions caused by the simulated loss:", tftp.retransmits)
    assert tftp.retransmits == 1
    print("check: OK (stop-and-wait recovered the lost block by timeout + resend)")
finally:
    tftp.close()
print("tftp thread stopped:", not tftp.thread.is_alive())
print("Stop-and-wait throughput = block size / RTT, e.g. 512 bytes per 10 ms = 51,200 B/s,")
print("however fast the link is. That is why TFTP is for small files only.")

# ===== SECTION 6: TELNET VS SSH AND THE KEY-EXCHANGE IDEA =====
print("\n===== SECTION 6: TELNET VS SSH AND THE KEY-EXCHANGE IDEA =====")
print(f"{'':<14}{'Telnet':<26}{'SSH'}")
for a, b, c2 in [("port", "23/TCP", "22/TCP"), ("encryption", "none (cleartext)", "yes, all traffic"),
                 ("server auth", "none", "host key (check fingerprint)"),
                 ("user auth", "password in clear", "password or public key"),
                 ("extras", "-", "port forwarding, SFTP, SCP"),
                 ("use today", "legacy / lab only", "standard for remote admin")]:
    print(f"{a:<14}{b:<26}{c2}")
iac = b"\xff\xfd\x01"
names = {255: "IAC", 253: "DO", 251: "WILL", 252: "WONT", 254: "DONT", 1: "ECHO"}
print("A Telnet option negotiation on the wire:", iac.hex(" "), "=", " ".join(names[b] for b in iac))
print("\nHow SSH gets a shared key without sending it (Diffie-Hellman idea, TOY numbers):")
p_, g_, a_, b_ = 23, 5, 6, 15
A = pow(g_, a_, p_)
B = pow(g_, b_, p_)
sa, sb = pow(B, a_, p_), pow(A, b_, p_)
print(f"  public: p={p_}, g={g_}.  client secret a={a_} -> sends A=g^a mod p={A}")
print(f"  server secret b={b_} -> sends B=g^b mod p={B}")
print(f"  client computes B^a mod p={sa}; server computes A^b mod p={sb}")
assert sa == sb == pow(g_, a_ * b_, p_)
print("check: OK (both sides get the same secret; an eavesdropper sees only p, g, A, B)")
print("Real SSH uses huge groups or elliptic curves (toy p=23 is trivially breakable),")
print("then derives session keys, authenticates the server with its host key and the")
print("user with a password or key pair. First connection: verify the fingerprint.")
print("SFTP (inside SSH, port 22) vs FTPS (FTP + TLS, ports 21/990): different protocols.")
