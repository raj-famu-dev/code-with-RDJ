# Tags: #Python #ComputerNetworks #SessionLayer #PresentationLayer #PublicKeyCryptoExchange | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Public-key cryptography: Diffie-Hellman key exchange (tiny worked numbers,
then a larger toy prime) and textbook RSA with small primes. All TOYS:
real systems use vetted libraries and padding (OAEP/PSS) or ECDH/X25519."""
from __future__ import annotations

import math
import random

print("WARNING: toy parameters and textbook RSA below are INSECURE on purpose.\n")


# ===== SECTION 1: DIFFIE-HELLMAN WITH TINY NUMBERS =====
print("===== SECTION 1: DIFFIE-HELLMAN, TINY NUMBERS =====")
p, g = 23, 5          # public: prime modulus and generator
a, b = 6, 15          # secrets of Alice and Bob
A = pow(g, a, p)      # Alice sends g^a mod p
B = pow(g, b, p)
print(f"  public p={p}, g={g}")
print(f"  Alice secret a={a}: A = {g}^{a} mod {p} = {A}")
print(f"  Bob   secret b={b}: B = {g}^{b} mod {p} = {B}")
s_alice = pow(B, a, p)
s_bob = pow(A, b, p)
print(f"  Alice: B^a mod p = {B}^{a} mod {p} = {s_alice}")
print(f"  Bob  : A^b mod p = {A}^{b} mod {p} = {s_bob}")
assert s_alice == s_bob == 2
print("  check: OK (shared secret 2, matches the classic worked example)")
print("  Eve sees p, g, A, B only. She must solve the discrete log: g^x = A mod p.")
x = next(i for i in range(1, p) if pow(g, i, p) == A)
print(f"  TRAP tiny p: Eve brute-forces a={x} instantly (only {p - 1} candidates).")


# ===== SECTION 2: DIFFIE-HELLMAN WITH A LARGER TOY PRIME =====
print("\n===== SECTION 2: DIFFIE-HELLMAN WITH A BIGGER PRIME (STILL A TOY) =====")


def is_probable_prime(n: int, rounds: int = 20, rng: random.Random | None = None) -> bool:
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % sp == 0:
            return n == sp
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    rng = rng or random.Random(0)
    for _ in range(rounds):
        x = pow(rng.randrange(2, n - 1), d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def find_safe_prime(bits: int, rng: random.Random) -> int:
    """Safe prime: p = 2q + 1 with q also prime."""
    while True:
        q = rng.getrandbits(bits - 1) | (1 << (bits - 2)) | 1
        if is_probable_prime(q, 12, rng) and is_probable_prime(2 * q + 1, 12, rng):
            return 2 * q + 1


rng = random.Random(7)  # seeded so output is repeatable; real keys need secrets
P = find_safe_prime(128, rng)
G = 2
print(f"  generated {P.bit_length()}-bit safe prime p (seeded, toy)")
print(f"  p = {P}")
a2 = rng.getrandbits(120)
b2 = rng.getrandbits(120)
A2, B2 = pow(G, a2, P), pow(G, b2, P)
k1, k2 = pow(B2, a2, P), pow(A2, b2, P)
print(f"  shared secret match: {k1 == k2}")
print(f"  shared secret = {k1:x}")
assert k1 == k2
print("  check: OK. pow(base, exp, mod) does fast modular exponentiation.")
print("  Real DH uses >= 2048-bit standardised groups (or X25519). Eve cannot")
print("  brute-force 2^120 secrets, but this 128-bit toy is still far too small.")
print("  Plain DH has NO authentication: a man-in-the-middle can sit between both")
print("  sides, so real protocols sign the exchange (see TLS module).")


# ===== SECTION 3: TEXTBOOK RSA WORKED END TO END =====
print("\n===== SECTION 3: TEXTBOOK RSA, SMALL PRIMES =====")
p1, q1 = 61, 53
n = p1 * q1
phi = (p1 - 1) * (q1 - 1)
e = 17
d = pow(e, -1, phi)   # modular inverse (Python 3.8+)
print(f"  p={p1}, q={q1}")
print(f"  n = p*q = {n}")
print(f"  phi = (p-1)(q-1) = {phi}")
print(f"  e = {e}  (gcd(e, phi) = {math.gcd(e, phi)}, it must be 1)")
print(f"  d = e^-1 mod phi = {d}   (check e*d mod phi = {e * d % phi})")
print(f"  public key (e,n) = ({e},{n}); private key (d,n) = ({d},{n})")
M = 65
C = pow(M, e, n)
back = pow(C, d, n)
print(f"  encrypt M={M}: C = {M}^{e} mod {n} = {C}")
print(f"  decrypt     : M = {C}^{d} mod {n} = {back}")
assert (n, phi, d, C, back) == (3233, 3120, 2753, 2790, 65)
print("  check: OK (classic 3233 / 2753 / 2790 example)")
text = "HI"
nums = [ord(c) for c in text]
enc = [pow(m, e, n) for m in nums]
print(f"  encrypt '{text}' byte by byte: {nums} -> {enc} -> "
      f"{''.join(chr(pow(c, d, n)) for c in enc)!r}")


# ===== SECTION 4: WHY PADDING IS NEEDED =====
print("\n===== SECTION 4: WHY TEXTBOOK RSA NEEDS PADDING =====")
print("  Textbook RSA is deterministic: same plaintext -> same ciphertext.")
yes, no = pow(1, e, n), pow(0, e, n)
print(f"  TRAP 1: M=0 -> {no}, M=1 -> {yes}: tiny messages leak, and an attacker")
print("          can encrypt guesses and compare (guess 'YES' vs 'NO').")
guess_table = {pow(m, e, n): m for m in range(n)}
print(f"          attacker without d inverts C={C}: M = {guess_table[C]}")
c1, c2 = pow(7, e, n), pow(11, e, n)
print(f"  TRAP 2: malleable: E(7)*E(11) mod n = {c1 * c2 % n} = E(77) = {pow(77, e, n)}")
assert c1 * c2 % n == pow(77, e, n)
print("  FIX: OAEP (encryption) / PSS (signatures) add randomness and structure.")
print("  Never hand-roll this; use a vetted library (e.g. the 'cryptography' package).")


# ===== SECTION 5: TRAP - TINY-KEY RSA FACTORED INSTANTLY =====
print("\n===== SECTION 5: TINY KEY FACTORED INSTANTLY =====")


def factor(n_: int) -> tuple[int, int]:
    f = 2
    while f * f <= n_:
        if n_ % f == 0:
            return f, n_ // f
        f += 1
    return n_, 1


pf, qf = factor(n)
print(f"  attacker factors n={n} by trial division: {pf} x {qf}")
d_stolen = pow(e, -1, (pf - 1) * (qf - 1))
print(f"  rebuilt private exponent d = {d_stolen}; decrypts C={C} to {pow(C, d_stolen, n)}")
assert d_stolen == d
big_p, big_q = 1000003, 1000033
big_n = big_p * big_q
print(f"  even n={big_n} (40-bit) falls to trial division: {factor(big_n)}")
print("  Security rests on factoring being hard: real RSA uses >= 2048-bit n")
print("  (two ~1024-bit primes); trial division would never finish.")
print("  Use vetted libraries only, never your own crypto.")
