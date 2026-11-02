# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches the csv module: reader/writer, DictReader/DictWriter, quoting rules,
and the two classic traps: naive split(',') and forgetting newline=''.
"""
import csv
import io
import tempfile
from pathlib import Path

tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)
p = base / "people.csv"

print("=== SECTION 1: csv.writer ===")
rows = [
    ["name", "age", "city"],
    ["Ada", 36, "London"],
    ["Linus", 54, "Portland"],
]
with open(p, "w", newline="", encoding="utf-8") as f:   # newline='' is REQUIRED
    w = csv.writer(f)
    w.writerow(rows[0])
    w.writerows(rows[1:])
print("raw bytes on disk:", p.read_bytes())
print("csv.writer ends rows with \\r\\n by default (RFC 4180).")

print("\n=== SECTION 2: csv.reader (everything is a string) ===")
with open(p, newline="", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)
with open(p, newline="", encoding="utf-8") as f:
    header, *data = list(csv.reader(f))
print("age column types:", {type(r[1]).__name__ for r in data}, "<- convert yourself")
print("sum of ages:", sum(int(r[1]) for r in data))

print("\n=== SECTION 3: DictReader and DictWriter ===")
with open(p, newline="", encoding="utf-8") as f:
    for rec in csv.DictReader(f):
        print(dict(rec))
q = base / "scores.csv"
with open(q, "w", newline="", encoding="utf-8") as f:
    dw = csv.DictWriter(f, fieldnames=["student", "score"])
    dw.writeheader()
    dw.writerow({"student": "Mia", "score": 91})
    dw.writerow({"student": "Noah", "score": 78})
with open(q, newline="", encoding="utf-8") as f:
    best = max(csv.DictReader(f), key=lambda r: int(r["score"]))
print("best:", best["student"], best["score"])
try:
    with open(q, "w", newline="", encoding="utf-8") as f:
        dw = csv.DictWriter(f, fieldnames=["student", "score"])
        dw.writerow({"student": "X", "grade": 1})       # unknown key
except ValueError as e:
    print("extra key ->", type(e).__name__ + ":", e)

print("\n=== SECTION 4: TRAP - naive split(',') vs real CSV quoting ===")
tricky = 'id,quote\n1,"Hello, world"\n2,"She said ""hi"""\n'
naive = [line.split(",") for line in tricky.splitlines()]
print("naive split :", naive[1], "<- WRONG: 3 fields, comma inside quotes broke it")
proper = list(csv.reader(io.StringIO(tricky)))
print("csv.reader  :", proper[1])
print("escaped quote:", proper[2])

print("\n=== SECTION 5: writer quoting rules ===")
out = io.StringIO()
csv.writer(out).writerow(["plain", "has,comma", 'has "quote"', "multi\nline"])
print("QUOTE_MINIMAL (default):", repr(out.getvalue()))
out = io.StringIO()
csv.writer(out, quoting=csv.QUOTE_ALL).writerow(["a", 1, 2.5])
print("QUOTE_ALL              :", repr(out.getvalue()))
out = io.StringIO()
csv.writer(out, quoting=csv.QUOTE_NONNUMERIC).writerow(["a", 1, 2.5])
print("QUOTE_NONNUMERIC       :", repr(out.getvalue()))
out = io.StringIO()
csv.writer(out, delimiter=";").writerow(["x", "y;z"])
print("delimiter=';'          :", repr(out.getvalue()))

print("\n=== SECTION 6: TRAP - newline='' ===")
note = base / "note.csv"
with open(note, "w", newline="", encoding="utf-8") as f:    # correct
    csv.writer(f).writerow(["a", "b"])
print("with newline=''   :", note.read_bytes())
# Without newline='', text mode would translate '\n' to the OS line ending.
# On Windows that turns '\r\n' into '\r\r\n' (a blank row between every row).
# We simulate that translation with an in-memory buffer so the output is the
# same on every OS:
simulated = "a,b\r\n".replace("\n", "\r\n")
print("Windows w/o newline='' would write:", repr(simulated), "<- doubled \\r")
print("Also: embedded newlines inside quoted fields only round-trip with newline=''.")
with open(note, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["multi\nline", "x"])
with open(note, newline="", encoding="utf-8") as f:
    print("round trip:", list(csv.reader(f)))

print("\n=== SECTION 7: dialects and missing columns ===")
tsv = io.StringIO("a\tb\n1\t2\n")
print("TSV via delimiter:", list(csv.reader(tsv, delimiter="\t")))
short = io.StringIO("a,b,c\n1,2\n")
print("short row DictReader:", dict(next(csv.DictReader(short))), "<- missing = None")
long = io.StringIO("a,b\n1,2,3\n")
print("long row DictReader :", dict(next(csv.DictReader(long))), "<- extras under None key")

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
