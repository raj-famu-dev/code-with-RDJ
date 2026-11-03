# `_5_PacketDissectionAndHeaders.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Packet dissection means taking the raw bytes of a captured frame and decoding them layer by layer: Ethernet header, then the IP header named by its EtherType, then the TCP header named by the IP protocol field, then the application data. Wireshark and tcpdump do exactly this for hundreds of protocols; building one by hand with Python's `struct` module shows what every field really is on the wire.

**Ethernet II header (14 bytes):** destination MAC (6), source MAC (6), EtherType (2; 0x0800 = IPv4, 0x86DD = IPv6, 0x0806 = ARP). A 4-byte frame check sequence (FCS, CRC-32) follows the payload on the wire, but the NIC verifies and strips it, so captures normally do not show it.

**IPv4 header (20 bytes without options):** version (4 bits) and IHL (4 bits, header length in 32-bit words, so 5 = 20 bytes); DSCP/ECN (1 byte); total length (2); identification (2); flags and fragment offset (2; 0x4000 = Don't Fragment); TTL (1); protocol (1; 6 = TCP, 17 = UDP, 1 = ICMP); header checksum (2); source address (4); destination address (4).

**TCP header (20 bytes without options):** source port (2), destination port (2), sequence number (4), acknowledgement number (4), data offset (4 bits, in 32-bit words) with reserved bits and flags (CWR, ECE, URG, ACK, PSH, RST, SYN, FIN), window (2), checksum (2), urgent pointer (2).

**Internet checksum (RFC 1071).** Treat the data as 16-bit words, add them with ones'-complement arithmetic (carries wrap around), and take the complement. To verify, sum everything *including* the checksum field: a valid block yields all ones, so the complemented result is 0. The IPv4 checksum covers only the IP header. The TCP checksum covers a *pseudo-header* (source IP, destination IP, a zero byte, protocol, TCP length) plus the TCP header and data; the pseudo-header is never transmitted but ties the segment to its addresses. If the data length is odd, pad with a zero byte for the calculation only. Because it is a simple sum, some errors (swapped words) go unnoticed, which is why layer 2 adds a CRC.

**Capture tools.** libpcap is the library that captures packets and reads and writes `.pcap` files. tcpdump is the command-line front end (one summary line per packet, BPF filters). Wireshark (and its command-line sibling tshark) decodes protocols in a three-pane view: packet list, packet details tree, raw bytes. Capturing on a real interface needs privileges and is appropriate only on networks you own or are authorised to monitor.

**pcap file layout (classic format).** A 24-byte global header: magic number 0xA1B2C3D4 (its byte order tells the reader the file's endianness; microsecond timestamps), version major 2 and minor 4, time zone offset, timestamp accuracy, snaplen (maximum bytes stored per packet) and link-layer type (1 = Ethernet). Then, for each packet, a 16-byte record header (timestamp seconds, timestamp microseconds, captured length, original length) followed by that many bytes of the frame. If the packet was longer than the snaplen, captured length < original length. The newer pcapng format is block-based.

Typical exam questions: label the fields of an IPv4 or TCP header; compute a header checksum; what is the pseudo-header; how long is each header; what is the IHL of a header with options.

## Full Line-by-Line Breakdown

### SECTION 1: BUILD A FRAME BY HAND
`inet_checksum` implements RFC 1071 (sum 16-bit words from `struct.unpack`, fold carries, complement). `build_tcp_segment` packs the header with the checksum zero, builds the pseudo-header, computes the checksum and splices it in at byte 16. `build_ipv4_packet` does the same with the IP header (checksum at byte 10). `build_frame` prepends the Ethernet header. The addresses are from the documentation ranges (192.0.2.0/24 and 198.51.100.0/24, RFC 5737), and the MACs are "locally administered" (second hex digit 2), so nothing refers to a real host. The payload is a 37-byte HTTP request. The hexdump prints offset, hex and ASCII like Wireshark's bytes pane.

```text
===== SECTION 1: BUILD A FRAME BY HAND =====
HTTP request: 37 bytes; TCP segment 57 B; IP packet 77 B; Ethernet frame 91 B
  = 14 (Ethernet) + 20 (IPv4) + 20 (TCP) + 37 (data) = 91
Wireshark-style hex dump of the whole frame:
  0000  02 00 00 00 00 14 02 00 00 00 00 0a 08 00 45 00  ..............E.
  0010  00 4d 1c 46 40 00 40 06 32 13 c0 00 02 0a c6 33  .M.F@.@.2......3
  0020  64 14 c0 00 00 50 00 00 03 e8 00 00 13 89 50 18  d....P........P.
  0030  ff ff a2 ee 00 00 47 45 54 20 2f 20 48 54 54 50  ......GET / HTTP
  0040  2f 31 2e 31 0d 0a 48 6f 73 74 3a 20 65 78 61 6d  /1.1..Host: exam
  0050  70 6c 65 2e 63 6f 6d 0d 0a 0d 0a                 ple.com....
```

### SECTION 2: DISSECT LAYER BY LAYER
`dissect` reverses the process: unpack Ethernet, read the IHL to find where TCP starts, unpack TCP, read the data offset to find where the payload starts. It verifies the IP checksum by summing the header *including* its checksum (must give 0 after complement) and the TCP checksum over pseudo-header plus segment. The `assert` confirms both pass and the payload round-trips byte for byte. Compare the printed fields with the hex dump above: for example `45 00` at offset 0x0E is version 4 / IHL 5, and `00 50` is destination port 80.

```text
===== SECTION 2: DISSECT LAYER BY LAYER =====
Ethernet II: dst=02:00:00:00:00:14 src=02:00:00:00:00:0a ethertype=0x0800 (IPv4)
IPv4: version=4 IHL=20 B total_len=77 ttl=64 proto=6 (TCP) src=192.0.2.10 dst=198.51.100.20 checksum=0x3213
      header checksum verifies (sum over header incl. checksum == 0): True
TCP: 49152 -> 80 seq=1000 ack=5001 flags=PSH+ACK window=65535 data offset=20 B checksum=0xa2ee
     checksum over pseudo-header + segment verifies: True
Payload (37 B): b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n'
check: OK (both checksums verify and the payload round-trips)
```

### SECTION 3: CHECKSUMS CATCH CORRUPTION; THE ETHERNET FCS
Flipping one bit in the HTTP data leaves the IP header checksum valid (it covers only the header) but breaks the TCP checksum. Flipping a bit in the TTL breaks the IP checksum (routers recompute it each hop because they decrement TTL). The FCS is the CRC-32 of the frame, computed with `zlib.crc32` and shown in the transmitted byte order, as a reminder that it exists but is not normally captured. Trap 2 shows the pseudo-header matters: leaving it out gives a different checksum value.

```text
===== SECTION 3: CHECKSUMS CATCH CORRUPTION; THE ETHERNET FCS =====
Flip 1 bit in the HTTP data: IP header still ok = True, TCP checksum ok = False
Flip 1 bit in the IP TTL:    IP header ok = False (routers also recompute it after TTL-1)
Ethernet FCS (CRC-32 over the frame, sent least-significant byte first): 558082bf
TRAP: captures normally do NOT show the FCS - the NIC checks and strips it. Wireshark shows a 14-byte Ethernet header and no trailer.
TRAP 2: the TCP checksum covers a PSEUDO-header (IPs, protocol, length) that is never sent; leaving it out gives a wrong sum:
  correct TCP checksum 0xa2ee vs without pseudo-header 0x8f80 -> differ: True
Weakness: a 16-bit checksum misses some errors (two swapped words give the same sum), hence the CRC at layer 2.
check: OK
```

### SECTION 4: WHAT WIRESHARK AND TCPDUMP SHOW
A table of libpcap, tcpdump and Wireshark and the three Wireshark panes mapped to the earlier sections. Nothing is captured by this script.

```text
===== SECTION 4: WHAT WIRESHARK AND TCPDUMP SHOW =====
Tool        What it is                                                       Typical use
libpcap     library that captures packets and reads/writes .pcap files       used by tcpdump, Wireshark, Scapy
tcpdump     command-line capture + one-line-per-packet summary               servers, quick filters (BPF), scripting
Wireshark   GUI/tshark: decodes hundreds of protocols, follows TCP streams   deep analysis, teaching, debugging
Capturing needs privileges on a real interface and is lawful only on networks you own or may monitor.
This file never captures: it builds bytes itself and reads a file it wrote.
Wireshark panes map to what we did: packet list (one line each), details (the tree printed in SECTION 2), bytes (hex dump).
```

### SECTION 5: A TINY PCAP FILE
A temporary directory holds `demo.pcap`. The code writes the global header with `struct.pack("<IHHiIII", ...)`, then four records for a TCP handshake and the HTTP request, each with a 16-byte record header. Timestamps are a fixed made-up value (1,700,000,000 seconds plus small offsets), not the current time, so output is reproducible; they are printed in UTC. The file is then read back from disk, each record is dissected and printed in a tcpdump-like line. File size 341 = 24 + 4 x 16 + (54 + 54 + 54 + 91 bytes of frames; SYN, SYN-ACK and ACK are 54 bytes each). Flags `S`, `S.`, `.`, `P.` mean SYN, SYN+ACK, ACK, PSH+ACK as tcpdump writes them. The directory is deleted when the `with` block ends.

```text
===== SECTION 5: A TINY PCAP FILE =====
Wrote demo.pcap: 341 bytes = 24 global header + 4 x (16 record header + frame)
Global header: magic=0xa1b2c3d4 version=2.4 snaplen=65535 linktype=1 (1 = Ethernet)
tcpdump-style summary (format is similar to, not identical to, real tcpdump):
  22:13:20.000000 IP 192.0.2.10.49152 > 198.51.100.20.80: Flags [S], seq 999, ack 0, length 0  (checksums ok: True)
  22:13:21.001500 IP 198.51.100.20.80 > 192.0.2.10.49152: Flags [S.], seq 5000, ack 1000, length 0  (checksums ok: True)
  22:13:22.003000 IP 192.0.2.10.49152 > 198.51.100.20.80: Flags [.], seq 1000, ack 5001, length 0  (checksums ok: True)
  22:13:23.004500 IP 192.0.2.10.49152 > 198.51.100.20.80: Flags [P.], seq 1000, ack 5001, length 37  (checksums ok: True)
check: OK (4 records read back; temp directory removed)
Layout: [global header 24 B][record hdr 16 B: ts_sec, ts_usec, captured len, original len][frame] ... repeated.
captured len < original len when snaplen truncates a big packet. pcapng is the newer block-based format.
```

## Worked Example
**Q.** Compute the IPv4 header checksum for the header `4500 004d 1c46 4000 4006 [checksum] c000 020a c633 6414` (source 192.0.2.10, destination 198.51.100.20).

1. Set the checksum field to 0000 and add the words in hexadecimal: 4500 + 004d = 454d; + 1c46 = 6193; + 4000 = a193; + 4006 = e199; + 0000 = e199; + c000 = 1a199 (carry out of 16 bits).
2. Fold the carry: a199 + 1 = a19a. Continue: + 020a = a3a4; + c633 = 169d7, fold: 69d7 + 1 = 69d8; + 6414 = cdec.
3. Complement: ~cdec = 3213.

The checksum is 0x3213, exactly what the dissector printed (`checksum=0x3213`). To verify, add all words including 3213: the sum is ffff, whose complement is 0.

## Key Rules / Gotchas Recap
- Use network byte order (`!` in `struct`): big-endian on the wire. The pcap record headers here are little-endian, a different convention.
- IHL and TCP data offset count 32-bit words: multiply by 4.
- The IP checksum covers the header only; the TCP/UDP checksum covers a pseudo-header + segment.
- Verify by summing everything including the checksum: result must complement to 0.
- Routers decrement TTL and therefore recompute the IP checksum at every hop.
- Captures normally lack the Ethernet FCS; captured length may be less than original length.
- Capture only on networks you own or may monitor.

## Why This Matters
Reading headers and hex is the fastest way to settle "is it the app or the network?" in debugging, and the same parsing skill underlies IDS rules, packet-processing code and security tooling. Understanding checksums and pcap files lets you build and test networking code offline, without touching a live network.
