# `_1_WirelessLansAndWifi.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A wireless LAN (WLAN) connects devices over radio instead of cable; Wi-Fi is the brand name for the IEEE 802.11 family of WLAN standards. Radio is a shared, noisy, broadcast medium where a sender cannot reliably detect collisions while it transmits, so 802.11 replaces Ethernet's CSMA/CD with CSMA/CA (collision avoidance) plus a link-layer acknowledgement.

**Architecture.** A *station* (STA) is any device with a Wi-Fi radio. An *access point* (AP) is a station that bridges the wireless side to a wired distribution system. One AP plus its associated stations is a *Basic Service Set* (BSS), identified by a BSSID (normally the AP's MAC address). Several BSSs that share a network name (the SSID) and are joined by a wired backbone form an *Extended Service Set* (ESS), which lets a station roam between APs. A BSS without an AP, where stations talk directly, is an *ad hoc* or IBSS network. A station finds networks by listening for periodic *beacon* frames (passive scan) or by sending *probe requests* (active scan), then goes through authentication and association before it can send data.

**CSMA/CA with ACK.** Before sending, a station senses the medium. If it has been idle for a DIFS (DCF Inter-Frame Space), the station may send; if busy, it waits for idle and then picks a random *backoff* counter from 0 to CW (contention window, starting at CWmin). The counter counts down only while the medium is idle and freezes when someone transmits. At zero the station sends. The receiver, after a short SIFS (shorter than DIFS, so the ACK wins the medium), returns an ACK. No ACK means a collision or loss: the sender doubles its window (binary exponential backoff, capped at CWmax) and tries again. Typical OFDM numbers (802.11g/a style): slot 9 microseconds, SIFS 10 microseconds, DIFS = SIFS + 2 x slot = 28 microseconds, CW from 15 to 1023.

**Hidden and exposed terminals.** Two stations are *hidden* from each other if both can reach a third station (often the AP) but cannot hear each other. They both sense an idle channel and transmit at the same time, and the frames collide at the receiver. *RTS/CTS* fixes this with virtual carrier sensing: the sender transmits a small Request To Send; the receiver answers Clear To Send; every station that hears either frame sets its *NAV* (Network Allocation Vector) timer from the duration field and stays silent. The *exposed terminal* problem is the opposite: a station hears a nearby transmitter, defers, although its own transmission would not disturb the other receiver, wasting capacity. RTS/CTS adds overhead, so it is applied only to frames larger than a configurable threshold.

**Frame types.** Every 802.11 frame starts with a 2-byte Frame Control field: protocol version (2 bits), type (2 bits), subtype (4 bits), then flags (To DS, From DS, More Fragments, Retry, Power Management, More Data, Protected Frame, Order). Three types exist: *management* (beacon, probe request/response, authentication, association, deauthentication), *control* (RTS, CTS, ACK, power-save poll) and *data*. A data frame can carry up to four MAC addresses, whose roles depend on the To DS/From DS bits, because a frame may need source, destination, transmitter and receiver (the AP) all at once. An ACK has first byte 0xD4, an RTS 0xB4, a CTS 0xC4 and a beacon 0x80.

**Security.** WEP (1997) used the RC4 stream cipher with a 24-bit initialisation vector (IV) sent in the clear and CRC-32 as its integrity check. The IV space is small, so IVs repeat, and a repeated IV means a reused keystream; CRC-32 is linear, so it detects accidental errors but not deliberate modification. Together with weaknesses in how RC4 keys were formed, WEP can be broken in practice and must not be used. WPA was an interim fix (TKIP, still RC4-based, with a message integrity check). WPA2 (802.11i) uses AES-CCMP and a 4-way handshake; in personal mode the Pairwise Master Key is derived with PBKDF2-HMAC-SHA1 from the passphrase and SSID with 4096 iterations, which an eavesdropper who captures a handshake can try to guess offline, so passphrase strength matters. WPA3 replaces the PSK exchange with SAE (Simultaneous Authentication of Equals, a password-authenticated key exchange) which resists offline dictionary attacks and gives forward secrecy, and it requires protected management frames. In an enterprise network, WPA2/WPA3-Enterprise uses 802.1X with a RADIUS server instead of a shared passphrase.

**Bands and standards.** 2.4 GHz travels farther and passes walls better but has only three non-overlapping 20 MHz channels in practice (1, 6, 11) and is crowded by Bluetooth, microwave ovens and neighbours. 5 GHz has many more channels and less interference but a shorter range; free-space loss alone is about 6.5 dB higher at 5 GHz for the same distance. Wi-Fi 6E and later use 6 GHz too.

| Standard | Year | Band | Peak PHY rate (theoretical) |
|---|---|---|---|
| 802.11b | 1999 | 2.4 GHz | 11 Mb/s |
| 802.11a | 1999 | 5 GHz | 54 Mb/s |
| 802.11g | 2003 | 2.4 GHz | 54 Mb/s |
| 802.11n (Wi-Fi 4) | 2009 | 2.4 and 5 GHz | 600 Mb/s |
| 802.11ac (Wi-Fi 5) | 2013 | 5 GHz | about 6.9 Gb/s |
| 802.11ax (Wi-Fi 6) | 2021 | 2.4, 5 (6 for 6E) | about 9.6 Gb/s |

Peak PHY rate is a ceiling; real throughput is much lower because of ACKs, backoff, protocol overhead and shared airtime.

**Bluetooth and Zigbee.** Bluetooth Classic is a short-range personal-area network at 2.4 GHz using frequency hopping across 79 channels of 1 MHz at 1600 hops per second (625 microsecond slots). One master and up to 7 active slaves form a *piconet*; linked piconets form a *scatternet*. Bluetooth Low Energy uses 40 channels of 2 MHz for low-power sensors. Zigbee is built on IEEE 802.15.4: low power, low rate (250 kb/s at 2.4 GHz, 16 channels numbered 11-26) and mesh routing for sensors and home automation.

Typical exam questions: why CSMA/CD does not work on wireless; explain the hidden terminal problem and how RTS/CTS helps; what is NAV; difference between BSS and ESS; why WEP is insecure; compare 2.4 and 5 GHz.

## Full Line-by-Line Breakdown

### SECTION 1: 802.11 ARCHITECTURE (BSS / ESS / AP) AND PATH LOSS
Two APs with the same SSID form one ESS. Free-space path loss is FSPL(dB) = 20 log10(d in km) + 20 log10(f in MHz) + 32.44. Received power is transmit power minus loss, and a station associates with the AP it hears strongest. Note the station at 27 m picks AP-1 by a small margin because it is a little closer; real roaming adds hysteresis, like the handoff in the mobile module. The last lines compute the extra loss at 5 GHz, which depends only on the frequency ratio: 20 log10(5180/2437). Walls and furniture make the real gap larger; this is the free-space ideal only. The transmit power is an assumption, not a measurement.

```text
===== SECTION 1: 802.11 ARCHITECTURE (BSS / ESS / AP) AND PATH LOSS =====
ESS 'CampusNet' = 2 BSSs (AP-1, AP-2) joined by a distribution system (wired LAN)
  station at x=  5.0 m  RSSI(AP-1)=  -34.2 dBm  RSSI(AP-2)=  -55.0 dBm  -> associates with AP-1
  station at x= 27.0 m  RSSI(AP-1)=  -48.8 dBm  RSSI(AP-2)=  -50.5 dBm  -> associates with AP-1
  station at x= 55.0 m  RSSI(AP-1)=  -55.0 dBm  RSSI(AP-2)=  -34.2 dBm  -> associates with AP-2
FSPL at 20 m: 2.4 GHz (ch 6) = 66.2 dB, 5 GHz (ch 36) = 72.7 dB, extra loss at 5 GHz = 6.5 dB (walls make it worse in practice)
check: OK (difference equals 20*log10(f2/f1))
```

### SECTION 2: CSMA/CA WITH ACK AND BINARY EXPONENTIAL BACKOFF
Four stations each hold one frame. Each draws a backoff counter in [0, CW]. Each round the smallest counter wins; everyone else's counter drops by the idle slots that passed (freezing while the winner sends). A unique winner sends and gets an ACK after SIFS. A tie is a collision: no ACK arrives, the contention window doubles (15 to 31), and a new backoff is drawn. The seed was found by searching 0..499 for the first run that contains a collision, so the demo is deterministic yet interesting. In the shown run B and C tie at 1 slot. The closing lines explain why Wi-Fi cannot do collision *detection*: a radio transmits at a power far above what it receives, so it cannot hear a collision while talking.

```text
===== SECTION 2: CSMA/CA WITH ACK AND BINARY EXPONENTIAL BACKOFF =====
Timing (802.11g/OFDM-style values): slot=9 us, SIFS=10 us, DIFS=SIFS+2*slot=28 us, CW 15..1023
First seed (0..499) where 4 stations collide at least once: 2
  round 1: counters [A:1, B:2, C:2, D:11] -> 1 idle slots then ['A'] transmit
           A sends DATA, receiver waits SIFS=10 us, sends ACK -> success
  round 2: counters [B:1, C:1, D:10] -> 1 idle slots then ['B', 'C'] transmit
           COLLISION of ['B', 'C']: no ACK, CW -> [31, 31], redraw backoff
  round 3: counters [B:10, C:19, D:9] -> 9 idle slots then ['D'] transmit
           D sends DATA, receiver waits SIFS=10 us, sends ACK -> success
  round 4: counters [B:1, C:10] -> 1 idle slots then ['B'] transmit
           B sends DATA, receiver waits SIFS=10 us, sends ACK -> success
  round 5: counters [C:9] -> 9 idle slots then ['C'] transmit
           C sends DATA, receiver waits SIFS=10 us, sends ACK -> success
Why ACK: a sender cannot hear its own collision on radio (it transmits far louder than it receives),
so Wi-Fi uses CA (avoidance) and a link-layer ACK instead of Ethernet's CD (detection).
```

### SECTION 3: HIDDEN AND EXPOSED TERMINALS, RTS/CTS
Positions on a line (0, 100, 200, 300 m) with a 120 m radio range give the "who hears whom" table: A hears only B, B hears A and C, and so on. A and C are hidden from each other, so when both send to B, B hears both and the frames collide. With RTS/CTS, A's RTS reaches only B, but B's CTS reaches both A and C. C sets its NAV and defers, even though it never heard A. The `assert` confirms C is protected. For the exposed terminal, B is sending to A; C hears B and defers, but D is out of B's range, so C -> D would have been harmless; the opportunity is wasted. RTS/CTS does not fix that, and it costs airtime, which is why a size threshold decides when to use it.

```text
===== SECTION 3: HIDDEN AND EXPOSED TERMINALS, RTS/CTS =====
Radio range 120 m; positions {'A': 0.0, 'B': 100.0, 'C': 200.0, 'D': 300.0}
Who hears whom: {'A': ['B'], 'B': ['A', 'C'], 'C': ['B', 'D'], 'D': ['C']}
-- Hidden terminal: A and C both send to B, but A and C cannot hear each other --
A hears C? False  (so C senses an idle medium while A transmits)
Both transmit at once; B hears ['A', 'C'] simultaneously -> COLLISION at B
-- Fix with RTS/CTS (virtual carrier sense, NAV) --
  A -> B : RTS(duration=...)   heard by ['B']
  B -> A : CTS(duration=...)   heard by ['A', 'C']
Stations that set NAV (defer) after the CTS: ['C'] -> C is silenced although it never heard A
check: OK (C is protected by hearing B's CTS)
-- Exposed terminal: B -> A is in progress; C wants to send to D --
C hears B? True -> plain CSMA makes C wait; but D hears B? False so the C->D frame would not disturb A. C waits needlessly.
RTS/CTS does not fully solve exposed terminals; trade-off: RTS/CTS adds overhead, so it is used only for
frames above a size threshold (the RTS threshold).
```

### SECTION 4: 802.11 FRAME TYPES AND THE FRAME CONTROL FIELD
The first Frame Control byte packs `subtype << 4 | type << 2 | version`. The code builds it, decodes it, and asserts the well-known values (ACK = 0xD4, Beacon = 0x80). For ACK: type 1 = `01`, subtype 13 = `1101`, version `00`, so the byte is `1101 0100` = 0xD4. Management frames join and leave networks; control frames (RTS, CTS, ACK) coordinate access; data frames carry user data.

```text
===== SECTION 4: 802.11 FRAME TYPES AND THE FRAME CONTROL FIELD =====
  Association request  type=0 (Management) subtype=0  first FC byte = 0x00
  Probe request        type=0 (Management) subtype=4  first FC byte = 0x40
  Beacon               type=0 (Management) subtype=8  first FC byte = 0x80
  Authentication       type=0 (Management) subtype=11 first FC byte = 0xB0
  RTS                  type=1 (Control   ) subtype=11 first FC byte = 0xB4
  CTS                  type=1 (Control   ) subtype=12 first FC byte = 0xC4
  ACK                  type=1 (Control   ) subtype=13 first FC byte = 0xD4
  Data                 type=2 (Data      ) subtype=0  first FC byte = 0x08
check: OK (ACK = 0xD4, Beacon = 0x80, round-trip decode works)
Management = join/leave the network, Control = help access the medium, Data = carry payload.
A data frame carries up to 4 MAC addresses (to/from-DS bits decide the roles) - unlike Ethernet's 2.
```

### SECTION 5: SECURITY - WHY WEP FAILED, WHAT WPA2/WPA3 DO
The IV is only 24 bits, so there are 16,777,216 possible values. By the birthday effect, a repeat is expected after roughly the square root of that number (a few thousand frames), and the seeded run saw its first repeat after the number of frames printed. A repeated IV with the same key reuses the keystream, and XORing the two ciphertexts removes the keystream and leaves the XOR of the plaintexts. Next, CRC-32 linearity: `crc(a) ^ crc(b) ^ crc(0) == crc(a ^ b)` for equal-length messages. This is the algebra that lets modification of ciphertext be accompanied by a matching CRC adjustment: CRC is an error-detecting code, not a message authentication code. Then the WPA2-Personal key derivation is computed with `hashlib.pbkdf2_hmac` and compared with the published IEEE 802.11i test vector (passphrase "password", SSID "IEEE"). The table summarises the protocols. This section demonstrates principles in memory only; it contains no attack tooling.

```text
===== SECTION 5: SECURITY - WHY WEP FAILED, WHAT WPA2/WPA3 DO =====
WEP design facts: RC4 stream cipher, a 24-bit IV sent in clear with every frame, CRC-32 as the 'integrity' check.
IV space = 2^24 = 16,777,216. With random IVs the FIRST repeat came after 5,197 frames (birthday bound ~ sqrt(2^24) = 4,096).
A repeated IV with the same key means the same keystream is reused -> XOR of two ciphertexts leaks XOR of plaintexts.
CRC-32 is linear: crc(a) ^ crc(b) ^ crc(0) == crc(a ^ b): True
-> bit-flips in ciphertext can be 'fixed up' so the CRC still passes; CRC detects noise, not tampering. Use a MAC.
WPA2-Personal: PMK = PBKDF2-HMAC-SHA1(passphrase, SSID, 4096 iterations, 256 bits)
  test vector (passphrase 'password', SSID 'IEEE'): f42c6fc52df0ebef...
check: OK (matches the published 802.11i test vector prefix)
Protocol  Cipher / integrity        Key setup                       Status
WEP       RC4 + CRC-32              shared static key               broken, do not use
WPA       RC4 + TKIP (MIC)          PSK or 802.1X, interim fix      deprecated
WPA2      AES-CCMP                  4-way handshake, PSK/802.1X     widely deployed; PSK exposed to offline guessing
WPA3      AES (CCMP/GCMP)           SAE replaces PSK handshake,     current; protected management frames required
                                    resists offline dictionary attack
```

### SECTION 6: BANDS AND CHANNELS
2.4 GHz channel n has centre frequency 2407 + 5n MHz (channel 1 = 2412, 6 = 2437, 11 = 2462). Channels are 5 MHz apart but each signal is about 20-22 MHz wide, so only channels at least 5 apart (1, 6, 11) avoid overlapping. The standards table lists peak theoretical PHY rates only.

```text
===== SECTION 6: BANDS AND CHANNELS =====
2.4 GHz channel centres (MHz) = 2407 + 5*n: {1: 2412, 6: 2437, 11: 2462, 13: 2472}
Channels are 5 MHz apart but ~20-22 MHz wide, so only channels >= 5 apart avoid overlap: [1, 6, 11]
In the US the usual non-overlapping set is 1, 6, 11 (channels 12-13 are restricted or unused there; other regions allow up to 13).
Std       Year  Band(s)          Max theoretical PHY rate
802.11b   1999  2.4              11 Mb/s   (peak PHY, real throughput is far lower)
802.11a   1999  5                54 Mb/s   (peak PHY, real throughput is far lower)
802.11g   2003  2.4              54 Mb/s   (peak PHY, real throughput is far lower)
802.11n   2009  2.4 + 5          600 Mb/s   (peak PHY, real throughput is far lower)
802.11ac  2013  5                ~6.9 Gb/s   (peak PHY, real throughput is far lower)
802.11ax  2021  2.4+5(+6)        ~9.6 Gb/s   (peak PHY, real throughput is far lower)
2.4 GHz: longer range, better wall penetration, crowded (Bluetooth, microwaves). 5 GHz: more channels, shorter range.
```

### SECTION 7: BLUETOOTH AND ZIGBEE OVERVIEW
1,000,000 microseconds divided by 1600 hops per second is 625 microseconds per slot. The rest is a compact reference table in words: piconet (master plus up to 7 active slaves), scatternet, BLE, Zigbee.

```text
===== SECTION 7: BLUETOOTH AND ZIGBEE OVERVIEW =====
Bluetooth Classic: 2.4 GHz, frequency hopping over 79 x 1 MHz channels, 1600 hops/s -> time slot = 625 us
check: OK (625 us slots)
Piconet: 1 master + up to 7 active slaves; several piconets form a scatternet. Master polls; slaves talk when polled.
Bluetooth Low Energy: 40 channels x 2 MHz (3 advertising), built for coin-cell sensors.
Zigbee (IEEE 802.15.4): 2.4 GHz band, 16 channels (11-26), 250 kb/s, low power, mesh routing; used for sensors/home automation.
Range classes (typical order): Bluetooth ~10 m, Zigbee ~10-100 m per hop, Wi-Fi ~tens of metres indoors.
```

## Worked Example
**Q1.** Compute the free-space path loss at 20 m for channel 6 (2437 MHz) and channel 36 (5180 MHz). How many dB worse is 5 GHz?

- 20 log10(0.020 km) = 20 x (-1.699) = -33.98 dB
- 2.4 GHz: 20 log10(2437) = 20 x 3.387 = 67.74 dB, so FSPL = -33.98 + 67.74 + 32.44 = 66.2 dB
- 5 GHz: 20 log10(5180) = 20 x 3.714 = 74.29 dB, so FSPL = -33.98 + 74.29 + 32.44 = 72.7 dB
- Difference = 6.5 dB (= 20 log10(5180/2437)). The code printed 66.2, 72.7 and 6.5.

**Q2.** What is the first Frame Control byte of an ACK? Type = control = 1 (binary 01), subtype = 13 (binary 1101), version 0. Bits (subtype, type, version) = `1101 01 00` = 0xD4, which the code asserts.

## Key Rules / Gotchas Recap
- Wireless cannot detect collisions, so it avoids them (CA) and confirms delivery with an ACK; no ACK means retry with a doubled window.
- SIFS < DIFS: the ACK goes out before any new contender may start.
- Hidden terminal: cannot hear each other, collide at the receiver. Fix: RTS/CTS and NAV. Exposed terminal: defers needlessly; RTS/CTS does not fix it.
- BSS = one AP + its stations; ESS = several BSSs with the same SSID and a wired backbone.
- WEP is broken (24-bit IV, RC4 key use, CRC-32 integrity). Use WPA2-AES at minimum, WPA3 where supported. WPA2-Personal can be attacked offline if the passphrase is weak.
- Non-overlapping 2.4 GHz channels: 1, 6, 11 (US). Do not use channels 2-5 or 7-10 in a dense deployment.
- Peak PHY rates are ceilings, not throughput.

## Why This Matters
Wi-Fi is the last hop for almost every user and many IoT devices, so slow or flaky "network" complaints are often airtime, channel overlap or security settings. AI edge deployments (cameras, sensors, robots) depend on understanding retries, roaming and band choice. Knowing what is broken about WEP and what WPA3 changes is basic wireless-security literacy.
