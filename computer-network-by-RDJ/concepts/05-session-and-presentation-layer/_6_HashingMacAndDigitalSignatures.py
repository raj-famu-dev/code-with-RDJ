# Tags: #Python #ComputerNetworks #SessionLayer #PresentationLayer #HashingMacDigitalSignatures | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Hash functions, HMAC, salted password hashing, toy RSA digital signatures,
the certificate/CA chain idea, and a small tamper-detection demo."""
from __future__ import annotations

import hashlib
import hmac

print("NOTE: the RSA signature below is a TOY (tiny key, no padding). Insecure.\n")


# ===== SECTION 1: HASH PROPERTIES AND THE AVALANCHE EFFECT =====
print("===== SECTION 1: HASH PROPERTIES AND AVALANCHE =====")
print("A cryptographic hash: fixed-size digest, deterministic, fast to compute,")
print("one-way (preimage resistant), second-preimage and collision resistant.")
for s in [b"", b"abc"]:
    print(f"  SHA-256({s!r}) = {hashlib.sha256(s).hexdigest()}")
assert hashlib.sha256(b"abc").hexdigest().startswith("ba7816bf8f01cfea")
print("  check: OK (matches the FIPS 180 test vector for 'abc')")


def bits_differ(a: bytes, b: bytes) -> int:
    return bin(int.from_bytes(a, "big") ^ int.from_bytes(b, "big")).count("1")


h1 = hashlib.sha256(b"Pay Bob $100").digest()
h2 = hashlib.sha256(b"Pay Bob $101").digest()
print("  'Pay Bob $100' ->", h1.hex())
print("  'Pay Bob $101' ->", h2.hex())
print(f"  one character changed -> {bits_differ(h1, h2)} of 256 digest bits differ (avalanche; ~128 expected)")
print("  digest sizes: MD5 128 bits, SHA-1 160, SHA-256 256, SHA3-256 256")
print("  output is always 256 bits, even for 1 MB input:",
      len(hashlib.sha256(b"x" * 10 ** 6).digest()) * 8, "bits")


# ===== SECTION 2: MD5 AND SHA-1 STATUS =====
print("\n===== SECTION 2: MD5 / SHA-1 STATUS =====")
print("  MD5   : practical collision attacks published (2004); do NOT use for")
print("          signatures/certificates. Fine only for non-security checksums.")
print("  SHA-1 : practical collision demonstrated publicly in 2017 (SHAttered);")
print("          deprecated for signatures. Use SHA-256/SHA-3 instead.")
print("  Collisions break signatures; this is not the same as 'password hashes")
print("  can be reversed'. Still, neither is suitable for passwords (too fast).")
print("  md5('abc')  =", hashlib.md5(b"abc").hexdigest())
print("  sha1('abc') =", hashlib.sha1(b"abc").hexdigest())


# ===== SECTION 3: HMAC AND CONSTANT-TIME COMPARE =====
print("\n===== SECTION 3: HMAC =====")
key = b"shared-secret-key"
msg = b"transfer 100 to bob"
tag = hmac.new(key, msg, hashlib.sha256).hexdigest()
print("  HMAC-SHA256 tag:", tag)


def my_hmac(k: bytes, m: bytes) -> bytes:
    """HMAC from RFC 2104: H((K^opad) || H((K^ipad) || m)), block size 64."""
    if len(k) > 64:
        k = hashlib.sha256(k).digest()
    k = k.ljust(64, b"\x00")
    ipad = bytes(x ^ 0x36 for x in k)
    opad = bytes(x ^ 0x5C for x in k)
    return hashlib.sha256(opad + hashlib.sha256(ipad + m).digest()).digest()


assert my_hmac(key, msg).hex() == tag
print("  check: OK (own RFC 2104 implementation equals hmac module)")
print("  Why not sha256(key + msg)? Length-extension attacks on Merkle-Damgard hashes.")
good = hmac.new(key, msg, hashlib.sha256).digest()
print("  verify with hmac.compare_digest:", hmac.compare_digest(good, bytes.fromhex(tag)))
print("  Use compare_digest, not ==: == can stop at the first differing byte,")
print("  leaking timing information about how many leading bytes were right.")
recomputed = hmac.new(key, b"transfer 9999 to eve", hashlib.sha256).digest()
print("  tampered message checked against the ORIGINAL tag accepted?:",
      hmac.compare_digest(recomputed, good))
print("  (an attacker without the key cannot produce a valid tag for new text)")


# ===== SECTION 4: SALTED PASSWORD HASHING =====
print("\n===== SECTION 4: SALTED PASSWORD HASHING =====")
pw = b"hunter2"
fast = hashlib.sha256(pw).hexdigest()
print("  TRAP plain sha256(password):", fast[:24] + "...")
print("    identical passwords -> identical hashes, and attackers use precomputed")
print("    tables / billions of guesses per second on GPUs.")
salt1, salt2 = bytes.fromhex("00" * 16), bytes.fromhex("11" * 16)  # fixed ONLY for repeatable output
d1 = hashlib.pbkdf2_hmac("sha256", pw, salt1, 100_000)
d2 = hashlib.pbkdf2_hmac("sha256", pw, salt2, 100_000)
print("  PBKDF2 salt A:", d1.hex()[:24] + "...")
print("  PBKDF2 salt B:", d2.hex()[:24] + "...  (same password, different hash)")
assert d1 != d2
s = hashlib.scrypt(pw, salt=salt1, n=2 ** 14, r=8, p=1, dklen=32)
print("  scrypt (n=2^14, r=8, p=1):", s.hex()[:24] + "...")
assert hashlib.scrypt(pw, salt=salt1, n=2 ** 14, r=8, p=1, dklen=32) == s
ok = hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", pw, salt1, 100_000), d1)
bad = hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", b"wrong", salt1, 100_000), d1)
print(f"  verify right password: {ok}; wrong password: {bad}")
print("  In real code: salt = os.urandom(16) per user, stored next to the hash;")
print("  deliberately slow hashing (work factor) makes guessing expensive.")


# ===== SECTION 5: DIGITAL SIGNATURE WITH TOY RSA =====
print("\n===== SECTION 5: DIGITAL SIGNATURE (TOY RSA) =====")
n, e, d = 3233, 17, 2753  # p=61, q=53 from the RSA module
print("  sign = hash with private key; verify = check with public key.")
doc = b"I owe Raj $5"
digest = int.from_bytes(hashlib.sha256(doc).digest(), "big") % n  # shrink to fit toy n
sig = pow(digest, d, n)
print(f"  digest (mod n) = {digest}; signature = digest^d mod n = {sig}")
print(f"  verify: sig^e mod n = {pow(sig, e, n)} == digest ? {pow(sig, e, n) == digest}")
doc2 = b"I owe Raj $500"
digest2 = int.from_bytes(hashlib.sha256(doc2).digest(), "big") % n
print(f"  modified doc digest = {digest2}; signature still valid? {pow(sig, e, n) == digest2}")
print("  TRAP: with n=3233 there are only 3233 possible digests, so collisions are")
print("  trivial; real signatures use 2048+ bit keys and padding (PSS) on a full hash.")
print("  Signature gives integrity + authentication + non-repudiation (HMAC does not")
print("  give non-repudiation: both sides hold the same key).")


# ===== SECTION 6: CERTIFICATES AND THE CA CHAIN =====
print("\n===== SECTION 6: CERTIFICATE CHAIN CONCEPT =====")
# Toy: each certificate = (subject, subject public key, issuer, signature by issuer).
# One toy RSA keypair per party, all tiny and insecure; the point is the chain.
def make_key(p_: int, q_: int, e_: int) -> tuple[int, int, int]:
    return p_ * q_, e_, pow(e_, -1, (p_ - 1) * (q_ - 1))


keys = {
    "RootCA": make_key(61, 53, 17),
    "InterCA": make_key(67, 71, 13),
    "site.example": make_key(73, 79, 5),
}


def cert_digest(subject: str, pub: tuple[int, int], issuer: str, mod: int) -> int:
    body = f"{subject}|{pub[0]}|{pub[1]}|{issuer}".encode()
    return int.from_bytes(hashlib.sha256(body).digest(), "big") % mod


def issue(subject: str, issuer: str) -> dict:
    sn, se, _ = keys[subject]
    isn, _, isd = keys[issuer]
    dig = cert_digest(subject, (sn, se), issuer, isn)
    return {"subject": subject, "pub": (sn, se), "issuer": issuer, "sig": pow(dig, isd, isn)}


def check(cert: dict, issuer_pub: tuple[int, int]) -> bool:
    isn, ise = issuer_pub
    dig = cert_digest(cert["subject"], cert["pub"], cert["issuer"], isn)
    return pow(cert["sig"], ise, isn) == dig


chain = [issue("site.example", "InterCA"), issue("InterCA", "RootCA"), issue("RootCA", "RootCA")]
trust_store = {"RootCA": (keys["RootCA"][0], keys["RootCA"][1])}  # shipped with the OS/browser
print("  chain: site.example <- InterCA <- RootCA (self-signed, in trust store)")
ok_chain = True
for i, cert in enumerate(chain):
    issuer_pub = trust_store["RootCA"] if cert["issuer"] == "RootCA" else chain[i + 1]["pub"]
    r = check(cert, issuer_pub)
    ok_chain &= r
    print(f"  {cert['subject']:<13} signed by {cert['issuer']:<7} signature valid: {r}")
print("  chain trusted:", ok_chain and chain[-1]["subject"] in trust_store)
forged = dict(chain[0], pub=(keys["site.example"][0], 7))  # attacker swaps the public key
print("  forged cert (key swapped) valid?:", check(forged, chain[1]["pub"]))
print("  Real X.509 certs also carry validity dates, names (SAN), key usage and are")
print("  revoked via CRL/OCSP. Toy keys here are tiny and unsafe.")


# ===== SECTION 7: TAMPER DETECTION DEMO =====
print("\n===== SECTION 7: TAMPER DETECTION =====")
log_lines = ["login alice", "transfer 10", "logout alice"]
prev = b"\x00" * 32
chain_hashes = []
for line in log_lines:
    prev = hashlib.sha256(prev + line.encode()).digest()  # each entry covers all before
    chain_hashes.append(prev.hex()[:12])
print("  hash chain:", chain_hashes)
tampered = ["login alice", "transfer 9999", "logout alice"]
prev = b"\x00" * 32
new_hashes = []
for line in tampered:
    prev = hashlib.sha256(prev + line.encode()).digest()
    new_hashes.append(prev.hex()[:12])
print("  tampered  :", new_hashes)
print("  first mismatch at entry index:",
      next(i for i, (a, b) in enumerate(zip(chain_hashes, new_hashes)) if a != b))
print("  A plain hash only detects accidental change (attacker recomputes it).")
print("  A MAC/signature detects deliberate change: attacker lacks the key.")
