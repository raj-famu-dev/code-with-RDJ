# `_5_TcpReliabilityAndRetransmission.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
TCP builds a reliable service on top of IP, which can lose, duplicate and reorder packets. It does this with sequence numbers, cumulative acknowledgements, a retransmission timer whose length is learned from measured round-trip times, and a shortcut called fast retransmit that uses duplicate ACKs to repair loss before the timer fires.

**Acknowledgements are cumulative.** `ACK = n` means "I have received every byte below n; the next one I want is n." A single ACK can therefore cover many segments, and a lost ACK is often harmless because a later one covers it. TCP does not (by default) acknowledge individual out-of-order segments. With the SACK option (RFC 2018) the receiver can additionally list the blocks it holds.

**Two ways to detect loss**
1. **Timeout:** the sender keeps a timer for the oldest unacknowledged segment. If no ACK arrives within the retransmission timeout (RTO), it resends that segment.
2. **Duplicate ACKs:** if a segment is lost but later ones arrive, the receiver sends an ACK for the *same* missing byte each time. Three duplicate ACKs (so four identical ACKs in total) in a row make the sender retransmit the missing segment immediately: **fast retransmit** (RFC 5681). Three is chosen because one or two duplicates can be caused by simple packet reordering.

Fast retransmit is much quicker than waiting for a timeout (which is at least one RTT and usually several), but it needs enough segments in flight after the lost one. A lost segment at the end of a burst can only be recovered by timeout.

**Choosing the RTO: Jacobson/Karels (RFC 6298).** A fixed timeout is wrong: too short causes needless resends, too long makes loss recovery slow. TCP measures the round-trip time R of segments and keeps two running values:
- First sample: `SRTT = R`, `RTTVAR = R / 2`.
- Each later sample: `RTTVAR = (1 - b) x RTTVAR + b x |SRTT - R|`, then `SRTT = (1 - a) x SRTT + a x R`, with `a = 1/8`, `b = 1/4`. (Update RTTVAR first, using the old SRTT.)
- `RTO = SRTT + 4 x RTTVAR` (plus a clock-granularity term; RFC 6298 also says RTO should be at least 1 second, and the initial RTO is 1 second).

Older textbooks use only `SRTT = a x SRTT + (1 - a) x R` with `a = 0.9` and `RTO = 2 x SRTT`. That ignores variation. The deviation term is what makes the timer safe when the network is jittery.

**Karn's algorithm.** If a segment was retransmitted, an arriving ACK is ambiguous: it may answer the original or the copy, so the measured time could be wrong by a whole RTO. Rule 1: never take an RTT sample from a retransmitted segment. Rule 2: on every timeout double the RTO (**exponential backoff**) and keep the doubled value until an ACK for fresh data yields a clean sample. Backoff also protects a congested network from a flood of retries.

**Tradeoffs.** Timeout recovery is simple but slow; fast retransmit is quick but needs a stream of later packets. TCP combines both. Go-Back-N style resending the whole window wastes bandwidth; TCP resends one segment (or only the SACK holes) at a time.

**Typical exam questions:** given SRTT, RTTVAR and a new sample, compute the next RTO; explain why Karn's algorithm exists; how many duplicate ACKs trigger fast retransmit (3); what does ACK 1001 mean; why is a lost last segment recovered by timeout, not fast retransmit; why double the RTO after a timeout.

## Full Line-by-Line Breakdown

### SECTION 1: RTT ESTIMATION (JACOBSON / KARELS, RFC 6298)
`RttEstimator.sample` implements the formulas exactly. Note the order inside: `RTTVAR` is updated with the old `SRTT` first. The table feeds the samples 100, 120, 90, 300, 110, 100 ms. Row 1: SRTT 100, RTTVAR 50, RTO 100 + 4 x 50 = 300. Row 2 (R = 120): RTTVAR = 0.75 x 50 + 0.25 x |100 - 120| = 42.5; SRTT = 0.875 x 100 + 0.125 x 120 = 102.5; RTO = 102.5 + 4 x 42.5 = 272.5. Two `assert`s lock these hand answers in. The 300 ms spike then pushes RTTVAR up from 35 to 76 and RTO up to 430 ms, then it decays as normal samples return. A minimum RTO of 1 s (as in the RFC) would flatten all this to 1000 ms. Last, the old textbook EWMA gives RTO = 2 x SRTT = 235 ms, which is below the 300 ms the network actually produced: the trap that variance tracking fixes.

Output from a real run:

```text
===== SECTION 1: RTT ESTIMATION (JACOBSON / KARELS, RFC 6298) =====
formulas: RTTVAR = 3/4 RTTVAR + 1/4 |SRTT - R| ; SRTT = 7/8 SRTT + 1/8 R ; RTO = SRTT + 4 RTTVAR
first sample: SRTT = R, RTTVAR = R/2
sample R     SRTT   RTTVAR      RTO   (all milliseconds)
     100  100.000   50.000  300.000
     120  102.500   42.500  272.500
      90  100.938   35.000  240.938
     300  125.820   76.016  429.883
     110  123.843   60.967  367.710
     100  120.862   51.686  327.606
check: R=100 -> (100, 50, 300) and R=120 -> (102.5, 42.5, 272.5) match hand calculation: OK
The spike R=300 raised RTTVAR a lot, so RTO jumped (a safety margin), then decays.
RFC 6298 also says RTO should be at least 1 s: final RTO = 1000 ms vs raw 327.6 ms

older textbook formula (EWMA only, no variance), alpha = 0.9:
  SRTT after the same samples = 117.683 ms; RTO = 2 x SRTT = 235.366 ms
  trap: 2 x SRTT ignores jitter; a 300 ms spike is far above it. Jacobson/Karels fixes that.
```

### SECTION 2: KARN'S ALGORITHM AND EXPONENTIAL BACKOFF
Starting from an estimator that has seen two 100 ms samples (RTO 250 ms), the script feeds one ambiguous ACK two ways. If you assume it belongs to the first send you get RTT 400 and RTO 550; if you assume the resend you get RTT 100 and RTO 212.5. You cannot know which, so Karn says to discard the sample. The backoff loop shows the timer doubling after each timeout: 300, 600, 1200, 2400, 4800 ms.

Output from a real run:

```text
===== SECTION 2: KARN'S ALGORITHM AND EXPONENTIAL BACKOFF =====
Problem: segment sent at t=0, timeout, resent at t=300, ACK arrives at t=400.
Is that ACK for the first copy (RTT 400) or the resend (RTT 100)? Nobody can tell.
RTO before: 250.0 ms; if we guess 400: 550.0 ms; if we guess 100: 212.5 ms
Both guesses can be wrong and poison the estimator.
Karn's rule: NEVER take an RTT sample from a retransmitted segment.
Plus: after each timeout double the RTO (exponential backoff) until a fresh sample arrives.
  timeout #1: wait 300 ms, then retransmit and set RTO = 600 ms
  timeout #2: wait 600 ms, then retransmit and set RTO = 1200 ms
  timeout #3: wait 1200 ms, then retransmit and set RTO = 2400 ms
  timeout #4: wait 2400 ms, then retransmit and set RTO = 4800 ms
  timeout #5: wait 4800 ms, then retransmit and set RTO = 9600 ms
Backoff keeps TCP from hammering a congested network; it is a form of congestion control.
```

### SECTION 3: SIMULATOR WITH LOSS (FAST RETRANSMIT vs TIMEOUT)
`simulate` is a tick-based model: one-way delay 5 ticks, a fixed RTO of 40 ticks, window of `window` segments, one new segment per tick. Loss is either forced (specific `(segment, transmission)` pairs) or drawn from a seeded `random.Random`. The receiver buffers out-of-order segments and ACKs the next segment it still needs. The sender counts duplicates and fast-retransmits on the third.

Scenario A loses segment 3. Segments 4, 5, 6 each make the receiver say "ACK 3" again; those arrive at the sender as duplicates #1, #2, #3 at ticks 13, 14, 15, and the resend leaves at tick 15, long before the timer (set at tick 11) would expire at tick 51. When segment 3 finally arrives the receiver's ACK jumps to 9: one cumulative ACK covers 3 to 8. (Two further duplicates, #4 and #5, are echoes of ACKs already in flight.) Scenario B has only one segment after the gap, giving a single duplicate ACK, so nothing happens until the timeout at tick 51. Scenario C runs 60 segments with 10% random loss of data and ACKs (seed 1) and reports totals only; every segment is eventually delivered, in order, at the price of extra transmissions.

Output from a real run:

```text
===== SECTION 3: SIMULATOR WITH LOSS (FAST RETRANSMIT vs TIMEOUT) =====
scenario A: 10 segments, window 6, segment 3 lost on its first transmission
  t=0   SEND seg 1
  t=1   SEND seg 2
  t=2   SEND seg 3   <-- LOST
  t=3   SEND seg 4
  t=4   SEND seg 5
  t=5     receiver got seg 1 -> ACK 2
  t=5   SEND seg 6
  t=6     receiver got seg 2 -> ACK 3
  t=8     receiver got seg 4 -> ACK 3
  t=9     receiver got seg 5 -> ACK 3
  t=10    sender got ACK 2 (new): base -> 2
  t=10    receiver got seg 6 -> ACK 3
  t=10  SEND seg 7
  t=11    sender got ACK 3 (new): base -> 3
  t=11  SEND seg 8
  t=13    sender got ACK 3 (DUPLICATE #1)
  t=14    sender got ACK 3 (DUPLICATE #2)
  t=15    sender got ACK 3 (DUPLICATE #3)
  t=15  SEND seg 3 (FAST RETRANSMIT after 3 dup ACKs)
  t=15    receiver got seg 7 -> ACK 3
  t=16    receiver got seg 8 -> ACK 3
  t=20    receiver got seg 3 -> ACK 9
  t=20    sender got ACK 3 (DUPLICATE #4)
  t=21    sender got ACK 3 (DUPLICATE #5)
  t=25    sender got ACK 9 (new): base -> 9
  t=25  SEND seg 9
  t=26  SEND seg 10
  t=30    receiver got seg 9 -> ACK 10
  t=31    receiver got seg 10 -> ACK 11
  t=35    sender got ACK 10 (new): base -> 10
  t=36    sender got ACK 11 (new): base -> 11
  result: {'sent': 11, 'fast': 1, 'timeout': 0, 'dupacks': 5, 'ticks': 36}
check: loss repaired by FAST RETRANSMIT (no timeout needed): OK
  a duplicate ACK is a hint: 'something after the gap arrived'. 3 of them = probably loss, not reorder.

scenario B: 4 segments, window 6, segment 3 lost (too few segments after it for 3 dup ACKs)
  t=0   SEND seg 1
  t=1   SEND seg 2
  t=2   SEND seg 3   <-- LOST
  t=3   SEND seg 4
  t=5     receiver got seg 1 -> ACK 2
  t=6     receiver got seg 2 -> ACK 3
  t=8     receiver got seg 4 -> ACK 3
  t=10    sender got ACK 2 (new): base -> 2
  t=11    sender got ACK 3 (new): base -> 3
  t=13    sender got ACK 3 (DUPLICATE #1)
  t=51  SEND seg 3 (TIMEOUT RETRANSMIT)
  t=56    receiver got seg 3 -> ACK 5
  t=61    sender got ACK 5 (new): base -> 5
  result: {'sent': 5, 'fast': 0, 'timeout': 1, 'dupacks': 1, 'ticks': 61}
check: only 1 segment follows the gap -> 1 dup ACK -> must wait for the TIMEOUT: OK

scenario C: 60 segments, window 8, 10% random loss of data AND acks, seed 1 (no log)
  result: {'sent': 68, 'fast': 5, 'timeout': 3, 'dupacks': 25, 'ticks': 259}
  60 needed, 68 transmissions: 8 extra = 8 loss-triggered resends (5 fast, 3 timeout)
  every run with seed 1 prints the same numbers; a different seed gives different ones.
  note: the simulator ends when everything is acknowledged, so all 60 were delivered in order.
```

## Worked Example
**Problem.** SRTT = 80 ms, RTTVAR = 20 ms. A new RTT sample R = 120 ms arrives. Use a = 1/8, b = 1/4. Find the new SRTT, RTTVAR and RTO.

**Solution.**
1. RTTVAR = 0.75 x 20 + 0.25 x |80 - 120| = 15 + 10 = 25 ms (use the OLD SRTT).
2. SRTT = 0.875 x 80 + 0.125 x 120 = 70 + 15 = 85 ms.
3. RTO = 85 + 4 x 25 = 185 ms.

Second part: sender sent segments 1 to 6; segment 2 was lost. How many ACKs, and what values, does the receiver send, and when does the sender fast-retransmit? Segment 1 gives ACK 2. Segments 3, 4, 5, 6 each give ACK 2 again: the sender sees ACK 2 five times (one original and four duplicates). On the third duplicate (caused by segment 5) it resends segment 2; the fourth (segment 6) is already in flight. The receiver then sends ACK 7.

The code's Section 1 verifies the same method with its first two rows (100/120 ms) and Scenario A is the same shape of loss pattern with segment 3 missing.

## Key Rules / Gotchas Recap
- ACK n means "next byte/segment expected is n", not "n was received".
- Fast retransmit triggers on the 3rd duplicate ACK (4th identical ACK).
- Update RTTVAR before SRTT in each step.
- RTO = SRTT + 4 x RTTVAR; initial RTO 1 s; floor 1 s in RFC 6298.
- Karn: no RTT samples from retransmitted segments; double RTO on each timeout.
- A loss at the tail of the data cannot generate 3 duplicate ACKs, so it needs a timeout.
- A lost ACK is often harmless thanks to cumulative acknowledgement.
- The simulator counts segments for clarity; real TCP counts bytes.

## Why This Matters
Slow requests in production are often retransmission stalls: a 1 s RTO floor turns one lost packet into a visible 1 s pause, which shows up as latency spikes in API calls and model-serving pipelines. Reading `ss -ti` output (rto, rtt, retrans) and understanding why a timeout is so much worse than a fast retransmit is a real debugging skill.
