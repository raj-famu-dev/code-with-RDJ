# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches electronic mail: UA / MTA / MDA architecture, SMTP commands and reply
codes, POP3 vs IMAP, MIME and base64 attachments (email package), and a tiny SMTP
server (socketserver) on loopback driven by smtplib. NO real mail is ever sent;
all addresses use the reserved .test domain. Spam/SPF/DKIM are explained only.
Syllabus idea: Electronic mail (SMTP, POP3, IMAP, MIME).
"""
import base64
import re
import socket
import socketserver
import smtplib
import threading
from email import message_from_bytes, policy
from email.message import EmailMessage

HOST = "127.0.0.1"
LOCAL_DOMAIN = "example.test"
CRLF = "\r\n"


class SmtpHandler(socketserver.StreamRequestHandler):
    """A very small SMTP server session: no auth, no TLS, local domain only."""
    timeout = 5

    def say(self, line: str) -> None:
        self.transcript.append("S: " + line)
        self.wfile.write((line + CRLF).encode())

    def handle(self) -> None:
        self.transcript: list[str] = []
        self.say(f"220 mail.{LOCAL_DOMAIN} ESMTP RDJ-Demo ready")
        sender: str | None = None
        rcpts: list[str] = []
        while True:
            raw = self.rfile.readline(1000)
            if not raw:
                return
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            self.transcript.append("C: " + line)
            cmd, _, arg = line.partition(" ")
            cmd = cmd.upper()
            if cmd == "EHLO":
                self.say(f"250-mail.{LOCAL_DOMAIN} greets {arg}")
                self.say("250 8BITMIME")
            elif cmd == "HELO":
                self.say(f"250 mail.{LOCAL_DOMAIN} greets {arg}")
            elif cmd == "MAIL":
                m = re.match(r"FROM:\s*<([^>]*)>", arg, re.I)
                if not m:
                    self.say("501 syntax: MAIL FROM:<address>")
                else:
                    sender, rcpts = m.group(1), []
                    self.say("250 sender ok")
            elif cmd == "RCPT":
                m = re.match(r"TO:\s*<([^>]*)>", arg, re.I)
                if sender is None:
                    self.say("503 bad sequence: MAIL FROM first")
                elif not m:
                    self.say("501 syntax: RCPT TO:<address>")
                elif not m.group(1).lower().endswith("@" + LOCAL_DOMAIN):
                    self.say("550 relaying denied: not a local recipient")
                else:
                    rcpts.append(m.group(1))
                    self.say("250 recipient ok")
            elif cmd == "DATA":
                if sender is None or not rcpts:
                    self.say("503 bad sequence: need MAIL and RCPT first")
                    continue
                self.say("354 end data with <CRLF>.<CRLF>")
                lines = []
                while True:
                    row = self.rfile.readline(10000).decode("utf-8", "replace")
                    if row in (".\r\n", ".\n", ""):                 # end of data
                        break
                    lines.append(row[1:] if row.startswith("..") else row)   # un-stuff
                self.transcript.append(f"C: [{len(lines)} data lines] + '.'")
                with self.server.lock:
                    self.server.mailbox.append({"from": sender, "to": list(rcpts),
                                                "data": "".join(lines).encode()})
                    number = len(self.server.mailbox)
                self.say(f"250 queued as msg-{number:04d}")
                sender, rcpts = None, []
            elif cmd == "RSET":
                sender, rcpts = None, []
                self.say("250 reset")
            elif cmd == "NOOP":
                self.say("250 ok")
            elif cmd == "QUIT":
                self.say("221 bye")
                with self.server.lock:
                    self.server.sessions.append(list(self.transcript))
                return
            else:
                self.say("500 command not recognized")


def start_smtp() -> socketserver.ThreadingTCPServer:
    srv = socketserver.ThreadingTCPServer((HOST, 0), SmtpHandler)
    srv.lock = threading.Lock()
    srv.mailbox, srv.sessions = [], []
    srv.thread = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05})
    srv.thread.start()
    return srv


srv = start_smtp()
PORT = srv.server_address[1]

try:
    # ===== SECTION 1: MAIL ARCHITECTURE =====
    print("===== SECTION 1: MAIL ARCHITECTURE =====")
    print("""  alice's UA --SMTP--> alice's MTA ==SMTP==> bob's MTA --MDA--> mailbox <--POP3/IMAP-- bob's UA
  (push)                 (push, server to server)               (pull: retrieval)
  UA  user agent : the mail program (Thunderbird, Outlook, a web mail page)
  MTA mail transfer agent : server that relays mail (Postfix, Exim, Exchange)
  MDA mail delivery agent : puts the message into the recipient's mailbox
  MAA mail access agent   : POP3 or IMAP server letting the UA read the mailbox""")
    print("SMTP PUSHES mail (UA->MTA and MTA->MTA, TCP port 25; submission port 587).")
    print("POP3 (110) and IMAP (143) PULL mail. Mail finds its server through the")
    print("recipient domain's MX record in DNS (see the DNS files).")

    # ===== SECTION 2: SMTP COMMANDS AND REPLY CODES =====
    print("\n===== SECTION 2: SMTP COMMANDS AND REPLY CODES =====")
    for cmd, meaning in [("HELO / EHLO host", "greet; EHLO also asks for extensions"),
                         ("MAIL FROM:<a@x>", "start a transaction, name the envelope sender"),
                         ("RCPT TO:<b@y>", "add one envelope recipient (repeat per recipient)"),
                         ("DATA", "then headers + blank line + body, ended by a line with only '.'"),
                         ("RSET / NOOP", "abort the transaction / do nothing"),
                         ("QUIT", "end the session")]:
        print(f"  {cmd:<18}{meaning}")
    print("Reply codes: first digit 2 = success, 3 = send more, 4 = temporary failure")
    print("(try later), 5 = permanent failure (do not retry).")
    for code, text in [(220, "service ready"), (221, "closing channel"), (250, "requested action OK"),
                       (354, "start mail input"), (421, "service not available"),
                       (450, "mailbox busy (temporary)"), (500, "command not recognized"),
                       (503, "bad sequence of commands"), (550, "mailbox unavailable / refused")]:
        print(f"  {code}  {text}")

    # ===== SECTION 3: A HAND-TYPED SMTP DIALOGUE ON LOOPBACK =====
    print("\n===== SECTION 3: A HAND-TYPED SMTP DIALOGUE ON LOOPBACK =====")
    dialogue = ["HELO client.example.test", "RCPT TO:<bob@example.test>", "MAIL FROM:<alice@example.test>",
                "RCPT TO:<bob@example.test>", "RCPT TO:<eve@elsewhere.test>", "FLY", "DATA",
                "Subject: hi", "", "Hello Bob.", ".", "QUIT"]
    with socket.create_connection((HOST, PORT), timeout=5) as s:
        f = s.makefile("rwb")
        print("S:", f.readline().decode().rstrip())
        in_data = False
        for line in dialogue:
            f.write((line + CRLF).encode())
            f.flush()
            print("C:", line)
            if in_data and line != ".":
                continue                                   # data lines get no reply
            reply = f.readline().decode().rstrip()
            print("S:", reply)
            in_data = reply.startswith("354") and line == "DATA"
        f.close()
    print("Note the errors: RCPT before MAIL -> 503, other domain -> 550, 'FLY' -> 500.")
    print("The transaction still succeeded because each failed command was just refused.")
    assert srv.mailbox[-1]["to"] == ["bob@example.test"]
    print("check: OK (only the accepted recipient was queued)")

    # ===== SECTION 4: MIME, BASE64 AND ATTACHMENTS =====
    print("\n===== SECTION 4: MIME, BASE64 AND ATTACHMENTS =====")
    attachment = bytes(range(48))                      # 48 bytes of binary data
    msg = EmailMessage()
    msg["From"] = "alice@example.test"
    msg["To"] = "bob@example.test"
    msg["Bcc"] = "carol@example.test"
    msg["Subject"] = "Lab report"
    msg["Date"] = "Mon, 01 Jan 2024 09:00:00 +0000"
    msg["Message-ID"] = "<demo-0001@example.test>"
    msg.set_content("Hello Bob,\nthe data file is attached.\n.a line starting with a dot\n.\nBye\n")
    msg.add_alternative("<p>Hello <b>Bob</b>, the data file is attached.</p>", subtype="html")
    msg.add_attachment(attachment, maintype="application", subtype="octet-stream", filename="data.bin")
    for n, part in enumerate(p for p in msg.walk() if p.is_multipart()):
        part.set_boundary(f"==DEMO-BOUNDARY-{n}==")       # fixed so output is repeatable
    print("MIME structure (walk):")
    for part in msg.walk():
        kind = part.get_content_type()
        print(f"  {kind:<26} cte={part.get('Content-Transfer-Encoding')} file={part.get_filename()}")
    print("\nTop of the raw message:")
    for line in msg.as_string().splitlines()[:11]:
        print("  |", line)
    b64 = base64.b64encode(attachment).decode()
    print(f"\nattachment: {len(attachment)} bytes -> {len(b64)} base64 characters (4 per 3 bytes, +33%)")
    print("  first base64 line:", b64[:40])
    att_part = [p for p in msg.walk() if p.get_filename()][0]
    assert att_part.get_payload(decode=True) == attachment
    assert len(b64) == 4 * ((len(attachment) + 2) // 3)
    print("check: OK (decoded payload equals the original bytes; length formula holds)")
    print("MIME adds: MIME-Version, Content-Type (with boundary), Content-Transfer-Encoding,")
    print("Content-Disposition. SMTP itself only carries 7-bit text, hence base64.")

    # ===== SECTION 5: smtplib CLIENT -> OUR SERVER; ENVELOPE VS HEADERS =====
    print("\n===== SECTION 5: smtplib CLIENT -> OUR SERVER; ENVELOPE VS HEADERS =====")
    before = len(srv.mailbox)
    with smtplib.SMTP(HOST, PORT, timeout=5, local_hostname="client.example.test") as client:
        refused = client.send_message(msg, to_addrs=["bob@example.test", "carol@example.test",
                                                      "eve@elsewhere.test"])
    print("recipients refused by the server:", refused)
    stored = srv.mailbox[before]
    print("envelope (RCPT TO) :", stored["to"])
    received = message_from_bytes(stored["data"], policy=policy.default)
    print("header To:         :", received["To"])
    print("header Bcc present?:", "Bcc" in received)
    print("Bcc recipients get the mail because the ENVELOPE lists them, but the header")
    print("is stripped, so other recipients never see them.")
    got = [p for p in received.walk() if p.get_filename()][0].get_payload(decode=True)
    assert got == attachment and "carol@example.test" in stored["to"] and "Bcc" not in received
    print("check: OK (attachment survived SMTP intact)")
    print("\nServer-side transcript of that session:")
    for line in srv.sessions[-1]:
        print("  ", line)

    # ===== SECTION 6: TRAP - A LINE WITH ONLY A DOT =====
    print("\n===== SECTION 6: TRAP - A LINE WITH ONLY A DOT =====")
    body_text = received.get_body(preferencelist=("plain",)).get_content()
    print("the plain-text body we sent contains the lines: '.a line starting with a dot' and '.'")
    print("body as received:", body_text.splitlines())
    print("SMTP ends DATA at a line containing only '.'. So the sender must DOT-STUFF:")
    print("  any body line starting with '.' gets an extra '.' (so '.' becomes '..').")
    print("The receiver removes one leading '.' from each such line.")

    def stuff(text: str) -> str:
        return CRLF.join(("." + l) if l.startswith(".") else l for l in text.split(CRLF))

    def unstuff(text: str) -> str:
        return CRLF.join(l[1:] if l.startswith("..") else l for l in text.split(CRLF))

    original = f"one{CRLF}.{CRLF}.hidden{CRLF}two"
    wire = stuff(original)
    print("  original:", original.split(CRLF))
    print("  on wire :", wire.split(CRLF))
    assert unstuff(wire) == original
    naive_stop = original.split(CRLF + "." + CRLF)[0]
    print("  naive end-of-data scan WITHOUT stuffing would stop after:", repr(naive_stop))
    print("check: OK (stuffing round-trips; smtplib did this for us, as the received body shows)")

    # ===== SECTION 7: POP3 VS IMAP, SPAM, SPF/DKIM/DMARC =====
    print("\n===== SECTION 7: POP3 VS IMAP, SPAM, SPF/DKIM/DMARC =====")
    print(f"{'':<14}{'POP3 (port 110, TLS 995)':<34}{'IMAP (port 143, TLS 993)'}")
    for a, b, c in [("model", "download then (usually) delete", "mail stays on server, synced"),
                    ("folders", "inbox only", "server-side folders and flags"),
                    ("devices", "awkward with several", "natural with several"),
                    ("offline", "good (it is all local)", "needs cache; works online"),
                    ("state", "simple, stateless-ish", "stateful session")]:
        print(f"{a:<14}{b:<34}{c}")
    print("Spam: unwanted bulk mail; fought by filters, blocklists, rate limits.")
    print("SPF  : domain lists (in DNS TXT) which servers may send its mail.")
    print("DKIM : sender MTA signs headers/body; receiver checks the signature using a")
    print("       public key published in DNS.")
    print("DMARC: policy telling receivers what to do when SPF/DKIM fail and where to report.")
    print("These stop forged 'From' domains; none of them encrypts the message. Use TLS")
    print("(STARTTLS or port 465) for transport and S/MIME or PGP for end-to-end secrecy.")
finally:
    srv.shutdown()
    srv.server_close()                    # also joins the handler threads
    srv.thread.join(timeout=5)
print("\nserver stopped:", not srv.thread.is_alive())
