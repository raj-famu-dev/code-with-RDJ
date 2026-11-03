# Tags: #Python #ComputerNetworks #SessionLayer #PresentationLayer #TlsSslSecureChannels | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""TLS/SSL secure channels: where TLS sits, handshake steps, cipher-suite
anatomy, TLS 1.2 vs 1.3, the record protocol, ssl-module default settings
(no network), an in-memory TOY handshake, and an optional loopback TLS wrap."""
from __future__ import annotations

import hashlib
import hmac
import os
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading


# ===== SECTION 1: WHERE TLS SITS =====
print("===== SECTION 1: WHERE TLS SITS IN THE STACK =====")
print("  Application  HTTP | SMTP | IMAP | FTP ...   (HTTPS = HTTP over TLS, port 443)")
print("  Secure chan. TLS (successor of SSL)         <- 'layer 5/6': between app and TCP")
print("  Transport    TCP (DTLS/QUIC for UDP-based)")
print("  Network      IP   (IPsec works HERE, below TCP/UDP)")
print("  SSL 2.0/3.0 and TLS 1.0/1.1 are obsolete/deprecated; use TLS 1.2 or 1.3.")
print("  TLS gives: confidentiality (encryption), integrity (MAC/AEAD),")
print("  server authentication (certificate), optional client authentication.")


# ===== SECTION 2: HANDSHAKE STEPS AND CIPHER SUITES =====
print("\n===== SECTION 2: HANDSHAKE AND CIPHER SUITE ANATOMY =====")
print("  TLS 1.2 (2 round trips for a full handshake):")
for step in [
    "C -> S  ClientHello         (versions, random, cipher suites)",
    "S -> C  ServerHello         (chosen suite, random)",
    "S -> C  Certificate         (server chain)",
    "S -> C  ServerKeyExchange   (e.g. ECDHE params, signed)",
    "S -> C  ServerHelloDone",
    "C -> S  ClientKeyExchange   (client ECDHE share)",
    "C -> S  ChangeCipherSpec + Finished  (encrypted from here)",
    "S -> C  ChangeCipherSpec + Finished",
]:
    print("   ", step)
print("  TLS 1.3 (1 round trip): ClientHello carries key shares up front;")
print("  everything after ServerHello (certificate, Finished) is encrypted.")
print("  Cipher-suite names:")
print("    TLS 1.2: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256")
print("             key exchange=ECDHE, authentication=RSA, cipher=AES-128-GCM, hash=SHA-256")
print("    TLS 1.3: TLS_AES_128_GCM_SHA256 (only cipher + hash; key exchange is negotiated apart)")
print("  1.2 vs 1.3: 1.3 removes RSA key transport, static DH, CBC, RC4, SHA-1,")
print("  compression, renegotiation; forward secrecy (ephemeral keys) is always on.")


# ===== SECTION 3: ssl MODULE DEFAULTS (NO NETWORK) =====
print("\n===== SECTION 3: ssl MODULE DEFAULT CONTEXT (NO NETWORK) =====")
ctx = ssl.create_default_context()
print("  OpenSSL runtime       :", ssl.OPENSSL_VERSION, "(environment-dependent)")
print("  minimum_version       :", ctx.minimum_version.name)
print("  maximum_version       :", ctx.maximum_version.name)
print("  verify_mode           :", ctx.verify_mode.name)
print("  check_hostname        :", ctx.check_hostname)
print("  has TLS 1.3 support   :", ssl.HAS_TLSv1_3)
print("  default context is SECURE by default: certificate + hostname verified.")
assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
# TRAP: the classic 'make the error go away' shortcut
bad = ssl.create_default_context()
bad.check_hostname = False
bad.verify_mode = ssl.CERT_NONE
print("  TRAP  context with verification off:", bad.verify_mode.name,
      "-> encrypted but UNAUTHENTICATED: a man-in-the-middle is not detected.")
print("  FIX   keep CERT_REQUIRED; trust a private CA via cafile=..., never disable checks.")
raw_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
print("  bare SSLContext(PROTOCOL_TLS_CLIENT) verify_mode:", raw_ctx.verify_mode.name,
      "(also CERT_REQUIRED in modern Python)")
print("  check: OK")


# ===== SECTION 4: IN-MEMORY TOY HANDSHAKE AND RECORD LAYER =====
print("\n===== SECTION 4: TOY HANDSHAKE SIMULATED IN MEMORY (NOT REAL TLS) =====")
P, G = 0xFFFFFFFFFFFFFFC5, 5  # 2^64 - 59: a 64-bit prime, toy size, insecure


def hkdf_like(secret: bytes, label: bytes) -> bytes:
    return hmac.new(secret, label, hashlib.sha256).digest()


transcript: list[bytes] = []


def send(frm: str, to: str, name: str, body: bytes) -> bytes:
    transcript.append(body)
    print(f"  {frm} -> {to}  {name:<18} {len(body):>3} bytes")
    return body


# Deterministic "random" values for a repeatable demo (real ones come from os.urandom).
c_rand = hashlib.sha256(b"client-random").digest()
s_rand = hashlib.sha256(b"server-random").digest()
c_priv = int.from_bytes(hashlib.sha256(b"c-priv").digest(), "big") % (P - 2) + 1
s_priv = int.from_bytes(hashlib.sha256(b"s-priv").digest(), "big") % (P - 2) + 1
c_pub, s_pub = pow(G, c_priv, P), pow(G, s_priv, P)
server_cert_key = b"toy-server-signing-key"  # stands in for the server's private key

send("Client", "Server", "ClientHello", c_rand + c_pub.to_bytes(8, "big") + b"TOY_AES_GCM")
send("Server", "Client", "ServerHello", s_rand + s_pub.to_bytes(8, "big") + b"TOY_AES_GCM")
cert = send("Server", "Client", "Certificate", b"CN=toy.example;pub=ABCD")
sig = hmac.new(server_cert_key, b"".join(transcript), hashlib.sha256).digest()
send("Server", "Client", "CertificateVerify", sig)

# Both sides derive the same traffic secret from DH + transcript hash.
shared_c = pow(s_pub, c_priv, P).to_bytes(8, "big")
shared_s = pow(c_pub, s_priv, P).to_bytes(8, "big")
assert shared_c == shared_s
th = hashlib.sha256(b"".join(transcript)).digest()
c_key = hkdf_like(shared_c + th, b"client traffic")
s_key = hkdf_like(shared_s + th, b"server traffic")
fin_s = hkdf_like(s_key, b"finished")
send("Server", "Client", "Finished", fin_s)
fin_c = hkdf_like(c_key, b"finished")
send("Client", "Server", "Finished", fin_c)
print("  both sides computed the same keys:",
      hkdf_like(shared_s + th, b"client traffic") == c_key)
print("  Finished = MAC over the whole transcript: any tampering during the")
print("  handshake makes it fail (this is how downgrade attempts are caught).")

print("\n  Record protocol (toy): split data into records, seq number, encrypt+MAC.")


def record_seal(key: bytes, seq: int, data: bytes) -> bytes:
    stream = hashlib.sha256(key + seq.to_bytes(8, "big")).digest()  # TOY keystream
    ct = bytes(b ^ stream[i % 32] for i, b in enumerate(data))
    tag = hmac.new(key, seq.to_bytes(8, "big") + ct, hashlib.sha256).digest()[:8]
    return seq.to_bytes(8, "big") + ct + tag


def record_open(key: bytes, rec: bytes) -> bytes:
    seq, ct, tag = int.from_bytes(rec[:8], "big"), rec[8:-8], rec[-8:]
    want = hmac.new(key, rec[:8] + ct, hashlib.sha256).digest()[:8]
    if not hmac.compare_digest(tag, want):
        raise ValueError("bad record MAC")
    stream = hashlib.sha256(key + seq.to_bytes(8, "big")).digest()
    return bytes(b ^ stream[i % 32] for i, b in enumerate(ct))


rec = record_seal(c_key, 0, b"GET / HTTP/1.1")
print("  sealed record:", rec.hex(" ")[:48] + "...")
print("  opened       :", record_open(c_key, rec))
flipped = rec[:9] + bytes([rec[9] ^ 1]) + rec[10:]
try:
    record_open(c_key, flipped)
except ValueError as exc:
    print("  flip one bit  ->", exc, "(integrity protected)")
print("  check: OK. Real TLS uses AEAD ciphers (AES-GCM, ChaCha20-Poly1305).")


# ===== SECTION 5: OPTIONAL LOOPBACK TLS WRAP =====
print("\n===== SECTION 5: LOOPBACK TLS WRAP (127.0.0.1 ONLY) =====")


def make_cert(tmp: str) -> tuple[str, str] | None:
    exe = shutil.which("openssl")
    if not exe:
        return None
    crt, key = os.path.join(tmp, "c.pem"), os.path.join(tmp, "k.pem")
    cmd = [exe, "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1",
           "-nodes", "-keyout", key, "-out", crt, "-days", "1", "-subj", "/CN=localhost",
           "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=10)
    except (subprocess.SubprocessError, OSError):
        return None
    return crt, key


def loopback_demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        made = make_cert(tmp)
        if made is None:
            print("  SKIPPED: openssl CLI not available here to create a throw-away cert.")
            return
        crt, key = made
        srv_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        srv_ctx.load_cert_chain(crt, key)
        cli_ctx = ssl.create_default_context(cafile=crt)  # trust ONLY our cert
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind(("127.0.0.1", 0))
        lsock.listen(1)
        lsock.settimeout(5)
        port = lsock.getsockname()[1]
        seen: list[bytes] = []

        def server() -> None:
            try:
                conn, _ = lsock.accept()
                conn.settimeout(5)
                with srv_ctx.wrap_socket(conn, server_side=True) as tls:
                    seen.append(tls.recv(100))
                    tls.sendall(b"hello over TLS")
            except (OSError, ssl.SSLError) as exc:
                seen.append(b"server error: " + str(exc).encode())

        t = threading.Thread(target=server)
        t.start()
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
                with cli_ctx.wrap_socket(raw, server_hostname="localhost") as tls:
                    tls.sendall(b"hello server")
                    reply = tls.recv(100)
                    print("  negotiated version :", tls.version(), "(depends on local OpenSSL)")
                    print("  cipher suite       :", tls.cipher()[0])
                    print("  server cert subject:", dict(x[0] for x in tls.getpeercert()["subject"]))
                    print("  client sent / got  :", b"hello server", "/", reply)
        finally:
            t.join(timeout=10)
            lsock.close()
        print("  server received    :", seen[0])
        # Trap: a client that does not trust our self-signed cert must refuse.
        lsock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock2.bind(("127.0.0.1", 0))
        lsock2.listen(1)
        lsock2.settimeout(5)
        port2 = lsock2.getsockname()[1]

        def server2() -> None:
            try:
                conn, _ = lsock2.accept()
                conn.settimeout(5)
                with srv_ctx.wrap_socket(conn, server_side=True):
                    pass
            except (OSError, ssl.SSLError):
                pass

        t2 = threading.Thread(target=server2)
        t2.start()
        try:
            with socket.create_connection(("127.0.0.1", port2), timeout=5) as raw:
                try:
                    ssl.create_default_context().wrap_socket(raw, server_hostname="localhost")
                    print("  TRAP default trust store accepted self-signed cert?! (unexpected)")
                except ssl.SSLCertVerificationError as exc:
                    print("  TRAP default trust store rejects our self-signed cert:", exc.verify_message)
        finally:
            t2.join(timeout=10)
            lsock2.close()
        print("  check: OK (private cert deleted with the temp directory)")


loopback_demo()


# ===== SECTION 6: OTHER SECURE-CHANNEL TECHNOLOGIES =====
print("\n===== SECTION 6: IPSEC / SSH / VPN PLACEMENT =====")
rows = [
    ("TLS", "above TCP", "per-application (HTTPS, SMTPS, IMAPS)"),
    ("SSH", "above TCP (port 22)", "remote login, file copy, port forwarding"),
    ("IPsec", "network layer (AH/ESP)", "protects all IP traffic; transport/tunnel mode; IKE keys"),
    ("VPN", "a use, not one protocol", "tunnel via IPsec, WireGuard, OpenVPN (TLS-based) ..."),
]
for name, where, note in rows:
    print(f"  {name:<6}{where:<26}{note}")
