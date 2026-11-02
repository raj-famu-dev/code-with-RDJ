# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches open(), file modes, encodings, and why the `with` statement exists.

Covers: modes (r, w, a, x, rb, wb), encoding= and the UTF-8 vs default trap,
what happens if you forget close(), and how `with` guarantees cleanup.
All files live in a temporary directory that is deleted at the end.
"""
import tempfile
from pathlib import Path

tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)

print("=== SECTION 1: open() and file modes ===")
p = base / "notes.txt"
f = open(p, "w", encoding="utf-8")      # "w" = write, TRUNCATES existing content
print("type of f:", type(f).__name__)
print("f.mode:", f.mode, "| f.closed:", f.closed)
f.write("first line\n")
f.close()                                # manual close: easy to forget!
print("after close, f.closed:", f.closed)

f = open(p, "a", encoding="utf-8")       # "a" = append, never truncates
f.write("second line\n")
f.close()

f = open(p, "r", encoding="utf-8")       # "r" = read (the default mode)
print("read back:", repr(f.read()))
f.close()

try:
    open(p, "x", encoding="utf-8")       # "x" = exclusive create, fails if exists
except FileExistsError as e:
    print("mode 'x' on existing file ->", type(e).__name__)

with open(base / "data.bin", "wb") as fb:   # "b" = bytes, no encoding allowed
    fb.write(bytes([0, 1, 2, 255]))
with open(base / "data.bin", "rb") as fb:
    print("binary read:", list(fb.read()))

print("\n=== SECTION 2: encodings and the default-encoding trap ===")
text = "café ✓"                  # 'cafe' with accent + check mark
with open(base / "utf8.txt", "w", encoding="utf-8") as fh:
    fh.write(text)
raw = (base / "utf8.txt").read_bytes()
print("bytes on disk (UTF-8):", raw)
print("byte count:", len(raw), "vs character count:", len(text))
# TRAP: opening without encoding= uses the platform default, which differs
# between machines (Windows often cp1252). Never rely on it.
with open(base / "utf8.txt", "r", encoding="latin-1") as fh:
    print("wrongly decoded as latin-1:", repr(fh.read()))
try:
    with open(base / "utf8.txt", "r", encoding="ascii") as fh:
        fh.read()
except UnicodeDecodeError as e:
    print("ascii decode ->", type(e).__name__)
print("FIX: always pass encoding='utf-8' explicitly")

print("\n=== SECTION 3: what happens WITHOUT `with` ===")
# Simulate an error between open() and close():
f = open(base / "leak2.txt", "w", encoding="utf-8")
try:
    f.write("data")
    raise RuntimeError("boom")
except RuntimeError:
    print("exception happened; f.closed =", f.closed, "(still open! leaked)")
f.close()                                        # we clean up manually here
print("manual cleanup done; f.closed =", f.closed)
print("Without `with`, every exit path needs its own close(), or you leak a handle.")

print("\n=== SECTION 4: `with` closes the file automatically ===")
with open(base / "safe.txt", "w", encoding="utf-8") as fh:
    fh.write("hello\n")
    print("inside with, closed =", fh.closed)
print("after with, closed =", fh.closed)

try:
    with open(base / "safe2.txt", "w", encoding="utf-8") as fh2:
        fh2.write("partial")
        raise RuntimeError("boom inside with")
except RuntimeError:
    print("exception inside with, but closed =", fh2.closed)
print("content flushed to disk:", (base / "safe2.txt").read_text(encoding="utf-8"))

with open(base / "a.txt", "w", encoding="utf-8") as fa, \
     open(base / "b.txt", "w", encoding="utf-8") as fb2:   # two resources at once
    fa.write("A")
    fb2.write("B")
print("two files in one with:", fa.closed, fb2.closed)

print("\n=== SECTION 5: opening a missing file ===")
try:
    with open(base / "nope.txt", encoding="utf-8") as fh:
        pass
except FileNotFoundError as e:
    print("FileNotFoundError, errno =", e.errno)

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
