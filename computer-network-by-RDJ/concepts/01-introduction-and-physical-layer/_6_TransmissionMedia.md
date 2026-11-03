# `_6_TransmissionMedia.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Transmission media are the physical paths that carry signals between devices: *guided* media (a cable that channels the signal) and *unguided* media (the signal travels through air or space). The medium sets the achievable bandwidth, the distance before the signal must be regenerated, the cost and how exposed the signal is to noise and eavesdropping. It belongs to the Physical layer (layer 1).

**Guided media.**

*Twisted pair.* Two insulated copper wires twisted together; the twist makes interference hit both wires almost equally so a differential receiver cancels it. UTP (unshielded) is cheap and common; STP adds a foil or braid shield for noisy places. Connector: RJ45 (8P8C). Ethernet runs 100 m per segment.

| Category | Typical use / rated speed |
|----------|---------------------------|
| Cat 3 | 10 Mbps Ethernet, telephones |
| Cat 5 | 100 Mbps |
| Cat 5e | 1 Gbps |
| Cat 6 | 1 Gbps; 10 Gbps over short runs (about 55 m) |
| Cat 6a | 10 Gbps up to 100 m |

*Coaxial cable.* A centre copper conductor, insulation, a braided shield and an outer jacket. Better shielding and bandwidth than twisted pair, so it lasted in cable TV and early Ethernet (10BASE5 thick, 10BASE2 thin). Bulkier and harder to install than UTP; connectors BNC/F-type.

*Optical fibre.* A glass (or plastic) core inside cladding of lower refractive index; light stays in the core by total internal reflection. *Multimode* fibre has a wide core (50 or 62.5 micrometres) so light takes many paths, causing modal dispersion and limiting distance to hundreds of metres or a few km. *Single-mode* fibre has a core of about 9 micrometres, one path, very low loss and reaches tens of km or more but needs laser sources. Advantages: huge bandwidth, low attenuation, immune to electromagnetic interference, hard to tap, light weight. Disadvantages: cost, fragile, specialised installation and splicing, unidirectional per strand (two strands needed for duplex).

**Unguided media (wireless).** Signals radiate through the air using the electromagnetic spectrum. Textbooks give approximate bands: *radio waves* about 3 kHz to 1 GHz (omnidirectional, pass through walls; AM/FM radio); *microwaves* about 1 to 300 GHz (unidirectional, line of sight, towers, satellite links, Wi-Fi at 2.4 and 5 GHz, cellular); *infrared* about 300 GHz to 400 THz (short range, blocked by walls, TV remotes). Wavelength = c / f, so higher frequencies have shorter wavelengths and more directional behaviour. Wireless gives mobility but the medium is shared and can be intercepted, so encryption matters. Unlicensed ISM bands such as 2.4 GHz are crowded.

**Impairments.**
- *Attenuation:* signal power falls with distance, measured in decibels `dB = 10 log10(P_out / P_in)`. Losses in dB add; a halving of power is about -3 dB. Fixed with amplifiers (analog) or repeaters (digital).
- *Distortion:* different frequencies travel at different speeds, so the shape changes.
- *Noise:* thermal, induced (motors, appliances), crosstalk (one pair leaking into another), impulse noise (lightning, switching).
- *EMI (electromagnetic interference):* external electromagnetic fields inducing unwanted voltage; twisting, shielding and fibre fight it.

**Guided vs unguided.**

| Point | Guided | Unguided |
|-------|--------|----------|
| Path | physical cable | air / space |
| Security | harder to tap | easy to intercept |
| Mobility | none | yes |
| Installation | cabling cost | antennas, licences |
| Interference | EMI, crosstalk | other transmitters, weather, obstacles |

**Typical exam questions.** Compare UTP, coax and fibre; difference between single-mode and multimode; why are wires twisted; define attenuation and compute dB; advantages of fibre; name the wireless bands and uses.

## Full Line-by-Line Breakdown

### SECTION 1: GUIDED MEDIA COMPARISON
Plain tables built from tuples: UTP categories and rated speeds, then each guided medium with its material, characteristics and use. Speeds are the commonly quoted ratings for the standards named, not measurements.

```text
===== SECTION 1: GUIDED MEDIA COMPARISON =====
Twisted-pair categories (UTP; STP adds a foil/braid shield):
  Cat 3  10 Mbps                               old telephone/10BASE-T
  Cat 5  100 Mbps                              100BASE-TX
  Cat 5e 1 Gbps                                1000BASE-T, 100 m
  Cat 6  1 Gbps (10 Gbps up to about 55 m)     tighter twist, often with a spline
  Cat 6a 10 Gbps at 100 m                      10GBASE-T, usually shielded or thicker
Ethernet over twisted pair reaches 100 m per segment (90 m permanent link + patch cords).

medium             material                characteristics                                               use
UTP twisted pair   copper                  cheap, easy; EMI/crosstalk, 100 m                             LAN cabling
STP twisted pair   copper+shield           less EMI, costlier, heavier                                   noisy sites
Coaxial            copper core+shield      better shielding and bandwidth than UTP; bulky                cable TV, old 10BASE2/5
Fibre, multimode   glass, 50/62.5 um core  light takes many paths -> modal dispersion; shorter reach     buildings, campus
Fibre, single-mode glass, ~9 um core       one path, lowest loss; costly gear; longest reach             long haul, ISPs
Fibre is immune to EMI, very high bandwidth, hard to tap casually; downsides: cost, fragile, special tools to splice.
```

### SECTION 2: ATTENUATION IN DECIBELS
`db()` implements the formula; halving power gives -3.01 dB and a drop of 100 to 1 mW gives -20 dB. The link-budget lines use *illustrative* loss figures (labelled as such in the output, chosen for practice, not taken from a datasheet) and an assumed launch power and receiver sensitivity, so the lengths are only a demonstration that lower loss per km gives longer reach. The trap shows that dB values add (two halvings = -6.02 dB = quarter power).

```text
===== SECTION 2: ATTENUATION IN DECIBELS =====
P drops 100 mW -> 50 mW : -3.01 dB (half the power is about -3 dB)
P drops 100 mW -> 1 mW  : -20.00 dB
Assumed budget = 0.0 dBm launch - (-28.0 dBm) sensitivity = 28.0 dB
  illustrative copper               20.0 dB/km -> max length about    1.40 km
  illustrative multimode fibre       3.0 dB/km -> max length about    9.33 km
  illustrative single-mode fibre     0.4 dB/km -> max length about   70.00 km
Amplifiers/repeaters are placed so total loss between them stays inside the budget.
Trap: two halvings in a row = -3.01 + -3.01 = -6.02 dB (adding), i.e. power ratio 0.25. Losing 50% twice leaves 25%, not 0%.
check: OK
```

### SECTION 3: WHY TWISTING CANCELS NOISE (EMI)
Simulates differential signalling. Wire A carries +1 or -1 V for a bit and wire B carries the opposite. A seeded random "common-mode" noise value, bigger than the signal itself, is added to both wires (this is what twisting achieves: both wires see nearly the same interference). A receiver that looks at one wire misreads bit 4, while the differential receiver `(A - B) / 2` removes the noise exactly and decodes all eight bits. Real cables only approximately cancel noise.

```text
===== SECTION 3: WHY TWISTING CANCELS NOISE (EMI) =====
sent bits          : [1, 0, 1, 1, 0, 0, 1, 0]
common-mode noise  : ['+0.6', '-1.9', '-0.9', '-1.1', '+0.9', '+0.7', '+1.6', '-1.7']
single-wire decode : [1, 0, 1, 0, 0, 0, 1, 0] errors=1
differential decode: [1, 0, 1, 1, 0, 0, 1, 0] errors=0
Twisting makes both wires pick up (nearly) the same interference, so the receiver's subtraction removes it.
Unequal pickup (untwisted pairs, bad connectors) breaks the cancellation; that residual is crosstalk/EMI damage.
check: OK
```

### SECTION 4: UNGUIDED MEDIA AND WAVELENGTH
Computes wavelength from frequency with c = 299,792,458 m/s for example bands. Wi-Fi at 2.4 GHz is about 12.5 cm, 5 GHz about 6 cm. The rest of the output restates the textbook spectrum split and the guided/unguided difference.

```text
===== SECTION 4: UNGUIDED MEDIA AND WAVELENGTH =====
band                             frequency    wavelength  notes
AM radio (example)               0.001 GHz       299.8 m  radio waves, omnidirectional, follow the ground/ionosphere
FM radio (example)               0.100 GHz       2.998 m  radio waves, line of sight
Wi-Fi 2.4 GHz band               2.400 GHz      0.1249 m  ISM band, walls ok, crowded (Bluetooth, microwave ovens)
Wi-Fi 5 GHz band                 5.000 GHz     0.05996 m  shorter range, more channels
Terrestrial microwave link      10.000 GHz     0.02998 m  narrow beam, needs line of sight and towers
Infrared remote              30000.000 GHz   9.993e-06 m  short range, blocked by walls, no licence
wavelength = speed of light / frequency; higher frequency -> shorter wavelength -> more directional, less wall penetration.
Textbook spectrum: radio ~3 kHz-1 GHz, microwave ~1-300 GHz, infrared ~300 GHz-400 THz (boundaries vary by book).
Satellite: geostationary orbit is about 35,786 km up; a hop is very long (see _9_DelayAndThroughput).
Guided = signal follows a cable (needs wires, secure, cheap per bit). Unguided = through air/space (mobility, but shared, interceptable).
```

### SECTION 5: WORKED EXAMPLE
Applies the dB formula to a cable.

```text
===== SECTION 5: WORKED EXAMPLE =====
loss = 2.0 dB/km x 5 km = 10.0 dB
P_out = 10.0 mW x 10^(-10.0/10) = 1.00 mW
check: OK
```

## Worked Example
**Problem.** A 10 mW signal enters a cable that loses 2 dB per km. What power remains after 5 km?

1. Total loss = 2 dB/km x 5 km = 10 dB.
2. P_out = P_in x 10^(-loss/10) = 10 mW x 10^(-1) = 1 mW.

The code prints 1.00 mW. Quick check: 10 dB of loss is a factor of ten, 3 dB is a factor of two.

## Key Rules / Gotchas Recap
- Ethernet twisted pair: 100 m per segment, regardless of category (Cat 6 at 10 Gbps is only about 55 m).
- Twisting cancels *common-mode* noise; it does not stop all crosstalk.
- Single-mode = small core, one path, long distance; multimode = bigger core, many paths, shorter.
- Fibre is immune to EMI, but it is fragile and can still be tapped with specialised equipment; "unhackable" is a myth.
- dB are logarithmic: add losses in dB, multiply ratios.
- Higher frequency means shorter wavelength, more directional and less wall penetration.
- Wireless is shared and interceptable; assume it needs encryption.

## Why This Matters
When a link is slow or flaky the first suspects are layer 1 problems: a bad cable, too long a run, EMI, or a weak wireless signal. Data-centre and AI-cluster networks pick copper or fibre (and the distance each can reach) on exactly these trade-offs.
