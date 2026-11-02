# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""pandas Series and DataFrame: constructing them, dtypes, head/info/describe,
and the index. Written against pandas 3.x (string dtype and copy-on-write defaults)."""

import io

import pandas as pd

pd.set_option("display.width", 100)

# ===== SECTION 1: SERIES =====
print("=== SECTION 1: Series (one labelled column) ===")
s = pd.Series([90, 85, 72], index=["ana", "ben", "cy"], name="score")
print(s)
print("s['ben'] =", s["ben"], "| s.iloc[0] =", s.iloc[0])
print("s.values type:", type(s.values).__name__, "| s.index:", list(s.index))
print("s * 2 (vectorised, aligned by label):")
print(s * 2)
print("alignment by label, not position:")
print(pd.Series([1, 2], index=["a", "b"]) + pd.Series([10, 20], index=["b", "c"]))
print("(a and c have no partner -> NaN)")

# ===== SECTION 2: DATAFRAME CONSTRUCTION =====
print("\n=== SECTION 2: DataFrame construction ===")
df = pd.DataFrame(
    {
        "name": ["ana", "ben", "cy", "dee"],
        "age": [20, 22, 21, 23],
        "gpa": [3.8, 3.1, 3.5, 2.9],
        "major": ["CS", "Math", "CS", "Bio"],
    }
)
print(df)
print("shape =", df.shape, "| columns =", list(df.columns))
rows = [("x", 1), ("y", 2)]
print("from list of tuples:\n", pd.DataFrame(rows, columns=["k", "v"]), sep="")
csv_text = "id,val\n1,10.5\n2,11.0\n3,9.75\n"
print("from CSV text (read_csv on an in-memory buffer):\n", pd.read_csv(io.StringIO(csv_text)), sep="")

# ===== SECTION 3: DTYPES =====
print("\n=== SECTION 3: dtypes ===")
print(df.dtypes)
print("pandas 3.x: text columns default to the dedicated string dtype ->", df["name"].dtype)
print("numbers stored as text are NOT numbers:")
txt = pd.Series(["1", "2", "3"])
print("  txt.dtype =", txt.dtype, "| txt.sum() =", repr(txt.sum()), "(string concatenation!)")
print("  after pd.to_numeric: sum =", pd.to_numeric(txt).sum())

# ===== SECTION 4: head / info / describe =====
print("\n=== SECTION 4: inspecting data ===")
print("df.head(2):\n", df.head(2), sep="")
print("df.tail(1):\n", df.tail(1), sep="")
print("df.info():")
df.info(memory_usage=False)
print("df.describe() (numeric columns only):")
print(df.describe())

# ===== SECTION 5: THE INDEX =====
print("\n=== SECTION 5: the index ===")
print("default index:", list(df.index), "(a RangeIndex)")
by_name = df.set_index("name")
print("after set_index('name'):\n", by_name, sep="")
print("by_name.loc['cy','gpa'] =", by_name.loc["cy", "gpa"])
print("reset_index() puts it back as a column:", list(by_name.reset_index().columns))
sub = df[df["major"] == "CS"]
print("TRAP: filtering keeps the ORIGINAL labels:", list(sub.index), "-> sub.loc[2] works, sub.loc[1] is a KeyError, sub.iloc[1] is the second ROW")
try:
    sub.loc[1]
except KeyError as e:
    print("sub.loc[1] raises KeyError:", e)
print("sub.iloc[1] (second row) name =", sub.iloc[1]["name"])
print("FIX when you want fresh numbering: sub.reset_index(drop=True).index =", list(sub.reset_index(drop=True).index))

# ===== SECTION 6: COPY-ON-WRITE (pandas 3 default) =====
print("\n=== SECTION 6: copy-on-write ===")
original = pd.DataFrame({"a": [1, 2, 3]})
other = original["a"]  # looks like a view
other.iloc[0] = 100
print("pandas 3 changes 'other' only; original['a'][0] is still:", original["a"].iloc[0])
print("No more SettingWithCopyWarning guessing: each derived object behaves as its own copy.")
