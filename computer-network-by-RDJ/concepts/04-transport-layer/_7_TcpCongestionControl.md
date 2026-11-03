# `_7_TcpCongestionControl.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Congestion control stops senders from collectively overloading the network. TCP has no help from the network: each sender keeps a congestion window (`cwnd`), probes upward gently until packets are lost, takes loss as a sign of congestion, and cuts its window; the result is the familiar sawtooth. This is separate from flow control, which protects the receiver.

**Why it exists.** In the 1980s the Internet suffered congestion collapse: senders kept retransmitting lost packets, which made congestion worse, and useful throughput dropped to almost nothing. Van Jacobson's 1988 algorithms (slow start, congestion avoidance, fast retransmit, fast recovery) fixed that, and they are specified in RFC 5681.

**The variables.** `cwnd` is the sender's estimate of how much data the network can carry in flight; `ssthresh` is the slow-start threshold. The sender may have at most `min(cwnd, rwnd)` unacknowledged bytes. Both `cwnd` and `ssthresh` are kept in bytes, but textbooks count them in MSS units.

**Phases**
1. **Slow start** (`cwnd < ssthresh`): start at 1 MSS (modern stacks start at about 10). Each ACK adds 1 MSS, so `cwnd` doubles every RTT. It is "slow" only compared with sending a full window at once. It ends when `cwnd` reaches `ssthresh`, or on loss.
2. **Congestion avoidance** (`cwnd >= ssthresh`): grow by about 1 MSS per RTT (`+ MSS x MSS / cwnd` per ACK). This is the *additive increase* of **AIMD**.
3. **Loss reaction** (*multiplicative decrease*):
   - Timeout: `ssthresh = max(cwnd/2, 2 MSS)`, `cwnd = 1 MSS`, back into slow start. Severe.
   - 3 duplicate ACKs: `ssthresh = max(cwnd/2, 2 MSS)`; fast retransmit the missing segment. What `cwnd` becomes depends on the variant.

**Tahoe vs Reno vs NewReno**

| Variant | On 3 dup ACKs | On timeout | Notes |
|---|---|---|---|
| Tahoe | Fast retransmit, then `cwnd = 1`, slow start | `cwnd = 1` | No fast recovery. Oldest of the three. |
| Reno | Fast retransmit, then **fast recovery**: `cwnd = ssthresh (+3 during recovery)`, continue in congestion avoidance | `cwnd = 1` | Duplicate ACKs prove packets are still getting through, so no need to collapse. Weak when several segments are lost from one window. |
| NewReno | Like Reno, but stays in fast recovery until every segment lost from that window is acknowledged (partial ACKs trigger the next retransmission) | `cwnd = 1` | Repairs multiple losses in a window without timing out. |

Fast recovery in detail (Reno): after the third dup ACK, `ssthresh = cwnd/2`, `cwnd = ssthresh + 3` (the three dup ACKs mean three segments left the network); each further dup ACK adds 1 (another segment left); when the ACK for new data arrives, `cwnd = ssthresh` and congestion avoidance continues. SACK-based recovery (RFC 6675) repairs several holes per RTT. Modern Linux uses CUBIC by default, a different growth curve, and Google's BBR estimates bandwidth and delay instead of using loss; both are beyond this file.

**Throughput.**
- Basic: `throughput = window / RTT`.
- Sawtooth: if loss occurs at window `W`, AIMD oscillates between `W/2` and `W`; the average window is `3/4 W`, so average throughput is about `0.75 x W x MSS / RTT`. If `W` equals the bandwidth-delay product, link utilisation is about 75%.
- Mathis et al. approximation for Reno-like TCP with random loss rate `p`: `throughput ~ (1.22 x MSS) / (RTT x sqrt(p))`. Lower RTT or lower loss gives more throughput.

**Fairness.** Chiu and Jain showed that AIMD makes competing flows converge toward equal shares: additive increase adds the same amount to each flow (the gap stays), multiplicative decrease halves each flow (the gap halves). Over repeated cycles the gap shrinks to nothing. Additive decrease (AIAD) and multiplicative increase do not converge. Caveat: flows with shorter RTT increase faster, so AIMD is fair only for similar RTTs, and parallel connections or UDP traffic can take more than a fair share.

**Typical exam questions:** trace cwnd for N RTTs given ssthresh and a loss at a given round (for Tahoe and Reno); what are ssthresh and cwnd after a timeout vs 3 dup ACKs; why does cwnd double each RTT in slow start; compute the average throughput of a sawtooth; why AIMD converges to fairness; difference between flow and congestion control.

## Full Line-by-Line Breakdown

### SECTION 1: THE RULES (cwnd IN UNITS OF MSS, ONE STEP = ONE RTT)
Prints the rules above in compact form, then builds the first slow-start steps by hand with `min(cwnd * 2, ssthresh)` and asserts the textbook sequence 1, 2, 4, 8, 16. The `min` is the detail that matters: slow start must not overshoot `ssthresh`.

Output from a real run:

```text
===== SECTION 1: THE RULES (cwnd IN UNITS OF MSS, ONE STEP = ONE RTT) =====
cwnd       congestion window: how much the sender may have in flight (limit = min(cwnd, rwnd))
ssthresh   slow-start threshold: where growth switches from exponential to linear
slow start          cwnd < ssthresh : +1 MSS per ACK  => cwnd DOUBLES every RTT
congestion avoidance cwnd >= ssthresh: +1/cwnd per ACK => cwnd grows by ~1 MSS per RTT (additive increase)
loss by 3 dup ACKs  (mild: network still delivering)  ssthresh = max(cwnd/2, 2)
loss by timeout     (severe: nothing getting through) ssthresh = max(cwnd/2, 2), cwnd = 1
Tahoe : any loss -> cwnd = 1, slow start again
Reno  : 3 dup ACKs -> fast retransmit + fast recovery: cwnd = ssthresh, stay in congestion avoidance
        timeout    -> cwnd = 1 (same as Tahoe)
NewReno: Reno, but stays in fast recovery until ALL segments lost from that window are repaired
AIMD  : Additive Increase (+1 MSS/RTT), Multiplicative Decrease (x 1/2 on loss)
slow start by hand (initial cwnd 1, ssthresh 16): 1 -> 2 -> 4 -> 8 -> 16 (then +1 per RTT)
check: 1, 2, 4, 8, 16 doubles each RTT: OK
```

### SECTION 2: SIMULATION: ONE TRIPLE-DUPLICATE-ACK LOSS
`simulate(variant, rounds, events)` returns `(cwnd, ssthresh, phase)` per RTT. Slow start doubles (capped at `ssthresh`), congestion avoidance adds 1, and a loss event at the end of round `r` applies the variant's rule. This is a per-RTT model, a simplification of packet-level TCP, and it says so. The table follows three variants side by side with `ssthresh` starting at 16. Slow start gives 1, 2, 4, 8, 16, then +1 per round until the loss at the end of round 9 when `cwnd` = 20. Then `ssthresh = 10`. Tahoe falls to 1 and re-climbs through slow start (1, 2, 4, 8) until it hits 10 at round 14; Reno and NewReno continue from 10. At round 20 Reno has 20 while Tahoe has 16. The assert pins down these values.

Output from a real run:

```text
===== SECTION 2: SIMULATION: ONE TRIPLE-DUPLICATE-ACK LOSS =====
initial ssthresh = 16; a triple-duplicate-ACK loss is detected at the end of round 9
rnd | Tahoe ssth |  Reno ssth | NewReno ssth | phase (Reno)
  1 |     1   16 |     1   16 |       1   16 | slow start
  2 |     2   16 |     2   16 |       2   16 | slow start
  3 |     4   16 |     4   16 |       4   16 | slow start
  4 |     8   16 |     8   16 |       8   16 | slow start
  5 |    16   16 |    16   16 |      16   16 | cong. avoid
  6 |    17   16 |    17   16 |      17   16 | cong. avoid
  7 |    18   16 |    18   16 |      18   16 | cong. avoid
  8 |    19   16 |    19   16 |      19   16 | cong. avoid
  9 |    20   16 |    20   16 |      20   16 | cong. avoid  <-- loss detected
 10 |     1   10 |    10   10 |      10   10 | cong. avoid
 11 |     2   10 |    11   10 |      11   10 | cong. avoid
 12 |     4   10 |    12   10 |      12   10 | cong. avoid
 13 |     8   10 |    13   10 |      13   10 | cong. avoid
 14 |    10   10 |    14   10 |      14   10 | cong. avoid
 15 |    11   10 |    15   10 |      15   10 | cong. avoid
 16 |    12   10 |    16   10 |      16   10 | cong. avoid
 17 |    13   10 |    17   10 |      17   10 | cong. avoid
 18 |    14   10 |    18   10 |      18   10 | cong. avoid
 19 |    15   10 |    19   10 |      19   10 | cong. avoid
 20 |    16   10 |    20   10 |      20   10 | cong. avoid
check: at loss cwnd was 20 -> ssthresh = 10. Tahoe restarts at 1; Reno/NewReno continue at 10: OK
Reno gets back to the pre-loss rate far sooner: that is the point of fast recovery.
(real Reno briefly inflates cwnd to ssthresh+3 during recovery and deflates afterwards;
 the per-RTT table shows the value after recovery.)
```

### SECTION 3: TIMEOUT, AND TWO LOSSES IN ONE WINDOW
A timeout makes all three variants behave identically (cwnd to 1). Then two segments are lost from one window of 20. Tahoe collapses to 1. Reno, in the best case, leaves recovery at the first partial ACK and is hit again, so `cwnd` falls to 5 (and often it would stall into a timeout, which the model does not show). NewReno stays in recovery, repairing one hole per RTT (two rounds held at 10), and halves only once. The code labels this as a simplified model of well-known behaviour, not a measurement.

Output from a real run:

```text
===== SECTION 3: TIMEOUT, AND TWO LOSSES IN ONE WINDOW =====
timeout at the end of round 9: cwnd path of all variants identical: True
  cwnd rounds 8..14: [19, 20, 1, 2, 4, 8, 10] (restart at 1 with ssthresh 10)

two segments lost from the SAME window (cwnd 20), 3 dup ACKs received, rounds 9..16:
  tahoe    cwnd: [20, 1, 2, 4, 8, 10, 11, 12]
  reno     cwnd: [20, 5, 6, 7, 8, 9, 10, 11]
  newreno  cwnd: [20, 10, 10, 11, 12, 13, 14, 15]
  Tahoe  : collapses to 1 either way.
  Reno   : leaves recovery after the first partial ACK; best case it halves again (20 -> 5),
           and often has to wait for a timeout instead (model shows the best case).
  NewReno: partial ACKs keep it in recovery; it repairs one hole per RTT and halves ONCE (20 -> 10).
  (a simplified model of well-known behaviour; real stacks also use SACK to repair faster)
```

### SECTION 4: ASCII PLOT OF cwnd (one # = 1 MSS)
The same two runs drawn as bars, one row per RTT: Tahoe on the left, Reno/NewReno on the right. The sawtooth shape is easy to see: both grow, drop at round 10, and climb linearly; Tahoe's drop goes to the floor, Reno's only to half.

Output from a real run:

```text
===== SECTION 4: ASCII PLOT OF cwnd (one # = 1 MSS) =====
rnd  Tahoe                      Reno / NewReno
  1  #                        |#
  2  ##                       |##
  3  ####                     |####
  4  ########                 |########
  5  ################         |################
  6  #################        |#################
  7  ##################       |##################
  8  ###################      |###################
  9  ####################     |####################
 10  #                        |##########
 11  ##                       |###########
 12  ####                     |############
 13  ########                 |#############
 14  ##########               |##############
 15  ###########              |###############
 16  ############             |################
 17  #############            |#################
 18  ##############           |##################
 19  ###############          |###################
 20  ################         |####################
Tahoe's sawtooth drops to the floor; Reno's drops by half. Both climb linearly (AIMD).
```

### SECTION 5: THROUGHPUT FORMULAS
Computes `window x MSS x 8 / RTT` for a few windows (1460-byte MSS, 100 ms RTT: 10 MSS is 1.168 Mbit/s, 100 MSS is 11.680 Mbit/s). It then works the exam example: a 10 Mbit/s link with a 100 ms RTT has a bandwidth-delay product of 10,000,000 x 0.1 / 8 = 125,000 bytes (83.3 MSS of 1500 bytes); a sawtooth that peaks at that window averages 75% of the link: 7.50 Mbit/s. A sawtooth between 40 and 80 is simulated 50 times and the mean is exactly 60, i.e. `0.75 W`. Finally the Mathis formula is evaluated for p = 0.0001: about 14.2 Mbit/s. That is an approximation for Reno-like behaviour, labelled as such.

Output from a real run:

```text
===== SECTION 5: THROUGHPUT FORMULAS =====
window/RTT rule:     throughput = window / RTT (bytes per second)
  cwnd  10 MSS, RTT 100 ms:   1.168 Mbit/s
  cwnd  44 MSS, RTT 100 ms:   5.139 Mbit/s
  cwnd 100 MSS, RTT 100 ms:  11.680 Mbit/s
AIMD sawtooth: cwnd oscillates between W/2 and W, so average window = 3/4 W,
  average throughput ~ 0.75 x W x MSS / RTT.
example: link 10 Mbit/s, RTT 100 ms, MSS 1500: BDP = 125000 bytes = 83.3 MSS
  if loss happens when cwnd reaches the BDP: average = 0.75 x 10 = 7.50 Mbit/s
sawtooth check: W = 80, simulated mean cwnd = 60.00 vs 0.75 W = 60.00
check: mean of a W/2..W sawtooth is about 3/4 W: OK
Mathis formula: throughput ~ 1.22 x MSS / (RTT x sqrt(p)); MSS 1460, RTT 100 ms, loss p = 0.0001:
  = 1,781,200 bytes/s = 14.2 Mbit/s   (an approximation for Reno-like AIMD)
  consequences: halve the RTT -> double the rate; quadruple the loss -> halve the rate.
Linux today uses CUBIC by default; BBR is a different, model-based approach (not simulated).
```

### SECTION 6: WHY AIMD IS FAIR (TWO FLOWS, ONE LINK)
Two flows share a link of capacity 100. Both add 1 each RTT while the sum fits; when it exceeds capacity both react. With AIMD they halve, so a starting gap of 60 (70 vs 10) shrinks by half at every loss and ends at 0.0. With AIAD (subtract 1) the gap stays at 60 forever. The asserts check both. The caveat prints the RTT-fairness limitation.

Output from a real run:

```text
===== SECTION 6: WHY AIMD IS FAIR (TWO FLOWS, ONE LINK) =====
AIAD: start (70, 10), gap 60 -> after 400 RTTs: (80.0, 20.0), gap 60.0
AIMD: start (70, 10), gap 60 -> after 400 RTTs: (49.0, 49.0), gap 0.0
check: AIMD closes the gap (each halving halves it, each increase leaves it unchanged);
       AIAD keeps the gap forever: OK
Caveat: AIMD is fair only between flows with SIMILAR RTTs; short-RTT flows grow faster.
```

## Worked Example
**Problem.** A TCP Reno connection starts with `cwnd = 1 MSS` and `ssthresh = 8 MSS`. Show `cwnd` at the start of each RTT for rounds 1 to 12, given that three duplicate ACKs are received at the end of round 7. Then repeat for Tahoe.

**Solution (Reno).**
1. Slow start: round 1: 1; round 2: 2; round 3: 4; round 4: 8 (reached `ssthresh`).
2. Congestion avoidance: round 5: 9; round 6: 10; round 7: 11.
3. Loss at end of round 7 with `cwnd = 11`: `ssthresh = floor(11/2) = 5`; fast recovery sets `cwnd = 5`.
4. Round 8: 5; round 9: 6; round 10: 7; round 11: 8; round 12: 9.

**Solution (Tahoe).** Same through round 7, then `ssthresh = 5` and `cwnd = 1`: round 8: 1; round 9: 2; round 10: 4; round 11: 5 (capped at `ssthresh`); round 12: 6.

If instead a **timeout** occurred at the end of round 7, Reno would also restart at 1 like Tahoe. The simulator in Section 2 reproduces this exact style of trace for ssthresh 16, and Section 3 shows the timeout case.

## Key Rules / Gotchas Recap
- Slow start doubles `cwnd` each RTT but is capped at `ssthresh`; congestion avoidance adds 1 MSS per RTT.
- On loss: `ssthresh = cwnd / 2` (minimum 2 MSS).
- Timeout: `cwnd = 1` in all variants. 3 dup ACKs: Tahoe `cwnd = 1`; Reno and NewReno `cwnd = ssthresh`.
- Dup ACKs mean the network is still working, so the reaction is milder than for a timeout.
- Limit is `min(cwnd, rwnd)`.
- Sawtooth average = `3/4 W`.
- AIMD converges to fairness; AIAD does not.
- Exam trap: ssthresh uses the `cwnd` at the time of loss, not the old ssthresh.
- The per-RTT table is a simplification; real TCP changes `cwnd` per ACK.

## Why This Matters
Throughput over long, lossy paths (cross-region data transfers, model-weight downloads, replication) is governed by exactly these equations, which is why a small loss rate on a high-RTT link cuts throughput so sharply. Understanding `cwnd` also explains why a fresh connection is slow at first and why connection reuse and larger initial windows matter for latency.
