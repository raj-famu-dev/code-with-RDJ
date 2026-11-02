> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Switch Expressions and Pattern Matching

## Concept

Modern `switch` produces a **value**, has no fall-through, and can match on **types** and on the **shape of records**.

## Full Line-by-Line Breakdown

**Section 1: the old switch statement.** Needs `break` on every branch; forgetting one **falls through** into the next case.

**Section 2: switch expression (Java 14).** Arrow form: no fall-through, several labels per case (`case MONDAY, FRIDAY, SUNDAY -> 6`). Over an enum it must cover **every** constant. A block with **`yield`** supplies the value when a case needs several statements:

```
weekend / Wednesday is a working day
```

**Section 3: pattern matching for `instanceof` (Java 16).** `if (o instanceof String s && !s.isEmpty())`: tests the type **and** gives a typed variable, no cast line. `s` exists only where the test is known true.

**Section 4: pattern matching for `switch` (Java 21).** `case Type name -> ...` with optional guards `when condition`:

```
null (handled explicitly, no NullPointerException)
integer 7
big integer 700
blank string
string "hi"
int array of length 2
a day: FRIDAY
something else: Double
```

Rules: the **first** matching case wins, so put specific cases (`Integer i when i > 100`) before general ones (swapping them is the compile error "dominated by a preceding case label"). `case null` is available; without it, `null` throws `NullPointerException`.

**Sealed shapes** make a switch exhaustive with no `default`.

**Section 5: record patterns (Java 21).** Take a record apart in the pattern, even nested:

```
the origin
point at 3,4
line of length 5.00
not a geometry object
```

`case Line(Point(var x1, var y1), Point(var x2, var y2))` extracts four numbers in one line.

**Section 6: rules.** Prefer arrow switches; expressions must be exhaustive; specific patterns first; do not use patterns where plain polymorphism (a method on each class you own) is simpler.

## Key Rules

1. Use `->` form: no accidental fall-through.
2. A switch expression must be exhaustive.
3. Order cases from specific to general.
4. `yield` returns a value from a block case.

## Gotchas Recap

- A `default` that swallows everything can hide a missing case.
- Guards (`when`) do not count toward exhaustiveness.
- Pattern switch on a `null` selector throws unless `case null` exists.

## Why This Structure Exists

It walks from the old switch's traps to each modern feature that fixes one, ending with the combination (record patterns) that is hardest to read first.
