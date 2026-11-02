# `_9_ModulesAndPackages.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A module is a single `.py` file and a package is a directory of modules with an `__init__.py`. You use `import` to load them; Python finds them by searching the directories listed in `sys.path`, runs the module once, and caches it in `sys.modules`. The special variable `__name__` equals `"__main__"` only when the file is run directly, which lets one file work as both a script and an importable library.

This file builds a real package in a temporary directory while it runs, so you can see every rule operate on actual files.

## Full Line-by-Line Breakdown

### SECTION 1: BUILD A PACKAGE IN A TEMP DIRECTORY
`tempfile.mkdtemp` makes a fresh directory and the script writes `shapes/__init__.py`, `shapes/utils.py` and `shapes/circle.py` into it. `__init__.py` makes the folder a package and runs when the package is first imported. It uses a RELATIVE import (`from .circle import area`: the dot means "this package").

Output from a real run:

```text
===== SECTION 1: BUILD A PACKAGE IN A TEMP DIRECTORY =====
files: ['shapes/__init__.py', 'shapes/circle.py', 'shapes/utils.py']
```

### SECTION 2: IMPORT VIA sys.path
First the import fails with `ModuleNotFoundError` because the temp directory is not on `sys.path`. After `sys.path.insert(0, root)` (and `importlib.invalidate_caches()` so the finder notices the new directory) the import succeeds. The prints show the loading order: `__init__` begins, imports `circle`, and `circle` reports it was imported with `__name__` equal to `'shapes.circle'`. The (indented) init message prints after because it is at the bottom of that file. A second import does nothing: modules are cached in `sys.modules`.

Output from a real run:

```text
===== SECTION 2: IMPORT VIA sys.path =====
Before sys.path change -> No module named 'shapes'
  (circle.py imported, __name__ is 'shapes.circle')
  (shapes/__init__.py ran)
shapes.circle_area(2): 12.56636
shapes.__name__: shapes
shapes.__all__: ['circle_area', 'PI']
Second import is cached, no re-run: True
```

### SECTION 3: importlib.import_module
`importlib.import_module("shapes.utils")` imports by a string name, handy for plugins chosen at runtime. `importlib.reload` re-executes a module's code and returns the same module object.

Output from a real run:

```text
===== SECTION 3: importlib.import_module =====
PI from dynamic import: 3.14159
shapes.circle in sys.modules: True
reload returns the same module object: True
```

### SECTION 4: __all__ AND from X import *
`__all__` is the list of names exported by `from module import *`. The package declares `['circle_area', 'PI']`, so exactly those come through. `utils` has no `__all__`, so the star import takes every name that does not start with an underscore (`PI`, `visible`) and skips `_private_helper`. `__all__` does not stop explicit access (`shapes.utils._private_helper`); it only controls star-imports and documents the public API. Star-imports are discouraged in real code.

Output from a real run:

```text
===== SECTION 4: __all__ AND from X import * =====
names from 'shapes import *': ['PI', 'circle_area']
names from 'shapes.utils import *': ['PI', 'visible']
(underscore names skipped when there is no __all__)
```

### SECTION 5: __name__ == '__main__'
Run directly, this file's `__name__` is `"__main__"`. `python -m shapes.circle` runs the module as a script from the project root: Python first imports the parent package (so the `__init__` and "imported" messages appear), then executes `circle.py` with `__name__ == "__main__"`, which triggers the demo branch. The subprocess has a timeout and only runs our own temporary files.

Output from a real run:

```text
===== SECTION 5: __name__ == '__main__' =====
this file's __name__: __main__
python -m shapes.circle -> (circle.py imported, __name__ is 'shapes.circle')
  (shapes/__init__.py ran)
circle.py run directly as a script, area(1) = 3.14159
```

### SECTION 6: TRAP - RELATIVE IMPORT RUN AS A SCRIPT
Running `python shapes/circle.py` makes the file the top-level script with no parent package, so `from .utils import PI` fails with `ImportError: attempted relative import with no known parent package`. Run it with `-m` from the project root, or use absolute imports.

Output from a real run:

```text
===== SECTION 6: TRAP - RELATIVE IMPORT RUN AS A SCRIPT =====
python shapes/circle.py -> ImportError: attempted relative import with no known parent package
Fix: run with -m from the project root, or use an absolute import.
```

### SECTION 7: CLEANUP
A `finally` block removes the path from `sys.path`, deletes the loaded modules from `sys.modules` and removes the temporary directory, so the script leaves nothing behind.

Output from a real run:

```text
===== SECTION 7: CLEANUP =====
temp directory removed: True
```

## Key Differences From Java
| Java | Python |
|---|---|
| `package com.x;` declared at the top, folders must match | Folder with `__init__.py` is the package; no declaration inside files |
| `import com.x.Foo;` imports a class | `import pkg.mod` / `from pkg.mod import name` imports a module or a name |
| One public class per file | Any number of classes/functions per file |
| `public static void main(String[] args)` | `if __name__ == "__main__":` |
| `CLASSPATH` / module path | `sys.path` (and `PYTHONPATH`) |
| `public`/package-private controls visibility | `__all__` and underscore convention (no enforcement) |
| Maven/Gradle | `pip` + `pyproject.toml` |
| Imports resolved at compile time | Imports execute code at runtime, once |

## Key Rules / Gotchas Recap
- A module is executed the first time it is imported, then cached in `sys.modules`.
- Do not name your files after standard modules (`random.py`, `json.py`): yours may shadow them.
- Use `if __name__ == "__main__":` to guard script code.
- Relative imports (`from . import x`) only work inside a package; run with `python -m package.module`.
- Avoid `from x import *`.
- Avoid circular imports by moving shared code to a third module or importing inside a function.
- Python 3 also allows packages without `__init__.py` (namespace packages), but add one for regular packages.

### Virtual environments and pip (explained only; not run by the script)

A virtual environment is an isolated folder with its own Python interpreter and its own installed packages, so each project has its own dependency versions. This is similar in spirit to per-project dependencies in Maven or Gradle, except Python installs into one shared global location unless you create an environment.

Typical workflow (shell, macOS/Linux):

```text
python3 -m venv .venv            # create the environment in ./.venv
source .venv/bin/activate        # activate it (Windows: .venv\Scripts\activate)
python -m pip install requests   # install a package into this environment only
python -m pip freeze > requirements.txt   # record exact versions
python -m pip install -r requirements.txt # recreate the environment elsewhere
deactivate                       # leave the environment
```

Put `.venv/` in `.gitignore` and commit `requirements.txt` (or a `pyproject.toml`). Use `python -m pip` so you are sure pip belongs to the interpreter you are running. Never run `sudo pip install` into the system Python. `pip` downloads from the Python Package Index (PyPI), so only install packages you trust; typosquatted package names are a real supply-chain risk.

## Why This Structure Exists
Every real project, from an AI service to a security scanner, is split into modules and packages and installs its dependencies in a virtual environment. Understanding `sys.path`, `__name__` and relative imports removes most of the confusing `ImportError` problems beginners hit.
