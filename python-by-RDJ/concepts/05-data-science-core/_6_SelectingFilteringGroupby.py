# Tags: #Python #DataScience #NumPy #Pandas #SelectingFilteringGroupby | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Selecting (loc/iloc), boolean filtering, sorting, groupby + aggregation,
and merge in pandas 3.x."""

import pandas as pd

pd.set_option("display.width", 100)

sales = pd.DataFrame(
    {
        "order": [101, 102, 103, 104, 105, 106],
        "cust": ["c1", "c2", "c1", "c3", "c2", "c1"],
        "region": ["east", "west", "east", "west", "east", "west"],
        "amount": [250.0, 100.0, 75.5, 300.0, 120.0, 60.0],
    }
)
print("sales =\n", sales, sep="")

# ===== SECTION 1: loc VS iloc =====
print("\n=== SECTION 1: loc (labels) vs iloc (positions) ===")
print("sales.loc[2, 'amount'] =", sales.loc[2, "amount"])
print("sales.iloc[2, 3] =", sales.iloc[2, 3], "(row position 2, column position 3)")
print("sales[['cust', 'amount']].head(2):\n", sales[["cust", "amount"]].head(2), sep="")
print("loc slice INCLUDES the end label: sales.loc[1:2, 'order'] ->", list(sales.loc[1:2, "order"]))
print("iloc slice EXCLUDES the end:     sales.iloc[1:2, 0]       ->", list(sales.iloc[1:2, 0]))
shuffled = sales.set_index("order")
print("with index = order ids, loc[103] is by LABEL:", shuffled.loc[103, "cust"])
print("iloc[103] would be a position error:", end=" ")
try:
    shuffled.iloc[103]
except IndexError as e:
    print("IndexError:", e)

# ===== SECTION 2: BOOLEAN FILTERING =====
print("\n=== SECTION 2: boolean filtering ===")
big = sales[sales["amount"] > 100]
print("amount > 100:\n", big, sep="")
both = sales[(sales["region"] == "east") & (sales["amount"] >= 100)]
print("east AND amount >= 100:\n", both, sep="")
print("isin: ", list(sales[sales["cust"].isin(["c2", "c3"])]["order"]))
print("query(): ", list(sales.query("region == 'west' and amount < 200")["order"]))
try:
    sales[sales["amount"] > 50 and sales["region"] == "east"]  # TRAP
except ValueError as e:
    print("TRAP 'and' between Series -> ValueError:", str(e)[:55] + "...")
print("FIX: use & with parentheses around each condition.")

# ===== SECTION 3: SORTING =====
print("\n=== SECTION 3: sorting ===")
print(sales.sort_values("amount", ascending=False).head(3)[["order", "amount"]])
print("two keys (region asc, amount desc):")
print(sales.sort_values(["region", "amount"], ascending=[True, False])[["region", "amount"]])
orig = sales["order"].tolist()
sales.sort_values("amount")
print("sort_values returns a NEW frame; sales unchanged:", sales["order"].tolist() == orig)

# ===== SECTION 4: GROUPBY + AGG =====
print("\n=== SECTION 4: groupby + agg ===")
print("total by region:\n", sales.groupby("region")["amount"].sum(), sep="")
summary = sales.groupby("cust").agg(
    orders=("order", "count"),
    total=("amount", "sum"),
    avg=("amount", "mean"),
    biggest=("amount", "max"),
)
print("named aggregation by customer:\n", summary, sep="")
print("groupby two keys:\n", sales.groupby(["region", "cust"])["amount"].sum(), sep="")
print("group sizes:", sales.groupby("region").size().to_dict())
print("groupby(...).transform adds a per-group value to every row:")
sales["share_of_region"] = (sales["amount"] / sales.groupby("region")["amount"].transform("sum")).round(3)
print(sales[["order", "region", "share_of_region"]])

# ===== SECTION 5: MERGE (SQL-style JOIN) =====
print("\n=== SECTION 5: merge ===")
custs = pd.DataFrame({"cust": ["c1", "c2", "c4"], "name": ["Ana", "Ben", "Dee"]})
print("customers:\n", custs, sep="")
inner = sales.merge(custs, on="cust", how="inner")
print("inner join (only matching keys):", sorted(inner["order"].tolist()), "-> c3's order 104 is DROPPED")
left = sales.merge(custs, on="cust", how="left")
print("left join keeps every sale; unmatched name is NaN:")
print(left[["order", "cust", "name"]])
outer = sales.merge(custs, on="cust", how="outer", indicator=True)
print("outer join with indicator, rows per side:", outer["_merge"].value_counts().to_dict())
dup = pd.DataFrame({"cust": ["c1", "c1"], "tier": ["gold", "silver"]})
print("TRAP duplicate keys multiply rows: 3 c1 orders x 2 tier rows =",
      len(sales[sales["cust"] == "c1"].merge(dup, on="cust")), "rows")
print("FIX: check dup.cust.is_unique ->", dup["cust"].is_unique, "or use validate='m:1' to raise.")
try:
    sales.merge(dup, on="cust", validate="m:1")
except pd.errors.MergeError as e:
    print("validate='m:1' raised MergeError:", str(e)[:60])
