# `_1_TransportLayerServicesAndPorts.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The transport layer (Layer 4) gives applications process-to-process communication: IP delivers a packet to the right machine, and the transport layer delivers the data to the right program on that machine. It does this with 16-bit port numbers, and it offers two main services: TCP (connection-oriented, reliable byte stream) and UDP (connectionless, best-effort datagrams).

**Why a new layer?** The network layer (IP) only knows hosts. A laptop runs a browser, a chat app and a music streamer at once, all sharing one IP address. Something has to say which incoming packet belongs to which program. That something is the port number carried in the transport header.

**Services the transport layer can provide**
- Process-to-process delivery (host-to-host is the network layer's job).
- Multiplexing at the sender and demultiplexing at the receiver.
- Segmentation and reassembly of application data (TCP).
- Error checking (both TCP and UDP have a checksum).
- Optionally: reliability, ordering, flow control, congestion control (TCP only).
- Connection management (TCP only).

**Port numbers (16 bits, 0 to 65535)**

| Range | Name | Use |
|---|---|---|
| 0 - 1023 | Well-known (system) ports | Standard services: HTTP 80, HTTPS 443, SSH 22, SMTP 25, DNS 53, FTP 20/21, DHCP 67/68, POP3 110, IMAP 143, NTP 123 |
| 1024 - 49151 | Registered (user) ports | Applications registered with IANA, e.g. MySQL 3306, alt-HTTP 8080 |
| 49152 - 65535 | Dynamic / private / ephemeral | Temporary client ports, chosen by the OS |

Real operating systems choose their own ephemeral range. Linux's default is 32768 to 60999, which does not match IANA's 49152 to 65535. An exam answers with the IANA ranges; real debugging needs the OS range.

**Socket and socket address.** A socket address is `IP address : port`, for example `127.0.0.1:5000`. A TCP connection is identified by the **5-tuple**: (protocol, source IP, source port, destination IP, destination port). Two browser tabs talking to the same web server use the same destination IP and port, but different source ports, so their 5-tuples differ and the server can keep them apart.

**Multiplexing and demultiplexing**
- Multiplexing (sender): many application processes hand data to the transport layer; each piece gets a header with the source and destination port, and everything goes down to one IP layer.
- Demultiplexing (receiver): the transport layer reads the destination port in the header and hands the data to the process that owns that port.
- UDP demultiplexes using only (destination IP, destination port). All senders to that port land in one socket.
- TCP demultiplexes using the full 4-tuple plus protocol: each connection gets its own socket on the server.

**Connection-oriented vs connectionless**

| | Connection-oriented (TCP) | Connectionless (UDP) |
|---|---|---|
| Setup | Three-way handshake before data | None; just send |
| Reliability | ACKs, retransmission | None |
| Ordering | Guaranteed | Not guaranteed |
| Boundaries | Byte stream, boundaries not kept | Each datagram is kept whole |
| Overhead | 20-byte header minimum, state at both ends | 8-byte header, no state |
| Examples | HTTP, SSH, SMTP, FTP | DNS queries, DHCP, streaming, games |

**Typical exam questions:** list the three port ranges; define socket address; explain multiplexing/demultiplexing; why does a client not need a well-known port; difference between a host-to-host and a process-to-process delivery; what identifies a TCP connection uniquely.

## Full Line-by-Line Breakdown

### SECTION 1: PORT NUMBER RANGES
`port_class` classifies a port by the IANA ranges and rejects values outside 0 to 65535, because a port is a 16-bit field (2 to the 16th is 65536 values). The loop prints well-known services, then boundary values (1023, 1024, 49151, 49152) because exam questions love off-by-one edges. The trap is 65536, which does not fit in 16 bits. Finally, `socket.getservbyname` asks the OS services database for the standard numbers and the code cross-checks that HTTP is 80, HTTPS is 443 and SMTP is 25. If your OS has no such database entry the check is skipped, not faked.

Output from a real run:

```text
===== SECTION 1: PORT NUMBER RANGES =====
A port is a 16-bit number: 2**16 = 65536 values (0..65535)
     20  FTP data     -> well-known (system)
     21  FTP control  -> well-known (system)
     22  SSH          -> well-known (system)
     25  SMTP         -> well-known (system)
     53  DNS          -> well-known (system)
     67  DHCP server  -> well-known (system)
     68  DHCP client  -> well-known (system)
     80  HTTP         -> well-known (system)
    110  POP3         -> well-known (system)
    123  NTP          -> well-known (system)
    143  IMAP         -> well-known (system)
    443  HTTPS        -> well-known (system)
   1023  (boundary)   -> well-known (system)
   1024  (boundary)   -> registered (user)
   3306  (boundary)   -> registered (user)
   8080  (boundary)   -> registered (user)
  49151  (boundary)   -> registered (user)
  49152  (boundary)   -> dynamic / private / ephemeral
  65535  (boundary)   -> dynamic / private / ephemeral
trap: 65536 is invalid -> port 65536 does not fit in 16 bits
check: getservbyname('http') == 80: OK
check: getservbyname('https') == 443: OK
check: getservbyname('smtp') == 25: OK
```

### SECTION 2: MULTIPLEXING / DEMULTIPLEXING (SIMULATED)
A tiny dictionary plays the role of the operating system's port table: destination port to owning process. Four incoming "segments" arrive at one host. Three are delivered by port. The fourth targets port 9999 where nobody is listening, so it is dropped; a real host answers UDP with an ICMP port-unreachable message and answers TCP with a reset (RST). The point: one IP address, many processes, the port picks.

Output from a real run:

```text
===== SECTION 2: MULTIPLEXING / DEMULTIPLEXING (SIMULATED) =====
IP gets a packet to the right HOST. The port gets the data to the right PROCESS.
  10.0.0.7:40001 -> port 80: deliver 'GET /' to web-server
  10.0.0.8:40002 -> port 53: deliver 'A? example.com' to dns-server
  10.0.0.7:40003 -> port 5000: deliver 'hello' to my-chat-app
  10.0.0.9:40004 -> port 9999: nobody bound -> dropped (UDP: ICMP port unreachable; TCP: RST)
Multiplexing = sender side: many apps share one IP, each tagged with a source port.
Demultiplexing = receiver side: the destination port picks the process.
```

### SECTION 3: REAL LOOPBACK: OS-ASSIGNED PORTS AND THE 5-TUPLE
A real TCP server binds to `127.0.0.1` port **0**, which means "OS, give me any free port". `getsockname()` reveals the choice. The number is different on every run, so the script prints only facts that are stable (it is in 1024..65535). Two clients connect without ever calling `bind`; the OS gives each an ephemeral source port. The script then reads each client's 5-tuple with `getsockname` and `getpeername` and proves: same destination, different source ports, therefore different 5-tuples. On the server side, `accept` returns a new socket per connection whose local port is still the listening port, and whose remote port equals the client's source port (the `check:` line). One short message per connection shows the streams are independent. Everything is closed and the accepting thread is joined.

Output from a real run:

```text
===== SECTION 3: REAL LOOPBACK: OS-ASSIGNED PORTS AND THE 5-TUPLE =====
server asked for port 0; OS gave a real port in 1024..65535: True
the number varies per run, so it is not printed. Note: the OS ephemeral range is OS-specific
(Linux default 32768-60999) and is NOT the same as IANA's 49152-65535 'dynamic' range.
client sockets (protocol, src ip, src port, dst ip, dst port):
  client 1: TCP 127.0.0.1:<ephemeral> -> 127.0.0.1:<server port>
  client 2: TCP 127.0.0.1:<ephemeral> -> 127.0.0.1:<server port>
both clients use the SAME destination (ip, port): True
but DIFFERENT source ports: True
so the two 5-tuples are different: True
accepted server-side sockets: 2
each accepted connection keeps local port == listening port: OK
check: server's view of client ports == clients' own ports: True
server received (order may differ by accept order): ['from client 0', 'from client 1']
all sockets closed, thread joined
```

### SECTION 4: CONNECTION-ORIENTED (TCP) VS CONNECTIONLESS (UDP)
A UDP client sends with `sendto` and no handshake; the server's `recvfrom` returns the data and the sender's address. A second UDP sender reaches the same single server socket, which demonstrates that UDP demultiplexing uses only the destination, not the source. The table summarises the contrast. The closing trap: never hard-code a client's source port. Only the server needs an agreed port.

Output from a real run:

```text
===== SECTION 4: CONNECTION-ORIENTED (TCP) VS CONNECTIONLESS (UDP) =====
UDP: first packet sent with no connection setup; server got: b'no handshake needed'
UDP server identifies the sender only per datagram; sender port is ephemeral: True
UDP: a second sender reached the SAME server socket: b'second sender' ; senders differ: True

  feature              TCP (SOCK_STREAM)              UDP (SOCK_DGRAM)
  setup                3-way handshake first          none
  demux key at server  full 5-tuple (one socket       dst ip + dst port only
                       per connection)                (one socket for all senders)
  delivery             reliable, ordered byte stream  best effort datagrams
  boundaries           NOT preserved                  preserved

trap: never hard-code the client's source port; the OS picks a different one each run.
Only the SERVER needs a well-known/agreed port so clients can find it.
```

## Worked Example
**Problem.** A host has IP 192.168.1.10. A browser opens two tabs to the same web server 93.184.216.34 on port 443. The OS gives the tabs source ports 50001 and 50002. (a) Write the two 5-tuples. (b) Why can the server tell them apart? (c) Which port class is 443, 50001, 3306?

**Solution.**
1. Tab 1: (TCP, 192.168.1.10, 50001, 93.184.216.34, 443). Tab 2: (TCP, 192.168.1.10, 50002, 93.184.216.34, 443).
2. Everything is equal except the source port, and a TCP connection is identified by the whole tuple, so the server keeps two separate connections and two separate sockets.
3. 443 is well-known (0 to 1023). 50001 is dynamic (49152 to 65535). 3306 is registered (1024 to 49151).

The code confirms the same logic on loopback: two clients, one destination, two source ports, two distinct 5-tuples, and the `port_class` boundary table matches the answers in step 3.

## Key Rules / Gotchas Recap
- A port is 16 bits: valid range 0 to 65535. 65536 is invalid.
- Boundaries: 1023 is well-known, 1024 is registered, 49151 is registered, 49152 is dynamic.
- IP finds the host; the port finds the process.
- A TCP connection is identified by the 5-tuple, not by the server port alone.
- UDP demultiplexes on (destination IP, destination port) only.
- Bind to port 0 to let the OS pick a free port; read it back with `getsockname()`.
- Clients get an ephemeral source port automatically; do not hard-code it.
- The OS ephemeral range (Linux 32768 to 60999) differs from IANA's 49152 to 65535.
- A segment for a port with no listener is rejected: RST for TCP, ICMP port unreachable for UDP.

## Why This Matters
Every network bug report eventually becomes "which process owns which port, and which 5-tuple is this?". Tools such as `ss` and `netstat`, firewall rules, load balancers and AI model servers (an inference API on port 8000, say) all depend on this model. Binding to port 0 is also the standard trick for writing tests that never collide with other services.
