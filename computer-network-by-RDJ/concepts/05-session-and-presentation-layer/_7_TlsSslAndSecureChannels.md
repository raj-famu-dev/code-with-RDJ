# `_7_TlsSslAndSecureChannels.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
TLS (Transport Layer Security, the successor of SSL) wraps an ordinary TCP connection in an encrypted, authenticated channel so that eavesdroppers cannot read or change the data and the client can be sure it is talking to the real server. HTTPS is simply HTTP carried over TLS. It combines everything in this chapter: certificates for identity, key exchange for a fresh secret, symmetric encryption for speed, and MACs/AEAD for integrity.

**Place in the stack.** TLS sits between the application protocol and TCP (loosely "session/presentation" in OSI). Application data goes into TLS, TLS sends records over TCP. HTTPS uses port 443; other protocols have TLS variants (SMTPS, IMAPS, or an upgrade command such as STARTTLS). DTLS and QUIC give the same ideas over UDP.

**History.** SSL 1.0 was never released; SSL 2.0 and 3.0 are broken and prohibited; TLS 1.0 and 1.1 are deprecated (RFC 8996). TLS 1.2 (RFC 5246) and TLS 1.3 (RFC 8446) are the versions to use.

**Full handshake, TLS 1.2 (RSA/ECDHE style)**
1. *ClientHello*: highest version, client random, list of cipher suites.
2. *ServerHello*: chosen version and cipher suite, server random.
3. *Certificate*: the server's certificate chain.
4. *ServerKeyExchange* (for ECDHE): the server's ephemeral public value, signed with its certificate key.
5. *ServerHelloDone*.
6. *ClientKeyExchange*: client's key share (or encrypted pre-master secret in old RSA key transport).
7. Both compute the master secret and session keys, send *ChangeCipherSpec* and an encrypted *Finished* (a MAC over the whole handshake transcript).
That is two round trips before application data.

**TLS 1.3 differences.** One round trip: the ClientHello already contains key shares for the guessed key-exchange group. After ServerHello everything (certificate included) is encrypted. Removed: RSA key transport, static DH, CBC and RC4 ciphers, SHA-1, compression, renegotiation. Only AEAD ciphers remain and forward secrecy is always on (ephemeral keys). Cipher suites name only the AEAD cipher and the hash (for example `TLS_AES_128_GCM_SHA256`). Session resumption and 0-RTT exist; 0-RTT data can be replayed, so it is limited to safe requests.

**Cipher suite anatomy (TLS 1.2).** `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` reads: key exchange ECDHE (ephemeral elliptic-curve DH), authentication RSA (server's certificate key signs), bulk cipher AES-128 in GCM mode, hash SHA-256 (used in the PRF/handshake).

**Record protocol.** After the handshake, data is split into records (up to 2^14 bytes of plaintext each), each protected with the negotiated cipher and integrity check (a sequence number prevents replay and reordering inside the connection), then sent over TCP. Record types include handshake, alert, application data.

**Forward secrecy.** With ephemeral DH keys, stealing the server's long-term key later does not decrypt recorded old traffic.

**Other secure channels**

| Technology | Layer | Notes |
|---|---|---|
| TLS | above TCP | per application; HTTPS, email |
| SSH | above TCP, port 22 | secure remote login, file copy, tunnels |
| IPsec | network layer | AH and ESP headers, transport and tunnel modes, IKE for keys |
| VPN | a service | a tunnel built with IPsec, WireGuard, OpenVPN (TLS based) |

**Typical exam questions.** Draw the TLS handshake. What does each cipher-suite part mean? Difference between TLS 1.2 and 1.3. Where do SSL/TLS and IPsec sit? What does a certificate do? What is forward secrecy?

## Full Line-by-Line Breakdown

### SECTION 1: WHERE TLS SITS IN THE STACK
A small diagram of the stack with TLS between the application and TCP, and IPsec at the network layer. Obsolete versions are listed.

```text
===== SECTION 1: WHERE TLS SITS IN THE STACK =====
  Application  HTTP | SMTP | IMAP | FTP ...   (HTTPS = HTTP over TLS, port 443)
  Secure chan. TLS (successor of SSL)         <- 'layer 5/6': between app and TCP
  Transport    TCP (DTLS/QUIC for UDP-based)
  Network      IP   (IPsec works HERE, below TCP/UDP)
  SSL 2.0/3.0 and TLS 1.0/1.1 are obsolete/deprecated; use TLS 1.2 or 1.3.
  TLS gives: confidentiality (encryption), integrity (MAC/AEAD),
  server authentication (certificate), optional client authentication.
```

### SECTION 2: HANDSHAKE AND CIPHER SUITE ANATOMY
Printed text for the TLS 1.2 message flow, the TLS 1.3 summary, and a breakdown of cipher-suite names. Nothing is computed.

```text
===== SECTION 2: HANDSHAKE AND CIPHER SUITE ANATOMY =====
  TLS 1.2 (2 round trips for a full handshake):
    C -> S  ClientHello         (versions, random, cipher suites)
    S -> C  ServerHello         (chosen suite, random)
    S -> C  Certificate         (server chain)
    S -> C  ServerKeyExchange   (e.g. ECDHE params, signed)
    S -> C  ServerHelloDone
    C -> S  ClientKeyExchange   (client ECDHE share)
    C -> S  ChangeCipherSpec + Finished  (encrypted from here)
    S -> C  ChangeCipherSpec + Finished
  TLS 1.3 (1 round trip): ClientHello carries key shares up front;
  everything after ServerHello (certificate, Finished) is encrypted.
  Cipher-suite names:
    TLS 1.2: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
             key exchange=ECDHE, authentication=RSA, cipher=AES-128-GCM, hash=SHA-256
    TLS 1.3: TLS_AES_128_GCM_SHA256 (only cipher + hash; key exchange is negotiated apart)
  1.2 vs 1.3: 1.3 removes RSA key transport, static DH, CBC, RC4, SHA-1,
  compression, renegotiation; forward secrecy (ephemeral keys) is always on.
```

### SECTION 3: ssl MODULE DEFAULT CONTEXT (NO NETWORK)
`ssl.create_default_context()` makes a client context with safe defaults: `verify_mode = CERT_REQUIRED` and `check_hostname = True`, and a minimum TLS version of 1.2 in this run. The OpenSSL version, the maximum version and TLS 1.3 support depend on the machine, which is why the first line says "environment-dependent". No connection is made. The trap is the common copy-pasted "fix" of turning off hostname and certificate checks: the traffic is still encrypted but you could be talking to an attacker. The right fix is to trust the right CA with `cafile=`.

```text
===== SECTION 3: ssl MODULE DEFAULT CONTEXT (NO NETWORK) =====
  OpenSSL runtime       : OpenSSL 3.5.9 29 Sep 2026 (environment-dependent)
  minimum_version       : TLSv1_2
  maximum_version       : MAXIMUM_SUPPORTED
  verify_mode           : CERT_REQUIRED
  check_hostname        : True
  has TLS 1.3 support   : True
  default context is SECURE by default: certificate + hostname verified.
  TRAP  context with verification off: CERT_NONE -> encrypted but UNAUTHENTICATED: a man-in-the-middle is not detected.
  FIX   keep CERT_REQUIRED; trust a private CA via cafile=..., never disable checks.
  bare SSLContext(PROTOCOL_TLS_CLIENT) verify_mode: CERT_REQUIRED (also CERT_REQUIRED in modern Python)
  check: OK
```

### SECTION 4: TOY HANDSHAKE SIMULATED IN MEMORY (NOT REAL TLS)
Both sides are in the same process. Each message is appended to a transcript and printed with its size. The flow mirrors TLS 1.3: ClientHello and ServerHello carry a random value and a DH public value (a 64-bit prime, `2^64 - 59`, toy size); the server sends its Certificate and a CertificateVerify (an HMAC over the transcript, standing in for a real signature); both derive keys from the DH secret and the transcript hash with HMAC (a simplified key-derivation); each side sends Finished, a MAC over the transcript. The record layer seals a message with a sequence number, a hash-based keystream (a toy) and a truncated HMAC tag. Flipping one bit makes the tag check fail ("bad record MAC"). Real TLS uses AEAD ciphers, proper HKDF and real signatures.

```text
===== SECTION 4: TOY HANDSHAKE SIMULATED IN MEMORY (NOT REAL TLS) =====
  Client -> Server  ClientHello         51 bytes
  Server -> Client  ServerHello         51 bytes
  Server -> Client  Certificate         23 bytes
  Server -> Client  CertificateVerify   32 bytes
  Server -> Client  Finished            32 bytes
  Client -> Server  Finished            32 bytes
  both sides computed the same keys: True
  Finished = MAC over the whole transcript: any tampering during the
  handshake makes it fail (this is how downgrade attempts are caught).

  Record protocol (toy): split data into records, seq number, encrypt+MAC.
  sealed record: 00 00 00 00 00 00 00 00 d9 9a fb 6c 98 fe c7 c4 ...
  opened       : b'GET / HTTP/1.1'
  flip one bit  -> bad record MAC (integrity protected)
  check: OK. Real TLS uses AEAD ciphers (AES-GCM, ChaCha20-Poly1305).
```

### SECTION 5: LOOPBACK TLS WRAP (127.0.0.1 ONLY)
If the `openssl` command-line tool exists, the script creates a throw-away self-signed EC certificate for `localhost` in a temporary directory, starts a TLS server thread on `127.0.0.1` port 0, and connects a client that trusts only that certificate (`create_default_context(cafile=...)`). The negotiated version and cipher are printed; they depend on the local OpenSSL, so treat them as measurements from this machine. If `openssl` were missing the section would print "SKIPPED". Second part (trap): a client with the normal system trust store refuses the same server with "self-signed certificate". Sockets have timeouts, threads are joined and sockets closed.

```text
===== SECTION 5: LOOPBACK TLS WRAP (127.0.0.1 ONLY) =====
  negotiated version : TLSv1.3 (depends on local OpenSSL)
  cipher suite       : TLS_AES_256_GCM_SHA384
  server cert subject: {'commonName': 'localhost'}
  client sent / got  : b'hello server' / b'hello over TLS'
  server received    : b'hello server'
  TRAP default trust store rejects our self-signed cert: self-signed certificate
  check: OK (private cert deleted with the temp directory)
```

### SECTION 6: IPSEC / SSH / VPN PLACEMENT
Table of where each secure-channel technology sits. IPsec works below TCP so applications need no changes; TLS and SSH work above TCP.

```text
===== SECTION 6: IPSEC / SSH / VPN PLACEMENT =====
  TLS   above TCP                 per-application (HTTPS, SMTPS, IMAPS)
  SSH   above TCP (port 22)       remote login, file copy, port forwarding
  IPsec network layer (AH/ESP)    protects all IP traffic; transport/tunnel mode; IKE keys
  VPN   a use, not one protocol   tunnel via IPsec, WireGuard, OpenVPN (TLS-based) ...
```

## Worked Example
**Problem.** For the suite `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`, name each part; then say how many round trips a full TLS 1.2 handshake needs before application data, compared with TLS 1.3, and what the client does if the server's certificate name does not match.

1. `ECDHE`: key exchange is ephemeral elliptic-curve Diffie-Hellman, giving forward secrecy.
2. `RSA`: the server proves its identity with an RSA signature using its certificate key.
3. `AES_256_GCM`: bulk encryption with AES, 256-bit key, GCM mode (authenticated encryption).
4. `SHA384`: the hash used for the handshake PRF and key derivation.
5. TLS 1.2 needs two round trips for a full handshake, TLS 1.3 needs one (resumption can be faster).
6. If the name or chain does not validate, a correct client aborts with a certificate error; Section 5 shows Python raising `SSLCertVerificationError` for an untrusted certificate.

## Key Rules / Gotchas Recap
- TLS = key exchange + authentication (certificate) + symmetric encryption + integrity.
- Use TLS 1.2 or 1.3; SSL and TLS 1.0/1.1 are obsolete.
- TLS 1.3: one round trip, encrypted certificate, only AEAD, always forward secrecy.
- Never disable certificate or hostname checking to silence an error.
- Encrypted does not mean authenticated: without verification a man-in-the-middle can read everything.
- IPsec is network layer; TLS and SSH sit above TCP.
- Toy handshakes in this file teach the flow only; use `ssl` or a vetted library for real traffic.

## Why This Matters
Every API call, model download and web login you will ship goes over TLS, and the common production failures are expired or mismatched certificates, old protocol versions and disabled verification. Security testing tools inspect exactly these settings, so reading a handshake and a cipher suite is a daily skill.
