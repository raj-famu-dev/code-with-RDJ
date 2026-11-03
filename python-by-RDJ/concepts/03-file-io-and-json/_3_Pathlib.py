# Tags: #Python #FileIO #JSON #Pathlib | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches pathlib.Path: building paths, inspecting them, creating folders,
globbing, reading/writing, and how it compares to os.path and Java NIO.2.

Everything happens inside a temporary directory that is deleted at the end.
"""
import os
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)

print("=== SECTION 1: building paths with / and joinpath ===")
cfg = base / "project" / "config" / "app.json"     # the / operator joins parts
same = base.joinpath("project", "config", "app.json")
print("/ operator == joinpath():", cfg == same)
rel = cfg.relative_to(base)
print("relative path:", rel.as_posix())
print("type:", type(cfg).__name__, "(PosixPath on Linux/macOS, WindowsPath on Windows)")
# TRAP: an absolute right-hand side REPLACES everything on the left
print("base / '/etc' ->", PurePosixPath("/a/b") / "/etc", "<- left side discarded!")

print("\n=== SECTION 2: path anatomy ===")
p = PurePosixPath("/data/logs/server.2024.log.gz")
print("name  :", p.name)
print("stem  :", p.stem)
print("suffix:", p.suffix)
print("suffixes:", p.suffixes)
print("parent:", p.parent)
print("parts :", p.parts)
print("with_suffix('.txt'):", p.with_suffix(".txt"))
print("with_name('x.bin') :", p.with_name("x.bin"))
w = PureWindowsPath("C:/Users/rdj/file.txt")
print("Windows flavour    :", w, "| drive:", w.drive)

print("\n=== SECTION 3: mkdir(parents=True, exist_ok=True) ===")
target = base / "a" / "b" / "c"
try:
    target.mkdir()                           # TRAP: parents missing
except FileNotFoundError:
    print("mkdir() without parents -> FileNotFoundError")
target.mkdir(parents=True, exist_ok=True)
target.mkdir(parents=True, exist_ok=True)    # second call is fine with exist_ok
print("created:", target.relative_to(base).as_posix(), "| is_dir:", target.is_dir())

print("\n=== SECTION 4: exists / is_file / is_dir / stat ===")
f = target / "hello.txt"
print("exists before write:", f.exists())
f.write_text("hello, pathlib\n", encoding="utf-8")
print("exists:", f.exists(), "| is_file:", f.is_file(), "| is_dir:", f.is_dir())
st = f.stat()
print("size in bytes:", st.st_size)
print("mtime is a float seconds-since-epoch:", isinstance(st.st_mtime, float))
print("read_text:", repr(f.read_text(encoding="utf-8")))
print("read_bytes:", f.read_bytes())

print("\n=== SECTION 5: glob, rglob, iterdir ===")
for name in ["x.py", "y.py", "z.txt"]:
    (base / name).write_text(name, encoding="utf-8")
(base / "sub").mkdir()
(base / "sub" / "deep.py").write_text("deep", encoding="utf-8")
print("iterdir (sorted):", sorted(c.name for c in base.iterdir()))
print("glob('*.py')    :", sorted(c.name for c in base.glob("*.py")))
print("rglob('*.py')   :", sorted(c.relative_to(base).as_posix() for c in base.rglob("*.py")))
print("glob() returns a lazy iterator, not a list:", not isinstance(base.glob("*"), list))

print("\n=== SECTION 6: rename, delete ===")
src = base / "x.py"
dst = base / "renamed.py"
src.rename(dst)
print("after rename x.py exists:", src.exists(), "| renamed.py exists:", dst.exists())
dst.unlink()                                  # delete a file
print("after unlink exists:", dst.exists())
dst.unlink(missing_ok=True)                   # no error if already gone
print("unlink(missing_ok=True) did not raise")
(base / "sub" / "deep.py").unlink()
(base / "sub").rmdir()                        # rmdir only works on EMPTY dirs
print("rmdir on empty dir ok")

print("\n=== SECTION 7: pathlib vs os.path ===")
old = os.path.join(str(base), "a", "b", "c", "hello.txt")
new = base / "a" / "b" / "c" / "hello.txt"
print("os.path.join == Path /:", old == str(new))
print("os.path.basename:", os.path.basename(old), "| Path.name:", new.name)
print("os.path.splitext:", os.path.splitext(old)[1], "| Path.suffix:", new.suffix)
print("os.path.exists:", os.path.exists(old), "| Path.exists:", new.exists())
print("os.fspath(Path) gives a str:", isinstance(os.fspath(new), str))

print("\n=== SECTION 8: resolve and the current directory ===")
odd = base / "a" / ".." / "a" / "b"
print("unresolved contains '..':", ".." in odd.parts)
print("resolved equals plain path:", odd.resolve() == (base / "a" / "b").resolve())
print("Path.cwd() is absolute:", Path.cwd().is_absolute())
print("Path('rel').is_absolute():", Path("rel").is_absolute())

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
