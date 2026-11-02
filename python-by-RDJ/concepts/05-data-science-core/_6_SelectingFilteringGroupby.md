# `_6_SelectingFilteringGroupby.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Once data is in a DataFrame you need to pull out the pieces you want and summarise them. `loc` and `iloc` select by label or position, boolean filters keep rows matching a condition, `sort_values` orders rows, `groupby(...).agg(...)` summarises per category, and `merge` joins two tables on a shared key, exactly like SQL `WHERE`, `ORDER BY`, `GROUP BY` and `JOIN`. These five tools cover most day-to-day analysis.

## Full Line-by-Line Breakdown

The file uses a small table of six orders (`order`, `cust`, `region`, `amount`), shown first.

### SECTION 1: loc (labels) vs iloc (positions)
`loc[2, "amount"]` means row label 2, column named `amount`; `iloc[2, 3]` means row position 2, column position 3. They agree here only because the index is the default `0..5`. A label slice with `loc` includes its end (`1:2` gives two rows), while an `iloc` slice excludes the end like normal Python. After `set_index("order")`, `loc[103]` looks up the order ID, while `iloc[103]` is out of range.

```text
=== SECTION 1: loc (labels) vs iloc (positions) ===
sales.loc[2, 'amount'] = 75.5
sales.iloc[2, 3] = 75.5 (row position 2, column position 3)
sales[['cust', 'amount']].head(2):
  cust  amount
0   c1   250.0
1   c2   100.0
loc slice INCLUDES the end label: sales.loc[1:2, 'order'] -> [102, 103]
iloc slice EXCLUDES the end:     sales.iloc[1:2, 0]       -> [102]
with index = order ids, loc[103] is by LABEL: c1
iloc[103] would be a position error: IndexError: single positional indexer is out-of-bounds
```

### SECTION 2: boolean filtering
`sales[sales["amount"] > 100]` builds a True/False mask and keeps matching rows. Combine conditions with `&`, `|` and parentheses (never `and`/`or`). `isin([...])` tests membership and `query("...")` writes the condition as a string. The trap is using `and`, which raises `ValueError` because Python cannot turn a whole Series into one True/False.

```text
=== SECTION 2: boolean filtering ===
amount > 100:
   order cust region  amount
0    101   c1   east   250.0
3    104   c3   west   300.0
4    105   c2   east   120.0
east AND amount >= 100:
   order cust region  amount
0    101   c1   east   250.0
4    105   c2   east   120.0
isin:  [102, 104, 105]
query():  [102, 106]
TRAP 'and' between Series -> ValueError: The truth value of a Series is ambiguous. Use a.empty, ...
FIX: use & with parentheses around each condition.
```

### SECTION 3: sorting
`sort_values("amount", ascending=False)` orders rows; passing a list sorts by several keys with a matching list of directions. It returns a new DataFrame; the original is unchanged unless you assign the result.

```text
=== SECTION 3: sorting ===
   order  amount
3    104   300.0
0    101   250.0
4    105   120.0
two keys (region asc, amount desc):
  region  amount
0   east   250.0
4   east   120.0
2   east    75.5
3   west   300.0
1   west   100.0
5   west    60.0
sort_values returns a NEW frame; sales unchanged: True
```

### SECTION 4: groupby + agg
`groupby("region")["amount"].sum()` splits into groups, sums each, and returns one row per group. Named aggregation (`orders=("order", "count")`) lets you compute several statistics at once and name the columns. Grouping by a list of columns gives a two-level index. `transform` returns a value for every original row (here each order's share of its region's total) instead of one row per group.

```text
=== SECTION 4: groupby + agg ===
total by region:
region
east    445.5
west    460.0
Name: amount, dtype: float64
named aggregation by customer:
      orders  total    avg  biggest
cust                               
c1         3  385.5  128.5    250.0
c2         2  220.0  110.0    120.0
c3         1  300.0  300.0    300.0
groupby two keys:
region  cust
east    c1      325.5
        c2      120.0
west    c1       60.0
        c2      100.0
        c3      300.0
Name: amount, dtype: float64
group sizes: {'east': 3, 'west': 3}
groupby(...).transform adds a per-group value to every row:
   order region  share_of_region
0    101   east            0.561
1    102   west            0.217
2    103   east            0.169
3    104   west            0.652
4    105   east            0.269
5    106   west            0.130
```

### SECTION 5: merge
`merge` joins on the `cust` column. An `inner` join keeps only keys present in both tables, so order 104 (customer `c3`, not in the customer table) disappears silently. A `left` join keeps every sale and fills the missing name with `NaN`. `outer` with `indicator=True` shows which side each row came from. The trap is duplicate keys on one side: three `c1` orders joined to two `c1` rows becomes six rows. `validate="m:1"` makes pandas raise `MergeError` instead.

```text
=== SECTION 5: merge ===
customers:
  cust name
0   c1  Ana
1   c2  Ben
2   c4  Dee
inner join (only matching keys): [101, 102, 103, 105, 106] -> c3's order 104 is DROPPED
left join keeps every sale; unmatched name is NaN:
   order cust name
0    101   c1  Ana
1    102   c2  Ben
2    103   c1  Ana
3    104   c3  NaN
4    105   c2  Ben
5    106   c1  Ana
outer join with indicator, rows per side: {'both': 5, 'left_only': 1, 'right_only': 1}
TRAP duplicate keys multiply rows: 3 c1 orders x 2 tier rows = 6 rows
FIX: check dup.cust.is_unique -> False or use validate='m:1' to raise.
validate='m:1' raised MergeError: Merge keys are not unique in right dataset; not a many-to-on
```

## Key Differences From Java
| Idea | Java | Python with pandas |
|---|---|---|
| Filter rows | `list.stream().filter(r -> r.amount() > 100).toList()` | `df[df["amount"] > 100]` |
| Sort | `list.sort(Comparator.comparing(...))` (in place) | `df.sort_values("amount")` (returns new) |
| Group and aggregate | `stream().collect(Collectors.groupingBy(...))` | `df.groupby("region")["amount"].sum()` |
| Join | Nested loops, a `Map` lookup, or SQL | `df.merge(other, on="cust")` |
| Combine conditions | `&&`, `||` | `&`, `|` with parentheses |

How you would do this in Java: define a record for each row, hold them in a `List`, and use streams with `Collectors.groupingBy` and `summingDouble`; for joins, build a `Map` by key and look up each row, or push the work into SQL via JDBC.

## Key Rules / Gotchas Recap
- `loc` is label-based and includes the slice end; `iloc` is position-based and excludes it.
- Use `&`, `|`, `~` with parentheses for combined conditions.
- `sort_values` and most pandas methods return new objects; assign the result.
- An inner join drops unmatched rows silently; check row counts after merging.
- Duplicate keys multiply rows on a merge; use `validate=`.

## Why This Structure Exists
Evaluating an AI system is a groupby problem: accuracy per category, per prompt type or per model. Joining labels to predictions is a merge. These operations are how you turn raw results into numbers you can put in a write-up.
