# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Mobile and cellular networks: cells and frequency reuse (cluster size N,
reuse distance, capacity), handoff with and without hysteresis, generations
1G-5G, GSM/LTE/5G core roles with a HLR/VLR location-update model, satellite
and LEO delay and orbit arithmetic, and Mobile IP (home agent, care-of address,
tunnelling; see module 03). All models run in memory."""
import math
import random
from dataclasses import dataclass, field

# ===== SECTION 1: CELLS, FREQUENCY REUSE AND THE REUSE FACTOR =====
print("===== SECTION 1: CELLS, FREQUENCY REUSE AND THE REUSE FACTOR =====")


def valid_cluster_sizes(limit: int) -> list[int]:
    """Hexagonal geometry only allows N = i^2 + i*j + j^2 for integers i, j >= 0."""
    return sorted({i * i + i * j + j * j for i in range(0, 8) for j in range(0, 8)
                   if 0 < i * i + i * j + j * j <= limit})


valid = valid_cluster_sizes(20)
print("Valid cluster sizes N = i^2+ij+j^2 up to 20:", valid)
print("TRAP: N=5, 6, 8, 10 look plausible but are NOT valid for hexagonal cells. In the valid list?",
      {n: n in valid for n in (5, 6, 8, 10)})

TOTAL_CHANNELS = 840  # duplex channels available to the operator (textbook-style number)
CLUSTERS = 32         # how many clusters tile the service area
R = 1.0               # cell radius, any unit
print(f"Operator has S={TOTAL_CHANNELS} channels; one cluster of N cells uses all S, so each cell gets k=S/N")
print("  N   channels/cell k=S/N   reuse factor 1/N   D/R=sqrt(3N)   SIR(6 interferers, n=4)")
for n in (3, 4, 7, 12):
    k = TOTAL_CHANNELS // n
    d_over_r = math.sqrt(3 * n)
    sir = d_over_r ** 4 / 6          # first-tier approximation, path-loss exponent 4
    print(f"{n:>3}   {k:>10}            1/{n:<12}  {d_over_r:>8.3f}"
          f"      {10 * math.log10(sir):6.1f} dB")
print("Capacity trade-off: a smaller N gives every cell more channels (more capacity) but a smaller D/R,")
print("so co-channel cells sit closer and the signal-to-interference ratio (SIR) falls.")
print(f"System capacity for M={CLUSTERS} clusters is C = M*S = {CLUSTERS * TOTAL_CHANNELS:,} channels; with smaller cells M grows.")
area_cells_7, area_cells_4 = 224, 224  # same number of CELLS in both plans
print(f"Same {area_cells_7} cells: N=7 -> {TOTAL_CHANNELS // 7} channels per cell, "
      f"N=4 -> {TOTAL_CHANNELS // 4} per cell (x{(TOTAL_CHANNELS // 4) / (TOTAL_CHANNELS // 7):.2f} capacity per cell)")
assert math.isclose(math.sqrt(3 * 7) * R, 4.5826, abs_tol=1e-3)
print("check: OK (D/R for N=7 is 4.583)")

# ===== SECTION 2: HANDOFF AND THE PING-PONG TRAP =====
print("\n===== SECTION 2: HANDOFF AND THE PING-PONG TRAP =====")
BS = {"BS1": 0.0, "BS2": 1000.0}  # positions in metres
rng = random.Random(3)


def rx_dbm(bs: str, x: float) -> float:
    d = max(abs(x - BS[bs]), 10.0)
    return 30 - 10 * 3.5 * math.log10(d) + rng.gauss(0, 4)  # path-loss exp 3.5 + shadow fading (dB)


def drive(hysteresis_db: float) -> tuple[int, list[tuple[float, str]]]:
    global rng
    rng = random.Random(3)  # identical radio noise for both runs, fair comparison
    serving, handoffs, trace = "BS1", 0, []
    for step in range(0, 1001, 20):
        x = float(step)
        s = {b: rx_dbm(b, x) for b in BS}
        other = "BS2" if serving == "BS1" else "BS1"
        if s[other] > s[serving] + hysteresis_db:
            serving, handoffs = other, handoffs + 1
            trace.append((x, serving))
    return handoffs, trace


h0, t0 = drive(0.0)
h6, t6 = drive(6.0)
print(f"Mobile drives 0 -> 1000 m past a cell edge at ~500 m, noisy signal (seeded).")
print(f"Switch whenever the other cell is stronger (0 dB hysteresis): {h0} handoffs: {t0}")
print(f"Switch only if stronger by 6 dB (hysteresis):                  {h6} handoffs: {t6}")
assert h6 < h0 and h6 >= 1
print("check: OK (hysteresis reduces the number of handoffs; a genuine crossing still hands off)")
print(f"Hysteresis cuts the flip-flopping ({h0} -> {h6} here) but does not remove it entirely; real systems add time-to-trigger too.")
print("Hard handoff = break-before-make (GSM, LTE, NR). Soft handoff = make-before-break (3G CDMA).")

# ===== SECTION 3: GENERATIONS 1G - 5G =====
print("\n===== SECTION 3: GENERATIONS 1G - 5G =====")
GENS = [
    ("1G", "1980s", "analog voice (e.g. AMPS), FDMA", "wireless voice at all"),
    ("2G", "early 1990s", "digital voice, GSM = TDMA+FDMA; IS-95 = CDMA", "digital + SMS + encryption (GPRS/EDGE add packet data)"),
    ("3G", "early 2000s", "UMTS/WCDMA, CDMA2000", "real mobile packet data, internet access"),
    ("4G", "around 2010", "LTE, OFDMA downlink, all-IP", "pure packet network, voice becomes VoLTE"),
    ("5G", "from about 2019", "NR, wider bands incl. mmWave, massive MIMO", "service-based core, slicing, ultra-low latency modes"),
]
print("Gen  Era (approx.)      Main technology                                 Main shift")
for g in GENS:
    print(f"{g[0]:<4} {g[1]:<16} {g[2]:<46}  {g[3]}")
print("Eras are approximate and differ by country/operator; speeds are NOT listed because real rates vary hugely.")

# ===== SECTION 4: CORE NETWORK ROLES AND A LOCATION UPDATE =====
print("\n===== SECTION 4: CORE NETWORK ROLES AND A LOCATION UPDATE =====")
print("Role                GSM                 LTE (EPC)            5G")
print("Radio node          BTS (+BSC)          eNodeB               gNB")
print("Mobility/attach     MSC/VLR             MME                  AMF")
print("Subscriber DB       HLR                 HSS                  UDM")
print("Packet gateway      GGSN/SGSN (GPRS)    SGW + PGW            UPF (user plane) + SMF (sessions)")


@dataclass
class Network:
    hlr: dict[str, str] = field(default_factory=dict)             # phone -> current VLR/MSC
    vlr: dict[str, set[str]] = field(default_factory=dict)        # MSC -> phones visiting

    def location_update(self, phone: str, msc: str) -> None:
        old = self.hlr.get(phone)
        if old and old != msc:
            self.vlr[old].discard(phone)
        self.vlr.setdefault(msc, set()).add(phone)
        self.hlr[phone] = msc
        print(f"  location update: {phone} now at {msc}; HLR points to {msc}" + (f" (was {old})" if old else ""))

    def route_call(self, phone: str) -> str:
        msc = self.hlr[phone]
        assert phone in self.vlr[msc]
        return f"call for {phone}: gateway asks HLR -> {msc} -> page via BTS in its area"


net = Network()
net.location_update("+1-555-0100", "MSC-Tallahassee")
print(" ", net.route_call("+1-555-0100"))
net.location_update("+1-555-0100", "MSC-Orlando")
print(" ", net.route_call("+1-555-0100"))
print("The HLR/HSS is the 'home' record; the VLR/MME is the 'visitor' record. Same idea as Mobile IP's home/foreign agent.")

# ===== SECTION 5: SATELLITE AND LEO =====
print("\n===== SECTION 5: SATELLITE AND LEO =====")
C_KM_S = 299_792.458
MU = 398_600.4418   # km^3/s^2, Earth's gravitational parameter
R_EARTH = 6378.137  # km, equatorial radius


def period_s(alt_km: float) -> float:
    a = R_EARTH + alt_km
    return 2 * math.pi * math.sqrt(a ** 3 / MU)


for name, alt in (("GEO", 35_786), ("LEO (550 km, example altitude)", 550)):
    one_way_ms = 2 * alt / C_KM_S * 1000  # ground -> satellite -> ground, satellite directly overhead
    print(f"{name:<32} altitude {alt:>6} km: orbital period {period_s(alt) / 60:8.1f} min, "
          f"min one-way hop {one_way_ms:6.1f} ms, min RTT {2 * one_way_ms:6.1f} ms")
geo = period_s(35_786)
assert abs(geo - 86_164) < 20
print(f"check: OK (GEO period {geo:.0f} s ~ one sidereal day 86164 s, so it hovers over one spot)")
print("These are propagation FLOORS (straight up and down at the speed of light), real delay adds processing and queuing.")
print("GEO: 3 satellites cover most of Earth but ~0.5 s RTT hurts TCP and voice. LEO: low latency, but each satellite")
print("moves quickly across the sky, so many satellites are needed and ground stations hand off between them (like cells).")

# ===== SECTION 6: MOBILE IP (LINK TO MODULE 03) =====
print("\n===== SECTION 6: MOBILE IP (LINK TO MODULE 03) =====")


@dataclass
class IpPacket:
    src: str
    dst: str
    payload: object
    proto: str = "TCP"


HOME_ADDR, HOME_AGENT, CARE_OF = "10.1.0.50", "10.1.0.1", "172.16.9.77"
bindings: dict[str, str] = {}
print(f"Mobile node's permanent home address {HOME_ADDR}; away on a foreign network with care-of address {CARE_OF}.")
bindings[HOME_ADDR] = CARE_OF
print(f"Registration: mobile -> home agent {HOME_AGENT}: 'binding {HOME_ADDR} => {CARE_OF}' (RFC 5944 for IPv4)")
orig = IpPacket("203.0.113.5", HOME_ADDR, "GET /")
print("1. Correspondent sends:", orig)
if orig.dst in bindings:
    tunnelled = IpPacket(HOME_AGENT, bindings[orig.dst], orig, proto="IP-in-IP")
    print("2. Home agent intercepts (proxy ARP) and encapsulates:", tunnelled)
    inner = tunnelled.payload
    print("3. At the care-of address the tunnel end removes the outer header:", inner)
assert inner == orig
print("check: OK (inner packet delivered unchanged; the correspondent never knew the mobile moved)")
print("Reply path: mobile -> correspondent directly (triangle routing: in via home agent, out direct).")
print(f"Overhead of IP-in-IP = one extra IPv4 header = 20 bytes per packet (RFC 2003).")
