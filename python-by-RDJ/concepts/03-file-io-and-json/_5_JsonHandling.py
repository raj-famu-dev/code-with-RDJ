# Tags: #Python #FileIO #JSON #JsonHandling | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Teaches the json module: dumps/loads (strings) vs dump/load (files),
pretty printing, sort_keys, type mapping, custom encoders for dataclasses and
datetimes, and handling JSONDecodeError.
"""
import json
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

print("=== SECTION 1: dumps and loads (strings) ===")
data = {"name": "Ada", "age": 36, "langs": ["Python", "Java"], "active": True, "boss": None}
s = json.dumps(data)
print("dumps:", s)
print("type:", type(s).__name__)
back = json.loads(s)
print("loads:", back)
print("round trip equal:", back == data)
print("Python -> JSON: True->true, None->null:", json.dumps([True, None, 1.5]))

print("\n=== SECTION 2: indent and sort_keys ===")
print(json.dumps(data, indent=2))
print("sort_keys:", json.dumps({"b": 1, "a": 2}, sort_keys=True))
print("compact  :", json.dumps({"a": 1, "b": [1, 2]}, separators=(",", ":")))
print("unicode default:", json.dumps({"city": "São Paulo"}))
print("ensure_ascii=False:", json.dumps({"city": "São Paulo"}, ensure_ascii=False))

print("\n=== SECTION 3: dump and load (files) ===")
tmp = tempfile.TemporaryDirectory()
base = Path(tmp.name)
p = base / "config.json"
with open(p, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)           # note: dump (no s) takes a file object
with open(p, encoding="utf-8") as f:
    loaded = json.load(f)
print("file round trip equal:", loaded == data)
print("first line on disk:", p.read_text(encoding="utf-8").splitlines()[0])

print("\n=== SECTION 4: JSON type-mapping surprises ===")
print("tuple becomes list:", json.loads(json.dumps((1, 2))))
print("int keys become str:", json.loads(json.dumps({1: "a"})))
print("set is NOT serialisable ->", end=" ")
try:
    json.dumps({1, 2})
except TypeError as e:
    print("TypeError:", e)
print("datetime is NOT serialisable ->", end=" ")
try:
    json.dumps({"when": datetime(2025, 1, 2, 3, 4, 5)})
except TypeError as e:
    print("TypeError:", e)

print("\n=== SECTION 5: custom encoder for dataclass and datetime ===")
@dataclass
class Event:
    title: str
    when: datetime
    tags: set[str]

class AppEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:      # called ONLY for unknown types
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, set):
            return sorted(o)               # sorted -> deterministic
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        return super().default(o)          # raises TypeError for the rest

ev = Event("Demo", datetime(2025, 6, 1, 9, 30), {"b", "a"})
text = json.dumps(ev, cls=AppEncoder, indent=2)
print(text)
print("Same result with a function:", json.dumps({"d": date(2025, 1, 1)}, default=str))
raw = json.loads(text)
print("decoded 'when' is just a str:", type(raw["when"]).__name__)
ev2 = Event(raw["title"], datetime.fromisoformat(raw["when"]), set(raw["tags"]))
print("manually rebuilt:", ev2 == ev)

print("\n=== SECTION 6: JSONDecodeError ===")
bad_inputs = {
    "single quotes": "{'a': 1}",
    "trailing comma": '{"a": 1,}',
    "empty string": "",
    "truncated": '{"a": [1, 2',
}
for label, bad in bad_inputs.items():
    try:
        json.loads(bad)
    except json.JSONDecodeError as e:
        print(f"{label:15} -> line {e.lineno} col {e.colno}: {e.msg}")
print("JSONDecodeError is a subclass of ValueError:", issubclass(json.JSONDecodeError, ValueError))

print("\n=== SECTION 7: safe loading from a file ===")
def load_json(path: Path, default: Any) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as e:
        print(f"  corrupt file {path.name}: {e.msg} at char {e.pos}")
        return default

(base / "corrupt.json").write_text('{"a": 1', encoding="utf-8")
(base / "empty.json").write_text("", encoding="utf-8")
print("missing :", load_json(base / "nope.json", {}))
print("corrupt :", load_json(base / "corrupt.json", {}))
print("empty   :", load_json(base / "empty.json", {}))
print("good    :", load_json(p, {})["name"])

print("\n=== SECTION 8: NaN and big numbers ===")
print("dumps(float('nan')):", json.dumps(float("nan")), "<- NOT valid JSON by spec!")
try:
    json.dumps(float("nan"), allow_nan=False)
except ValueError as e:
    print("allow_nan=False ->", type(e).__name__)
print("big int survives in Python:", json.loads("123456789012345678901234567890"))

tmp.cleanup()
print("\ntemp dir removed:", not base.exists())
