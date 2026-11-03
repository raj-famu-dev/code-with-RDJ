# `_6_HashingMacAndDigitalSignatures.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A hash function turns any input into a short fixed-size fingerprint (the digest), a MAC adds a secret key so only key holders can create or check the fingerprint, and a digital signature uses a private key so anyone can verify who produced it. Together they provide integrity, authentication and non-repudiation, which encryption alone does not.

**Hash function properties.** Deterministic (same input, same digest); fixed output size; fast to compute; *preimage resistance* (given a digest, cannot find an input); *second-preimage resistance* (given an input, cannot find another with the same digest); *collision resistance* (cannot find any two inputs with the same digest). The *avalanche effect*: changing one input bit flips about half of the output bits.

**Algorithms and their status (stated carefully).** MD5 (128-bit): practical collision attacks have been known since 2004; not acceptable for signatures or certificates. SHA-1 (160-bit): the first public practical collision (SHAttered) was shown in 2017; deprecated for signatures. SHA-256 (SHA-2 family) and SHA-3 are the current general-purpose choices. A collision attack is not the same as being able to reverse a hash. Even so, none of the fast hashes is suitable for storing passwords.

**HMAC.** `HMAC(K, m) = H((K xor opad) || H((K xor ipad) || m))` with `ipad = 0x36...`, `opad = 0x5C...` (RFC 2104). The sender sends `m` and the tag; the receiver recomputes it. Only someone with `K` can make a valid tag. Do not use `H(K || m)`: Merkle-Damgard hashes such as SHA-256 allow length-extension attacks. Compare tags with a constant-time function (`hmac.compare_digest`), because `==` may return at the first differing byte and leak timing.

**Password storage.** Store a slow, salted hash, never the password. A *salt* is a random per-user value stored next to the hash; it makes equal passwords hash differently and kills precomputed (rainbow) tables. Slow, tunable functions (PBKDF2, scrypt, bcrypt, Argon2) make each guess expensive. The Python standard library has `hashlib.pbkdf2_hmac` and `hashlib.scrypt`.

**Digital signatures.** The signer hashes the message and transforms the digest with the private key; anyone verifies with the public key (`sig^e mod n == digest`). This gives integrity, authentication and non-repudiation. HMAC cannot give non-repudiation because both sides share the key. Real RSA signatures use padding (PSS or PKCS#1 v1.5) and key sizes of 2048 bits or more; ECDSA and Ed25519 are common alternatives.

**Certificates and CAs.** A public key is useless unless you know whose it is. An X.509 certificate binds an identity (a name such as a domain) to a public key and is signed by a Certificate Authority (CA). A chain of trust runs from the site certificate, via intermediate CA(s), to a root CA whose certificate is already in your OS/browser trust store. The client verifies each signature up the chain, the validity dates, the name match, and the revocation status (CRL, OCSP).

**Comparison**

| | Hash | MAC (HMAC) | Digital signature |
|---|---|---|---|
| Key | none | shared secret | private/public pair |
| Detects accidental change | yes | yes | yes |
| Detects deliberate change | no (attacker recomputes) | yes | yes |
| Proves who | no | only to the other key holder | anyone, with the public key |
| Non-repudiation | no | no | yes |

**Typical exam questions.** Properties of hash functions; hash vs MAC vs signature; how a signature is created and verified; role of a CA; why salt passwords; why not use MD5.

## Full Line-by-Line Breakdown

### SECTION 1: HASH PROPERTIES AND AVALANCHE
SHA-256 of the empty string and of `abc`, checked against the published `abc` test vector prefix. Changing `$100` to `$101` flips 108 of the 256 digest bits (about half is expected). The output length stays 256 bits even for a 1,000,000-byte input.

```text
NOTE: the RSA signature below is a TOY (tiny key, no padding). Insecure.
```

```text
===== SECTION 1: HASH PROPERTIES AND AVALANCHE =====
A cryptographic hash: fixed-size digest, deterministic, fast to compute,
one-way (preimage resistant), second-preimage and collision resistant.
  SHA-256(b'') = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  SHA-256(b'abc') = ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
  check: OK (matches the FIPS 180 test vector for 'abc')
  'Pay Bob $100' -> ab08a25e535550241188537da46324a9137e8b80b38f2e965da5b59fb5addaff
  'Pay Bob $101' -> 382a1b5ed1e6b81567a2457938ba5c8b75ed8f34f26844049a25eb9bbb866fb1
  one character changed -> 108 of 256 digest bits differ (avalanche; ~128 expected)
  digest sizes: MD5 128 bits, SHA-1 160, SHA-256 256, SHA3-256 256
  output is always 256 bits, even for 1 MB input: 256 bits
```

### SECTION 2: MD5 / SHA-1 STATUS
Statements only (no collision is produced): MD5 collisions published 2004, SHA-1 practical collision 2017. The digests of `abc` are printed for reference.

```text
===== SECTION 2: MD5 / SHA-1 STATUS =====
  MD5   : practical collision attacks published (2004); do NOT use for
          signatures/certificates. Fine only for non-security checksums.
  SHA-1 : practical collision demonstrated publicly in 2017 (SHAttered);
          deprecated for signatures. Use SHA-256/SHA-3 instead.
  Collisions break signatures; this is not the same as 'password hashes
  can be reversed'. Still, neither is suitable for passwords (too fast).
  md5('abc')  = 900150983cd24fb0d6963f7d28e17f72
  sha1('abc') = a9993e364706816aba3e25717850c26c9cd0d89d
```

### SECTION 3: HMAC
`hmac.new(key, msg, sha256)` gives the tag. The file implements RFC 2104 itself (pad the key to the 64-byte block, XOR with `0x36`/`0x5C`, hash twice) and asserts it equals the module's result. Verification uses `hmac.compare_digest`. A modified message checked against the original tag is rejected.

```text
===== SECTION 3: HMAC =====
  HMAC-SHA256 tag: c3e2b5cb52e9b0f62c7efef90eb5b2c7701478157c3b3716ebdc5f5ba4e8c5b5
  check: OK (own RFC 2104 implementation equals hmac module)
  Why not sha256(key + msg)? Length-extension attacks on Merkle-Damgard hashes.
  verify with hmac.compare_digest: True
  Use compare_digest, not ==: == can stop at the first differing byte,
  leaking timing information about how many leading bytes were right.
  tampered message checked against the ORIGINAL tag accepted?: False
  (an attacker without the key cannot produce a valid tag for new text)
```

### SECTION 4: SALTED PASSWORD HASHING
Trap: plain `sha256(password)` is fast and the same for everyone with that password. PBKDF2-HMAC-SHA256 (100,000 iterations) with two different salts gives different outputs for `hunter2`. scrypt with `n=2^14, r=8, p=1` is shown too, and verification uses `compare_digest`. The salts are fixed constants only to make the output repeatable; real code uses `os.urandom(16)` per user. Only the first 24 hex characters of each hash are printed.

```text
===== SECTION 4: SALTED PASSWORD HASHING =====
  TRAP plain sha256(password): f52fbd32b2b3b86ff88ef6c4...
    identical passwords -> identical hashes, and attackers use precomputed
    tables / billions of guesses per second on GPUs.
  PBKDF2 salt A: ffa776fac4d4d3f1490dbb7f...
  PBKDF2 salt B: 5faa7d5599a9bd48c06674bd...  (same password, different hash)
  scrypt (n=2^14, r=8, p=1): e0fa5a3610d37e741281ac07...
  verify right password: True; wrong password: False
  In real code: salt = os.urandom(16) per user, stored next to the hash;
  deliberately slow hashing (work factor) makes guessing expensive.
```

### SECTION 5: DIGITAL SIGNATURE (TOY RSA)
Uses the `n=3233, e=17, d=2753` key from the RSA lesson. The SHA-256 digest is reduced modulo `n` so it fits the toy key (a real scheme hashes then pads). Signing: `digest^d mod n`; verification: `sig^e mod n` must equal the digest. A modified document produces a different digest, so the old signature fails. The trap is stated in the output: with `n=3233` only 3233 digests exist so collisions are trivial.

```text
===== SECTION 5: DIGITAL SIGNATURE (TOY RSA) =====
  sign = hash with private key; verify = check with public key.
  digest (mod n) = 1490; signature = digest^d mod n = 994
  verify: sig^e mod n = 1490 == digest ? True
  modified doc digest = 1975; signature still valid? False
  TRAP: with n=3233 there are only 3233 possible digests, so collisions are
  trivial; real signatures use 2048+ bit keys and padding (PSS) on a full hash.
  Signature gives integrity + authentication + non-repudiation (HMAC does not
  give non-repudiation: both sides hold the same key).
```

### SECTION 6: CERTIFICATE CHAIN CONCEPT
Each toy certificate contains subject, public key, issuer and a signature over the digest of those fields made with the issuer's private key. Three parties each get a small RSA key (`make_key`). `check` verifies a certificate with the issuer's public key. The chain is site, then intermediate, then root; the root is self-signed and trusted only because it is in the pretend `trust_store`. When an attacker swaps the site's public key in the certificate, the signature check fails. Real X.509 adds validity dates, names, key usage and revocation.

```text
===== SECTION 6: CERTIFICATE CHAIN CONCEPT =====
  chain: site.example <- InterCA <- RootCA (self-signed, in trust store)
  site.example  signed by InterCA signature valid: True
  InterCA       signed by RootCA  signature valid: True
  RootCA        signed by RootCA  signature valid: True
  chain trusted: True
  forged cert (key swapped) valid?: False
  Real X.509 certs also carry validity dates, names (SAN), key usage and are
  revoked via CRL/OCSP. Toy keys here are tiny and unsafe.
```

### SECTION 7: TAMPER DETECTION
Each log entry's hash covers the previous hash plus the new line (a hash chain, the idea behind blockchains and transparency logs). Changing entry 1 changes its hash and every later one; the first mismatch is at index 1. Caution: a plain hash only proves the data matches the hash you hold; an attacker who can change the data and the hash can recompute both, which is why a MAC or signature is needed against deliberate attack.

```text
===== SECTION 7: TAMPER DETECTION =====
  hash chain: ['366aacc5c9dd', 'b6c72aab1f41', 'b31f765ff326']
  tampered  : ['366aacc5c9dd', '3b236f49e694', '3cb299491655']
  first mismatch at entry index: 1
  A plain hash only detects accidental change (attacker recomputes it).
  A MAC/signature detects deliberate change: attacker lacks the key.
```

## Worked Example
**Problem.** Alice signs a digest `h = 42` with a toy RSA key `p=7, q=11, e=7, d=43` (so `n=77`). Bob verifies. Then Mallory changes the document so its digest becomes 43. Does the old signature still verify?

1. Sign: `s = 42^43 mod 77`. Compute with the Chinese remainder idea: mod 7, `42 = 0` so `s = 0 mod 7`; mod 11, `42 = 9`, and `9^43 = 9^(43 mod 10) = 9^3 = 729 = 729 - 66x11 = 3` so `s = 3 mod 11`. Find `s` with `s = 0 mod 7` and `s = 3 mod 11`: candidates 0, 7, 14: `14 mod 11 = 3`. So `s = 14`.
2. Verify: `14^7 mod 77`: mod 7 gives 0; mod 11, `14 = 3`, `3^7 = 2187 = 198 x 11 + 9`, so 9. `x = 0 mod 7` and `x = 9 mod 11`: 0, 7, 14, 21, 28, 35, 42: `42 mod 11 = 9`, so `x = 42`. It equals `h`: valid.
3. Mallory's document has digest 43, but `14^7 mod 77 = 42 != 43`, so verification fails.

You can confirm with `pow(42, 43, 77)` and `pow(14, 7, 77)`.

## Key Rules / Gotchas Recap
- Hash = fingerprint, no key; HMAC = keyed fingerprint; signature = private-key fingerprint.
- MD5 and SHA-1 are broken for collisions: use SHA-256/SHA-3 for integrity and signatures.
- Never `sha256(key + msg)`; use `hmac`.
- Compare secrets and tags with `hmac.compare_digest`, not `==`.
- Passwords: per-user random salt plus a slow KDF (scrypt, PBKDF2, bcrypt, Argon2). Never a plain fast hash.
- A hash alone cannot stop a determined attacker from tampering; a MAC or signature can.
- Trust in a signature is only as good as trust in the public key, so certificates and CAs exist.

## Why This Matters
Package integrity checks, API request signing (HMAC), JWT validation, password storage and certificate validation all use these primitives; mistakes here (fast password hashes, `==` on tags, disabled verification) are everyday security bugs. In AI engineering, model and dataset checksums protect the supply chain.
