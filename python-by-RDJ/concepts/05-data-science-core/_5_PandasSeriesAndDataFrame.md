# `_5_PandasSeriesAndDataFrame.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
pandas adds labels to NumPy arrays. A `Series` is one labelled column (values plus an index), and a `DataFrame` is a table of Series sharing the same index, much like a spreadsheet or a SQL table held in memory. You will use `head`, `info` and `describe` on every dataset you ever open, and knowing the dtype and index of each column prevents most beginner bugs. This file was run on pandas 3.x, where text columns default to a dedicated `str` dtype and copy-on-write is always on.

## Full Line-by-Line Breakdown

### SECTION 1: Series
`pd.Series([90, 85, 72], index=[...], name="score")` builds one column with labels. You can look a value up by label (`s["ben"]`) or by position (`s.iloc[0]`). Operations are vectorised, and when you combine two Series, pandas aligns them by label rather than position: labels present in only one Series produce `NaN` (missing value), and the result becomes float because `NaN` is a float.

```text
=== SECTION 1: Series (one labelled column) ===
ana    90
ben    85
cy     72
Name: score, dtype: int64
s['ben'] = 85 | s.iloc[0] = 90
s.values type: ndarray | s.index: ['ana', 'ben', 'cy']
s * 2 (vectorised, aligned by label):
ana    180
ben    170
cy     144
Name: score, dtype: int64
alignment by label, not position:
a     NaN
b    12.0
c     NaN
dtype: float64
(a and c have no partner -> NaN)
```

### SECTION 2: DataFrame construction
The usual constructor takes a dict of column name to list. You can also build from a list of tuples with `columns=`, or read a CSV (here from an in-memory string with `io.StringIO`, so no file is needed). `.shape` is `(rows, columns)`.

```text
=== SECTION 2: DataFrame construction ===
  name  age  gpa major
0  ana   20  3.8    CS
1  ben   22  3.1  Math
2   cy   21  3.5    CS
3  dee   23  2.9   Bio
shape = (4, 4) | columns = ['name', 'age', 'gpa', 'major']
from list of tuples:
   k  v
0  x  1
1  y  2
from CSV text (read_csv on an in-memory buffer):
   id    val
0   1  10.50
1   2  11.00
2   3   9.75
```

### SECTION 3: dtypes
`.dtypes` lists the type of each column. In pandas 3 text is shown as `str`. The trap is numbers stored as text: summing a column of `"1","2","3"` concatenates the strings to `'123'`. `pd.to_numeric` converts them, after which the sum is 6.

```text
=== SECTION 3: dtypes ===
name         str
age        int64
gpa      float64
major        str
dtype: object
pandas 3.x: text columns default to the dedicated string dtype -> str
numbers stored as text are NOT numbers:
  txt.dtype = str | txt.sum() = '123' (string concatenation!)
  after pd.to_numeric: sum = 6
```

### SECTION 4: inspecting data
`head(n)` and `tail(n)` show the first or last rows. `info()` shows row count, non-null counts per column and dtypes (the file turns off memory usage because that figure varies by platform). `describe()` gives count, mean, standard deviation, min, quartiles and max for numeric columns.

```text
=== SECTION 4: inspecting data ===
df.head(2):
  name  age  gpa major
0  ana   20  3.8    CS
1  ben   22  3.1  Math
df.tail(1):
  name  age  gpa major
3  dee   23  2.9   Bio
df.info():
<class 'pandas.DataFrame'>
RangeIndex: 4 entries, 0 to 3
Data columns (total 4 columns):
 #   Column  Non-Null Count  Dtype  
---  ------  --------------  -----  
 0   name    4 non-null      str    
 1   age     4 non-null      int64  
 2   gpa     4 non-null      float64
 3   major   4 non-null      str    
dtypes: float64(1), int64(1), str(2)df.describe() (numeric columns only):
             age       gpa
count   4.000000  4.000000
mean   21.500000  3.325000
std     1.290994  0.403113
min    20.000000  2.900000
25%    20.750000  3.050000
50%    21.500000  3.300000
75%    22.250000  3.575000
max    23.000000  3.800000
```

### SECTION 5: the index
Every DataFrame has an index (row labels). The default is `0, 1, 2, ...`. `set_index("name")` makes a column the index so `loc["cy", "gpa"]` works by label, and `reset_index()` moves it back. The trap: filtering keeps the original labels, so after selecting the CS students the labels are `[0, 2]`; `loc[1]` fails with `KeyError` while `iloc[1]` means "the second row". `reset_index(drop=True)` renumbers.

```text
=== SECTION 5: the index ===
default index: [0, 1, 2, 3] (a RangeIndex)
after set_index('name'):
      age  gpa major
name                
ana    20  3.8    CS
ben    22  3.1  Math
cy     21  3.5    CS
dee    23  2.9   Bio
by_name.loc['cy','gpa'] = 3.5
reset_index() puts it back as a column: ['name', 'age', 'gpa', 'major']
TRAP: filtering keeps the ORIGINAL labels: [0, 2] -> sub.loc[2] works, sub.loc[1] is a KeyError, sub.iloc[1] is the second ROW
sub.loc[1] raises KeyError: 1
sub.iloc[1] (second row) name = cy
FIX when you want fresh numbering: sub.reset_index(drop=True).index = [0, 1]
```

### SECTION 6: copy-on-write
In pandas 3, derived objects behave as independent copies: modifying `other = original["a"]` does not change `original`. In older pandas versions this was a source of `SettingWithCopyWarning` and silent bugs. (If you read older tutorials, they describe the old behaviour.)

```text
=== SECTION 6: copy-on-write ===
pandas 3 changes 'other' only; original['a'][0] is still: 1
No more SettingWithCopyWarning guessing: each derived object behaves as its own copy.
```

## Key Differences From Java
| Idea | Java | Python with pandas |
|---|---|---|
| A table | `List<Row>` of your own class, or JDBC `ResultSet` | `DataFrame` |
| A column | A `List<Double>` field you extract with a loop or stream | `df["gpa"]` (a `Series`) |
| Missing value | `null` (or `Optional`) | `NaN` / `NaT` / `pd.NA` |
| Summary stats | Write loops or use streams (`DoubleSummaryStatistics`) | `df.describe()` |
| Types | Fixed at compile time per field | Inferred per column at load time |

How you would do this in Java: there is no built-in data-frame. You would define a class per row (a record), keep a `List` of them, and write streams or loops for statistics, or add a library such as Tablesaw or Apache Spark.

## Key Rules / Gotchas Recap
- Check `.dtypes` and `.info()` first; numbers stored as text are the most common issue.
- Series arithmetic aligns on labels, producing `NaN` for unmatched labels.
- Filtering keeps original index labels; use `reset_index(drop=True)` if you want fresh numbering.
- `loc` is by label, `iloc` is by position.
- pandas 3: text defaults to `str` dtype and copy-on-write is always on; older tutorials may disagree.

## Why This Structure Exists
Real AI projects start with tabular data: logs, labels, evaluation results. A DataFrame is the standard container for loading, inspecting and reshaping it before a model ever sees a number.
