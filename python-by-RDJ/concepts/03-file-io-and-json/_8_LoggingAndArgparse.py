# Tags: #Python #FileIO #JSON #LoggingArgparse | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches the logging module (levels, handlers, formatters, logger hierarchy)
and argparse (positional/optional args, types, choices, flags, errors).

argparse always parses an explicit list of strings here, never the real
sys.argv, so the output is deterministic.
"""
import argparse
import contextlib
import io
import logging
import tempfile
from pathlib import Path

print("=== SECTION 1: logging levels and the default threshold ===")
print("levels:", {n: logging.getLevelName(n) for n in (10, 20, 30, 40, 50)})
root_default = logging.getLogger().level
print("root logger default level:", logging.getLevelName(root_default), "<- DEBUG/INFO hidden by default")

print("\n=== SECTION 2: a logger with a handler and format ===")
stream = io.StringIO()                                # capture instead of printing to stderr
handler = logging.StreamHandler(stream)
handler.setFormatter(logging.Formatter("%(levelname)-8s %(name)s: %(message)s"))
log = logging.getLogger("rdj.demo")
log.addHandler(handler)
log.setLevel(logging.DEBUG)
log.propagate = False                                 # do not also hit the root logger
log.debug("debug message")
log.info("info message")
log.warning("disk at %d%%", 91)                       # lazy %-style args
log.error("something failed")
print(stream.getvalue(), end="")
print("TRAP: use log.info('x=%s', x), not f-strings: formatting is skipped when the level is off.")

print("\n=== SECTION 3: handler level vs logger level ===")
stream2 = io.StringIO()
h2 = logging.StreamHandler(stream2)
h2.setLevel(logging.WARNING)                          # handler filters again
h2.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
log2 = logging.getLogger("rdj.filtered")
log2.setLevel(logging.DEBUG)
log2.addHandler(h2)
log2.propagate = False
log2.debug("hidden")
log2.info("hidden")
log2.warning("shown")
log2.critical("shown too")
print(stream2.getvalue(), end="")

print("\n=== SECTION 4: logging to a file and exceptions ===")
tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)
logfile = base / "app.log"
fh = logging.FileHandler(logfile, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(levelname)s|%(funcName)s|%(message)s"))
flog = logging.getLogger("rdj.file")
flog.setLevel(logging.INFO)
flog.addHandler(fh)
flog.propagate = False

def risky() -> None:
    try:
        1 / 0
    except ZeroDivisionError:
        flog.exception("caught a problem")            # ERROR level + traceback

flog.info("starting")
risky()
fh.close()
flog.removeHandler(fh)
lines = logfile.read_text(encoding="utf-8").splitlines()
print("first line :", lines[0])
print("second line:", lines[1])
print("traceback present:", any("ZeroDivisionError" in ln for ln in lines))

print("\n=== SECTION 5: logger hierarchy (dots) ===")
parent = logging.getLogger("shop")
child = logging.getLogger("shop.cart")
print("child.parent is parent:", child.parent is parent)
stream3 = io.StringIO()
h3 = logging.StreamHandler(stream3)
h3.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
parent.addHandler(h3)
parent.setLevel(logging.INFO)
child.info("item added")                              # no handler on child; propagates up
print(stream3.getvalue(), end="")
print("effective level of child:", logging.getLevelName(child.getEffectiveLevel()))
parent.removeHandler(h3)
print("Libraries should call getLogger(__name__) and never configure handlers.")

print("\n=== SECTION 6: argparse basics ===")
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="tool", description="Demo CLI")
    ap.add_argument("filename")                                # positional, required
    ap.add_argument("-n", "--count", type=int, default=1)      # optional, typed
    ap.add_argument("-v", "--verbose", action="store_true")    # flag, no value
    ap.add_argument("--mode", choices=["fast", "slow"], default="fast")
    ap.add_argument("--tag", action="append", default=[])      # repeatable
    return ap

ap = build_parser()
args = ap.parse_args(["data.txt", "-n", "3", "-v", "--tag", "a", "--tag", "b"])
print("parsed:", args)
print("args.count is int:", isinstance(args.count, int), "| args.verbose:", args.verbose)
defaults = ap.parse_args(["only.txt"])
print("defaults:", vars(defaults))
print("sys.argv was NOT used; we passed a list.")

print("\n=== SECTION 7: argparse errors exit with code 2 ===")
def try_parse(argv: list[str]) -> None:
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            build_parser().parse_args(argv)
    except SystemExit as e:                           # argparse calls sys.exit on error
        print(f"argv={argv} -> exit code {e.code}")
        print("   ", err.getvalue().strip().splitlines()[-1])

try_parse([])                                         # missing positional
try_parse(["f.txt", "-n", "abc"])                     # wrong type
try_parse(["f.txt", "--mode", "medium"])              # not in choices
print("TRAP: parse_args() calls sys.exit() on bad input; tests must catch SystemExit.")

print("\n=== SECTION 8: subcommands ===")
top = argparse.ArgumentParser(prog="git-lite")
sub = top.add_subparsers(dest="command", required=True)
add = sub.add_parser("add")
add.add_argument("path")
commit = sub.add_parser("commit")
commit.add_argument("-m", "--message", required=True)
print(top.parse_args(["add", "file.py"]))
print(top.parse_args(["commit", "-m", "first"]))

print("\n=== SECTION 9: wiring both together ===")
def run(argv: list[str]) -> str:
    p = argparse.ArgumentParser(prog="app")
    p.add_argument("-v", "--verbose", action="store_true")
    ns = p.parse_args(argv)
    lg = logging.getLogger("rdj.app")
    out = io.StringIO()
    hh = logging.StreamHandler(out)
    hh.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    lg.handlers = [hh]
    lg.propagate = False
    lg.setLevel(logging.DEBUG if ns.verbose else logging.WARNING)
    lg.debug("detail")
    lg.warning("heads up")
    return out.getvalue()

print("without -v:", repr(run([])))
print("with -v   :", repr(run(["-v"])))

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
