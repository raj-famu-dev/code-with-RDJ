# `_5_PublicKeyCryptoAndKeyExchange.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Public-key (asymmetric) cryptography solves the key-distribution problem: two people who have never met can agree on a secret, or send each other encrypted messages, using keys that can be published safely. Diffie-Hellman (DH) lets two parties compute a shared secret over an open channel; RSA lets anyone encrypt with a public key so only the private-key owner can decrypt (and the reverse for signatures). Both rely on maths that is easy in one direction and believed hard in the other.

**Hard problems.** *Discrete logarithm*: given `g`, `p` and `g^x mod p`, finding `x` is hard for large `p`. *Integer factorisation*: given `n = p x q`, finding `p` and `q` is hard for large `n`.

**Diffie-Hellman key exchange**
1. Alice and Bob publicly agree on a prime `p` and a generator `g`.
2. Alice picks a secret `a` and sends `A = g^a mod p`. Bob picks `b` and sends `B = g^b mod p`.
3. Alice computes `B^a mod p`, Bob computes `A^b mod p`. Both equal `g^(ab) mod p`, the shared secret.
An eavesdropper sees `p, g, A, B` but not `a` or `b`. Weakness: plain DH is unauthenticated, so a man-in-the-middle can run two exchanges (one with each side). Real protocols authenticate it with signatures/certificates. Modern systems use *ephemeral* DH (DHE/ECDHE, often X25519) to get forward secrecy.

**RSA (Rivest, Shamir, Adleman)**
1. Choose two primes `p` and `q`; `n = p x q`; `phi = (p-1)(q-1)`.
2. Choose `e` with `gcd(e, phi) = 1` (65537 is common).
3. Compute `d = e^-1 mod phi` (so `e x d = 1 mod phi`).
4. Public key `(e, n)`; private key `(d, n)`.
5. Encrypt `C = M^e mod n`; decrypt `M = C^d mod n`. It works by Euler's theorem. `M` must be smaller than `n`.
Signatures run it backwards: sign with `d`, verify with `e`.

**Why padding.** Textbook RSA is deterministic (the same message always gives the same ciphertext), leaks for tiny messages (0 and 1 map to themselves), and is malleable (`E(a) x E(b) = E(a x b)`). Real systems use randomised padding: OAEP for encryption and PSS for signatures.

**Key sizes.** RSA and DH need about 2048 bits or more to be considered safe today; elliptic-curve versions (ECDH, ECDSA, Ed25519) give similar security with much smaller keys. Do not trust a number I give you for "years to break"; check current guidance (for example NIST SP 800-57).

**Never roll your own.** Use a vetted library (for example Python's `cryptography` package), not hand-written maths. This file exists to teach, and its parameters are insecure on purpose.

**Typical exam questions.** DH with given `p, g, a, b`. RSA with small primes: compute `n`, `phi`, `d`, encrypt and decrypt. Why is DH vulnerable to man-in-the-middle? How many keys for n users with public-key crypto?

## Full Line-by-Line Breakdown

### SECTION 1: DIFFIE-HELLMAN, TINY NUMBERS
The classic exam numbers: `p=23, g=5, a=6, b=15`. `pow(g, a, p)` is modular exponentiation. A = 8, B = 19, both sides get 2. The trap: with `p = 23` Eve simply tries every exponent from 1 to 22 until `5^x mod 23 = 8` and finds `a = 6` at once.

```text
WARNING: toy parameters and textbook RSA below are INSECURE on purpose.
```

```text
===== SECTION 1: DIFFIE-HELLMAN, TINY NUMBERS =====
  public p=23, g=5
  Alice secret a=6: A = 5^6 mod 23 = 8
  Bob   secret b=15: B = 5^15 mod 23 = 19
  Alice: B^a mod p = 19^6 mod 23 = 2
  Bob  : A^b mod p = 8^15 mod 23 = 2
  check: OK (shared secret 2, matches the classic worked example)
  Eve sees p, g, A, B only. She must solve the discrete log: g^x = A mod p.
  TRAP tiny p: Eve brute-forces a=6 instantly (only 22 candidates).
```

### SECTION 2: DIFFIE-HELLMAN WITH A BIGGER PRIME (STILL A TOY)
No standard prime is copied from an RFC. The code builds its own 128-bit *safe prime* (`p = 2q + 1` with `q` prime) using a Miller-Rabin primality test written in the file and a seeded random generator so the output is repeatable. Both sides compute the same shared secret with `pow`, which uses fast square-and-multiply, so even huge exponents take microseconds. A 128-bit prime is far too small for real use (real groups are 2048 bits or more, or X25519); this section shows the mechanics and that Python integers have no size limit.

```text
===== SECTION 2: DIFFIE-HELLMAN WITH A BIGGER PRIME (STILL A TOY) =====
  generated 128-bit safe prime p (seeded, toy)
  p = 219696744652113973279370777339351347463
  shared secret match: True
  shared secret = 35d51c423ce47681bdbfa7941367b6e0
  check: OK. pow(base, exp, mod) does fast modular exponentiation.
  Real DH uses >= 2048-bit standardised groups (or X25519). Eve cannot
  brute-force 2^120 secrets, but this 128-bit toy is still far too small.
  Plain DH has NO authentication: a man-in-the-middle can sit between both
  sides, so real protocols sign the exchange (see TLS module).
```

### SECTION 3: TEXTBOOK RSA, SMALL PRIMES
The classic example: `p=61, q=53`, `n=3233`, `phi=3120`, `e=17`, `d=2753`. `pow(e, -1, phi)` is the modular inverse. Encrypting `M=65` gives `C=2790`, decrypting returns 65. The text `HI` is encrypted one character code at a time, only possible because each code (72, 73) is smaller than `n`.

```text
===== SECTION 3: TEXTBOOK RSA, SMALL PRIMES =====
  p=61, q=53
  n = p*q = 3233
  phi = (p-1)(q-1) = 3120
  e = 17  (gcd(e, phi) = 1, it must be 1)
  d = e^-1 mod phi = 2753   (check e*d mod phi = 1)
  public key (e,n) = (17,3233); private key (d,n) = (2753,3233)
  encrypt M=65: C = 65^17 mod 3233 = 2790
  decrypt     : M = 2790^2753 mod 3233 = 65
  check: OK (classic 3233 / 2753 / 2790 example)
  encrypt 'HI' byte by byte: [72, 73] -> [3000, 1486] -> 'HI'
```

### SECTION 4: WHY TEXTBOOK RSA NEEDS PADDING
Three problems: (1) messages 0 and 1 encrypt to themselves; (2) because encryption is deterministic and the public key is public, an attacker can build a table `E(m) -> m` for every possible message (here all 3233) and invert any ciphertext without `d`, shown by recovering 65 from 2790; (3) malleability: `E(7) x E(11) mod n = E(77)`, so an attacker can modify an encrypted value without knowing it. OAEP/PSS fix these.

```text
===== SECTION 4: WHY TEXTBOOK RSA NEEDS PADDING =====
  Textbook RSA is deterministic: same plaintext -> same ciphertext.
  TRAP 1: M=0 -> 0, M=1 -> 1: tiny messages leak, and an attacker
          can encrypt guesses and compare (guess 'YES' vs 'NO').
          attacker without d inverts C=2790: M = 65
  TRAP 2: malleable: E(7)*E(11) mod n = 3123 = E(77) = 3123
  FIX: OAEP (encryption) / PSS (signatures) add randomness and structure.
  Never hand-roll this; use a vetted library (e.g. the 'cryptography' package).
```

### SECTION 5: TINY KEY FACTORED INSTANTLY
Trial division finds `3233 = 53 x 61` in a few steps, the attacker recomputes `phi`, `d`, and decrypts. Even the 40-bit modulus `1000003 x 1000033` falls instantly. Real RSA moduli are 2048 bits (about 617 decimal digits), so this loop would never finish.

```text
===== SECTION 5: TINY KEY FACTORED INSTANTLY =====
  attacker factors n=3233 by trial division: 53 x 61
  rebuilt private exponent d = 2753; decrypts C=2790 to 65
  even n=1000036000099 (40-bit) falls to trial division: (1000003, 1000033)
  Security rests on factoring being hard: real RSA uses >= 2048-bit n
  (two ~1024-bit primes); trial division would never finish.
  Use vetted libraries only, never your own crypto.
```

## Worked Example
**Problem.** RSA with `p = 7`, `q = 11`, `e = 7`. Find `n`, `phi`, `d`, then encrypt `M = 5`.

1. `n = 7 x 11 = 77`. `phi = 6 x 10 = 60`.
2. `gcd(7, 60) = 1`, so `e = 7` is valid.
3. `d` with `7d = 1 mod 60`: `7 x 43 = 301 = 5 x 60 + 1`, so `d = 43`.
4. Encrypt: `C = 5^7 mod 77`. `5^2 = 25`, `5^4 = 625 mod 77 = 625 - 616 = 9`, `5^7 = 5^4 x 5^2 x 5 = 9 x 25 x 5 = 1125`, and `1125 mod 77 = 1125 - 1078 = 47`. So `C = 47`.
5. Decrypt: `47^43 mod 77` returns 5 (you can confirm with `pow(47, 43, 77)`; `pow(5, 7, 77)` gives 47).

For DH with `p=23, g=5, a=6, b=15` see the output of Section 1: both sides reach 2.

## Key Rules / Gotchas Recap
- DH agrees a shared key; RSA encrypts/signs. Both need big numbers.
- Plain DH has no authentication: man-in-the-middle works without signatures.
- RSA: `n = pq`, `phi = (p-1)(q-1)`, `ed = 1 mod phi`, `C = M^e mod n`.
- Small keys are factored or logged instantly; use 2048 bits or more (or elliptic curves).
- Textbook RSA is deterministic and malleable: always use OAEP/PSS.
- `pow(base, exp, mod)` and `pow(e, -1, phi)` do modular maths in Python.
- Use vetted libraries only; never your own crypto.

## Why This Matters
TLS, SSH, Signal and certificates are built from exactly these two ideas, so understanding them explains what a handshake is doing. In security work, "weak or reused keys" and "unpadded RSA" are standard review findings.
