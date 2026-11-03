# Tags: #Python #FileIO #JSON #ReadingWritingText | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches reading and writing text files.

Covers: read(), readline(), readlines(), iterating a file line by line,
write() vs writelines() (which adds NO newlines), append mode, newline
handling, and the "\\n stays in the line" trap.
"""
import tempfile
from pathlib import Path

tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)
p = base / "poem.txt"

print("=== SECTION 1: write() and the missing-newline trap ===")
with open(p, "w", encoding="utf-8") as f:
    n = f.write("roses are red")       # write() returns number of characters
    f.write("violets are blue")        # TRAP: no newline added automatically
print("write() returned:", n)
print("content:", repr(p.read_text(encoding="utf-8")))
with open(p, "w", encoding="utf-8") as f:
    f.write("roses are red\n")
    f.write("violets are blue\n")
    f.write("python is neat\n")
print("fixed content:", repr(p.read_text(encoding="utf-8")))

print("\n=== SECTION 2: read(), readline(), readlines() ===")
with open(p, encoding="utf-8") as f:
    print("read():", repr(f.read()))
    print("read() again (at EOF):", repr(f.read()))
    f.seek(0)                                # rewind to start
    print("readline():", repr(f.readline()))
    print("readline():", repr(f.readline()))
    f.seek(0)
    print("read(5):", repr(f.read(5)), "<- 5 characters only")
    f.seek(0)
    print("readlines():", f.readlines())

print("\n=== SECTION 3: iterating a file (the idiomatic way) ===")
with open(p, encoding="utf-8") as f:
    for lineno, line in enumerate(f, start=1):   # lazy: one line at a time
        print(lineno, repr(line))
print("TRAP: each line keeps its trailing '\\n'. Use .rstrip('\\n') or .strip():")
with open(p, encoding="utf-8") as f:
    print([line.rstrip("\n") for line in f])

print("\n=== SECTION 4: writelines() adds NO newlines ===")
lines = ["alpha", "beta", "gamma"]
q = base / "lines.txt"
with open(q, "w", encoding="utf-8") as f:
    f.writelines(lines)                      # TRAP: glued together
print("writelines(no \\n):", repr(q.read_text(encoding="utf-8")))
with open(q, "w", encoding="utf-8") as f:
    f.writelines(line + "\n" for line in lines)   # FIX
print("writelines(with \\n):", repr(q.read_text(encoding="utf-8")))
with open(q, "w", encoding="utf-8") as f:
    print(*lines, sep="\n", file=f)          # print(file=...) adds newline for you
print("print(file=f):", repr(q.read_text(encoding="utf-8")))

print("\n=== SECTION 5: append mode ===")
with open(q, "a", encoding="utf-8") as f:
    f.write("delta\n")
print("after append:", q.read_text(encoding="utf-8").splitlines())
with open(q, "w", encoding="utf-8") as f:    # TRAP: 'w' wipes the file
    f.write("only this\n")
print("after accidental 'w':", q.read_text(encoding="utf-8").splitlines())

print("\n=== SECTION 6: newline handling (\\n vs \\r\\n) ===")
win = base / "windows.txt"
win.write_bytes(b"one\r\ntwo\r\nthree")     # raw Windows-style bytes
with open(win, encoding="utf-8") as f:      # universal newlines: \r\n -> \n
    print("text mode read:", repr(f.read()))
with open(win, "rb") as f:
    print("binary mode read:", f.read())
with open(win, encoding="utf-8", newline="") as f:   # newline='' keeps as-is
    print("newline='' read:", repr(f.read()))
out = base / "out.txt"
with open(out, "w", encoding="utf-8", newline="\n") as f:   # force \n on write
    f.write("a\nb\n")
print("bytes written with newline='\\n':", out.read_bytes())
print("splitlines():", "x\ny\r\nz".splitlines(), "<- handles all newline styles")

print("\n=== SECTION 7: reading a big file safely ===")
big = base / "big.txt"
with open(big, "w", encoding="utf-8") as f:
    for i in range(1000):
        f.write(f"row {i}\n")
count = 0
with open(big, encoding="utf-8") as f:
    for _ in f:                              # never loads all 1000 lines at once
        count += 1
print("counted lines lazily:", count)
print("read() / readlines() load EVERYTHING into memory; iteration does not.")

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
