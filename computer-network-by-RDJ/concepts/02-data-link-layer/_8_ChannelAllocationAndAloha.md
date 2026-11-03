# `_8_ChannelAllocationAndAloha.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
When many stations share one channel, something must decide who transmits when. Channel allocation can be static (each station gets a fixed slice) or dynamic (stations compete or take turns). ALOHA is the oldest random-access protocol: just transmit when you have data and retransmit after a random delay if there is a collision. Analysing it gives the classic throughput formulas and the famous 18.4 percent and 36.8 percent limits.

**Static allocation.** FDM (frequency slices) or TDM (time slots) gives each of N users 1/N of the capacity. It is efficient only for steady traffic. For bursty traffic, a slice sits idle while others queue; queueing theory shows the mean delay of N sub-channels is N times the delay of one shared channel with the same total capacity (T = 1/(mu*C - lambda)). So we prefer dynamic allocation.

**Dynamic allocation assumptions.** Independent stations, single channel, collisions are the only errors, time continuous or slotted, carrier sense or not.

**Pure ALOHA.** Stations send whenever they like. A frame of duration T collides if any other frame starts within one frame time before or after it: the vulnerable (vacuum) period is 2T. If the offered load is G frames per frame time (Poisson), P(no other start in 2T) = e^(-2G), so throughput S = G * e^(-2G). S is maximal at G = 0.5, S = 1/(2e) = 0.184, 18.4 percent. Beyond that, more load means more collisions and less throughput.

**Slotted ALOHA.** Time is divided into slots equal to the frame time and stations may start only at slot boundaries (synchronisation needed). The vulnerable period halves to T, so S = G * e^(-G), maximum at G = 1: S = 1/e = 0.368, 36.8 percent. Of all slots about 36.8 percent are successes, 36.8 percent are empty and 26.4 percent collide.

| | Pure ALOHA | Slotted ALOHA |
|---|---|---|
| Vulnerable period | 2T | T |
| Throughput | G e^(-2G) | G e^(-G) |
| Max throughput | 18.4 percent at G = 0.5 | 36.8 percent at G = 1 |
| Needs synchronisation | no | yes |

Carrier-sensing protocols (next file) beat these numbers because stations listen before sending.

## Full Line-by-Line Breakdown

### SECTION 1: STATIC VS DYNAMIC ALLOCATION
Using the M/M/1 delay formula, one shared 100 Mbps channel carrying 5000 frames per second of 10000 bits has mean delay 0.2 ms. Splitting the same capacity into N = 10 static slices, each with a tenth of the load, gives 2 ms, exactly N times worse. The assert checks the ratio.

Output from a real run:

```text
===== SECTION 1: STATIC VS DYNAMIC ALLOCATION =====
Mean delay of an M/M/1 queue: T = 1 / (mu*C - lambda)
C = 100 Mbps, frame = 10000 bits, total load = 5000 frames/s
one shared channel      : T = 0.200 ms
FDM/TDM split into N=10  : T = 2.000 ms  (= N x worse)
Static allocation: each user owns a fixed slice even when idle -> waste when bursty.
Dynamic allocation: stations compete (ALOHA, CSMA) or take turns (token/polling).
```

### SECTION 2: PURE ALOHA FORMULA
Pure ALOHA throughput S = G e^(-2G) printed for sample loads. The maximum is found two ways: a brute-force search over G in a fine grid (G = 0.5, S = 0.1839) and calculus (dS/dG = 0 gives G = 1/2, S = 1/(2e)). Both agree, which is the "derive by computing" the syllabus asks for.

Output from a real run:

```text
===== SECTION 2: PURE ALOHA FORMULA =====
Frame time T. A frame sent at t collides with any other started in (t-T, t+T):
vulnerable (vacuum) period = 2T. G = mean frames offered per frame time T.
P(no other start in 2T) = e^(-2G)  ->  S = G * e^(-2G)
    G   S pure
  0.1   0.0819
 0.25   0.1516
  0.5   0.1839
  1.0   0.1353
  2.0   0.0366
  3.0   0.0074
numeric search for the maximum: G = 0.5000, S = 0.1839 = 18.4%
calculus: dS/dG = e^(-2G)(1 - 2G) = 0 -> G = 1/2, S = 1/(2e) = 0.1839
```

### SECTION 3: SLOTTED ALOHA FORMULA
Slotted ALOHA S = G e^(-G): the same two ways give G = 1 and S = 1/e = 0.3679.

Output from a real run:

```text
===== SECTION 3: SLOTTED ALOHA FORMULA =====
Stations may start only at slot boundaries -> vulnerable period shrinks to T.
P(no other start in T) = e^(-G)  ->  S = G * e^(-G)
    G  S slotted
  0.1     0.0905
  0.5     0.3033
  1.0     0.3679
  2.0     0.2707
  3.0     0.1494
numeric search: G = 1.0000, S = 0.3679 = 36.8%
calculus: dS/dG = e^(-G)(1 - G) = 0 -> G = 1, S = 1/e = 0.3679
Pure max 18.4% (G = 0.5), slotted max 36.8% (G = 1): slotting doubles it.
```

### SECTION 4: EXAM EXAMPLE
Exam style: a 1 Mbps channel, 1000-bit frames, so T = 1 ms; 500 frames per second offered gives G = 0.5. Pure ALOHA delivers 0.1839 frames per frame time, 183.9 frames per second; slotted ALOHA 0.3033, 303.3 frames per second. The trap line shows that more offered load (G = 3) reduces pure-ALOHA throughput to 0.0074.

Output from a real run:

```text
===== SECTION 4: EXAM EXAMPLE =====
Channel 1 Mbps, frame 1000 bits -> T = 1.0 ms; 500 frames/s offered
G = 500 * 0.001 = 0.5
pure ALOHA   : S = 0.1839 -> 183.9 frames/s succeed
slotted ALOHA: S = 0.3033 -> 303.3 frames/s succeed
TRAP: more load is not better. G = 3 (pure): 0.0074 vs G = 0.5: 0.1839
```

### SECTION 5: MONTE-CARLO (seeded measurement, not theory)
This is a MEASUREMENT, not theory. Pure ALOHA: frame start times are drawn with exponential inter-arrival times (a Poisson process) and a frame succeeds if no neighbour starts within one frame time on either side. Slotted ALOHA: the number of arrivals in each slot is Poisson(G); the slot succeeds when exactly one station sends. The results with fixed seeds are within 0.01 of the formulas (the asserts), which supports the derivation. Different seeds would give slightly different digits.

Output from a real run:

```text
===== SECTION 5: MONTE-CARLO (seeded measurement, not theory) =====
    G  pure sim  pure theory  slot sim  slot theory
 0.25    0.1507       0.1516    0.1953       0.1947
  0.5    0.1839       0.1839    0.3019       0.3033
  1.0    0.1333       0.1353    0.3674       0.3679
  2.0    0.0370       0.0366    0.2710       0.2707
measured values (seeds 1 and 2, 100000 frames/slots) sit within 0.01 of theory: check: OK
```

## Worked Example
**Problem.** A pure ALOHA channel carries 1000-bit frames at 1 Mbps. At what offered load G is throughput maximal, and what is the maximum frame rate?

**Solution.** T = 1 ms, so the channel can carry at most 1000 frames/s. Throughput is maximal at G = 0.5 (500 frames/s offered), giving S = 0.5 * e^(-1) = 0.1839, that is about 184 successful frames per second. The program prints G = 0.5000, S = 0.1839 and, for this load, 183.9 frames/s.

## Key Rules / Gotchas Recap
- Pure ALOHA: vulnerable period 2T, S = G e^(-2G), max 18.4 percent at G = 0.5.
- Slotted ALOHA: vulnerable period T, S = G e^(-G), max 36.8 percent at G = 1.
- More offered load past the peak lowers throughput (unstable).
- Static allocation wastes capacity for bursty traffic (delay grows N times).
- Simulation results are measurements for fixed seeds, within about 0.01 of theory here.
- Slotted ALOHA needs all stations synchronised to slot boundaries.

## Why This Matters
Random access is how shared radio (Wi-Fi, cellular random-access channels, LoRa, RFID) starts; the collision-and-backoff reasoning also appears in distributed systems retry logic. Being able to derive a limit and then check it by simulation is a habit worth keeping for performance work.
