# `_11_ComparableVsComparator.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
Sorting needs a rule for "which comes first". `Comparable` builds **one natural rule into the class**. `Comparator` is a rule supplied **from outside**, and you can have as many as you like.

## Full Line-by-Line Breakdown

### The `Student` record
```java
record Student(String name, int grade, double gpa) implements Comparable<Student> {
    public int compareTo(Student other) { return name.compareTo(other.name); }
}
```
Natural order is by name. `compareTo` returns a negative number (this comes first), `0` (equal), or a positive number (this comes later). The four students are Maya, Ben, Ava, Zoe.

### SECTION 1: Natural order
`Collections.sort(students)` needs no extra argument: Ava, Ben, Maya, Zoe.

### SECTION 2: A different order from outside
`students.sort(Comparator.comparingDouble(Student::gpa))` sorts by GPA ascending: Zoe (3.2), Maya (3.5), Ava (3.9), Ben (3.9). Ava and Ben tie on GPA, so their relative order is unchanged (the sort is **stable**).

### SECTION 3: Chaining tie-breakers
```java
Comparator.comparingInt(Student::grade)
          .thenComparing(Student::gpa, Comparator.reverseOrder())
          .thenComparing(Student::name);
```
Grade ascending, then GPA high-to-low, then name: Ava, Maya, Ben, Zoe. `ranking.reversed()` flips the whole thing, so Zoe is first.

### SECTION 4: `nullsFirst`
`Comparator.nullsFirst(Comparator.naturalOrder())` sorts `["b", null, "a"]` to `[null, a, b]` instead of crashing.

### SECTION 5: Trap: comparing by subtraction
`(a, b) -> a - b` overflows with large values. `compare(Integer.MAX_VALUE, -1)` computes `MAX_VALUE - (-1)`, which wraps to `-2147483648`, claiming `MAX_VALUE < -1`. `Integer.compare` returns `1` (correct). Always use `Integer.compare` or `Comparator.comparingInt`.

### SECTION 6: Consistency with `equals`
`compareTo` should return `0` only when `equals` is `true`. Sorted collections (`TreeSet`, `TreeMap`) rely on the comparison, not on `equals` (see `_5`).

### SECTION 7: Comparable vs Comparator
Comparable: one natural order, inside the class, `compareTo(other)`. Comparator: any number of external orders, `compare(a, b)`.

## Key Rules / Gotchas Recap
- Never compare numbers by subtraction
- `thenComparing` handles ties; without it, ties stay in their previous order
- A `Comparator` works even on classes you cannot edit

## Why This Structure Exists
Real data is ranked by several rules at once (score, then level, then name). Comparator chains express that without writing nested `if` statements, and they are reused again in streams (`08-lambdas-streams`).
