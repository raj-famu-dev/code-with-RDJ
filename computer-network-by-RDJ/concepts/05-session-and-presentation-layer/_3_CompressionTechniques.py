# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Presentation-layer compression: lossless vs lossy, run-length encoding,
Huffman coding (code table + ratio), a small LZW, and a measured zlib
comparison. JPEG/MP3/MPEG are described in the walkthrough."""
from __future__ import annotations

import heapq
import random
import zlib
from collections import Counter


# ===== SECTION 1: LOSSLESS VS LOSSY =====
print("===== SECTION 1: LOSSLESS VS LOSSY =====")
print("Lossless: decompress gives back EXACT bytes (text, code, PNG, ZIP).")
print("Lossy   : throws away detail humans barely notice (JPEG, MP3, MPEG).")
samples = [10, 12, 11, 200, 202, 201]
quantised = [round(v / 50) * 50 for v in samples]
print("lossy toy: values", samples, "-> quantised to multiples of 50 ->", quantised)
print("(original cannot be recovered exactly: that is the price of lossy)")


# ===== SECTION 2: RUN-LENGTH ENCODING =====
print("\n===== SECTION 2: RUN-LENGTH ENCODING =====")


def rle_encode(s: str) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for ch in s:
        if out and out[-1][0] == ch:
            out[-1] = (ch, out[-1][1] + 1)
        else:
            out.append((ch, 1))
    return out


def rle_decode(pairs: list[tuple[str, int]]) -> str:
    return "".join(ch * n for ch, n in pairs)


s = "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"
pairs = rle_encode(s)
print("input :", s, f"({len(s)} chars)")
print("pairs :", pairs)
text = "".join(f"{n}{c}" for c, n in pairs)
print("RLE   :", text, f"({len(text)} chars)")
assert rle_decode(pairs) == s
print("check: OK (the classic Wikipedia sample decodes back)")
bad = "ABCDEFGH"
bad_text = "".join(f"{n}{c}" for c, n in rle_encode(bad))
print(f"TRAP  no runs: '{bad}' ({len(bad)}) -> '{bad_text}' ({len(bad_text)}): RLE DOUBLED it")


# ===== SECTION 3: HUFFMAN CODING =====
print("\n===== SECTION 3: HUFFMAN CODING =====")


def huffman_codes(freq: dict[str, int]) -> dict[str, str]:
    # Heap entries: (weight, tiebreak, tree). Tiebreak keeps output deterministic.
    heap: list[tuple[int, int, object]] = []
    for i, (sym, w) in enumerate(sorted(freq.items())):
        heap.append((w, i, sym))
    heapq.heapify(heap)
    counter = len(heap)
    while len(heap) > 1:
        w1, _, a = heapq.heappop(heap)
        w2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (w1 + w2, counter, (a, b)))
        counter += 1
    codes: dict[str, str] = {}

    def walk(node: object, prefix: str) -> None:
        if isinstance(node, tuple):
            walk(node[0], prefix + "0")
            walk(node[1], prefix + "1")
        else:
            codes[str(node)] = prefix or "0"

    walk(heap[0][2], "")
    return codes


msg = "ABRACADABRA"
freq = dict(Counter(msg))
codes = huffman_codes(freq)
print("message:", msg, "frequencies:", dict(sorted(freq.items())))
print("code table (more frequent -> shorter):")
for sym in sorted(codes, key=lambda c: (len(codes[c]), c)):
    print(f"  {sym}: freq={freq[sym]} code={codes[sym]}")
bits = "".join(codes[c] for c in msg)
print("encoded:", bits)
fixed_bits = len(msg) * 3  # 5 symbols need 3 bits fixed-length
print(f"Huffman {len(bits)} bits vs fixed 3-bit {fixed_bits} bits vs ASCII {len(msg) * 8} bits")
print(f"compression ratio vs ASCII: {len(msg) * 8 / len(bits):.2f} : 1")
# Decode (prefix-free, so greedy matching works).
rev = {v: k for k, v in codes.items()}
buf, out = "", []
for bit in bits:
    buf += bit
    if buf in rev:
        out.append(rev[buf])
        buf = ""
assert "".join(out) == msg
print("check: OK (decoded back to ABRACADABRA). Total 23 bits is the textbook optimum.")
assert len(bits) == 23


# ===== SECTION 4: LZW =====
print("\n===== SECTION 4: LZW (DICTIONARY CODING) =====")


def lzw_encode(data: str) -> list[int]:
    table = {chr(i): i for i in range(256)}
    nxt, w, out = 256, "", []
    for ch in data:
        if w + ch in table:
            w += ch
        else:
            out.append(table[w])
            table[w + ch] = nxt
            nxt += 1
            w = ch
    if w:
        out.append(table[w])
    return out


def lzw_decode(codes_: list[int]) -> str:
    table = {i: chr(i) for i in range(256)}
    nxt = 256
    w = table[codes_[0]]
    out = [w]
    for k in codes_[1:]:
        entry = table[k] if k in table else w + w[0]  # the KwKwK special case
        out.append(entry)
        table[nxt] = w + entry[0]
        nxt += 1
        w = entry
    return "".join(out)


lz = "TOBEORNOTTOBEORTOBEORNOT"
enc = lzw_encode(lz)
print("input  :", lz, f"({len(lz)} symbols)")
print("output :", enc, f"({len(enc)} codes)")
assert lzw_decode(enc) == lz
assert lzw_decode(lzw_encode("AAAAAAA")) == "AAAAAAA"
print("check: OK (incl. the tricky 'AAAAAAA' case). LZ77 is the sliding-window")
print("cousin: it emits (distance, length) back-references. DEFLATE = LZ77 + Huffman.")


# ===== SECTION 5: zlib COMPARISON (MEASURED) =====
print("\n===== SECTION 5: zlib COMPARISON (MEASURED ON THESE INPUTS) =====")
english = ("the quick brown fox jumps over the lazy dog. " * 40).encode()
rand_like = random.Random(1).randbytes(1800)  # seeded noise: high entropy
runs = b"A" * 900 + b"B" * 900
for label, data in [("repeated text", english), ("random bytes", rand_like), ("long runs", runs)]:
    z = zlib.compress(data, 9)
    assert zlib.decompress(z) == data
    print(f"  {label:<14} {len(data):>5} -> {len(z):>4} bytes  ratio {len(data) / len(z):6.2f} : 1")
assert len(zlib.compress(rand_like, 9)) >= len(rand_like)
print("check: OK. Random (high-entropy) data does not shrink at all (it grows slightly);")
print("highly repetitive data shrinks a lot. Always measure on YOUR data.")
