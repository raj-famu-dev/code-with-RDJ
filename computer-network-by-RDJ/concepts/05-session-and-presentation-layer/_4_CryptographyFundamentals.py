# Tags: #Python #ComputerNetworks #SessionLayer #PresentationLayer #CryptographyFundamentals | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Cryptography fundamentals (presentation-layer security): CIA goals,
classical substitution/transposition ciphers as INSECURE TOYS, symmetric vs
asymmetric and block vs stream (concepts), and the one-time-pad XOR demo
with the key-reuse trap. DES/AES are described, not implemented."""
from __future__ import annotations

import random
import string

print("WARNING: every cipher implemented in this file is a TOY for learning.")
print("         NEVER use any of it to protect real data.\n")

# ===== SECTION 1: GOALS AND VOCABULARY =====
print("===== SECTION 1: GOALS AND VOCABULARY =====")
goals = [
    ("Confidentiality", "only intended readers can read it (encryption)"),
    ("Integrity", "data was not changed (hash/MAC/signature)"),
    ("Availability", "the service stays usable (not a cipher job)"),
    ("Authentication", "who sent it? (MAC/signature/certificate)"),
    ("Non-repudiation", "sender cannot deny sending (digital signature)"),
]
for g, d in goals:
    print(f"  {g:<16} {d}")
print("plaintext --encrypt(key)--> ciphertext --decrypt(key)--> plaintext")
print("Kerckhoffs: security must rest on the KEY, not on a secret algorithm.")


# ===== SECTION 2: CAESAR CIPHER (TOY) =====
print("\n===== SECTION 2: CAESAR CIPHER (TOY, INSECURE) =====")
ALPHA = string.ascii_uppercase


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if ch in ALPHA:
            out.append(ALPHA[(ALPHA.index(ch) + shift) % 26])
        else:
            out.append(ch)
    return "".join(out)


pt = "ATTACK AT DAWN"
ct = caesar(pt, 3)
print(f"  plaintext {pt!r} shift 3 -> {ct!r}")
assert caesar(ct, -3) == pt and ct == "DWWDFN DW GDZQ"
print("  decrypt = shift back by 3. check: OK (textbook DWWDFN DW GDZQ)")
print("  BREAK: only 25 keys. Brute force prints all candidates:")
for k in range(1, 26):
    cand = caesar(ct, -k)
    if cand == pt:
        print(f"    key={k}: {cand}   <- readable, done")


# ===== SECTION 3: VIGENERE CIPHER (TOY) =====
print("\n===== SECTION 3: VIGENERE CIPHER (TOY, INSECURE) =====")


def vigenere(text: str, key: str, decrypt: bool = False) -> str:
    out, i = [], 0
    for ch in text:
        if ch in ALPHA:
            k = ALPHA.index(key[i % len(key)])
            out.append(ALPHA[(ALPHA.index(ch) + (-k if decrypt else k)) % 26])
            i += 1
        else:
            out.append(ch)
    return "".join(out)


v = vigenere("ATTACKATDAWN", "LEMON")
print("  ATTACKATDAWN with key LEMON ->", v)
assert v == "LXFOPVEFRNHR" and vigenere(v, "LEMON", True) == "ATTACKATDAWN"
print("  check: OK (textbook LXFOPVEFRNHR). Repeating key leaks: Kasiski/")
print("  frequency analysis recovers it; broken since the 1800s.")


# ===== SECTION 4: RAIL FENCE TRANSPOSITION (TOY) =====
print("\n===== SECTION 4: RAIL FENCE (TRANSPOSITION, TOY) =====")


def rail_pattern(n: int, rails: int) -> list[int]:
    pat, r, d = [], 0, 1
    for _ in range(n):
        pat.append(r)
        if rails > 1:
            if r == 0:
                d = 1
            elif r == rails - 1:
                d = -1
            r += d
    return pat


def rail_encrypt(text: str, rails: int) -> str:
    pat = rail_pattern(len(text), rails)
    return "".join(text[i] for r in range(rails) for i in range(len(text)) if pat[i] == r)


def rail_decrypt(text: str, rails: int) -> str:
    pat = rail_pattern(len(text), rails)
    order = [i for r in range(rails) for i in range(len(text)) if pat[i] == r]
    out = [""] * len(text)
    for pos, ch in zip(order, text):
        out[pos] = ch
    return "".join(out)


msg = "WEAREDISCOVEREDFLEEATONCE"
print("  zig-zag over 3 rails:")
pat = rail_pattern(len(msg), 3)
for r in range(3):
    print("   ", "".join(msg[i] if pat[i] == r else "." for i in range(len(msg))))
enc = rail_encrypt(msg, 3)
print("  ciphertext:", enc)
assert enc == "WECRLTEERDSOEEFEAOCAIVDEN" and rail_decrypt(enc, 3) == msg
print("  check: OK (Wikipedia example). Letters are only MOVED, so letter")
print("  frequencies are unchanged: transposition alone is weak.")


# ===== SECTION 5: CONCEPTS - SYMMETRIC/ASYMMETRIC, BLOCK/STREAM, DES/AES =====
print("\n===== SECTION 5: SYMMETRIC VS ASYMMETRIC, BLOCK VS STREAM =====")
rows = [
    ("", "Symmetric", "Asymmetric"),
    ("Keys", "one shared secret", "public + private pair"),
    ("Speed", "fast (bulk data)", "slow (small data)"),
    ("Problem", "how to share the key?", "key size, speed"),
    ("Examples", "AES, ChaCha20, 3DES", "RSA, ECC, DH (key exchange)"),
]
for a, b, c in rows:
    print(f"  {a:<9}| {b:<24}| {c}")
print("  Block cipher : fixed blocks (AES = 128-bit block; key 128/192/256 bits).")
print("  Stream cipher: keystream XORed with data (ChaCha20, RC4-legacy).")
print("  DES: 64-bit block, 56-bit key, 16 Feistel rounds; broken by brute force,")
print("       3DES is deprecated. AES (Rijndael): SP-network, 10/12/14 rounds.")
print("  Real systems = hybrid: asymmetric to agree a key, symmetric for the data.")
key_space = {"Caesar": 25, "DES (56-bit)": 2 ** 56, "AES-128": 2 ** 128}
for name, n in key_space.items():
    print(f"  key space {name:<13}= {n:,}")


# ===== SECTION 6: ONE-TIME PAD AND THE KEY-REUSE TRAP =====
print("\n===== SECTION 6: ONE-TIME PAD (XOR) AND KEY REUSE =====")


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


rng = random.Random(2024)  # seeded for determinism; real OTP needs secrets/os.urandom
m1 = b"MEET AT NOON!"
key = bytes(rng.randrange(256) for _ in m1)
c1 = xor(m1, key)
print("  msg   :", m1)
print("  key   :", key.hex(" "))
print("  cipher:", c1.hex(" "))
assert xor(c1, key) == m1
print("  decrypt = XOR with same key. check: OK")
print("  OTP is unbreakable ONLY if the key is truly random, as long as the")
print("  message, kept secret, and used exactly ONCE.")
m2 = b"ATTACK AT 9AM"
c2 = xor(m2, key)  # TRAP: same key reused
leak = xor(c1, c2)
print("  TRAP key reused: C1 xor C2 =", leak.hex(" "))
print("       which equals M1 xor M2 :", leak == xor(m1, m2), "(key cancelled out!)")
guess = b"MEET AT NOON!"
print("       attacker guesses M1 (crib) and recovers M2:", xor(leak, guess))
print("  FIX: never reuse the key/keystream (same rule for stream ciphers and AES-CTR nonces).")
