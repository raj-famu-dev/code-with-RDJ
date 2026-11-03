# `_4_OsiModel.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The OSI (Open Systems Interconnection) model is a seven-layer reference model, published by ISO, that splits network communication into layers so each layer has one job and talks only to the layer above and below. It exists so different vendors' equipment can interoperate and so problems can be located ("is it a layer 1 cable fault or a layer 7 application bug?").

**Principles.** Each layer offers a *service* to the layer above and uses the service of the layer below. Each layer talks logically to its *peer* layer on the other machine using a *protocol*; the actual data goes down the sender's stack, across the medium and up the receiver's stack. The unit of data at a layer is its PDU (protocol data unit). Going down, each layer adds a header (the data-link layer also adds a trailer): this is encapsulation. Going up, each layer strips its header: decapsulation.

**The seven layers (top to bottom).**

| # | Layer | PDU | Main responsibilities | Examples | Device |
|---|-------|-----|-----------------------|----------|--------|
| 7 | Application | data | interface for user programs: web, mail, file transfer, directory | HTTP, SMTP, FTP, DNS | gateway |
| 6 | Presentation | data | translation (character sets), encryption, compression | JPEG, ASCII/Unicode, TLS (placement debated) | gateway |
| 5 | Session | data | establish, maintain, terminate sessions; dialog control (half/full duplex), synchronisation checkpoints | RPC, NetBIOS | gateway |
| 4 | Transport | segment (TCP), user datagram (UDP) | process-to-process delivery via ports, segmentation, flow control, error control, connection management | TCP, UDP | gateway, firewall |
| 3 | Network | packet | logical (IP) addressing, routing, fragmentation, congestion control | IP, ICMP, OSPF, BGP | router |
| 2 | Data Link | frame | framing, physical (MAC) addressing, hop-to-hop error detection, flow control, medium access | Ethernet, PPP, 802.11 | switch, bridge, NIC |
| 1 | Physical | bit | signals, voltages, connectors, data rate, topology, transmission mode | RJ45, fibre, DSL | hub, repeater, cable |

**Mnemonics.** Bottom to top: "Please Do Not Throw Sausage Pizza Away" (Physical, Data link, Network, Transport, Session, Presentation, Application). Top to bottom: "All People Seem To Need Data Processing".

**Key ideas and distinctions.**
- Layers 1-3 are the *network support* layers; 5-7 are *user support* layers; 4 links the two.
- Data link = hop to hop (MAC addresses, change at every hop); network = host to host across networks (IP addresses, usually unchanged end to end); transport = process to process (port numbers).
- The data-link layer is often split into LLC and MAC sublayers.
- Session and presentation are not separate layers in the TCP/IP model; their jobs are done by the application.
- OSI is a *reference* model; the Internet runs TCP/IP. Exams ask for both.

**Typical exam questions.** List layers with functions; name the PDU at each layer; which layer does routing / error detection / encryption; which device works at which layer; explain encapsulation; what is peer-to-peer communication.

## Full Line-by-Line Breakdown

### SECTION 1: THE SEVEN LAYERS
A frozen dataclass `Layer` holds number, name, PDU, job, protocols and device; `LAYERS` is the list from layer 7 down. The tables are printed from this data. The mnemonic is split into words and the code checks that the first letters of the seven words equal the first letters of the layer names read bottom-up (`PDNTSPA`), so a typo in either breaks the `assert`.

```text
===== SECTION 1: THE SEVEN LAYERS =====
#  layer        PDU                     job
7  Application  data                    services for the user's program
6  Presentation data                    format, encryption, compression
5  Session      data                    open, manage, close dialogs; sync points
4  Transport    segment / user datagram end-to-end delivery, ports, reliability
3  Network      packet                  logical addressing, routing
2  Data Link    frame                   hop-to-hop delivery, MAC addressing, error detection
1  Physical     bit                     move raw bits as signals

layer        example protocols                               device
Application  HTTP, SMTP, DNS, FTP                            gateway
Presentation TLS (placed here by some books), JPEG, ASCII    gateway
Session      NetBIOS, RPC, PPTP (examples)                   gateway
Transport    TCP, UDP                                        gateway / firewall
Network      IP, ICMP, OSPF                                  router
Data Link    Ethernet, PPP, ARP*                             switch, bridge, NIC
Physical     RJ45, fibre, 802.3 signalling                   hub, repeater, cable
Transport PDU: 'segment' for TCP, 'datagram' (user datagram) for UDP.
* ARP is often described as sitting between layers 2 and 3.
Mnemonic, layer 1 up to 7: 1=Please 2=Do 3=Not 4=Throw 5=Sausage 6=Pizza 7=Away
Top down (7 to 1): All People Seem To Need Data Processing
check: mnemonic initials PDNTSPA == layer initials PDNTSPA: OK
```

### SECTION 2: ENCAPSULATION (WRAP)
`wrap()` loops from layer 7 down to 1. Layers 7 to 2 prepend a tag standing for their header (`AH` application header, `PH`, `SH`, `TH`, `NH`, `DH`); layer 2 also appends the trailer `DT` (the frame check sequence lives in a trailer). Layer 1 adds nothing: it turns the frame into bits. Each line shows the PDU as it exists after that layer has worked on it, so you can watch the onion grow.

```text
===== SECTION 2: ENCAPSULATION (WRAP) =====
Sender wraps:
  L7 Application  -> [AH]HELLO
  L6 Presentation -> [PH][AH]HELLO
  L5 Session      -> [SH][PH][AH]HELLO
  L4 Transport    -> [TH][SH][PH][AH]HELLO
  L3 Network      -> [NH][TH][SH][PH][AH]HELLO
  L2 Data Link    -> [DH][NH][TH][SH][PH][AH]HELLO[DT]
  L1 Physical     -> [DH][NH][TH][SH][PH][AH]HELLO[DT] (bits on the wire)
```

### SECTION 3: DECAPSULATION (UNWRAP) AND PEER-TO-PEER VIEW
`unwrap()` goes up from layer 1; at layer 2 it first removes the trailer and then the header, checking each tag is really present. If a layer cannot find its header it raises `ValueError`; the trap deliberately drops the data-link header and shows the resulting failure, which is how a real stack discards a damaged frame. The two printed rules explain peer communication.

```text
===== SECTION 3: DECAPSULATION (UNWRAP) AND PEER-TO-PEER VIEW =====
Receiver unwraps:
  L1 Physical     <- [DH][NH][TH][SH][PH][AH]HELLO[DT]
  L2 Data Link    <- [NH][TH][SH][PH][AH]HELLO
  L3 Network      <- [TH][SH][PH][AH]HELLO
  L4 Transport    <- [SH][PH][AH]HELLO
  L5 Session      <- [PH][AH]HELLO
  L6 Presentation <- [AH]HELLO
  L7 Application  <- HELLO
delivered 'HELLO'; check: OK
Peer-to-peer rule: each layer only reads the header written by the SAME layer on the other host.
Layer 3 of the sender 'talks to' layer 3 of the receiver, but the data physically goes down and up the stacks.

Trap: the frame arrives with its data-link header damaged/missing, so layer 2 cannot do its job:
  ValueError -> layer 2: expected header [DH] at the front of '[NH][TH][SH][PH][AH]HELLO'
```

### SECTION 4: INTERMEDIATE DEVICES AND LAYERS
A hub works only at layer 1, a switch reads up to the data-link header, a router up to the network header, and a gateway or proxy may read as high as layer 7. In the router example the data-link header and trailer are replaced (`A` to `B`) while the network layer and above travel unchanged. In real IP the router also decrements the TTL and recomputes the header checksum.

```text
===== SECTION 4: INTERMEDIATE DEVICES AND LAYERS =====
Which layers does each device unwrap? (it opens the frame only as high as its job needs)
  hub/repeater   reads up to L1 (Physical   ) -> processes L1
  switch/bridge  reads up to L2 (Data Link  ) -> processes L1, L2
  router         reads up to L3 (Network    ) -> processes L1, L2, L3
  gateway/proxy  reads up to L7 (Application) -> processes L1, L2, L3, L4, L5, L6, L7
Router example: frame arrives, L2 stripped, L3 chooses next hop, a NEW L2 header is attached on the way out.
  in : [DH-A][NH][TH]data[DT-A]
  out: [DH-B][NH][TH]data[DT-B] (only the data-link parts changed; L3 and above untouched, except TTL in real IP)
```

### SECTION 5: WORKED EXAMPLE
Adds up illustrative header sizes to show overhead.

```text
===== SECTION 5: WORKED EXAMPLE =====
payload 10 B + headers 62 B + L2 trailer 4 B = 76 B on the wire
overhead = 66 B = 87% of the frame
check: OK (header sizes are illustrative; see _5_TcpIpModelAndEncapsulation for real ones)
```

## Worked Example
**Problem.** A 10-byte application payload passes through OSI layers that add 4, 2, 2, 20, 20 and 14 bytes of header at layers 7 to 2 and a 4-byte trailer at layer 2. How many bytes go on the wire and what fraction is overhead?

1. Headers: 4 + 2 + 2 + 20 + 20 + 14 = 62 bytes.
2. Add the trailer: 62 + 4 = 66 bytes of overhead.
3. Frame = 10 + 66 = 76 bytes.
4. Overhead share = 66 / 76 = 86.8%, printed as 87%.

(These header sizes are made up for practice; the next file measures real TCP/IP headers.)

## Key Rules / Gotchas Recap
- Memorise order and PDUs: bit, frame, packet, segment/datagram, data.
- Only the data-link layer adds a trailer (frame check sequence).
- Data-link addresses change on every hop; IP addresses normally do not.
- Hub = L1, switch/bridge = L2, router = L3; "gateway" can mean any layer up to 7.
- A layer reads only its own peer's header; it treats everything above as opaque payload.
- OSI is a teaching/reference model; the real Internet is TCP/IP.
- Session and presentation duties are merged into the application in TCP/IP.

## Why This Matters
Troubleshooting (ping, traceroute, packet captures, firewall rules) is organised by layer, and security tools are described by layer (WAF at 7, firewall at 3/4, MAC filtering at 2). Understanding encapsulation makes packet captures readable.
