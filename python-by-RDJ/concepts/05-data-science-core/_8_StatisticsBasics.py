# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Descriptive statistics by hand and with NumPy: mean, median, variance, standard
deviation, correlation, each with a plain-English meaning."""

import math
import statistics

import numpy as np
import pandas as pd

data = [4, 8, 6, 5, 3, 7, 9, 5]
arr = np.array(data, dtype=float)
print("data =", data)

# ===== SECTION 1: MEAN =====
print("\n=== SECTION 1: mean ===")
mean_hand = sum(data) / len(data)
print("by hand: sum / count =", sum(data), "/", len(data), "=", mean_hand)
print("np.mean =", np.mean(arr))
print("Plain English: the balance point. Add everything, share it out equally.")

# ===== SECTION 2: MEDIAN =====
print("\n=== SECTION 2: median ===")
ordered = sorted(data)
mid = len(ordered) // 2
median_hand = (ordered[mid - 1] + ordered[mid]) / 2 if len(ordered) % 2 == 0 else ordered[mid]
print("sorted:", ordered, "-> middle two", ordered[mid - 1], ordered[mid], "-> median", median_hand)
print("np.median =", np.median(arr))
print("Plain English: the middle value. Half the data is below, half above.")
with_outlier = np.append(arr, 1000.0)
print("TRAP: one outlier (1000) -> mean =", round(float(np.mean(with_outlier)), 3), "| median =", np.median(with_outlier))
print("The mean is dragged by outliers; the median barely moves.")

# ===== SECTION 3: VARIANCE AND STANDARD DEVIATION =====
print("\n=== SECTION 3: variance and standard deviation ===")
sq_dev = [(x - mean_hand) ** 2 for x in data]
print("squared deviations from the mean:", sq_dev)
var_pop = sum(sq_dev) / len(data)
var_sample = sum(sq_dev) / (len(data) - 1)
print("population variance (divide by n)  =", var_pop)
print("sample variance     (divide by n-1) =", round(var_sample, 6))
print("std dev = sqrt(variance): population", round(math.sqrt(var_pop), 6), "| sample", round(math.sqrt(var_sample), 6))
print("np.var(arr)           =", np.var(arr), "(population, ddof=0 by default)")
print("np.var(arr, ddof=1)   =", round(float(np.var(arr, ddof=1)), 6), "(sample)")
print("np.std(arr, ddof=1)   =", round(float(np.std(arr, ddof=1)), 6))
print("statistics.stdev      =", round(statistics.stdev(data), 6), "(stdlib uses SAMPLE by default)")
print("pd.Series(data).std()    =", round(float(pd.Series(data).std()), 6), "(pandas default ddof=1)")
print("TRAP: numpy defaults to ddof=0, pandas .std() defaults to ddof=1 -> different answers!")
print("Plain English: variance = average squared distance from the mean; std dev = typical")
print("distance, back in the original units. Bigger = more spread out.")

# ===== SECTION 4: CORRELATION =====
print("\n=== SECTION 4: correlation ===")
hours = np.array([1, 2, 3, 4, 5, 6], dtype=float)
score = np.array([52, 55, 61, 64, 70, 71], dtype=float)
dx, dy = hours - hours.mean(), score - score.mean()
cov = (dx * dy).sum() / (len(hours) - 1)
r_hand = cov / (hours.std(ddof=1) * score.std(ddof=1))
print("covariance (sample) =", round(float(cov), 6))
print("r by hand =", round(float(r_hand), 6))
print("np.corrcoef(hours, score)[0, 1] =", round(float(np.corrcoef(hours, score)[0, 1]), 6))
print("Plain English: r near +1 -> rise together; near -1 -> one rises as the other falls;")
print("near 0 -> no STRAIGHT-LINE relationship.")
x = np.linspace(-3, 3, 7)
print("TRAP: y = x^2 is perfectly determined by x, yet r =", round(float(np.corrcoef(x, x**2)[0, 1]), 6))
print("Correlation only sees linear patterns, and correlation is not causation.")

# ===== SECTION 5: PUTTING IT TOGETHER =====
print("\n=== SECTION 5: standardising (z-scores) ===")
z = (arr - arr.mean()) / arr.std()
print("z-scores:", np.round(z, 3))
print("z mean ~", round(float(z.mean()), 6), "| z std =", round(float(z.std()), 6))
print("This rescaling is routine before feeding features to ML models.")
