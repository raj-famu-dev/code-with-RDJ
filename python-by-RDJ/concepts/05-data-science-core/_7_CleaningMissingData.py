# Tags: #Python #DataScience #NumPy #Pandas #CleaningMissingData | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Cleaning messy data: detecting NaN, fillna/dropna, duplicates, type fixes and
string cleaning, on a deliberately messy inline dataset (pandas 3.x)."""

import io

import numpy as np
import pandas as pd

pd.set_option("display.width", 120)

RAW = """id,name,age,city,salary,joined
1,  Alice ,30,NEW YORK,"$72,000",2021-03-01
2,bob,,new york,65000,2020-07-15
3,CAROL,41,Boston,N/A,2019-11-30
4,Dave,29,boston ,58000,not a date
2,bob,,new york,65000,2020-07-15
5,,35,Chicago,91000,2022-01-10
6,Frank,-5,Chicago,48000,2021-12-25
7,Grace,38,,"$80,500",2018-05-05
"""
df = pd.read_csv(io.StringIO(RAW))
print("=== RAW messy data ===")
print(df)
print(df.dtypes.to_string())

# ===== SECTION 1: DETECTING MISSING VALUES =====
print("\n=== SECTION 1: detecting missing values ===")
print("isna().sum() per column:\n", df.isna().sum().to_string(), sep="")
print("rows with any missing value:", df.isna().any(axis=1).sum())
print("NOTE: 'N/A' was read as NaN automatically; the string 'not a date' was not.")
print("TRAP: np.nan == np.nan is", np.nan == np.nan, "| use isna(), never == np.nan")

# ===== SECTION 2: DUPLICATES =====
print("\n=== SECTION 2: duplicates ===")
print("duplicated rows:", list(df[df.duplicated()]["id"]))
df = df.drop_duplicates().reset_index(drop=True)
print("after drop_duplicates, rows =", len(df))
print("duplicates by key only (id):", df.duplicated(subset="id").sum())

# ===== SECTION 3: STRING CLEANING =====
print("\n=== SECTION 3: string cleaning ===")
df["name"] = df["name"].str.strip().str.title()
df["city"] = df["city"].str.strip().str.title()
print(df[["id", "name", "city"]])
print("unique cities now:", sorted(df["city"].dropna().unique()))

# ===== SECTION 4: TYPE FIXES =====
print("\n=== SECTION 4: type fixes ===")
print("salary dtype before:", df["salary"].dtype, "(text, because of '$' and ',')")
df["salary"] = pd.to_numeric(df["salary"].str.replace(r"[$,]", "", regex=True), errors="coerce")
print("salary dtype after:", df["salary"].dtype, "->", df["salary"].tolist())
df["joined"] = pd.to_datetime(df["joined"], errors="coerce")
print("joined after to_datetime(errors='coerce'):")
print(df["joined"].to_string())
print("(the bad date became NaT, 'not a time')")
bad_age = df["age"] < 0
print("impossible ages (<0):", list(df[bad_age]["id"]), "-> treat as missing")
df.loc[bad_age, "age"] = np.nan

# ===== SECTION 5: fillna / dropna =====
print("\n=== SECTION 5: fillna / dropna ===")
print("missing counts now:\n", df.isna().sum().to_string(), sep="")
filled = df.copy()
filled["age"] = filled["age"].fillna(filled["age"].median())
filled["city"] = filled["city"].fillna("Unknown")
filled["name"] = filled["name"].fillna("Unknown")
filled["salary"] = filled["salary"].fillna(filled["salary"].median())
print("filled copy:\n", filled[["id", "name", "age", "city", "salary"]], sep="")
print("median age used:", df["age"].median(), "(computed from the non-missing ages only)")
dropped = df.dropna(subset=["salary", "name"])
print("dropna(subset=['salary','name']) keeps ids:", list(dropped["id"]))
print("dropna() with no subset keeps ids:", list(df.dropna()["id"]), "(too aggressive: loses almost everything)")
print("DECISION RULE: dropping loses rows; filling invents values. Pick per column and record why.")

# ===== SECTION 6: THE CLEAN RESULT =====
print("\n=== SECTION 6: clean result ===")
print(filled.dtypes.to_string())
print(filled)
