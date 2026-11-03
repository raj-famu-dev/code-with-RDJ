# `_8_Multiplexing.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Multiplexing combines several signals so they share one link, and demultiplexing separates them at the far end. It exists because a high-capacity cable or fibre is costly, so one link is divided among many users, either by frequency (FDM), by time (TDM) or by light colour (WDM).

**Frequency-division multiplexing (FDM).** The link bandwidth is divided into non-overlapping frequency bands; each source modulates its own carrier and all are sent simultaneously. *Guard bands* separate channels to prevent interference. Minimum bandwidth for n channels of width W with guard G: `n*W + (n-1)*G`. Example: 5 channels of 100 kHz with 10 kHz guards need 540 kHz. Used in radio/TV broadcasting, analog telephone trunks (12 voice channels of 4 kHz form a 48 kHz "group") and cable TV. Problems: crosstalk and intermodulation, and bandwidth wasted when a channel is idle.

**Time-division multiplexing (TDM).** The link is shared in time: each source gets a repeating time slot. Digital technique. Two kinds:
- *Synchronous TDM:* slot k is permanently assigned to source k, in every frame, used or not. A *frame* is one round of slots (one slot from each source). No addresses are needed because the position identifies the source. Idle slots are wasted. Output rate = n x input rate (plus framing bits). Frame rate equals the data rate per source in units. Synchronisation is kept with framing bits. Variations: multilevel, multiple-slot allocation, pulse stuffing for unequal input rates. Slot size may be 1 bit (bit interleaving) or a byte/character (character interleaving).
- *Statistical (asynchronous) TDM:* slots are given only to sources that have data, so the link can be smaller than the sum of the inputs. Because position no longer identifies the source, every slot carries an *address* plus data, and a buffer queues bursts. Better utilisation; costs address overhead, buffering delay and possible loss if overloaded.

**Wavelength-division multiplexing (WDM).** FDM for optical fibre: each signal uses a different light wavelength; a prism or grating combines them and splits them at the far end. *CWDM* uses wide 20 nm spacing (cheap), *DWDM* packs many channels on a 50 or 100 GHz grid (many tens of channels, long haul). Multiplies a fibre's capacity without laying new cable: `total = channels x rate per channel`.

**Spread spectrum.** Instead of saving bandwidth, deliberately spread the signal over a much wider band than needed. Benefits: resistance to jamming, interference and eavesdropping, and allowing several users to share the band (code-division). Two main methods:
- *FHSS (frequency hopping):* the carrier hops between many channels in a pseudo-random pattern known to both ends (classic Bluetooth: 79 one-megahertz channels).
- *DSSS (direct sequence):* each data bit is replaced by a longer chip sequence (802.11 originally used an 11-chip Barker code); the receiver correlates against the same code and so tolerates many corrupted chips. Bandwidth grows by the spreading factor.

**Comparison table.**

| | FDM | Sync TDM | Statistical TDM | WDM |
|---|-----|----------|-----------------|-----|
| Shares | frequency | time slots (fixed) | time slots (on demand) | wavelength |
| Signal | analog | digital | digital | optical |
| Address needed | no | no | yes | no |
| Idle capacity | wasted | wasted | reused | wasted |
| Needs guard | guard bands | framing bits | buffers | channel spacing |

**Typical exam questions.** Compute FDM total bandwidth; synchronous TDM frame size, frame rate, output rate and bit/slot duration; efficiency of synchronous vs statistical; T1 rate; define guard bands; FHSS vs DSSS.

## Full Line-by-Line Breakdown

### SECTION 1: FDM CHANNEL PLAN
`fdm_plan()` lays out channels from a start frequency, adding a guard band after each. The assert checks that no channel touches the next and that the total equals `5 x 100 + 4 x 10 = 540` kHz. The telephone group example gives 12 channels x 4 kHz = 48 kHz from 60 to 108 kHz. The trap forgets the guard bands.

```text
===== SECTION 1: FDM CHANNEL PLAN =====
  channel 1:      0 -    100 kHz
  channel 2:    110 -    210 kHz
  channel 3:    220 -    320 kHz
  channel 4:    330 -    430 kHz
  channel 5:    440 -    540 kHz
minimum link bandwidth = 5 x 100 + 4 guard bands x 10 = 540 kHz
12 voice channels of 4 kHz (a telephone 'group'): 60-108 kHz = 48 kHz
FDM is ANALOG-style: signals share the medium at the SAME time, each on its own frequency band (carriers modulated).
Trap: forgetting the 4 guard bands gives 500 kHz, but 540 kHz are needed.
```

### SECTION 2: SYNCHRONOUS TDM SIMULATOR
First the numbers for four 1 Mbps sources with one bit per slot: the frame is 4 bits, 1,000,000 frames per second, a frame lasts 1 microsecond, a slot 0.25 microsecond and the output is 4 Mbps. Then the simulator: each source has a fixed script of units to send (`.` = nothing). In every tick, slot A, B, C or D is filled by its own source or left empty (`--`). Only 15 of 32 slots carry data (47% utilisation), the cost of synchronous reservation.

```text
===== SECTION 2: SYNCHRONOUS TDM SIMULATOR =====
Four 1 Mbps sources, one bit per slot:
  frame = 4 slots x 1 bit = 4 bits; frame rate = 1,000,000/s
  frame duration = 1.00 us; slot duration = 0.25 us; output rate = 4 Mbps
  output rate = n x input rate (no framing bits); adding 1 framing bit makes each frame 5 bits -> 5 Mbps.

tick | slot A slot B slot C slot D
   0 | A1      --      C1      --
   1 | A2      B1      C2      --
   2 | --      --      C3      --
   3 | A3      --      C4      D1
   4 | --      --      C5      --
   5 | --      B2      C6      --
   6 | A4      --      C7      --
   7 | --      --      C8      --
slots sent = 32, slots carrying data = 15, EMPTY = 17 -> utilisation 47%
Synchronous TDM reserves slot k for source k in EVERY frame, so idle sources waste capacity.
```

### SECTION 3: STATISTICAL TDM
The same traffic is sent over a link carrying only 2 slots per frame. New arrivals join a FIFO queue and up to 2 units leave per frame, each tagged with a source address `[A|A1]`. All 15 units are delivered in 8 frames (the last one half empty). Counting address bits, the statistical link sends 160 bits against 256 for synchronous: a smaller link carrying the same data, paid for with the address bits and queueing.

```text
===== SECTION 3: STATISTICAL TDM =====
frame  0: [A|A1] [C|C1]
frame  1: [A|A2] [B|B1]
frame  2: [C|C2] [C|C3]
frame  3: [A|A3] [C|C4]
frame  4: [D|D1] [C|C5]
frame  5: [B|B2] [C|C6]
frame  6: [A|A4] [C|C7]
frame  7: [C|C8]
data units delivered: sync=15, statistical=15
synchronous : 32 slots x 8 bits = 256 bits sent (no address needed)
statistical : 16 slots x (8+2 address) = 160 bits sent (address needed: slots are not owned)
Statistical TDM carried the same 15 units on a link HALF as wide (2 slots per frame instead of 4),
drained in 8 frames; the price is 2 address bits per slot and queueing (peak backlog after each frame = 1 unit(s) waiting).
check: OK
```

### SECTION 4: WDM
8 wavelengths at 10 Gbps give 80 Gbps on a single fibre. The width of a 100 GHz slot around 1550 nm is computed from `delta_lambda = lambda^2 x delta_f / c`, about 0.8 nm, the figure behind DWDM grids.

```text
===== SECTION 4: WDM =====
8 wavelengths x 10 Gbps = 80 Gbps on ONE fibre
A 100 GHz DWDM grid slot near 1550 nm is about 0.80 nm wide (delta-lambda = lambda^2 x delta-f / c)
CWDM spaces channels far apart (20 nm), cheap lasers; DWDM packs 50-100 GHz slots, 40-96+ channels, costlier.
WDM = FDM idea applied to LIGHT: a prism/grating combines on transmit and splits on receive.
```

### SECTION 5: SPREAD SPECTRUM
DSSS: each bit (+1 or -1) is multiplied by the 11-chip Barker sequence, so 5 bits become 55 chips. 12 of the 55 chips are flipped at random (seeded) and correlation (multiply by the code and add) still recovers all five bits because the sum is dominated by the correct chips. FHSS: two parties with the same seed generate the same channel sequence; a party with the wrong seed matches none. The PRNG here is only a demonstration of the idea; real systems define their own hopping kernels.

```text
===== SECTION 5: SPREAD SPECTRUM =====
data bits       : [1, 0, 1, 1, 0]
chips (first 22): [1, -1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, -1, 1, 1, 1]  (55 chips total = 5 bits x 11)
after flipping 12 of 55 chips: recovered bits = [1, 0, 1, 1, 0]
Spreading lowers the power per hertz and lets correlation vote the data out of burst noise/jamming (processing gain).
Bandwidth grows by the spreading factor 11; that is the cost.
FHSS transmitter channels : [60, 23, 74, 38, 25, 52, 33, 68, 31, 63]
receiver with same seed   : match on 10/10 hops
receiver with wrong seed  : match on 0/10 hops (it listens on the wrong channel)
Bluetooth (classic) hops over 79 channels of 1 MHz; the seed idea is real, this PRNG is only a demonstration.
check: OK
```

### SECTION 6: WORKED EXAMPLE (T1)
The standard T1 line: 24 voice channels x 8 bits + 1 framing bit = 193 bits per frame, 8000 frames per second.

```text
===== SECTION 6: WORKED EXAMPLE (T1) =====
T1 frame = 24 x 8 + 1 framing = 193 bits; 8,000 frames/s
line rate = 193 x 8,000 = 1,544,000 bps = 1.544 Mbps; payload = 1,536,000 bps
each voice channel = 64,000 bps = 64 kbps; framing overhead = 8,000 bps (0.52%)
check: OK
```

## Worked Example
**Problem.** A T1 carrier multiplexes 24 voice channels, 8 bits per sample, 1 framing bit per frame, 8000 frames per second. Find the line rate and the framing overhead.

1. Frame = 24 x 8 + 1 = 193 bits.
2. Line rate = 193 x 8000 = 1,544,000 bps = 1.544 Mbps.
3. Each channel gets 8 x 8000 = 64 kbps.
4. Framing overhead = 1 x 8000 = 8 kbps = 1/193 = 0.52%.

The code prints exactly these values.

## Key Rules / Gotchas Recap
- FDM total bandwidth includes the (n-1) guard bands.
- Synchronous TDM output rate = n x input rate (plus framing); the frame rate equals each source's unit rate.
- Synchronous TDM wastes idle slots; statistical TDM does not but adds addresses and queueing.
- No address field is needed in synchronous TDM because the slot position identifies the source.
- WDM is FDM for light; capacity = channels x rate each.
- Spread spectrum trades bandwidth for robustness; the spreading factor is the bandwidth multiplier.
- DSSS needs the same code at the receiver; FHSS needs the same hop sequence and timing.

## Why This Matters
Multiplexing underlies telephone trunks, DSL, cable broadband, Wi-Fi/Bluetooth coexistence and the fibre links that connect data centres. The sync-vs-statistical trade-off is the same one as reserved vs shared capacity in cloud networking and GPU clusters.
