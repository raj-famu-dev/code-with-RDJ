# Tags: #Python #FileIO #JSON #OsSysShutilSubprocess | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches the "talk to the operating system" modules: os (environment),
sys (argv, platform), shutil (copy/move/rmtree) and subprocess (run another
program safely). Everything destructive happens inside a temp directory.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

print("=== SECTION 1: os.environ ===")
print("type:", type(os.environ).__name__, "(dict-like, str -> str only)")
os.environ["RDJ_DEMO_VAR"] = "hello"           # affects THIS process and its children only
print("os.environ['RDJ_DEMO_VAR']:", os.environ["RDJ_DEMO_VAR"])
print("get with default:", os.environ.get("RDJ_DOES_NOT_EXIST", "<default>"))
try:
    os.environ["RDJ_NOPE"]
except KeyError as e:
    print("missing key via [] ->", type(e).__name__)
try:
    os.environ["RDJ_BAD"] = 5                   # type: ignore[assignment]
except TypeError as e:
    print("non-str value -> TypeError:", e)
print("getenv alias:", os.getenv("RDJ_DEMO_VAR"))
del os.environ["RDJ_DEMO_VAR"]
print("after del:", os.getenv("RDJ_DEMO_VAR"))
print("Secrets (API keys) belong in env vars, never in source code.")

print("\n=== SECTION 2: sys.argv, sys.platform, sys.version_info ===")
print("sys.argv[0] ends with this file:", sys.argv[0].endswith("_7_OsSysShutilAndSubprocess.py"))
print("extra args received:", sys.argv[1:], "<- empty when run with no arguments")
print("sys.platform (environment-dependent):", sys.platform)
print("Python >= 3.10:", sys.version_info >= (3, 10))
print("os.name (environment-dependent):", os.name)
print("sys.executable is a path to the running interpreter:", Path(sys.executable).is_file())

print("\n=== SECTION 3: shutil copy / move / rmtree on temp dirs ===")
tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)
src = base / "src"
src.mkdir()
(src / "a.txt").write_text("alpha", encoding="utf-8")
(src / "nested").mkdir()
(src / "nested" / "b.txt").write_text("beta", encoding="utf-8")

shutil.copy(src / "a.txt", base / "a_copy.txt")
print("copy:", (base / "a_copy.txt").read_text(encoding="utf-8"))
shutil.copytree(src, base / "src_backup")
print("copytree:", sorted(p.relative_to(base / "src_backup").as_posix()
                          for p in (base / "src_backup").rglob("*")))
try:
    shutil.copytree(src, base / "src_backup")      # TRAP: destination exists
except FileExistsError:
    print("copytree onto existing dir -> FileExistsError")
shutil.copytree(src, base / "src_backup", dirs_exist_ok=True)
print("dirs_exist_ok=True merges instead")
shutil.move(str(base / "a_copy.txt"), str(base / "moved.txt"))
print("move: old exists =", (base / "a_copy.txt").exists(), "| new exists =", (base / "moved.txt").exists())
os.remove(base / "moved.txt")                      # delete single file
try:
    os.rmdir(src)                                  # TRAP: dir not empty
except OSError as e:
    print("os.rmdir on non-empty dir ->", type(e).__name__)
shutil.rmtree(src)                                 # recursive delete (dangerous!)
print("rmtree removed src:", not src.exists())
print("RULE: only rmtree paths you built yourself; never a path from user input.")
print("disk usage keys:", list(shutil.disk_usage(base)._fields))

print("\n=== SECTION 4: subprocess.run with a list ===")
result = subprocess.run(
    [sys.executable, "--version"],                 # sys.executable = same interpreter
    capture_output=True, text=True, timeout=10, check=True,
)
print("returncode:", result.returncode)
print("stdout starts with 'Python':", result.stdout.startswith("Python"))
print("stdout (environment-dependent):", result.stdout.strip())
print("stderr empty:", result.stderr == "")
code = "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)"
r2 = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=10)
print("exit code:", r2.returncode, "| stdout:", repr(r2.stdout), "| stderr:", repr(r2.stderr))
try:
    subprocess.run([sys.executable, "-c", "raise SystemExit(5)"], check=True, timeout=10)
except subprocess.CalledProcessError as e:
    print("check=True raises CalledProcessError, returncode =", e.returncode)
try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.3)
except subprocess.TimeoutExpired:
    print("timeout=0.3 -> TimeoutExpired (child is killed)")
try:
    subprocess.run(["definitely-not-a-program-xyz"], timeout=5)
except FileNotFoundError:
    print("unknown program -> FileNotFoundError")

print("\n=== SECTION 5: why never shell=True with user input ===")
user_input = "hello; echo INJECTED"               # hostile-looking text
show_args = "import sys; print(sys.argv[1:])"
safe = subprocess.run([sys.executable, "-c", show_args, user_input],
                      capture_output=True, text=True, timeout=10)
print("list form passes it as ONE literal argument:", safe.stdout.strip())
print("With shell=True the string would go to /bin/sh, where ';' starts a second")
print("command. That is command injection. We deliberately do NOT run that here.")
print("Rule: pass a list, keep shell=False (the default), never build commands")
print("with f-strings from untrusted text.")

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
