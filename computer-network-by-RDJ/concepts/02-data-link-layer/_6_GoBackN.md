# `_6_GoBackN.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Go-Back-N (GBN) is a sliding-window ARQ protocol: the sender may have up to N unacknowledged frames in flight (pipelining), the receiver accepts only the next frame it expects, and after a loss the sender goes back and retransmits the lost frame and everything after it. It keeps the link busy, unlike Stop-and-Wait, with a very simple receiver.

**Windows.** With m-bit sequence numbers (0 to 2^m - 1) the sender window may be at most 2^m - 1. The receiver window is 1: it keeps only the variable "next expected sequence number". The sender keeps `base` (oldest unacked frame) and `nextseq`, and one timer for the oldest unacked frame.

**Receiver behaviour.** If a frame arrives with the expected number it is delivered and acknowledged; any other frame (out of order, duplicate) is discarded and the receiver re-sends the ACK for the last in-order frame. ACKs are cumulative: ACK k means "all frames up to and including k arrived". So a lost ACK is often harmless: a later ACK covers it.

**Sender behaviour.** Send while nextseq < base + N. On ACK k, slide base to k+1 and restart the timer. On timeout of the oldest frame, resend base, base+1, ..., nextseq-1 (go back N).

**Why the window must be at most 2^m - 1.** If N = 2^m, a whole window could be received and all ACKs lost; the retransmitted frame 0 then carries the same number as the next new frame 0 and the receiver cannot tell old from new. The program demonstrates this.

**Throughput.** U = N/(1+2a) for N < 1 + 2a, and U = 1 when N >= 1 + 2a, where a = Tp/Tt. To fill the pipe the window must be at least 1 + 2a frames, so the sequence space must be larger than that. With loss probability p, Go-Back-N wastes bandwidth because one lost frame forces N retransmissions; Selective Repeat (next file) resends only the lost frame.

Advantages: simple receiver, no buffering, good link utilisation. Disadvantages: wasteful when errors are frequent or the window is large; discards correctly received frames.

## Full Line-by-Line Breakdown

### SECTION 1: WINDOWS AND SEQUENCE NUMBERS
A small table of m, the sequence space 2^m, and the GBN maximum window 2^m - 1. Remember the receiver window is 1.

Output from a real run:

```text
===== SECTION 1: WINDOWS AND SEQUENCE NUMBERS =====
 m bits  seq space  GBN max sender window
      1          2                      1
      2          4                      3
      3          8                      7
      4         16                     15
Receiver window is 1: it accepts only the next in-order frame.
```

### SECTION 2: SIMULATION WITH ONE LOST FRAME
`gbn` is a tick-based simulator: one frame can start per tick (Tt = 1), data takes Tt + Tp to arrive and an ACK takes Tp to return (Tp = 2), the timeout is 7 ticks and the window is 4. Frame 2's first transmission is lost. The log shows the receiver delivering 0 and 1, then discarding 3, 4 and 5 (expected 2) while it keeps re-sending ACK 1 (duplicates the sender ignores). When the timer for frame 2 fires at tick 13 the sender goes back and resends 2, 3, 4, 5. Total: 12 transmissions for 8 frames; the one loss cost 4 extra.

Output from a real run:

```text
===== SECTION 2: SIMULATION WITH ONE LOST FRAME =====
total=8 frames, window N=4, tt=1, tp=2, timeout=7 ticks, frame 2 lost once
  t=  0  sender sends 0
  t=  1  sender sends 1
  t=  2  sender sends 2  -- LOST
  t=  3  receiver gets 0: in order, delivered, ACK 0
  t=  3  sender sends 3
  t=  4  receiver gets 1: in order, delivered, ACK 1
  t=  5  sender gets ACK 0: cumulative, window slides base 0->1
  t=  5  sender sends 4
  t=  6  sender gets ACK 1: cumulative, window slides base 1->2
  t=  6  receiver gets 3: expected 2, DISCARDED
  t=  6  sender sends 5
  t=  8  sender gets ACK 1: duplicate, ignored
  t=  8  receiver gets 4: expected 2, DISCARDED
  t=  9  receiver gets 5: expected 2, DISCARDED
  t= 10  sender gets ACK 1: duplicate, ignored
  t= 11  sender gets ACK 1: duplicate, ignored
  t= 13  TIMEOUT for frame 2: go back, resend 2..5
  t= 13  sender sends 2
  t= 14  sender sends 3
  t= 15  sender sends 4
  t= 16  receiver gets 2: in order, delivered, ACK 2
  t= 16  sender sends 5
  t= 17  receiver gets 3: in order, delivered, ACK 3
  t= 18  sender gets ACK 2: cumulative, window slides base 2->3
  t= 18  receiver gets 4: in order, delivered, ACK 4
  t= 18  sender sends 6
  t= 19  sender gets ACK 3: cumulative, window slides base 3->4
  t= 19  receiver gets 5: in order, delivered, ACK 5
  t= 19  sender sends 7
  t= 20  sender gets ACK 4: cumulative, window slides base 4->5
  t= 21  sender gets ACK 5: cumulative, window slides base 5->6
  t= 21  receiver gets 6: in order, delivered, ACK 6
  t= 22  receiver gets 7: in order, delivered, ACK 7
  t= 23  sender gets ACK 6: cumulative, window slides base 6->7
  t= 24  sender gets ACK 7: cumulative, window slides base 7->8
delivered in order: [0, 1, 2, 3, 4, 5, 6, 7]
transmissions     : [0, 1, 2, 3, 4, 5, 2, 3, 4, 5, 6, 7]
extra transmissions caused by one loss: 4 (the whole window is resent)
```

### SECTION 3: NO LOSS VS LOSS
Same transfer with no loss takes 8 transmissions and finishes at tick 13; with one loss it takes 12 transmissions and finishes at tick 24. This is the cost of go-back.

Output from a real run:

```text
===== SECTION 3: NO LOSS VS LOSS =====
no loss : 8 transmissions, finished tick 13
one loss: 12 transmissions, finished tick 24
Compare Selective Repeat (file 7): only frame 2 would be resent.
```

### SECTION 4: THROUGHPUT FORMULA
With Tt = 1 ms and Tp = 2 ms, a = 2 and 1+2a = 5. The formula predicts U = N/5: 0.2, 0.4, 0.6, 0.8, 1.0, 1.0. The simulation for 200 frames matches closely; it is slightly lower for large N because the tail of the last acknowledgement is counted in the finish time (a finite-run effect). N = 1 is Stop-and-Wait.

Output from a real run:

```text
===== SECTION 4: THROUGHPUT FORMULA =====
U = min(1, N / (1 + 2a)), a = Tp / Tt
Exam: Tt = 1 ms, Tp = 2 ms -> a = 2.0, 1+2a = 5
  N  formula U  simulated U
  1      0.200        0.200
  2      0.400        0.398
  3      0.600        0.593
  4      0.800        0.787
  5      1.000        0.976
  6      1.000        0.976
N = 1 is Stop-and-Wait (U = 1/(1+2a) = 0.2). N = 1+2a = 5 fills the pipe.
Ideal window for full utilisation = 1 + 2a frames, needing sequence space > that.
```

### SECTION 5: TRAP - WINDOW SIZE 2^m BREAKS GO-BACK-N
With m = 2 (numbers 0..3), window 3 is safe: when the old frame 0 is retransmitted the receiver expects 3 and rejects it. With window 4 every frame arrived, the ACKs were lost, and the receiver now expects number 0 again, so the retransmitted old frame 0 is accepted as new data. The assertion confirms the bug appears at N = 2^m.

Output from a real run:

```text
===== SECTION 5: TRAP - WINDOW SIZE 2^m BREAKS GO-BACK-N =====
m = 2, sequence space 0..3
N = 3: receiver expects seq 3, retransmitted seq 0 is rejected (correct)
N = 4: all 4 frames arrived, receiver expects seq 0 again; retransmitted old frame 0 is ACCEPTED AS NEW DATA (bug)
check: OK  -> sender window must be at most 2^m - 1 for Go-Back-N
```

## Worked Example
**Problem.** Tt = 1 ms, Tp = 2 ms, window N = 3. Find utilisation and the number of sequence-number bits needed to reach full utilisation.

**Solution.** a = Tp/Tt = 2, so 1+2a = 5. U = N/(1+2a) = 3/5 = 0.6. For full utilisation N = 5 frames, so the sequence space must be at least N+1 = 6 numbers, which needs m = 3 bits (2^3 - 1 = 7 >= 5). The program's table shows U = 0.600 for N = 3 and 1.000 from N = 5.

## Key Rules / Gotchas Recap
- Sender window <= 2^m - 1; receiver window = 1.
- Receiver discards out-of-order frames and re-ACKs the last in-order frame.
- ACKs are cumulative; a later ACK covers a lost earlier ACK.
- One timer, for the oldest unacknowledged frame; timeout resends the whole window.
- U = min(1, N/(1+2a)).
- Window 2^m confuses old and new frames (shown in the trap).
- One loss costs up to N retransmissions.

## Why This Matters
TCP's cumulative ACK and its idea of a sliding window come from this family; the cost of "resend everything after the loss" explains why modern transports add selective acknowledgements. Window sizing against the bandwidth-delay product is the daily tuning problem of data transfer.
