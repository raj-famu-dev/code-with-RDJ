# `_8_ExceptionsCapstone.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A batch input validator that combines the whole folder: a custom exception hierarchy, throwing early, chaining a cause, catch ordering, and catching **at the boundary** that can recover, so one bad record never crashes the run.

## Full Line-by-Line Breakdown

### The exception hierarchy
```
ValidationException (carries the field name)
  MissingFieldException
  InvalidFormatException   (keeps the original cause)
  OutOfRangeException      (carries value, min, max)
```
`ValidationException` is the shared parent. `record Person(name, age, email)` is the successful result.

### `parse(String line) throws ValidationException`
Splits the line on commas, then validates in order:
1. wrong field count → `ValidationException("record", ...)`
2. empty name → `MissingFieldException("name")`
3. non-numeric age → catches `NumberFormatException` and throws `InvalidFormatException(..., e)` (cause chained)
4. age outside 0 to 120 → `OutOfRangeException`
5. email without `@` → `ValidationException("email", ...)`

`parse` **reports** problems but does not decide what to do about them.

### SECTION 1: The input
Seven hard-coded lines, several deliberately bad.

### SECTION 2: Catching at the boundary
The loop is where the decision belongs: record the reason and move on. The `catch` order is specific subclasses first (`OutOfRangeException`, `InvalidFormatException`), then the parent `ValidationException`, which also covers `MissingFieldException` and the generic cases. For the format error the original cause is read from `e.getCause()`.

### SECTION 3: The report
```
Accepted 2 of 7 records:
  Person[name=Ava, age=30, email=ava@example.com]
  Person[name=Fay, age=35, email=fay@example.com]
Rejected 5:
  line 2 [format] age: 'abc' is not a whole number (cause: NumberFormatException)
  line 3 [other]  name: is required
  line 4 [range]  age: value 200 must be between 0 and 120
  line 5 [other]  email: 'dev-at-example.com' is missing '@'
  line 6 [other]  record: expected 3 fields but found 2
```

### SECTION 4: What this file puts together
Custom hierarchy (`_4`), throw early with clear messages (`_3`), chained cause (`_6`), catch order (`_1`), catch where you can recover.

## Key Rules / Gotchas Recap
- Throw deep, catch at the layer that can decide what to do
- Order `catch` blocks specific → general
- One bad record should not stop the batch

## Why This Structure Exists
Real input is messy. This pattern, validate in one place and handle failures in another, is the shape of almost every import, form, and API handler you will write later (and of `project-05`).
