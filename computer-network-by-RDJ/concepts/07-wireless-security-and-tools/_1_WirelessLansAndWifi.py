# Tags: #Python #ComputerNetworks #Wireless #NetworkSecurity #WirelessLansWifi | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Wireless LANs and Wi-Fi (IEEE 802.11): BSS/ESS/AP architecture, free-space
path loss for 2.4 vs 5 GHz, CSMA/CA with ACK, hidden and exposed terminals and
RTS/CTS, frame-control decoding, why WEP is broken and what WPA2/WPA3 changed,
channels/bands, and a Bluetooth/Zigbee overview. Everything is an in-memory model."""
import hashlib
import math
import random
import zlib

# ===== SECTION 1: 802.11 ARCHITECTURE (BSS / ESS / AP) AND PATH LOSS =====
print("===== SECTION 1: 802.11 ARCHITECTURE (BSS / ESS / AP) AND PATH LOSS =====")


def fspl_db(distance_m: float, freq_mhz: float) -> float:
    """Free-space path loss in dB: 20log10(d_km) + 20log10(f_MHz) + 32.44."""
    return 20 * math.log10(distance_m / 1000) + 20 * math.log10(freq_mhz) + 32.44


TX_POWER_DBM = 20.0  # a typical-order-of-magnitude transmit power, an assumption
APS = {"AP-1": 0.0, "AP-2": 60.0}  # positions on a line, metres; same SSID => one ESS
SSID = "CampusNet"
print(f"ESS '{SSID}' = 2 BSSs (AP-1, AP-2) joined by a distribution system (wired LAN)")
for x in (5.0, 27.0, 55.0):
    rssi = {ap: TX_POWER_DBM - fspl_db(max(abs(x - pos), 1.0), 2437) for ap, pos in APS.items()}
    best = max(rssi, key=rssi.get)
    print(f"  station at x={x:5.1f} m  RSSI(AP-1)={rssi['AP-1']:7.1f} dBm  "
          f"RSSI(AP-2)={rssi['AP-2']:7.1f} dBm  -> associates with {best}")
loss24, loss5 = fspl_db(20, 2437), fspl_db(20, 5180)
print(f"FSPL at 20 m: 2.4 GHz (ch 6) = {loss24:.1f} dB, 5 GHz (ch 36) = {loss5:.1f} dB, "
      f"extra loss at 5 GHz = {loss5 - loss24:.1f} dB (walls make it worse in practice)")
assert abs((loss5 - loss24) - 20 * math.log10(5180 / 2437)) < 1e-9
print("check: OK (difference equals 20*log10(f2/f1))")

# ===== SECTION 2: CSMA/CA WITH ACK AND BINARY EXPONENTIAL BACKOFF =====
print("\n===== SECTION 2: CSMA/CA WITH ACK AND BINARY EXPONENTIAL BACKOFF =====")
SLOT_US, SIFS_US = 9, 10
DIFS_US = SIFS_US + 2 * SLOT_US
CW_MIN, CW_MAX = 15, 1023
print(f"Timing (802.11g/OFDM-style values): slot={SLOT_US} us, SIFS={SIFS_US} us, "
      f"DIFS=SIFS+2*slot={DIFS_US} us, CW {CW_MIN}..{CW_MAX}")


def csma_ca(names: list[str], seed: int, verbose: bool) -> int:
    """One frame per station. Returns the number of collisions that happened."""
    rng = random.Random(seed)
    cw = {n: CW_MIN for n in names}
    counter = {n: rng.randint(0, cw[n]) for n in names}
    waiting = list(names)
    collisions = 0
    rnd = 0
    while waiting:
        rnd += 1
        low = min(counter[n] for n in waiting)
        winners = [n for n in waiting if counter[n] == low]
        for n in waiting:
            counter[n] -= low  # countdown froze when the winner(s) started
        if verbose:
            state = ", ".join(f"{n}:{counter[n] + low}" for n in waiting)
            print(f"  round {rnd}: counters [{state}] -> {low} idle slots then {winners} transmit")
        if len(winners) == 1:
            w = winners[0]
            if verbose:
                print(f"           {w} sends DATA, receiver waits SIFS={SIFS_US} us, sends ACK -> success")
            waiting.remove(w)
        else:
            collisions += 1
            for w in winners:  # no ACK arrives => double the window, redraw
                cw[w] = min(2 * cw[w] + 1, CW_MAX)
                counter[w] = rng.randint(0, cw[w])
            if verbose:
                print(f"           COLLISION of {winners}: no ACK, CW -> "
                      f"{[cw[w] for w in winners]}, redraw backoff")
    return collisions


seed_with_collision = next(s for s in range(500) if csma_ca(["A", "B", "C", "D"], s, False) > 0)
print(f"First seed (0..499) where 4 stations collide at least once: {seed_with_collision}")
csma_ca(["A", "B", "C", "D"], seed_with_collision, True)
print("Why ACK: a sender cannot hear its own collision on radio (it transmits far louder than it receives),")
print("so Wi-Fi uses CA (avoidance) and a link-layer ACK instead of Ethernet's CD (detection).")

# ===== SECTION 3: HIDDEN AND EXPOSED TERMINALS, RTS/CTS =====
print("\n===== SECTION 3: HIDDEN AND EXPOSED TERMINALS, RTS/CTS =====")
RANGE_M = 120.0
POS = {"A": 0.0, "B": 100.0, "C": 200.0, "D": 300.0}


def hears(x: str, y: str) -> bool:
    return x != y and abs(POS[x] - POS[y]) <= RANGE_M


print(f"Radio range {RANGE_M:.0f} m; positions {POS}")
print("Who hears whom:", {n: [m for m in POS if hears(n, m)] for n in POS})

print("-- Hidden terminal: A and C both send to B, but A and C cannot hear each other --")
print(f"A hears C? {hears('A', 'C')}  (so C senses an idle medium while A transmits)")
heard_at_B = [s for s in ("A", "C") if hears(s, "B")]
print(f"Both transmit at once; B hears {heard_at_B} simultaneously -> "
      f"{'COLLISION at B' if len(heard_at_B) > 1 else 'ok'}")

print("-- Fix with RTS/CTS (virtual carrier sense, NAV) --")
nav_blocked: set[str] = set()
log = []
log.append("A -> B : RTS(duration=...)   heard by " + str([n for n in POS if hears('A', n)]))
log.append("B -> A : CTS(duration=...)   heard by " + str([n for n in POS if hears('B', n)]))
for n in POS:
    if hears("B", n) and n != "A":
        nav_blocked.add(n)  # anyone hearing the CTS sets its NAV and stays quiet
for line in log:
    print("  " + line)
print(f"Stations that set NAV (defer) after the CTS: {sorted(nav_blocked)} -> C is silenced although it never heard A")
assert "C" in nav_blocked
print("check: OK (C is protected by hearing B's CTS)")

print("-- Exposed terminal: B -> A is in progress; C wants to send to D --")
print(f"C hears B? {hears('C', 'B')} -> plain CSMA makes C wait; "
      f"but D hears B? {hears('D', 'B')} so the C->D frame would not disturb A. C waits needlessly.")
print("RTS/CTS does not fully solve exposed terminals; trade-off: RTS/CTS adds overhead, so it is used only for")
print("frames above a size threshold (the RTS threshold).")

# ===== SECTION 4: 802.11 FRAME TYPES AND THE FRAME CONTROL FIELD =====
print("\n===== SECTION 4: 802.11 FRAME TYPES AND THE FRAME CONTROL FIELD =====")
TYPES = {0: "Management", 1: "Control", 2: "Data"}
SUBTYPES = {
    (0, 0): "Association request", (0, 4): "Probe request", (0, 8): "Beacon",
    (0, 11): "Authentication", (1, 11): "RTS", (1, 12): "CTS", (1, 13): "ACK",
    (2, 0): "Data",
}


def frame_control_first_byte(ftype: int, subtype: int, version: int = 0) -> int:
    """Bits 0-1 protocol version, bits 2-3 type, bits 4-7 subtype."""
    return (subtype << 4) | (ftype << 2) | version


def decode_first_byte(b: int) -> tuple[int, str, str]:
    version, ftype, subtype = b & 0b11, (b >> 2) & 0b11, b >> 4
    return version, TYPES.get(ftype, "Reserved"), SUBTYPES.get((ftype, subtype), f"subtype {subtype}")


for (t, s), name in SUBTYPES.items():
    fb = frame_control_first_byte(t, s)
    assert decode_first_byte(fb)[1:] == (TYPES[t], name)
    print(f"  {name:<20} type={t} ({TYPES[t]:<10}) subtype={s:<2} first FC byte = 0x{fb:02X}")
assert frame_control_first_byte(1, 13) == 0xD4 and frame_control_first_byte(0, 8) == 0x80
print("check: OK (ACK = 0xD4, Beacon = 0x80, round-trip decode works)")
print("Management = join/leave the network, Control = help access the medium, Data = carry payload.")
print("A data frame carries up to 4 MAC addresses (to/from-DS bits decide the roles) - unlike Ethernet's 2.")

# ===== SECTION 5: SECURITY - WHY WEP FAILED, WHAT WPA2/WPA3 DO =====
print("\n===== SECTION 5: SECURITY - WHY WEP FAILED, WHAT WPA2/WPA3 DO =====")
print("WEP design facts: RC4 stream cipher, a 24-bit IV sent in clear with every frame, CRC-32 as the 'integrity' check.")
rng = random.Random(7)
seen: set[int] = set()
frames = 0
while True:
    frames += 1
    iv = rng.getrandbits(24)
    if iv in seen:
        break
    seen.add(iv)
print(f"IV space = 2^24 = {2**24:,}. With random IVs the FIRST repeat came after {frames:,} frames "
      f"(birthday bound ~ sqrt(2^24) = {math.isqrt(2**24):,}).")
print("A repeated IV with the same key means the same keystream is reused -> XOR of two ciphertexts leaks XOR of plaintexts.")
a, b, zero = b"PAY ALICE 0100", b"PAY BOB   9900", bytes(14)
xor = bytes(x ^ y for x, y in zip(a, b))
print("CRC-32 is linear: crc(a) ^ crc(b) ^ crc(0) == crc(a ^ b):",
      (zlib.crc32(a) ^ zlib.crc32(b) ^ zlib.crc32(zero)) == zlib.crc32(xor))
print("-> bit-flips in ciphertext can be 'fixed up' so the CRC still passes; CRC detects noise, not tampering. Use a MAC.")
PBKDF2_PMK = hashlib.pbkdf2_hmac("sha1", b"password", b"IEEE", 4096, 32).hex()
print("WPA2-Personal: PMK = PBKDF2-HMAC-SHA1(passphrase, SSID, 4096 iterations, 256 bits)")
print("  test vector (passphrase 'password', SSID 'IEEE'):", PBKDF2_PMK[:16] + "...")
assert PBKDF2_PMK.startswith("f42c6fc52df0ebef")
print("check: OK (matches the published 802.11i test vector prefix)")
print("Protocol  Cipher / integrity        Key setup                       Status")
print("WEP       RC4 + CRC-32              shared static key               broken, do not use")
print("WPA       RC4 + TKIP (MIC)          PSK or 802.1X, interim fix      deprecated")
print("WPA2      AES-CCMP                  4-way handshake, PSK/802.1X     widely deployed; PSK exposed to offline guessing")
print("WPA3      AES (CCMP/GCMP)           SAE replaces PSK handshake,     current; protected management frames required")
print("                                    resists offline dictionary attack")

# ===== SECTION 6: BANDS AND CHANNELS =====
print("\n===== SECTION 6: BANDS AND CHANNELS =====")
centres = {ch: 2407 + 5 * ch for ch in range(1, 14)}
print("2.4 GHz channel centres (MHz) = 2407 + 5*n:", {k: centres[k] for k in (1, 6, 11, 13)})
WIDTH = 20
non_overlap = [1]
while non_overlap[-1] + 5 <= 13:
    non_overlap.append(non_overlap[-1] + 5)
print(f"Channels are 5 MHz apart but ~{WIDTH}-22 MHz wide, so only channels >= 5 apart avoid overlap: {non_overlap}")
print("In the US the usual non-overlapping set is 1, 6, 11 (channels 12-13 are restricted or unused there; other regions allow up to 13).")
print("Std       Year  Band(s)          Max theoretical PHY rate")
for row in [("802.11b", 1999, "2.4", "11 Mb/s"), ("802.11a", 1999, "5", "54 Mb/s"), ("802.11g", 2003, "2.4", "54 Mb/s"),
            ("802.11n", 2009, "2.4 + 5", "600 Mb/s"), ("802.11ac", 2013, "5", "~6.9 Gb/s"),
            ("802.11ax", 2021, "2.4+5(+6)", "~9.6 Gb/s")]:
    print(f"{row[0]:<9} {row[1]:<5} {row[2]:<16} {row[3]}   (peak PHY, real throughput is far lower)")
print("2.4 GHz: longer range, better wall penetration, crowded (Bluetooth, microwaves). 5 GHz: more channels, shorter range.")

# ===== SECTION 7: BLUETOOTH AND ZIGBEE OVERVIEW =====
print("\n===== SECTION 7: BLUETOOTH AND ZIGBEE OVERVIEW =====")
HOPS_PER_S = 1600
slot_us = 1_000_000 / HOPS_PER_S
print(f"Bluetooth Classic: 2.4 GHz, frequency hopping over 79 x 1 MHz channels, {HOPS_PER_S} hops/s "
      f"-> time slot = {slot_us:.0f} us")
assert slot_us == 625
print("check: OK (625 us slots)")
print("Piconet: 1 master + up to 7 active slaves; several piconets form a scatternet. Master polls; slaves talk when polled.")
print("Bluetooth Low Energy: 40 channels x 2 MHz (3 advertising), built for coin-cell sensors.")
print("Zigbee (IEEE 802.15.4): 2.4 GHz band, 16 channels (11-26), 250 kb/s, low power, mesh routing; used for sensors/home automation.")
print("Range classes (typical order): Bluetooth ~10 m, Zigbee ~10-100 m per hop, Wi-Fi ~tens of metres indoors.")
