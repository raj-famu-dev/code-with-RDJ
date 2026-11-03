# `_7_EmailSmtpPop3Imap.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Electronic mail is a store-and-forward system: your mail program hands a message to a mail server, servers pass it on to the recipient's server, and the recipient later fetches it from a mailbox. It is built from three protocol roles: SMTP to push mail between machines, a message format (RFC 5322 headers plus MIME for attachments and non-ASCII text), and POP3 or IMAP so users can read their mailbox. Mail is asynchronous: the recipient does not have to be online when you send.

**Architecture.** User agent (UA) is the mail client. A mail transfer agent (MTA) is the server that accepts and relays mail. The sender's MTA looks up the MX record of the recipient's domain in DNS and connects to that server on TCP port 25. A mail delivery agent (MDA) puts the final message in the user's mailbox. A mail access agent (MAA), the POP3 or IMAP server, lets the UA retrieve it. Mail that cannot be delivered right now (a 4xx reply or no connection) is queued and retried, typically for days, then bounced.

**SMTP (RFC 5321).** Text commands over TCP, one reply per command; replies start with a three-digit code (2xx success, 3xx need more input, 4xx temporary failure, 5xx permanent failure). A transaction is: `EHLO name`, `MAIL FROM:<sender>`, one or more `RCPT TO:<recipient>`, `DATA` (server answers 354; the client then sends the headers, a blank line, the body, and a line containing only a dot), `QUIT`. The addresses in `MAIL FROM` and `RCPT TO` are the envelope, what the servers use to route, and they may differ from the `From:`, `To:` and `Cc:` header lines in the message. A Bcc recipient exists only in the envelope. Ports: 25 server to server; 587 for clients submitting mail (with login and STARTTLS); 465 for implicit-TLS submission. SMTP itself is a push protocol and, with the original design, carries only 7-bit ASCII.

| Code | Meaning |
|---|---|
| 220 | service ready (greeting) |
| 221 | closing connection |
| 250 | requested action OK |
| 354 | start mail input, end with `<CRLF>.<CRLF>` |
| 421 | service not available (temporary) |
| 450 / 550 | mailbox unavailable: temporary / permanent |
| 500 / 501 | command not recognised / syntax error in arguments |
| 503 | bad sequence of commands |

**MIME.** Multipurpose Internet Mail Extensions add headers (`MIME-Version`, `Content-Type`, `Content-Transfer-Encoding`, `Content-Disposition`) so a message can contain several parts (`multipart/mixed` for attachments, `multipart/alternative` for text and HTML versions), other character sets and binary data. Binary parts are encoded with base64: every 3 bytes become 4 printable characters, so size grows by one third (length = 4 x ceil(n / 3)). Quoted-printable is used for mostly-ASCII text. Parts are separated by a boundary string that must not occur in the data.

**POP3 vs IMAP.**

| | POP3 (port 110, TLS 995) | IMAP (port 143, TLS 993) |
|---|---|---|
| Model | download messages, usually delete from server | mail stays on server, clients synchronise |
| Folders and flags | no (single inbox) | yes, kept on server |
| Several devices | awkward | natural |
| Offline | everything is local | needs a local cache |
| Complexity | very simple | more states and commands |

HTTP-based web mail uses HTTP between browser and mail provider, but SMTP between providers.

**Spam and authentication.** Anyone can write any `From:` header, so forged mail is easy. Defences: SPF (the domain publishes in a DNS TXT record which servers may send for it), DKIM (the sending server signs the message; the public key is in DNS), DMARC (a policy for what receivers do when SPF/DKIM fail and where to send reports). Together with content filters, blocklists and rate limits they reduce spam and phishing. None of them encrypts the message: transport encryption is STARTTLS or TLS ports, and end-to-end secrecy needs S/MIME or PGP.

**Typical exam questions.** Draw the path of a message from Alice to Bob with the protocols on each hop. List the SMTP commands in order with reply codes. Compare POP3 and IMAP. What is MIME and why base64? Why does SMTP need a dot at the end of data? Difference between envelope and header addresses.

## Full Line-by-Line Breakdown

### SECTION 1: MAIL ARCHITECTURE
An ASCII picture of the path UA, MTA, MTA, MDA, mailbox, then POP3/IMAP back to the UA, plus the one-line definition of each agent and the ports. The remark about MX records links this chapter to DNS.

Output from a real run:

```text
===== SECTION 1: MAIL ARCHITECTURE =====
  alice's UA --SMTP--> alice's MTA ==SMTP==> bob's MTA --MDA--> mailbox <--POP3/IMAP-- bob's UA
  (push)                 (push, server to server)               (pull: retrieval)
  UA  user agent : the mail program (Thunderbird, Outlook, a web mail page)
  MTA mail transfer agent : server that relays mail (Postfix, Exim, Exchange)
  MDA mail delivery agent : puts the message into the recipient's mailbox
  MAA mail access agent   : POP3 or IMAP server letting the UA read the mailbox
SMTP PUSHES mail (UA->MTA and MTA->MTA, TCP port 25; submission port 587).
POP3 (110) and IMAP (143) PULL mail. Mail finds its server through the
recipient domain's MX record in DNS (see the DNS files).
```

### SECTION 2: SMTP COMMANDS AND REPLY CODES
Printed tables of the commands and the reply-code families with the common codes.

Output from a real run:

```text
===== SECTION 2: SMTP COMMANDS AND REPLY CODES =====
  HELO / EHLO host  greet; EHLO also asks for extensions
  MAIL FROM:<a@x>   start a transaction, name the envelope sender
  RCPT TO:<b@y>     add one envelope recipient (repeat per recipient)
  DATA              then headers + blank line + body, ended by a line with only '.'
  RSET / NOOP       abort the transaction / do nothing
  QUIT              end the session
Reply codes: first digit 2 = success, 3 = send more, 4 = temporary failure
(try later), 5 = permanent failure (do not retry).
  220  service ready
  221  closing channel
  250  requested action OK
  354  start mail input
  421  service not available
  450  mailbox busy (temporary)
  500  command not recognized
  503  bad sequence of commands
  550  mailbox unavailable / refused
```

### SECTION 3: A HAND-TYPED SMTP DIALOGUE ON LOOPBACK
The server is `SmtpHandler`, a `socketserver.StreamRequestHandler` run by `ThreadingTCPServer` on `127.0.0.1` port 0, so each client gets its own thread. It reads one line at a time, splits it into command and argument, and answers with the right code. It is deliberately tiny: no authentication, no TLS, and it only accepts recipients at `example.test` (a reserved test domain), so nothing can leave the machine and no real mail exists. Here a raw socket plays the client and shows mistakes: `RCPT TO` before `MAIL FROM` gets 503, a recipient in another domain gets 550, the nonsense command `FLY` gets 500. After `DATA` and the 354 reply the client sends header, blank line, body and the lone `.`; the server stores the message and replies 250.

Output from a real run:

```text
===== SECTION 3: A HAND-TYPED SMTP DIALOGUE ON LOOPBACK =====
S: 220 mail.example.test ESMTP RDJ-Demo ready
C: HELO client.example.test
S: 250 mail.example.test greets client.example.test
C: RCPT TO:<bob@example.test>
S: 503 bad sequence: MAIL FROM first
C: MAIL FROM:<alice@example.test>
S: 250 sender ok
C: RCPT TO:<bob@example.test>
S: 250 recipient ok
C: RCPT TO:<eve@elsewhere.test>
S: 550 relaying denied: not a local recipient
C: FLY
S: 500 command not recognized
C: DATA
S: 354 end data with <CRLF>.<CRLF>
C: Subject: hi
C: 
C: Hello Bob.
C: .
S: 250 queued as msg-0001
C: QUIT
S: 221 bye
Note the errors: RCPT before MAIL -> 503, other domain -> 550, 'FLY' -> 500.
The transaction still succeeded because each failed command was just refused.
check: OK (only the accepted recipient was queued)
```

### SECTION 4: MIME, BASE64 AND ATTACHMENTS
`EmailMessage` builds a `multipart/mixed` message with a nested `multipart/alternative` (plain text and HTML) plus a binary attachment of 48 bytes (0 to 47). `set_boundary` fixes the separator text, which the library would otherwise randomise. The structure walk shows the tree: the attachment part is `application/octet-stream` with `base64`. 48 bytes become 64 characters (4 x 16), cross-checked against the `base64` module and by decoding the payload back. The Bcc header is present at this stage; Section 5 shows what happens to it.

Output from a real run:

```text
===== SECTION 4: MIME, BASE64 AND ATTACHMENTS =====
MIME structure (walk):
  multipart/mixed            cte=None file=None
  multipart/alternative      cte=None file=None
  text/plain                 cte=7bit file=None
  text/html                  cte=7bit file=None
  application/octet-stream   cte=base64 file=data.bin

Top of the raw message:
  | From: alice@example.test
  | To: bob@example.test
  | Bcc: carol@example.test
  | Subject: Lab report
  | Date: Mon, 01 Jan 2024 09:00:00 +0000
  | Message-ID: <demo-0001@example.test>
  | MIME-Version: 1.0
  | Content-Type: multipart/mixed; boundary="==DEMO-BOUNDARY-0=="
  | 
  | --==DEMO-BOUNDARY-0==
  | Content-Type: multipart/alternative; boundary="==DEMO-BOUNDARY-1=="

attachment: 48 bytes -> 64 base64 characters (4 per 3 bytes, +33%)
  first base64 line: AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwd
check: OK (decoded payload equals the original bytes; length formula holds)
MIME adds: MIME-Version, Content-Type (with boundary), Content-Transfer-Encoding,
Content-Disposition. SMTP itself only carries 7-bit text, hence base64.
```

### SECTION 5: smtplib CLIENT -> OUR SERVER; ENVELOPE VS HEADERS
`smtplib.SMTP(...)` is the real standard-library client. It sends `EHLO`, `MAIL FROM`, one `RCPT TO` per address, `DATA` and `QUIT`. We give three recipients; the server refuses the foreign one, and `send_message` returns that refusal while delivering to the other two. `send_message` also removes the `Bcc` header from the transmitted copy, so the stored message has no Bcc line yet carol is in the envelope list. The server transcript (server-side log lines; the DATA body is summarised as 39 lines) shows the actual protocol conversation. Note that smtplib sends commands in lowercase; SMTP commands are case-insensitive.

Output from a real run:

```text
===== SECTION 5: smtplib CLIENT -> OUR SERVER; ENVELOPE VS HEADERS =====
recipients refused by the server: {'eve@elsewhere.test': (550, b'relaying denied: not a local recipient')}
envelope (RCPT TO) : ['bob@example.test', 'carol@example.test']
header To:         : bob@example.test
header Bcc present?: False
Bcc recipients get the mail because the ENVELOPE lists them, but the header
is stripped, so other recipients never see them.
check: OK (attachment survived SMTP intact)

Server-side transcript of that session:
   S: 220 mail.example.test ESMTP RDJ-Demo ready
   C: ehlo client.example.test
   S: 250-mail.example.test greets client.example.test
   S: 250 8BITMIME
   C: mail from:<alice@example.test>
   S: 250 sender ok
   C: rcpt to:<bob@example.test>
   S: 250 recipient ok
   C: rcpt to:<carol@example.test>
   S: 250 recipient ok
   C: rcpt to:<eve@elsewhere.test>
   S: 550 relaying denied: not a local recipient
   C: data
   S: 354 end data with <CRLF>.<CRLF>
   C: [39 data lines] + '.'
   S: 250 queued as msg-0002
   C: QUIT
   S: 221 bye
```

### SECTION 6: TRAP - A LINE WITH ONLY A DOT
SMTP ends the message at a line holding only `.`. If a user's text contains such a line it would cut the message short (and the rest could even be misread as commands). The cure is dot-stuffing: the sender doubles any leading dot and the receiver removes one. Our message deliberately contains `.a line starting with a dot` and a lone `.`. They arrive intact because `smtplib` stuffs them and our server unstuffs them. The pure functions `stuff` and `unstuff` show the wire form, and a naive scanner that looks for the end marker without stuffing would have stopped at `one`.

Output from a real run:

```text
===== SECTION 6: TRAP - A LINE WITH ONLY A DOT =====
the plain-text body we sent contains the lines: '.a line starting with a dot' and '.'
body as received: ['Hello Bob,', 'the data file is attached.', '.a line starting with a dot', '.', 'Bye']
SMTP ends DATA at a line containing only '.'. So the sender must DOT-STUFF:
  any body line starting with '.' gets an extra '.' (so '.' becomes '..').
The receiver removes one leading '.' from each such line.
  original: ['one', '.', '.hidden', 'two']
  on wire : ['one', '..', '..hidden', 'two']
  naive end-of-data scan WITHOUT stuffing would stop after: 'one'
check: OK (stuffing round-trips; smtplib did this for us, as the received body shows)
```

### SECTION 7: POP3 VS IMAP, SPAM, SPF/DKIM/DMARC
Text summary of the access protocols and the anti-forgery trio. There is no network code in this section; no DNS lookups are made.

Output from a real run:

```text
===== SECTION 7: POP3 VS IMAP, SPAM, SPF/DKIM/DMARC =====
              POP3 (port 110, TLS 995)          IMAP (port 143, TLS 993)
model         download then (usually) delete    mail stays on server, synced
folders       inbox only                        server-side folders and flags
devices       awkward with several              natural with several
offline       good (it is all local)            needs cache; works online
state         simple, stateless-ish             stateful session
Spam: unwanted bulk mail; fought by filters, blocklists, rate limits.
SPF  : domain lists (in DNS TXT) which servers may send its mail.
DKIM : sender MTA signs headers/body; receiver checks the signature using a
       public key published in DNS.
DMARC: policy telling receivers what to do when SPF/DKIM fail and where to report.
These stop forged 'From' domains; none of them encrypts the message. Use TLS
(STARTTLS or port 465) for transport and S/MIME or PGP for end-to-end secrecy.

server stopped: True
```

## Worked Example
**Problem.** Alice (`alice@a.test`) mails Bob (`bob@b.test`) a 1 MB photo. (a) List the SMTP commands and expected reply codes. (b) About how large is the base64 attachment on the wire? (c) Does Bob use SMTP to read the mail?

**Solution.** (a) Server greeting `220`; `EHLO a.test` -> `250`; `MAIL FROM:<alice@a.test>` -> `250`; `RCPT TO:<bob@b.test>` -> `250`; `DATA` -> `354`; the headers, blank line, body and `.` -> `250`; `QUIT` -> `221`. (b) Base64 expands by 4/3, so 1 MB becomes about 1.33 MB (plus line breaks), and the mail server may reject it for exceeding a size limit with a 552. (c) No: SMTP only pushes mail to Bob's server; Bob retrieves it with IMAP or POP3 (or a web mail page over HTTP). The code confirmed the sequence in Section 3 and the 4/3 growth in Section 4 (48 bytes to 64 characters).

## Key Rules / Gotchas Recap
- SMTP pushes, POP3 and IMAP pull. Servers find each other with the MX record.
- Reply code first digit: 2 OK, 3 continue, 4 try later, 5 never.
- Command order: HELO/EHLO, MAIL, RCPT (one or more), DATA, `.`, QUIT; wrong order gives 503.
- Envelope (MAIL/RCPT) is separate from the header lines; Bcc lives only in the envelope.
- Base64 = 4 chars per 3 bytes (+33%); parts are separated by a boundary.
- Dot-stuff lines that start with `.`; never end DATA on an unstuffed lone dot.
- SPF, DKIM, DMARC authenticate the sending domain; they do not encrypt.
- Never send test mail to real addresses; this code only talks to its own loopback server.

## Why This Matters
Email is still the identity and notification backbone of most systems (password resets, alerts), and mail headers are a standard phishing and spoofing battleground. Writing the server side once makes it clear why parsers must handle framing, ordering and untrusted input carefully.
