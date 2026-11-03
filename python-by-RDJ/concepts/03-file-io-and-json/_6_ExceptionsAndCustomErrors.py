# Tags: #Python #FileIO #JSON #ExceptionsCustomErrors | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches Python exception handling: try/except/else/finally, multiple except
clauses, `raise ... from`, custom exception hierarchies, EAFP vs LBYL, and
handling missing / empty / corrupt files.
"""
import json
import tempfile
from pathlib import Path

print("=== SECTION 1: try / except / else / finally ===")
def divide(a: int, b: int) -> float | None:
    try:
        result = a / b
    except ZeroDivisionError as e:
        print("  except ran:", e)
        return None
    else:                                  # runs ONLY if try raised nothing
        print("  else ran: no error")
        return result
    finally:                               # ALWAYS runs, even after return
        print("  finally ran")

print("divide(6, 3):")
print(" ->", divide(6, 3))
print("divide(1, 0):")
print(" ->", divide(1, 0))

print("\n=== SECTION 2: multiple except clauses and order ===")
def parse(value: str) -> int:
    return int(value)

for raw in ["42", "abc", None]:
    try:
        print("parsed:", parse(raw))                    # type: ignore[arg-type]
    except ValueError as e:
        print("ValueError:", e)
    except (TypeError, KeyError) as e:                  # tuple = one handler, several types
        print("TypeError/KeyError:", type(e).__name__)
# TRAP: order matters, first matching clause wins. Catch SPECIFIC before GENERAL.
try:
    open("/definitely/not/here.txt", encoding="utf-8")
except OSError:
    print("FileNotFoundError is a subclass of OSError:", issubclass(FileNotFoundError, OSError))
print("bare `except:` also catches KeyboardInterrupt; prefer `except Exception`.")

print("\n=== SECTION 3: custom exception hierarchy ===")
class AppError(Exception):
    """Base class for every error this app raises on purpose."""

class ConfigError(AppError):
    def __init__(self, message: str, path: str | None = None) -> None:
        super().__init__(message)
        self.path = path

class ConfigMissingError(ConfigError):
    pass

class ConfigCorruptError(ConfigError):
    pass

for exc in (ConfigMissingError("no file", "a.json"), ConfigCorruptError("bad json")):
    try:
        raise exc
    except ConfigMissingError as e:
        print("missing handler:", e, "| path =", e.path)
    except ConfigError as e:                  # parent catches the rest of the family
        print("generic config handler:", e, "| path =", e.path)
print("MRO:", [c.__name__ for c in ConfigMissingError.__mro__])

print("\n=== SECTION 4: raise ... from (exception chaining) ===")
tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)

def load_config(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ConfigMissingError("config file not found", str(path.name)) from e
    except json.JSONDecodeError as e:
        raise ConfigCorruptError(f"invalid JSON: {e.msg}", str(path.name)) from e

try:
    load_config(base / "app.json")
except ConfigError as e:
    print("caught:", type(e).__name__, "-", e)
    print("  __cause__:", type(e.__cause__).__name__)
    print("  __suppress_context__:", e.__suppress_context__)
try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise ValueError("replacement") from None          # hide the original
except ValueError as e:
    print("raise from None -> __cause__:", e.__cause__)
print("Bare `raise` inside except re-raises the SAME exception unchanged.")

print("\n=== SECTION 5: EAFP vs LBYL ===")
d = {"a": 1}
# LBYL: Look Before You Leap
if "b" in d:
    val = d["b"]
else:
    val = 0
print("LBYL:", val)
# EAFP: Easier to Ask Forgiveness than Permission (Pythonic)
try:
    val = d["b"]
except KeyError:
    val = 0
print("EAFP:", val)
print("dict.get is the shortest:", d.get("b", 0))
p = base / "race.txt"
print("LBYL file race: exists() ->", p.exists(), "(file could appear/vanish before open!)")
try:
    p.read_text(encoding="utf-8")
except FileNotFoundError:
    print("EAFP: just try it; no race window between check and use")

print("\n=== SECTION 6: missing, empty and corrupt files ===")
(base / "good.json").write_text('{"port": 8080}', encoding="utf-8")
(base / "empty.json").write_text("", encoding="utf-8")
(base / "corrupt.json").write_text('{"port": ', encoding="utf-8")
(base / "dir.json").mkdir()
for name in ["good.json", "missing.json", "empty.json", "corrupt.json", "dir.json"]:
    try:
        cfg = load_config(base / name)
    except ConfigMissingError as e:
        print(f"{name:13} -> MISSING  ({e})")
    except ConfigCorruptError as e:
        print(f"{name:13} -> CORRUPT  ({e})")
    except OSError as e:
        print(f"{name:13} -> OS ERROR ({type(e).__name__})")
    else:
        print(f"{name:13} -> OK {cfg}")

print("\n=== SECTION 7: finally for cleanup; assert is not validation ===")
def process() -> None:
    f = open(base / "work.txt", "w", encoding="utf-8")
    try:
        f.write("x")
        raise RuntimeError("fail midway")
    finally:
        f.close()
        print("  finally: file closed =", f.closed)
try:
    process()
except RuntimeError as e:
    print("propagated:", e)
print("`with` is just try/finally packaged (see _1_OpenAndWithStatement).")
print("Use `raise ValueError` for input checks, not `assert`: python -O strips asserts.")

print("\n=== SECTION 8: ExceptionGroup (3.11+), a brief look ===")
try:
    raise ExceptionGroup("batch", [ValueError("v"), TypeError("t")])
except* ValueError as eg:
    print("except* ValueError got:", [type(x).__name__ for x in eg.exceptions])
except* TypeError as eg:
    print("except* TypeError got:", [type(x).__name__ for x in eg.exceptions])

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
