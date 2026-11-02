# `_8_StatisticsBasics.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Descriptive statistics summarise a pile of numbers with a few values: the mean and median (the centre), the variance and standard deviation (the spread), and correlation (how two variables move together). This file computes each one by hand with plain Python first and then with NumPy, so you can see that the library functions are just formulas, and attaches a plain-English meaning to each.

## Full Line-by-Line Breakdown

The dataset is `[4, 8, 6, 5, 3, 7, 9, 5]`.

### SECTION 1: mean
The mean is the sum divided by the count: 47 / 8 = 5.875. `np.mean` agrees. In plain English it is the balance point: share the total out equally.

```text
=== SECTION 1: mean ===
by hand: sum / count = 47 / 8 = 5.875
np.mean = 5.875
Plain English: the balance point. Add everything, share it out equally.
```

### SECTION 2: median
Sort the values, then take the middle one; with an even count, average the middle two (5 and 6, giving 5.5). In plain English, half the data is below it and half above. The trap shows why it matters: adding one outlier (1000) drags the mean to 116.333 but moves the median only to 6.0.

```text
=== SECTION 2: median ===
sorted: [3, 4, 5, 5, 6, 7, 8, 9] -> middle two 5 6 -> median 5.5
np.median = 5.5
Plain English: the middle value. Half the data is below, half above.
TRAP: one outlier (1000) -> mean = 116.333 | median = 6.0
The mean is dragged by outliers; the median barely moves.
```

### SECTION 3: variance and standard deviation
For each value take its distance from the mean and square it (so negatives do not cancel), then average. Dividing by n gives the population variance (3.609375); dividing by n-1 gives the sample variance (4.125), used when your data is a sample from something bigger. The standard deviation is the square root, which returns to the original units. The trap: `np.var` and `np.std` default to `ddof=0` (population), while pandas `.std()` and `statistics.stdev` default to the sample formula (`ddof=1`), so the same data gives different answers unless you set `ddof` deliberately.

```text
=== SECTION 3: variance and standard deviation ===
squared deviations from the mean: [3.515625, 4.515625, 0.015625, 0.765625, 8.265625, 1.265625, 9.765625, 0.765625]
population variance (divide by n)  = 3.609375
sample variance     (divide by n-1) = 4.125
std dev = sqrt(variance): population 1.899836 | sample 2.03101
np.var(arr)           = 3.609375 (population, ddof=0 by default)
np.var(arr, ddof=1)   = 4.125 (sample)
np.std(arr, ddof=1)   = 2.03101
statistics.stdev      = 2.03101 (stdlib uses SAMPLE by default)
pd.Series(data).std()    = 2.03101 (pandas default ddof=1)
TRAP: numpy defaults to ddof=0, pandas .std() defaults to ddof=1 -> different answers!
Plain English: variance = average squared distance from the mean; std dev = typical
distance, back in the original units. Bigger = more spread out.
```

### SECTION 4: correlation
Covariance measures how two variables move together; dividing by both standard deviations gives the correlation coefficient r between -1 and +1. The file computes r by hand for study hours versus score and gets the same result from `np.corrcoef`. The trap: `y = x^2` is completely determined by `x`, yet r is 0 on symmetric data, because correlation only detects straight-line relationships. Also, correlation does not show that one thing causes the other.

```text
=== SECTION 4: correlation ===
covariance (sample) = 14.3
r by hand = 0.988718
np.corrcoef(hours, score)[0, 1] = 0.988718
Plain English: r near +1 -> rise together; near -1 -> one rises as the other falls;
near 0 -> no STRAIGHT-LINE relationship.
TRAP: y = x^2 is perfectly determined by x, yet r = 0.0
Correlation only sees linear patterns, and correlation is not causation.
```

### SECTION 5: standardising (z-scores)
A z-score is `(value - mean) / std`. The standardised data has mean about 0 and standard deviation 1. Putting features on a common scale like this is routine before training many models, including the gradient descent in the next topic.

```text
=== SECTION 5: standardising (z-scores) ===
z-scores: [-0.987  1.119  0.066 -0.461 -1.513  0.592  1.645 -0.461]
z mean ~ 0.0 | z std = 1.0
This rescaling is routine before feeding features to ML models.
```

## Key Differences From Java
| Idea | Java | Python |
|---|---|---|
| Mean | `Arrays.stream(a).average()` or a loop | `np.mean(a)`, or `statistics.mean(a)` in the standard library |
| Median | Sort and pick the middle yourself | `np.median(a)`, `statistics.median(a)` |
| Std dev | Write the formula (or Apache Commons Math `StandardDeviation`) | `np.std(a, ddof=1)`, `statistics.stdev(a)` |
| Correlation | Apache Commons Math `PearsonsCorrelation` | `np.corrcoef(x, y)` |
| Summary | `DoubleSummaryStatistics` (count, sum, min, avg, max only) | `df.describe()` |

How you would do this in Java: `DoubleSummaryStatistics` gives count, sum, min, max and average only. For variance, median and correlation you would write the formulas yourself or add Apache Commons Math. Python's standard library already has a `statistics` module, and NumPy adds the array versions.

## Key Rules / Gotchas Recap
- Mean is sensitive to outliers; median is robust.
- Population variance divides by n; sample variance divides by n-1.
- NumPy defaults to `ddof=0`; pandas and `statistics.stdev` default to sample (`ddof=1`).
- Correlation measures only linear association and does not imply causation.
- Standardise features (z-scores) before comparing or training on columns with different scales.

## Why This Structure Exists
Every evaluation you report (mean accuracy, spread across runs, correlation between a feature and a label) uses these numbers, and mixing up `ddof` defaults is an easy way to publish a wrong figure. Mean, variance and normalisation also reappear inside machine-learning methods.
