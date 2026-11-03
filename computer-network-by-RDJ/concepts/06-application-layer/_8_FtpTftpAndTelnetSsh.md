# `_8_FtpTftpAndTelnetSsh.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
FTP, TFTP, Telnet and SSH are the classic application protocols for moving files and logging in to remote machines. FTP and Telnet are old and send everything, including passwords, in clear text; TFTP is a stripped-down file copier for tiny jobs; SSH is the encrypted replacement used for remote administration today. They are worth studying because they show clear design choices (separate control and data channels, stop-and-wait over UDP, why encryption matters).

**FTP (RFC 959).** File Transfer Protocol uses two TCP connections. The control connection (server port 21) lasts for the whole session and carries text commands and numeric replies. For each file transfer or directory listing a separate data connection is opened and closed. Because control information is sent "out of band" on its own connection, FTP is described as out-of-band; HTTP, in contrast, is in-band. FTP is stateful: the server remembers the login and the current directory.

*Active mode:* the client opens a listening port and sends `PORT h1,h2,h3,h4,p1,p2` (its IP address as four numbers and the port as two bytes, port = p1 x 256 + p2); the server connects from its port 20 to that address. This usually fails when the client is behind a firewall or NAT. *Passive mode:* the client sends `PASV`; the server opens a port and answers `227 Entering Passive Mode (h1,h2,h3,h4,p1,p2)`; the client opens the data connection. Passive mode is the default in modern clients.

| Command | Purpose | Command | Purpose |
|---|---|---|---|
| USER, PASS | log in | RETR | download a file |
| PWD, CWD | show / change directory | STOR | upload a file |
| LIST | directory listing (over data connection) | PORT, PASV | choose active / passive mode |
| TYPE | ASCII or binary (image) mode | QUIT | end session |

Reply codes: 1xx positive preliminary (150 opening data connection), 2xx positive completion (200 OK, 226 transfer complete, 230 logged in, 227 passive mode, 257 path), 3xx need more information (331 need password), 4xx temporary failure (425 cannot open data connection), 5xx permanent failure (530 not logged in, 550 file unavailable). Anonymous FTP lets anyone log in as `anonymous` with an e-mail-like password for public, usually read-only, files.

Security: FTP sends passwords and data in clear text. The "FTP bounce attack" abuses `PORT` to make a server connect to a third host, so servers must accept `PORT` only for the client's own address. FTPS is FTP wrapped in TLS (explicit on port 21 with `AUTH TLS`, or implicit on port 990). SFTP is a completely different protocol that runs as a subsystem of SSH on port 22.

**TFTP (RFC 1350).** Trivial File Transfer Protocol: UDP port 69, no login, no directory listing, only read (RRQ) and write (WRQ) of whole files. Five packet types: RRQ 1, WRQ 2, DATA 3, ACK 4, ERROR 5. Files are sent in blocks of 512 bytes, numbered from 1. It uses stop-and-wait: after each DATA block the sender waits for the matching ACK, retransmitting on timeout. A block of fewer than 512 bytes signals the end, so a file whose size is an exact multiple of 512 ends with an empty block (number of blocks = size // 512 + 1). The server answers from a new ephemeral port (the transfer ID), the client then talks to that port. Simplicity makes it small enough for firmware (network booting, router and phone configuration), but throughput is at most one block per round trip (512 bytes per RTT).

**Telnet (RFC 854) vs SSH (RFC 4251 family).** Telnet gives a remote terminal over TCP port 23; what you type, including the password, travels as plain text, and options are negotiated with command bytes that start with 255 (IAC). SSH, TCP port 22, provides the same remote shell with strong security: the two sides run a key exchange (Diffie-Hellman style) to agree a session key without sending it, the client verifies the server's host key (the first connection shows a fingerprint that you should check), the user is authenticated by password or, better, a public/private key pair, and all traffic is encrypted and integrity-protected. SSH also offers port forwarding, SCP and SFTP.

| | Telnet | SSH |
|---|---|---|
| Port | 23 | 22 |
| Encryption | none | all traffic |
| Server authentication | none | host key |
| Typical use today | legacy equipment, labs | remote administration |

**Typical exam questions.** Why does FTP use two connections? Explain active and passive mode with a diagram. Which port numbers do FTP, TFTP, Telnet and SSH use (21 and 20, 69, 23, 22)? Why does TFTP use UDP and how does it get reliability? Compare FTP and TFTP. Why is Telnet insecure? Difference between SFTP and FTPS.

## Full Line-by-Line Breakdown

### SECTION 1: FTP IDEAS
A diagram and a summary of the control and data connections, active and passive mode, reply codes, and the port arithmetic `p1 x 256 + p2` (19 x 256 + 137 = 5001, an assertion).

Output from a real run:

```text
===== SECTION 1: FTP IDEAS =====
  client                                   server
  ctrl port N  ----- control connection ----- port 21   (commands + replies, text)
  data port    ----- data connection    ----- port 20 (active) or a server-chosen port (passive)
  The control connection lives for the whole session ("out-of-band" control).
  A NEW data connection is opened for each file transfer or directory listing.
ACTIVE mode : client says PORT h1,h2,h3,h4,p1,p2; the SERVER connects to the client.
PASSIVE mode: client says PASV; the server opens a port and tells it; the CLIENT
              connects. Passive works through client-side firewalls/NAT, so it is
              the usual choice today. Port number = p1 x 256 + p2.
FTP is stateful (login, current directory) and sends passwords in CLEARTEXT.
Anonymous FTP: user 'anonymous', password = any e-mail-like string, read-only files.
Reply codes: 1xx preliminary, 2xx done, 3xx need more, 4xx temporary error, 5xx error.
  220 ready, 331 need password, 230 logged in, 257 path, 227 passive mode, 150 opening
  data connection, 226 transfer complete, 530 not logged in, 550 file unavailable, 221 bye
check: OK (p1=19, p2=137 -> port 19*256+137 = 5001)
```

### SECTION 2: A MINI FTP SERVER - PASSIVE MODE SESSION
`FtpHandler` is a `socketserver.StreamRequestHandler`: the control channel. It keeps per-session state (user, logged in, current directory, pending PASV listener or PORT address) and speaks a small FTP subset over an in-memory file table (`FILES`). The reply to `PASV` is `227 (127,0,0,1,P1,P2)`; the actual port numbers are masked by `mask()` so the output is the same every run. In the transcript: `LIST` before login gets 530, a wrong password gets 530, the right one 230. After `PASV` the client opens a second socket to the advertised port, sends `LIST` on the control connection, reads the listing from the data socket until the server closes it, and finally reads `226`. The same pattern downloads `notes.txt`; the check compares the downloaded bytes with the server's copy. Notice that three different sockets are involved: the control connection, the data connection for the listing and a new one for the download.

Output from a real run:

```text
===== SECTION 2: A MINI FTP SERVER - PASSIVE MODE SESSION =====
   S: 220 RDJ mini FTP ready
   C: LIST
   S: 530 please log in first
   C: USER student
   S: 331 password please
   C: PASS wrong
   S: 530 login incorrect
   C: PASS pa55word
   S: 230 logged in
   C: PWD
   S: 257 "/" is the current directory
   C: CWD pub
   S: 250 directory changed
   C: PASV
   S: 227 Entering Passive Mode (127,0,0,1,P1,P2)
   C: LIST
   S: 150 opening data connection
   S: 226 transfer complete
   data connection carried: ['big.bin', 'notes.txt']
   C: PASV / RETR notes.txt
   S: 150 opening data connection
   S: 226 transfer complete
   downloaded: b'Control connection: commands. Data connection: bytes.\n'
   C: QUIT
   S: 221 bye
check: OK (file bytes equal the server's copy; control and data were separate sockets)
```

### SECTION 3: ACTIVE MODE AND THE PORT-BOUNCE CHECK
Now the client listens (`PORT 127,0,0,1,P1,P2`) and the server connects back when `RETR` runs (the `150` reply arrives while the server connects to us; we `accept` and read until EOF). This session uses `anonymous`. Then `PORT 10,0,0,5,0,80` names a different address; the server compares it with `self.client_address[0]` and refuses with 504 without connecting anywhere. A request for a missing file returns 550.

Output from a real run:

```text
===== SECTION 3: ACTIVE MODE AND THE PORT-BOUNCE CHECK =====
   S: 220 RDJ mini FTP ready
   C: USER anonymous
   S: 331 anonymous ok, send e-mail as password
   C: PASS rdj@example.test
   S: 230 logged in
   C: PORT 127,0,0,1,P1,P2
   S: 200 PORT ok
   C: RETR README.txt
   S: 150 opening data connection
   S: 226 transfer complete
   active mode: the SERVER opened the data connection; we received: b'Welcome to the RDJ mini FTP server.\n'
Trap (FTP bounce): a malicious client could say PORT <victim ip>,<victim port>
and make the server connect to a third machine. Defence: refuse any PORT whose
address is not the client's own address.
   C: PORT 10,0,0,5,0,80
   S: 504 PORT address must be the client's own (bounce protection)
   C: RETR nothing.txt
   S: 550 file unavailable
   C: QUIT
   S: 221 bye
check: OK (active transfer worked; bounce attempt refused with 504)
```

### SECTION 4: WHAT A CAPTURE WOULD SHOW - CLEARTEXT
Prints the server-side log of the first session. Both the username and the (demo) password appear as ordinary text lines; any device on the path could read them. This is the reason to use SFTP or FTPS today.

Output from a real run:

```text
===== SECTION 4: WHAT A CAPTURE WOULD SHOW - CLEARTEXT =====
Server-side log of the first session (this is what anyone on the path sees):
    S: 220 RDJ mini FTP ready
    C: LIST
    S: 530 please log in first
    C: USER student
    S: 331 password please
    C: PASS wrong
    S: 530 login incorrect
    C: PASS pa55word
    S: 230 logged in
The password 'pa55word' (a demo value) travels as readable text. The same holds
for Telnet and for the files themselves. FTPS wraps FTP in TLS; SFTP is a
different protocol that runs inside SSH (port 22). They are NOT the same thing.
```

### SECTION 5: TFTP - UDP, 512-BYTE BLOCKS, STOP-AND-WAIT
A table of block counts for several file sizes (0 and 511 need 1, 512 needs 2 because of the empty final block, 1024 needs 3). `TftpServer` listens on UDP port 0; for each read request it opens a new socket (a new "transfer ID" port) and sends DATA block n, waits up to 0.3 s for ACK n, and resends on timeout. To demonstrate recovery, the first transmission of block 2 of `two_blocks.bin` is skipped, as if the network had lost it; the timeout fires and the resend succeeds, counted as 1 retransmission. `tftp_get` is the client: it sends RRQ, takes the server's new port as the transfer ID, ACKs each block, ignores duplicates, stops at the first short block and handles ERROR packets (code 1, file not found). `exact512.bin` shows the empty final block.

Output from a real run:

```text
===== SECTION 5: TFTP - UDP, 512-BYTE BLOCKS, STOP-AND-WAIT =====
TFTP (port 69/UDP): no login, no directories, tiny; used for network boot and
router config files. Opcodes: 1 RRQ, 2 WRQ, 3 DATA, 4 ACK, 5 ERROR.
Each DATA block carries up to 512 bytes. A block shorter than 512 ENDS the file.
Stop-and-wait: send block n, wait for ACK n, only then send n+1; on timeout resend.
 file size  DATA blocks  (last block is shorter than 512, maybe empty)
         0            1
       100            1
       511            1
       512            2
       513            2
      1024            3

Downloads from the loopback TFTP server (block 2 of two_blocks.bin is 'lost' once):
  hello.txt        ->   16 bytes in blocks [1]  correct=True
  exact512.bin     ->  512 bytes in blocks [1, 2]  correct=True
  two_blocks.bin   -> 1024 bytes in blocks [1, 2, 3]  correct=True
  nope.txt         -> ERROR code 1 (1 = file not found)
exact512.bin is exactly 512 bytes, so block 2 is EMPTY: that is how the receiver
knows the file ended. (A 513-byte file needs block 2 with 1 byte.)
server retransmissions caused by the simulated loss: 1
check: OK (stop-and-wait recovered the lost block by timeout + resend)
tftp thread stopped: True
Stop-and-wait throughput = block size / RTT, e.g. 512 bytes per 10 ms = 51,200 B/s,
however fast the link is. That is why TFTP is for small files only.
```

### SECTION 6: TELNET VS SSH AND THE KEY-EXCHANGE IDEA
A comparison table, then the three bytes `ff fd 01` decoded as `IAC DO ECHO` (a Telnet negotiation request: "please echo"). The Diffie-Hellman demo uses toy numbers `p=23, g=5` and secrets a=6, b=15. Each side sends only `g^secret mod p` (8 and 19); each computes the shared value (2) by raising what it received to its own secret. An eavesdropper sees `p, g, A, B` but would need a discrete logarithm to find the secret, which is infeasible for the huge numbers used in real SSH but trivial for 23. The assertion proves both sides agree and equal `g^(ab) mod p`.

Output from a real run:

```text
===== SECTION 6: TELNET VS SSH AND THE KEY-EXCHANGE IDEA =====
              Telnet                    SSH
port          23/TCP                    22/TCP
encryption    none (cleartext)          yes, all traffic
server auth   none                      host key (check fingerprint)
user auth     password in clear         password or public key
extras        -                         port forwarding, SFTP, SCP
use today     legacy / lab only         standard for remote admin
A Telnet option negotiation on the wire: ff fd 01 = IAC DO ECHO

How SSH gets a shared key without sending it (Diffie-Hellman idea, TOY numbers):
  public: p=23, g=5.  client secret a=6 -> sends A=g^a mod p=8
  server secret b=15 -> sends B=g^b mod p=19
  client computes B^a mod p=2; server computes A^b mod p=2
check: OK (both sides get the same secret; an eavesdropper sees only p, g, A, B)
Real SSH uses huge groups or elliptic curves (toy p=23 is trivially breakable),
then derives session keys, authenticates the server with its host key and the
user with a password or key pair. First connection: verify the fingerprint.
SFTP (inside SSH, port 22) vs FTPS (FTP + TLS, ports 21/990): different protocols.
```

## Worked Example
**Problem.** (a) An FTP server tells a client `227 Entering Passive Mode (192,168,1,20,19,137)`. To which address and port should the client connect for the data connection? (b) How many TFTP DATA blocks and ACKs are needed for a 1300-byte file, and what does the last block carry? (c) If RTT is 20 ms, what is the maximum TFTP throughput?

**Solution.** (a) IP 192.168.1.20, port 19 x 256 + 137 = 4864 + 137 = 5001. (b) 1300 // 512 + 1 = 3 blocks: 512, 512 and 276 bytes; 3 ACKs. The last block is shorter than 512, so it ends the transfer. (c) One 512-byte block per RTT: 512 / 0.020 s = 25,600 bytes per second, regardless of link speed. Section 2 confirms the port arithmetic and Section 5 the block counts.

## Key Rules / Gotchas Recap
- FTP = two TCP connections: control (21) and data (20 in active mode, server-chosen port in passive). Passive mode works behind firewalls and NAT.
- Port in `PORT` and `PASV` = p1 x 256 + p2.
- Reject `PORT` for any address except the client's own (bounce attack).
- TFTP: UDP 69, 512-byte blocks, stop-and-wait, last block shorter than 512; an exact multiple needs an empty last block.
- TFTP server replies from a new port; the client must remember that port (transfer ID).
- Telnet (23) and FTP send passwords in clear text. SSH (22) encrypts. SFTP is over SSH; FTPS is FTP over TLS.
- Check the SSH host fingerprint on first connection.
- Never test with real hosts; this code only uses its own loopback servers and demo credentials.

## Why This Matters
Engineers still meet these protocols: SFTP/SSH for deployments and model or data transfers, TFTP and FTP in embedded devices and legacy pipelines. Seeing credentials in a transcript explains why insecure protocols are first targets in security assessments, and the bounce check is a real example of validating an untrusted instruction from a client.
