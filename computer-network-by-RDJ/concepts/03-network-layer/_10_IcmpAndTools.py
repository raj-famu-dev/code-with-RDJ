# Tags: #Python #ComputerNetworks #NetworkLayer #IcmpTools | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""ICMP: message types/codes, pack/unpack with the Internet checksum, and
in-memory simulations of ping (RTT table) and traceroute (TTL decrement
through a router chain). NO real packets are sent anywhere."""
from __future__ import annotations

import random
import struct
from dataclasses import dataclass


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"           # odd length: pad with a zero byte for the sum only
    s = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


# ===== SECTION 1: ICMP TYPES AND CODES =====
print("===== SECTION 1: ICMP TYPES AND CODES =====")
TYPES = {
    (0, 0): "Echo Reply (ping answer)",
    (3, 0): "Destination Unreachable: network unreachable",
    (3, 1): "Destination Unreachable: host unreachable",
    (3, 3): "Destination Unreachable: port unreachable",
    (3, 4): "Destination Unreachable: fragmentation needed and DF set",
    (5, 1): "Redirect: for the host (use a better first hop)",
    (8, 0): "Echo Request (ping)",
    (11, 0): "Time Exceeded: TTL expired in transit",
    (11, 1): "Time Exceeded: fragment reassembly time exceeded",
    (12, 0): "Parameter Problem: pointer indicates the error",
}
print(f"{'type':>4} {'code':>4}  meaning")
for (t, c), m in sorted(TYPES.items()):
    print(f"{t:>4} {c:>4}  {m}")
print("ICMP rides inside IP (protocol number 1). It REPORTS problems and answers queries;")
print("it does not make IP reliable, and no ICMP error is sent about an ICMP error.")


# ===== SECTION 2: PACK / UNPACK WITH CHECKSUM =====
print("\n===== SECTION 2: PACK / UNPACK WITH CHECKSUM =====")


def pack_icmp(typ: int, code: int, rest: int, payload: bytes) -> bytes:
    """type(1) code(1) checksum(2) rest-of-header(4) data."""
    head = struct.pack("!BBHI", typ, code, 0, rest)
    cs = checksum(head + payload)
    return struct.pack("!BBHI", typ, code, cs, rest) + payload


def unpack_icmp(b: bytes) -> dict:
    typ, code, cs, rest = struct.unpack("!BBHI", b[:8])
    return {"type": typ, "code": code, "checksum": cs, "rest": rest,
            "payload": b[8:], "valid": checksum(b) == 0}


def pack_echo(ident: int, seq: int, data: bytes, reply: bool = False) -> bytes:
    return pack_icmp(0 if reply else 8, 0, (ident << 16) | seq, data)


msg = pack_echo(0x1234, 1, b"abcdefgh")
print("echo request bytes:", msg.hex(" "))
u = unpack_icmp(msg)
print(f"type={u['type']} code={u['code']} checksum=0x{u['checksum']:04x} id=0x{u['rest'] >> 16:04x} seq={u['rest'] & 0xFFFF} data={u['payload']!r} valid={u['valid']}")
assert u["valid"] and u["type"] == 8
print("check: OK")
bad = bytearray(msg)
bad[9] ^= 0xFF
print("after corrupting one data byte: valid =", unpack_icmp(bytes(bad))["valid"], "(receiver silently discards)")
odd = pack_echo(1, 1, b"abc")          # odd payload length
print("odd-length payload (3 bytes) still verifies:", unpack_icmp(odd)["valid"], "(zero pad is used only in the sum)")
assert unpack_icmp(odd)["valid"]
reply = pack_echo(0x1234, 1, b"abcdefgh", reply=True)
print("echo reply : type", unpack_icmp(reply)["type"], "same id/seq/data, checksum 0x%04x (differs because type changed)" % unpack_icmp(reply)["checksum"])
print("Error messages (types 3, 5, 11, 12) carry the offending IP header + first 8 bytes of its data,")
print("so the sender can tell which packet/port caused it.")


# ===== SECTION 3: IN-MEMORY ROUTER CHAIN =====
print("\n===== SECTION 3: IN-MEMORY ROUTER CHAIN =====")


@dataclass
class Hop:
    name: str
    ip: str
    in_ms: float             # simulated one-way delay of the link INTO this hop


CHAIN = [Hop("gw", "192.168.1.1", 0.8), Hop("isp1", "10.20.0.1", 5.0),
         Hop("core", "10.30.0.1", 12.0), Hop("edge", "10.40.0.1", 8.0), Hop("target", "198.51.100.7", 4.0)]
print("simulated path:", " -> ".join(f"{h.name}({h.ip})" for h in CHAIN))
print("Delays below are SIMULATED numbers from a seeded RNG, not measurements of anything real.")


def send(ttl: int, rng: random.Random, proto: str = "icmp") -> tuple[str, str, float]:
    """Walk the chain decrementing TTL. Returns (reply kind, replier ip, rtt_ms)."""
    elapsed = 0.0
    for i, hop in enumerate(CHAIN):
        elapsed += hop.in_ms + rng.uniform(0, 0.6)
        ttl -= 1                                  # every router decrements TTL on forwarding
        if i == len(CHAIN) - 1:                  # destination host
            kind = "Echo Reply" if proto == "icmp" else "Port Unreachable"
            return kind, hop.ip, 2 * elapsed
        if ttl == 0:
            return "Time Exceeded", hop.ip, 2 * elapsed
    raise RuntimeError


# ===== SECTION 4: PING SIMULATION =====
print("\n===== SECTION 4: PING SIMULATION (RTT TABLE) =====")
rng = random.Random(2024)
rtts = []
print(f"PING {CHAIN[-1].ip} (simulated), 8 data bytes")
for seq in range(1, 6):
    pkt = pack_echo(0x77, seq, b"abcdefgh")
    assert unpack_icmp(pkt)["valid"]
    kind, ip, rtt = send(64, rng)
    rtts.append(rtt)
    print(f"  seq={seq} reply from {ip}: {kind}, ttl={64 - (len(CHAIN) - 1)}, time={rtt:.1f} ms (simulated)")
print(f"summary: 5 sent, 5 received, 0% loss, rtt min/avg/max = {min(rtts):.1f}/{sum(rtts) / len(rtts):.1f}/{max(rtts):.1f} ms (simulated)")
print("Reply TTL = 64 - 4 routers' decrements = 60: the TTL in a reply hints at the hop count.")
assert all(r > 0 for r in rtts)
print("check: OK")


# ===== SECTION 5: TRACEROUTE SIMULATION =====
print("\n===== SECTION 5: TRACEROUTE SIMULATION (TTL = 1, 2, 3 ...) =====")
rng = random.Random(7)
print(f"traceroute to {CHAIN[-1].ip} (simulated), max 10 hops, 3 probes each")
reached = None
for ttl in range(1, 11):
    probes = [send(ttl, rng, proto="udp") for _ in range(3)]
    ip = probes[0][1]
    times = "  ".join(f"{p[2]:.1f} ms" for p in probes)
    print(f" {ttl:>2}  {ip:15} {times}   <- {probes[0][0]}")
    if probes[0][0] == "Port Unreachable":
        reached = ttl
        break
assert reached == len(CHAIN)
print(f"check: OK (destination reached at TTL {reached} = number of devices on the path)")
print("How it works: probe with TTL 1 dies at router 1, which returns ICMP Time Exceeded (11,0)")
print("revealing its address; TTL 2 dies at router 2; ... until the destination answers")
print("(Port Unreachable for UDP probes to a closed high port, or Echo Reply for ICMP probes).")
print("Caveat: many routers rate-limit or drop ICMP, giving '* * *' lines; paths may also change between probes.")
print("TRAP: a router that decrements TTL to 0 must drop the packet, never forward it:")
kind, ip, _ = send(2, random.Random(1))
print(f"  probe with TTL 2 -> {kind} from {ip}")
