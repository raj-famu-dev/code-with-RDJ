# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Modules and packages: builds a small package in a temp directory at runtime,
imports it via sys.path and importlib, shows __name__ == "__main__", __all__,
and relative imports. Virtual environments/pip are explained in the .md only."""
import importlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


# ===== SECTION 1: BUILD A PACKAGE ON DISK =====
print("===== SECTION 1: BUILD A PACKAGE IN A TEMP DIRECTORY =====")
root = Path(tempfile.mkdtemp(prefix="rdj_pkg_"))
pkg = root / "shapes"
pkg.mkdir()


def write(path: Path, body: str) -> None:
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")


write(pkg / "__init__.py", '''
    """shapes package."""
    from .circle import area as circle_area  # relative import
    from .utils import PI

    __all__ = ["circle_area", "PI"]
    print("  (shapes/__init__.py ran)")
''')
write(pkg / "utils.py", '''
    PI = 3.14159
    _private_helper = "hidden from star-imports"
    visible = "included only if listed in __all__ or no __all__ exists"
''')
write(pkg / "circle.py", '''
    from .utils import PI  # sibling module via relative import

    __all__ = ["area"]

    def area(r: float) -> float:
        return PI * r * r

    if __name__ == "__main__":
        print("circle.py run directly as a script, area(1) =", area(1))
    else:
        print("  (circle.py imported, __name__ is %r)" % __name__)
''')
print("files:", sorted(p.relative_to(root).as_posix() for p in pkg.iterdir()))

try:
    # ===== SECTION 2: IMPORT IT VIA sys.path =====
    print("\n===== SECTION 2: IMPORT VIA sys.path =====")
    try:
        import shapes  # type: ignore  # noqa: F401
    except ModuleNotFoundError as e:
        print("Before sys.path change ->", e)
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    import shapes  # type: ignore  # noqa: E402
    print("shapes.circle_area(2):", shapes.circle_area(2))
    print("shapes.__name__:", shapes.__name__)
    print("shapes.__all__:", shapes.__all__)
    print("Second import is cached, no re-run:", importlib.import_module("shapes") is shapes)

    # ===== SECTION 3: importlib =====
    print("\n===== SECTION 3: importlib.import_module =====")
    util = importlib.import_module("shapes.utils")
    print("PI from dynamic import:", util.PI)
    name = "shapes.circle"
    print(name, "in sys.modules:", name in sys.modules)
    reloaded = importlib.reload(util)
    print("reload returns the same module object:", reloaded is util)

    # ===== SECTION 4: __all__ AND STAR IMPORT =====
    print("\n===== SECTION 4: __all__ AND from X import * =====")
    ns1: dict = {}
    exec("from shapes import *", ns1)
    print("names from 'shapes import *':", sorted(k for k in ns1 if not k.startswith("__")))
    ns2: dict = {}
    exec("from shapes.utils import *", ns2)  # no __all__: all public names
    print("names from 'shapes.utils import *':", sorted(k for k in ns2 if not k.startswith("__")))
    print("(underscore names skipped when there is no __all__)")

    # ===== SECTION 5: __name__ == "__main__" =====
    print("\n===== SECTION 5: __name__ == '__main__' =====")
    print("this file's __name__:", __name__)
    result = subprocess.run(
        [sys.executable, "-m", "shapes.circle"],
        cwd=root, capture_output=True, text=True, timeout=10,
    )
    print("python -m shapes.circle ->", result.stdout.strip())

    # ===== SECTION 6: TRAP - RELATIVE IMPORT IN A SCRIPT =====
    print("\n===== SECTION 6: TRAP - RELATIVE IMPORT RUN AS A SCRIPT =====")
    result = subprocess.run(
        [sys.executable, str(pkg / "circle.py")],
        cwd=root, capture_output=True, text=True, timeout=10,
    )
    print("python shapes/circle.py ->", result.stderr.strip().splitlines()[-1])
    print("Fix: run with -m from the project root, or use an absolute import.")
finally:
    # ===== SECTION 7: CLEANUP =====
    print("\n===== SECTION 7: CLEANUP =====")
    if str(root) in sys.path:
        sys.path.remove(str(root))
    for m in [k for k in sys.modules if k == "shapes" or k.startswith("shapes.")]:
        del sys.modules[m]
    shutil.rmtree(root, ignore_errors=True)
    print("temp directory removed:", not root.exists())
