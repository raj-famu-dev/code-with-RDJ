# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Switching techniques: circuit, message and packet switching, datagram vs
virtual-circuit packet networks, and a worked end-to-end delay comparison.
Implements the 'switching' part of the Introduction chapter."""
import random

# ===== SECTION 1: THE WORKED SCENARIO =====
print("===== SECTION 1: THE WORKED SCENARIO =====")
L = 800_000          # message size in bits
R = 1_000_000        # every link: 1 Mbps
LINKS = 4            # source - SW1 - SW2 - SW3 - destination = 4 links, 3 switches
PROP = 0.002         # propagation per link: 2 ms
PKT_PAYLOAD = 8_000  # bits of data per packet
HEADER = 400         # bits of header per packet
SETUP = 0.050        # circuit set-up signalling time (assumed): 50 ms
print(f"message = {L:,} bits, link rate = {R:,} bps, links = {LINKS} ({LINKS - 1} switches)")
print(f"propagation per link = {PROP * 1000:.0f} ms; packet = {PKT_PAYLOAD:,} payload + {HEADER} header bits")
print(f"circuit set-up (assumed) = {SETUP * 1000:.0f} ms")


# ===== SECTION 2: DELAY OF EACH TECHNIQUE =====
print("\n===== SECTION 2: DELAY OF EACH TECHNIQUE =====")


def circuit_delay() -> float:
    """Set-up, then one continuous stream: the bits cross all links as one pipe.
    delay = setup + L/R + propagation over all links (no store-and-forward wait)."""
    return SETUP + L / R + LINKS * PROP


def message_delay() -> float:
    """Whole message stored then forwarded at every hop: links * (L/R) + propagation."""
    return LINKS * (L / R) + LINKS * PROP


def packet_count() -> int:
    return -(-L // PKT_PAYLOAD)   # ceiling division


def packet_delay() -> float:
    """Pipelined store-and-forward: first packet crosses all links, the rest follow
    one transmission time apart: (links + P - 1) * (pkt_bits/R) + propagation."""
    p = packet_count()
    t_pkt = (PKT_PAYLOAD + HEADER) / R
    return (LINKS + p - 1) * t_pkt + LINKS * PROP


c, m, p = circuit_delay(), message_delay(), packet_delay()
print(f"circuit : {SETUP:.3f} + {L / R:.3f} + {LINKS * PROP:.3f} = {c:.3f} s")
print(f"message : {LINKS} x {L / R:.3f} + {LINKS * PROP:.3f} = {m:.3f} s")
print(f"packet  : P={packet_count()} packets, ({LINKS}+{packet_count()}-1) x {(PKT_PAYLOAD + HEADER) / R:.4f} + {LINKS * PROP:.3f} = {p:.3f} s")
print("Ranking (fastest first):", [(k, round(v, 3)) for k, v in sorted([("circuit", c), ("packet", p), ("message", m)], key=lambda x: x[1])])
assert c < p < m
print("Packet switching beats message switching because packets pipeline across links;")
print("circuit switching is slightly faster HERE (only because the assumed set-up is a small 50 ms), but it")
print("reserves the line even when idle and its set-up cost does not shrink for short messages.")
print("check: OK")

# Trap: ignoring the header overhead makes packet switching look faster than it is.
no_header = (LINKS + packet_count() - 1) * (PKT_PAYLOAD / R) + LINKS * PROP
print(f"Trap: forgetting headers gives {no_header:.3f} s, but the real packet delay is {p:.3f} s "
      f"({HEADER / (PKT_PAYLOAD + HEADER):.1%} overhead bits).")


# ===== SECTION 3: PACKET SIZE TRADE-OFF =====
print("\n===== SECTION 3: PACKET SIZE TRADE-OFF =====")
print(f"{'payload bits':>13}{'packets':>9}{'delay (s)':>11}")
best = None
for payload in (400, 1_000, 4_000, 8_000, 40_000, 200_000, 800_000):
    pk = -(-L // payload)
    d = (LINKS + pk - 1) * ((payload + HEADER) / R) + LINKS * PROP
    best = d if best is None else min(best, d)
    print(f"{payload:>13,}{pk:>9,}{d:>11.3f}")
print("Tiny packets: header overhead dominates. Huge packets: no pipelining (a single 800,000-bit packet = message switching).")
print(f"Best delay in this table: {best:.3f} s")


# ===== SECTION 4: DATAGRAM vs VIRTUAL CIRCUIT =====
print("\n===== SECTION 4: DATAGRAM vs VIRTUAL CIRCUIT =====")
rng = random.Random(7)
# Two possible paths with different total delays (seconds).
PATHS = {"upper": 0.020, "lower": 0.035}


def datagram_send(n: int) -> list[tuple[int, str, float]]:
    """Each packet is routed independently: path chosen per packet (router load changes)."""
    out = []
    for seq in range(n):
        path = rng.choice(sorted(PATHS))
        send_t = seq * 0.004
        out.append((seq, path, send_t + PATHS[path]))
    return out


def vc_send(n: int) -> list[tuple[int, str, float]]:
    """A virtual circuit fixes ONE path at set-up; every packet follows it."""
    return [(seq, "upper", seq * 0.004 + PATHS["upper"]) for seq in range(n)]


for label, sender in (("datagram", datagram_send), ("virtual circuit", vc_send)):
    pkts = sender(8)
    arrival_order = [s for s, _, _ in sorted(pkts, key=lambda x: x[2])]
    print(f"{label:<16} paths={[p[1][0] for p in pkts]} arrival order={arrival_order}"
          f" in order={arrival_order == sorted(arrival_order)}")
print("Datagram: no set-up, per-packet routing, packets may arrive out of order (TCP/IP fixes this above IP).")
print("Virtual circuit: set-up phase, a short VC identifier in each header, in order, state kept in every switch.")
vc_table = {("port1", 5): ("port3", 9)}
print("VC switch table maps (in-port, in-VCI) -> (out-port, out-VCI):", vc_table)


# ===== SECTION 5: COMPARISON AND WORKED EXAMPLE =====
print("\n===== SECTION 5: COMPARISON AND WORKED EXAMPLE =====")
cmp_rows = [
    ("set-up", "yes (before data)", "no", "no"),
    ("resources", "dedicated", "per hop, on demand", "shared, on demand"),
    ("store-and-forward unit", "none", "entire message", "small packet"),
    ("delay problem", "set-up delay", "big buffers, long delay", "queuing, reorder, loss"),
    ("typical use", "old telephone", "telegram, e-mail relays", "Internet"),
]
print(f"{'':<24}{'circuit':<20}{'message':<26}{'packet'}")
for r in cmp_rows:
    print(f"{r[0]:<24}{r[1]:<20}{r[2]:<26}{r[3]}")
# Exam problem: 3 hops, 4 links, 1 Mbps, message 800,000 bits => message switching delay
print(f"Worked example answer: message switching over {LINKS} links = {m:.3f} s; packet switching = {p:.3f} s")
assert round(m, 3) == 3.208 and round(p, 4) == 0.8732
print("check: OK")
