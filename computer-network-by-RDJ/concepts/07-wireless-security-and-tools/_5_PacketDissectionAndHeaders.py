# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Packet dissection and headers: hand-build an Ethernet + IPv4 + TCP frame
carrying an HTTP request with struct, dissect it back layer by layer, verify the
IP and TCP checksums, then write and read a tiny pcap file in a temp directory
to see how Wireshark/tcpdump store captures. NO live capture, no sockets."""
import datetime
import ipaddress
import struct
import tempfile
import zlib
from pathlib import Path

# ===== SECTION 1: BUILD A FRAME BY HAND =====
print("===== SECTION 1: BUILD A FRAME BY HAND =====")


def inet_checksum(data: bytes) -> int:
    """RFC 1071 Internet checksum: ones'-complement sum of 16-bit words, then complemented."""
    if len(data) % 2:
        data += b"\x00"                      # odd length: pad with a zero byte for the sum only
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def mac_bytes(mac: str) -> bytes:
    return bytes(int(x, 16) for x in mac.split(":"))


def build_tcp_segment(src_ip: str, dst_ip: str, sport: int, dport: int, seq: int, ack: int,
                      flags: int, payload: bytes = b"") -> bytes:
    offset_flags = (5 << 12) | flags         # data offset = 5 words (20 bytes), no options
    hdr = struct.pack("!HHIIHHHH", sport, dport, seq, ack, offset_flags, 65535, 0, 0)
    pseudo = (ipaddress.ip_address(src_ip).packed + ipaddress.ip_address(dst_ip).packed
              + struct.pack("!BBH", 0, 6, len(hdr) + len(payload)))
    csum = inet_checksum(pseudo + hdr + payload)
    return hdr[:16] + struct.pack("!H", csum) + hdr[18:] + payload


def build_ipv4_packet(src_ip: str, dst_ip: str, proto: int, payload: bytes, ident: int = 0x1C46) -> bytes:
    total_len = 20 + len(payload)
    hdr = struct.pack("!BBHHHBBH4s4s", (4 << 4) | 5, 0, total_len, ident, 0x4000, 64, proto, 0,
                      ipaddress.ip_address(src_ip).packed, ipaddress.ip_address(dst_ip).packed)
    csum = inet_checksum(hdr)
    return hdr[:10] + struct.pack("!H", csum) + hdr[12:] + payload


def build_frame(dst_mac: str, src_mac: str, ip_packet: bytes) -> bytes:
    return mac_bytes(dst_mac) + mac_bytes(src_mac) + struct.pack("!H", 0x0800) + ip_packet


SRC_IP, DST_IP = "192.0.2.10", "198.51.100.20"        # documentation ranges (RFC 5737), not real hosts
SRC_MAC, DST_MAC = "02:00:00:00:00:0a", "02:00:00:00:00:14"
HTTP = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
tcp = build_tcp_segment(SRC_IP, DST_IP, 49152, 80, 1000, 5001, 0x18, HTTP)   # PSH+ACK
ip = build_ipv4_packet(SRC_IP, DST_IP, 6, tcp)
frame = build_frame(DST_MAC, SRC_MAC, ip)
print(f"HTTP request: {len(HTTP)} bytes; TCP segment {len(tcp)} B; IP packet {len(ip)} B; Ethernet frame {len(frame)} B")
print(f"  = 14 (Ethernet) + 20 (IPv4) + 20 (TCP) + {len(HTTP)} (data) = {14 + 20 + 20 + len(HTTP)}")
assert len(frame) == 14 + 20 + 20 + len(HTTP)


def hexdump(data: bytes) -> None:
    for off in range(0, len(data), 16):
        chunk = data[off:off + 16]
        hexpart = " ".join(f"{b:02x}" for b in chunk)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {off:04x}  {hexpart:<47}  {text}")


print("Wireshark-style hex dump of the whole frame:")
hexdump(frame)

# ===== SECTION 2: DISSECT LAYER BY LAYER =====
print("\n===== SECTION 2: DISSECT LAYER BY LAYER =====")
TCP_FLAGS = [(0x01, "FIN"), (0x02, "SYN"), (0x04, "RST"), (0x08, "PSH"), (0x10, "ACK"), (0x20, "URG")]


def dissect(frame: bytes, verbose: bool = True) -> dict:
    out: dict = {}
    dst, src, etype = struct.unpack("!6s6sH", frame[:14])
    out["eth"] = (":".join(f"{b:02x}" for b in dst), ":".join(f"{b:02x}" for b in src), etype)
    if verbose:
        print(f"Ethernet II: dst={out['eth'][0]} src={out['eth'][1]} ethertype=0x{etype:04x} "
              f"({'IPv4' if etype == 0x0800 else 'other'})")
    ip = frame[14:]
    vihl, tos, total_len, ident, frag, ttl, proto, csum, sip, dip = struct.unpack("!BBHHHBBH4s4s", ip[:20])
    ihl = (vihl & 0x0F) * 4
    out["ip"] = dict(version=vihl >> 4, ihl=ihl, total_len=total_len, ttl=ttl, proto=proto,
                     src=str(ipaddress.ip_address(sip)), dst=str(ipaddress.ip_address(dip)),
                     checksum=csum, header_ok=inet_checksum(ip[:ihl]) == 0)
    if verbose:
        o = out["ip"]
        print(f"IPv4: version={o['version']} IHL={o['ihl']} B total_len={o['total_len']} ttl={o['ttl']} "
              f"proto={o['proto']} (TCP) src={o['src']} dst={o['dst']} checksum=0x{csum:04x}")
        print(f"      header checksum verifies (sum over header incl. checksum == 0): {o['header_ok']}")
    seg = ip[ihl:total_len]
    sport, dport, seq, ack, off_flags, win, tcsum, urg = struct.unpack("!HHIIHHHH", seg[:20])
    doff = (off_flags >> 12) * 4
    flags = [n for bit, n in TCP_FLAGS if off_flags & bit]
    pseudo = sip + dip + struct.pack("!BBH", 0, proto, len(seg))
    out["tcp"] = dict(sport=sport, dport=dport, seq=seq, ack=ack, flags=flags, window=win, doff=doff,
                      checksum=tcsum, ok=inet_checksum(pseudo + seg) == 0)
    payload = seg[doff:]
    out["payload"] = payload
    if verbose:
        o = out["tcp"]
        print(f"TCP: {sport} -> {dport} seq={seq} ack={ack} flags={'+'.join(flags)} window={win} "
              f"data offset={doff} B checksum=0x{tcsum:04x}")
        print(f"     checksum over pseudo-header + segment verifies: {o['ok']}")
        print(f"Payload ({len(payload)} B): {payload!r}")
    return out


parsed = dissect(frame)
assert parsed["ip"]["header_ok"] and parsed["tcp"]["ok"] and parsed["payload"] == HTTP
print("check: OK (both checksums verify and the payload round-trips)")

# ===== SECTION 3: CHECKSUMS CATCH CORRUPTION; THE ETHERNET FCS =====
print("\n===== SECTION 3: CHECKSUMS CATCH CORRUPTION; THE ETHERNET FCS =====")
broken = bytearray(frame)
broken[14 + 20 + 20 + 5] ^= 0x01        # flip one bit inside the HTTP data
res = dissect(bytes(broken), verbose=False)
print(f"Flip 1 bit in the HTTP data: IP header still ok = {res['ip']['header_ok']}, TCP checksum ok = {res['tcp']['ok']}")
broken2 = bytearray(frame)
broken2[14 + 8] ^= 0x01                 # flip a bit in the IP TTL
res2 = dissect(bytes(broken2), verbose=False)
print(f"Flip 1 bit in the IP TTL:    IP header ok = {res2['ip']['header_ok']} (routers also recompute it after TTL-1)")
assert not res["tcp"]["ok"] and not res2["ip"]["header_ok"]
fcs = struct.pack("<I", zlib.crc32(frame))
print(f"Ethernet FCS (CRC-32 over the frame, sent least-significant byte first): {fcs.hex()}")
print("TRAP: captures normally do NOT show the FCS - the NIC checks and strips it. Wireshark shows a 14-byte Ethernet header and no trailer.")
print("TRAP 2: the TCP checksum covers a PSEUDO-header (IPs, protocol, length) that is never sent; leaving it out gives a wrong sum:")
wrong = inet_checksum(tcp[:16] + b"\x00\x00" + tcp[18:])   # computed without the pseudo-header
print(f"  correct TCP checksum 0x{parsed['tcp']['checksum']:04x} vs without pseudo-header 0x{wrong:04x} -> differ: "
      f"{wrong != parsed['tcp']['checksum']}")
print("Weakness: a 16-bit checksum misses some errors (two swapped words give the same sum), hence the CRC at layer 2.")
assert wrong != parsed["tcp"]["checksum"]
print("check: OK")

# ===== SECTION 4: WHAT WIRESHARK AND TCPDUMP SHOW =====
print("\n===== SECTION 4: WHAT WIRESHARK AND TCPDUMP SHOW =====")
print("Tool        What it is                                                       Typical use")
print("libpcap     library that captures packets and reads/writes .pcap files       used by tcpdump, Wireshark, Scapy")
print("tcpdump     command-line capture + one-line-per-packet summary               servers, quick filters (BPF), scripting")
print("Wireshark   GUI/tshark: decodes hundreds of protocols, follows TCP streams   deep analysis, teaching, debugging")
print("Capturing needs privileges on a real interface and is lawful only on networks you own or may monitor.")
print("This file never captures: it builds bytes itself and reads a file it wrote.")
print("Wireshark panes map to what we did: packet list (one line each), details (the tree printed in SECTION 2), bytes (hex dump).")

# ===== SECTION 5: A TINY PCAP FILE =====
print("\n===== SECTION 5: A TINY PCAP FILE =====")
PCAP_MAGIC = 0xA1B2C3D4        # classic pcap, microsecond timestamps; written here little-endian
LINKTYPE_ETHERNET = 1
frames = [
    ("S", build_tcp_segment(SRC_IP, DST_IP, 49152, 80, 999, 0, 0x02)),
    ("S.", build_tcp_segment(DST_IP, SRC_IP, 80, 49152, 5000, 1000, 0x12)),
    (".", build_tcp_segment(SRC_IP, DST_IP, 49152, 80, 1000, 5001, 0x10)),
    ("P.", tcp),
]
BASE_TS = 1_700_000_000        # made-up fixed timestamp (not "now") so the output is reproducible
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "demo.pcap"
    blob = struct.pack("<IHHiIII", PCAP_MAGIC, 2, 4, 0, 0, 65535, LINKTYPE_ETHERNET)
    for i, (_name, seg) in enumerate(frames):
        a, b = (SRC_IP, DST_IP) if seg[:2] != struct.pack("!H", 80) else (DST_IP, SRC_IP)
        data = build_frame(DST_MAC if a == SRC_IP else SRC_MAC, SRC_MAC if a == SRC_IP else DST_MAC,
                           build_ipv4_packet(a, b, 6, seg, ident=0x1C46 + i))
        blob += struct.pack("<IIII", BASE_TS + i, i * 1500, len(data), len(data)) + data
    path.write_bytes(blob)
    print(f"Wrote {path.name}: {path.stat().st_size} bytes = 24 global header + {len(frames)} x (16 record header + frame)")
    raw = path.read_bytes()
    magic, vmaj, vmin, tz, sig, snap, link = struct.unpack("<IHHiIII", raw[:24])
    print(f"Global header: magic=0x{magic:08x} version={vmaj}.{vmin} snaplen={snap} linktype={link} (1 = Ethernet)")
    assert magic == PCAP_MAGIC
    pos, n = 24, 0
    print("tcpdump-style summary (format is similar to, not identical to, real tcpdump):")
    while pos < len(raw):
        ts_s, ts_us, incl, orig = struct.unpack("<IIII", raw[pos:pos + 16])
        pkt = raw[pos + 16:pos + 16 + incl]
        d = dissect(pkt, verbose=False)
        when = datetime.datetime.fromtimestamp(ts_s, datetime.timezone.utc).strftime("%H:%M:%S") + f".{ts_us:06d}"
        t, i = d["tcp"], d["ip"]
        print(f"  {when} IP {i['src']}.{t['sport']} > {i['dst']}.{t['dport']}: Flags [{''.join(f[0] if f != 'ACK' else '.' for f in t['flags'])}], "
              f"seq {t['seq']}, ack {t['ack']}, length {len(d['payload'])}  (checksums ok: {i['header_ok'] and t['ok']})")
        assert i["header_ok"] and t["ok"]
        pos += 16 + incl
        n += 1
assert n == len(frames)
print(f"check: OK ({n} records read back; temp directory removed)")
print("Layout: [global header 24 B][record hdr 16 B: ts_sec, ts_usec, captured len, original len][frame] ... repeated.")
print("captured len < original len when snaplen truncates a big packet. pcapng is the newer block-based format.")
