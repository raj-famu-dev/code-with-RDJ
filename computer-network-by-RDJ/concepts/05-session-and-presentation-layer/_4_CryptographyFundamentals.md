# `_4_CryptographyFundamentals.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Cryptography is the science of protecting information so that only the intended people can read it or so that changes can be detected. Network traffic crosses machines you do not control, so encryption and authentication are needed to keep it secret and trustworthy. This lesson explains the vocabulary and shows how the oldest ciphers work and why they fail; every cipher in the code is a toy and is clearly labelled insecure.

**Security goals (CIA and friends)**
- **Confidentiality**: only authorised parties can read the data (encryption).
- **Integrity**: data has not been altered (hash, MAC, signature).
- **Availability**: the system is up when needed (resilience, DoS protection; not a cipher job).
- **Authentication**: proof of who sent it. **Non-repudiation**: the sender cannot deny it (digital signature).

**Vocabulary.** *Plaintext* is the readable message; *ciphertext* is the scrambled output; *encryption* turns plaintext into ciphertext with a key; *decryption* reverses it. *Cryptanalysis* is breaking ciphers. **Kerckhoffs's principle**: a system must stay secure even if everything except the key is public. "Security by obscurity" is not security.

**Classical ciphers**
- **Substitution** replaces letters. *Caesar*: shift every letter by k (`C = (P + k) mod 26`); only 25 useful keys so brute force wins. *Vigenere*: a repeating key word gives a different shift per letter; it hides single-letter frequencies but a short repeating key can be found with the Kasiski test and frequency analysis.
- **Transposition** rearranges the letters without changing them. *Rail fence*: write the text in a zigzag over k rails and read row by row. Letter frequencies are unchanged, so it is weak alone.
- Modern ciphers combine substitution and transposition in many rounds (confusion and diffusion).

**Symmetric vs asymmetric**

| | Symmetric | Asymmetric (public key) |
|---|---|---|
| Keys | same secret key both sides | public key + private key |
| Speed | fast | slow |
| Main problem | key distribution | speed, trust in public keys |
| Examples | AES, ChaCha20, DES, 3DES | RSA, ECC, Diffie-Hellman |
| Typical use | bulk data | key exchange, signatures |

Real systems are hybrid: public-key methods agree on a session key, then a symmetric cipher encrypts the data (this is what TLS does).

**Block vs stream ciphers.** A block cipher encrypts fixed-size blocks (AES: 128-bit block, 128/192/256-bit key) and needs a *mode of operation* for longer data (CBC, CTR, GCM; ECB is insecure because equal blocks give equal ciphertext). A stream cipher generates a keystream and XORs it with the data bit by bit (ChaCha20).

**DES and AES (described, not implemented).** DES: 64-bit blocks, 56-bit key, 16 Feistel rounds; the key space is now small enough to brute-force, so DES is obsolete and 3DES (three DES passes) is deprecated. AES (Rijndael, the 2001 NIST standard): substitution-permutation network, 10, 12 or 14 rounds for 128-, 192-, 256-bit keys, each round with SubBytes, ShiftRows, MixColumns and AddRoundKey. Implement neither yourself.

**One-time pad.** XOR the message with a truly random key as long as the message, used once. It is information-theoretically secure but impractical (key distribution). Reusing the key destroys it: `C1 xor C2 = M1 xor M2`, which leaks both messages.

**Typical exam questions.** Encrypt with Caesar or Vigenere; rail-fence encrypt/decrypt; symmetric vs asymmetric; define CIA; block vs stream; how many keys are needed for n users (symmetric n(n-1)/2, asymmetric 2n).

## Full Line-by-Line Breakdown

### SECTION 1: GOALS AND VOCABULARY
Prints the goals table, the encrypt/decrypt chain, and Kerckhoffs's principle. A WARNING banner at the top of the file states that every cipher below is a toy.

```text
WARNING: every cipher implemented in this file is a TOY for learning.
         NEVER use any of it to protect real data.
```

```text
===== SECTION 1: GOALS AND VOCABULARY =====
  Confidentiality  only intended readers can read it (encryption)
  Integrity        data was not changed (hash/MAC/signature)
  Availability     the service stays usable (not a cipher job)
  Authentication   who sent it? (MAC/signature/certificate)
  Non-repudiation  sender cannot deny sending (digital signature)
plaintext --encrypt(key)--> ciphertext --decrypt(key)--> plaintext
Kerckhoffs: security must rest on the KEY, not on a secret algorithm.
```

### SECTION 2: CAESAR CIPHER (TOY, INSECURE)
`caesar` shifts each uppercase letter by `shift` modulo 26 and leaves other characters unchanged. `ATTACK AT DAWN` with shift 3 gives `DWWDFN DW GDZQ` (the textbook answer, asserted). The brute-force loop tries all 25 shifts and stops printing at the readable one: a key space of 25 is no protection.

```text
===== SECTION 2: CAESAR CIPHER (TOY, INSECURE) =====
  plaintext 'ATTACK AT DAWN' shift 3 -> 'DWWDFN DW GDZQ'
  decrypt = shift back by 3. check: OK (textbook DWWDFN DW GDZQ)
  BREAK: only 25 keys. Brute force prints all candidates:
    key=3: ATTACK AT DAWN   <- readable, done
```

### SECTION 3: VIGENERE CIPHER (TOY, INSECURE)
The key `LEMON` is repeated over the letters (index `i` advances only on letters). Letter A plus L (11) gives L, T plus E (4) gives X, and so on, producing the textbook `LXFOPVEFRNHR`. Decryption subtracts the shifts.

```text
===== SECTION 3: VIGENERE CIPHER (TOY, INSECURE) =====
  ATTACKATDAWN with key LEMON -> LXFOPVEFRNHR
  check: OK (textbook LXFOPVEFRNHR). Repeating key leaks: Kasiski/
  frequency analysis recovers it; broken since the 1800s.
```

### SECTION 4: RAIL FENCE (TRANSPOSITION, TOY)
`rail_pattern` computes which rail each position falls on as the cursor bounces down and up. The printed diagram shows the zigzag; reading the rails row by row gives `WECRLTEERDSOEEFEAOCAIVDEN`. Decryption recomputes the same positions and puts the letters back. Notice the letters are the same, only the order changed.

```text
===== SECTION 4: RAIL FENCE (TRANSPOSITION, TOY) =====
  zig-zag over 3 rails:
    W...E...C...R...L...T...E
    .E.R.D.S.O.E.E.F.E.A.O.C.
    ..A...I...V...D...E...N..
  ciphertext: WECRLTEERDSOEEFEAOCAIVDEN
  check: OK (Wikipedia example). Letters are only MOVED, so letter
  frequencies are unchanged: transposition alone is weak.
```

### SECTION 5: SYMMETRIC VS ASYMMETRIC, BLOCK VS STREAM
A comparison table and facts about DES and AES, followed by key-space sizes computed with Python integers: Caesar 25, DES 2^56 = 72,057,594,037,927,936, AES-128 2^128. This section describes DES and AES; it does not implement them.

```text
===== SECTION 5: SYMMETRIC VS ASYMMETRIC, BLOCK VS STREAM =====
           | Symmetric               | Asymmetric
  Keys     | one shared secret       | public + private pair
  Speed    | fast (bulk data)        | slow (small data)
  Problem  | how to share the key?   | key size, speed
  Examples | AES, ChaCha20, 3DES     | RSA, ECC, DH (key exchange)
  Block cipher : fixed blocks (AES = 128-bit block; key 128/192/256 bits).
  Stream cipher: keystream XORed with data (ChaCha20, RC4-legacy).
  DES: 64-bit block, 56-bit key, 16 Feistel rounds; broken by brute force,
       3DES is deprecated. AES (Rijndael): SP-network, 10/12/14 rounds.
  Real systems = hybrid: asymmetric to agree a key, symmetric for the data.
  key space Caesar       = 25
  key space DES (56-bit) = 72,057,594,037,927,936
  key space AES-128      = 340,282,366,920,938,463,463,374,607,431,768,211,456
```

### SECTION 6: ONE-TIME PAD (XOR) AND KEY REUSE
`xor` combines two byte strings. A random-looking key (from a seeded generator, only for repeatable output; a real pad needs `os.urandom`) encrypts `MEET AT NOON!` and decrypts by XOR again. Trap: the same key is used for a second message. XORing the two ciphertexts cancels the key and equals `M1 xor M2`; if an attacker knows or guesses one message (a "crib"), the other appears at once. Fix: never reuse a key or keystream, which also applies to stream ciphers and to nonces in modes such as AES-CTR/GCM.

```text
===== SECTION 6: ONE-TIME PAD (XOR) AND KEY REUSE =====
  msg   : b'MEET AT NOON!'
  key   : f0 5d 9b 66 d1 87 7d ff b5 d4 6f 9e a9
  cipher: bd 18 de 32 f1 c6 29 df fb 9b 20 d0 88
  decrypt = XOR with same key. check: OK
  OTP is unbreakable ONLY if the key is truly random, as long as the
  message, kept secret, and used exactly ONCE.
  TRAP key reused: C1 xor C2 = 0c 11 11 15 63 0a 74 61 1a 6f 76 0f 6c
       which equals M1 xor M2 : True (key cancelled out!)
       attacker guesses M1 (crib) and recovers M2: b'ATTACK AT 9AM'
  FIX: never reuse the key/keystream (same rule for stream ciphers and AES-CTR nonces).
```

## Worked Example
**Problem.** Encrypt `HELLO` with a Caesar shift of 5, then encrypt `HELLO` with Vigenere key `KEY`.

Caesar (add 5 to each letter number, A=0): H(7)+5=12 M, E(4)+5=9 J, L(11)+5=16 Q, L to Q, O(14)+5=19 T. Ciphertext `MJQQT`.

Vigenere key `KEY` = shifts 10, 4, 24, repeated: H(7)+10=17 R, E(4)+4=8 I, L(11)+24=35 mod 26=9 J, L(11)+10=21 V, O(14)+4=18 S. Ciphertext `RIJVS`.

You can check both by calling the `caesar("HELLO", 5)` and `vigenere("HELLO", "KEY")` functions in the file (the file itself verifies the textbook cases `DWWDFN DW GDZQ` and `LXFOPVEFRNHR`).

## Key Rules / Gotchas Recap
- Classical ciphers (Caesar, Vigenere, rail fence) are teaching tools only.
- Security must depend on the key only (Kerckhoffs); never invent your own cipher.
- Symmetric = fast, one shared key; asymmetric = slow, two keys; real systems use both.
- Key reuse in XOR / stream ciphers leaks the XOR of the plaintexts.
- A one-time pad is perfect only with a truly random, secret, single-use key as long as the message.
- Encoding (Base64) and hashing are not encryption.
- DES and 3DES are obsolete; use AES-GCM or ChaCha20-Poly1305 from a vetted library.

## Why This Matters
Knowing why old ciphers fail trains the thinking used in security tooling and code review: reused nonces, tiny key spaces and home-made crypto are real findings. For AI engineering, API keys, model artifacts and data in transit all depend on correctly used standard ciphers.
