# `_7_SelectiveRepeat.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Selective Repeat (SR) is a sliding-window ARQ protocol that retransmits only the frames that were actually lost or damaged. The receiver accepts and buffers out-of-order frames inside its window, acknowledges each frame individually, and delivers frames to the network layer in order once the gap is filled. It is the most efficient of the three ARQ protocols and the most complex.

**Windows.** With m-bit sequence numbers the sender window and the receiver window are both at most 2^(m-1), half of the sequence space. The receiver window is bigger than 1, so it needs a buffer for out-of-order frames.

**Sender.** Keeps one timer per outstanding frame. When the timer of frame k expires, only frame k is resent. ACKs are individual; the window slides forward past the leading run of acknowledged frames.

**Receiver.** Frames inside [rcv_base, rcv_base + N - 1] are accepted even when out of order and buffered; frames below rcv_base are old duplicates that are re-acknowledged (so the sender can move on) but not delivered again. When the frame at rcv_base arrives, it and any consecutive buffered frames are delivered and the window slides.

**Why the window must be at most half the sequence space.** Suppose m = 2 (numbers 0..3) and the window is 3. The sender sends 0,1,2; all arrive; the receiver's window slides to [3,0,1]; all ACKs are lost. The sender times out and resends frame 0. The receiver sees number 0, which lies inside its new window, and accepts it as a NEW frame: duplicate data delivered as if new. With window 2 the new receive window is [2,3] and the old 0 is correctly recognised as a duplicate. General rule: the old and new windows must not overlap, so N + N <= 2^m.

**Comparison of the three ARQ protocols.**

| Feature | Stop-and-Wait | Go-Back-N | Selective Repeat |
|---|---|---|---|
| Sender window | 1 | 2^m - 1 | 2^(m-1) |
| Receiver window | 1 | 1 | 2^(m-1) |
| Receiver buffering | no | no | yes |
| ACK type | per frame | cumulative | individual |
| On loss, resend | that frame | whole window | that frame only |
| Efficiency | 1/(1+2a) | N/(1+2a) | N/(1+2a) |
| Sequence-number bits for window N | 1 | about log2(N+1) | about log2(2N) |

**Pipelining** means sending several frames before the first acknowledgement returns, so the link stays busy during the round trip. **Piggybacking** means putting the ACK of received data inside a data frame travelling the other way instead of sending a separate ACK frame, saving frames and header overhead; if no reverse data is ready, the receiver waits briefly for a ride and then sends a stand-alone ACK.

## Full Line-by-Line Breakdown

### SECTION 1: WINDOW RULE
The table shows the SR maximum window for m = 2, 3, 4: 2, 4, 8. Both windows have this size.

Output from a real run:

```text
===== SECTION 1: WINDOW RULE =====
 m bits  seq space   SR max window (2^(m-1))
      2          4                         2
      3          8                         4
      4         16                         8
Both sender AND receiver have a window of this size.
```

### SECTION 2: SIMULATION WITH ONE LOST FRAME
The same tick-based model as the Go-Back-N file, but now the sender has a send time per frame and a separate timer for each, and the receiver buffers. Frame 2's first transmission is lost. Frames 3, 4 and 5 arrive out of order and are BUFFERED (waiting for 2); the sender receives individual ACKs for them. At t = 9 the timer of frame 2 fires and ONLY frame 2 is resent. When it arrives at t = 12, frames 2, 3, 4 and 5 are delivered together. Only 1 extra transmission versus 4 in Go-Back-N.

Output from a real run:

```text
===== SECTION 2: SIMULATION WITH ONE LOST FRAME =====
total=8, window N=4, tt=1, tp=2, timeout=7, frame 2 lost once
  t=  0  sender sends 0
  t=  1  sender sends 1
  t=  2  sender sends 2  -- LOST
  t=  3  receiver gets 0: in order
  t=  3     deliver 0 to network layer
  t=  3  sender sends 3
  t=  4  receiver gets 1: in order
  t=  4     deliver 1 to network layer
  t=  5  sender gets ACK 0 (individual)
  t=  5  sender sends 4
  t=  6  sender gets ACK 1 (individual)
  t=  6  receiver gets 3: out of order, BUFFERED (waiting for 2)
  t=  6  sender sends 5
  t=  8  sender gets ACK 3 (individual)
  t=  8  receiver gets 4: out of order, BUFFERED (waiting for 2)
  t=  9  receiver gets 5: out of order, BUFFERED (waiting for 2)
  t=  9  sender TIMEOUT, resends only 2
  t= 10  sender gets ACK 4 (individual)
  t= 11  sender gets ACK 5 (individual)
  t= 12  receiver gets 2: in order
  t= 12     deliver 2 to network layer
  t= 12     deliver 3 to network layer
  t= 12     deliver 4 to network layer
  t= 12     deliver 5 to network layer
  t= 14  sender gets ACK 2 (individual)
  t= 14  sender sends 6
  t= 15  sender sends 7
  t= 17  receiver gets 6: in order
  t= 17     deliver 6 to network layer
  t= 18  receiver gets 7: in order
  t= 18     deliver 7 to network layer
  t= 19  sender gets ACK 6 (individual)
  t= 20  sender gets ACK 7 (individual)
delivered in order: [0, 1, 2, 3, 4, 5, 6, 7]
transmissions     : [0, 1, 2, 3, 4, 5, 2, 6, 7]
extra transmissions: 1 (only frame 2 resent)
```

### SECTION 3: DEMONSTRATED FAILURE WITH A TOO-LARGE WINDOW
For m = 3 (numbers 0..7) the table shows, for each window size N, where the receiver's NEW window lands after N frames were received and all ACKs were lost. If the old frame 0 falls inside that window it is accepted as new data. This happens exactly for N = 5, 6, 7, that is N > 2^(m-1) = 4. The assertion proves it for every N.

Output from a real run:

```text
===== SECTION 3: DEMONSTRATED FAILURE WITH A TOO-LARGE WINDOW =====
m = 3, sequence numbers 0..7
 window        new rx window   old 0 accepted as new?
      1                  [1]                       no
      2               [2, 3]                       no
      3            [3, 4, 5]                       no
      4         [4, 5, 6, 7]                       no
      5      [5, 6, 7, 0, 1]                YES (BUG)
      6   [6, 7, 0, 1, 2, 3]                YES (BUG)
      7 [7, 0, 1, 2, 3, 4, 5]                YES (BUG)
check: OK -> failure appears exactly when N > 2^(m-1) = 4
Concrete case m=2, N=3: old 0 lands in new window [3,0,1] and is delivered as frame 4: DUPLICATE/WRONG data.
```

### SECTION 4: COMPARISON TABLE
The comparison table from the concept section, printed so it can be copied into notes.

Output from a real run:

```text
===== SECTION 4: COMPARISON TABLE =====
Feature          Stop-and-Wait  Go-Back-N     Selective Repeat
Sender window    1              2^m - 1       2^(m-1)
Receiver window  1              1             2^(m-1)
Min seq bits     1              m             m
Receiver buffer  no             no            yes
ACK type         per frame      cumulative    individual
On loss resend   that frame     whole window  that frame only
Efficiency       1/(1+2a)       N/(1+2a)      N/(1+2a)
Complexity       lowest         medium        highest
```

### SECTION 5: PIPELINING AND PIGGYBACKING
Pipelining and piggybacking. The idealised count says that if A and B each send 10 data frames and every data frame can carry the ACK for the other side's last frame, 20 frames suffice instead of 40. A `Frame` dataclass shows a frame carrying both `seq` and `ack`. The trap: if one side has nothing to send, its ACK would wait forever, so real protocols run an ACK timer.

Output from a real run:

```text
===== SECTION 5: PIPELINING AND PIGGYBACKING =====
Pipelining = sending several frames before the first ACK returns.
Stop-and-Wait sends 1 frame per RTT; with window N it sends N per RTT
(see the U table in file 6). Piggybacking = carry the ACK inside the
reverse-direction DATA frame instead of a separate ACK frame.
A and B each send 10 data frames (idealised, no loss, traffic in step):
  separate ACK frames : 40 frames on the wire
  piggybacked ACKs    : 20 frames on the wire
example piggybacked frame: Frame(seq=3, ack=5, payload='hello') -> carries data 3 AND ACK for B's frame 5
Trap: if B has nothing to send, the ACK waits. Real protocols start an
ACK timer and send a bare ACK if no data appears in time.
```

## Worked Example
**Problem.** m = 4 bits of sequence number. Give the maximum window for GBN and SR, and say what happens with SR window 9.

**Solution.** Sequence space 16. GBN max window = 2^4 - 1 = 15. SR max window = 2^3 = 8. With SR window 9 the old and new receiver windows overlap by 2 numbers (9 + 9 = 18 > 16), so a retransmitted old frame whose number falls in the overlap is accepted as new data. The program's m = 3 table shows the same effect starting at N = 5 (> 4).

## Key Rules / Gotchas Recap
- SR windows: both sender and receiver are 2^(m-1).
- Out-of-order frames are buffered, ACKs are individual, each frame has its own timer.
- Old duplicates (below rcv_base) are re-ACKed but never delivered twice.
- Window > half the sequence space makes old and new frames indistinguishable.
- SR needs a bigger sequence space than GBN for the same window (about 2N vs N+1).
- Piggybacking saves frames; the ACK timer prevents indefinite waiting.

## Why This Matters
TCP with selective acknowledgements (SACK) works like SR from the sender's point of view, and QUIC does individual packet numbers and loss detection. Knowing the window-size rule explains protocol limits such as sequence-number wrap and why long fat networks need window scaling.
