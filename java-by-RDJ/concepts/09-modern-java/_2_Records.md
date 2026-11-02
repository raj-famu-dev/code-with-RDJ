> 📘 Reference material drafted with Claude. Not yet learned: retype `_2_Records.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Records

## Concept

A **record** is a transparent, immutable holder of data. From the header alone, `record Point(int x, int y) { }` gives you: private final fields, a constructor, accessors `x()` and `y()` (not `getX()`), and `equals`, `hashCode`, `toString` based on all components.

## Full Line-by-Line Breakdown

**Section 1: free behaviour.**

```
toString:  Point[x=3, y=4]
accessors: x() = 3, y() = 4
equals:    true, same object: false
```

The hand-written `OldPoint` (about 30 lines) behaves the same.

**Section 2: compact constructor.** `Email { ... }` has no parameter list and no field assignments: the compiler assigns the fields **after** your code runs, so reassigning the parameter changes what is stored:

```
normalized email: Email[address=ada@example.com], domain: example.com
validation: not an email: nonsense
```

Records can have ordinary methods (`domain()`).

**Section 3: extras.** A `static final` constant (`Range.EMPTY`), another constructor (it must delegate with `this(...)`), and a static factory `Range.of(9, 2)` that fixes the order (`Range[low=2, high=9]`). Validation throws `low 5 > high 1`.

**Section 4: shallow immutability.** Fields are final, but a `List` inside is still a mutable list:

```
leaky team members: [Ada, Linus, Intruder]
safe team members:  [Ada, Linus]
```

`SafeTeam` makes a defensive copy with `List.copyOf` in the compact constructor; modifying it throws `UnsupportedOperationException`.

**Section 5: other features.** Records can implement interfaces (`Circle implements Shape`), be generic (`Pair<A, B>`), and be declared **locally** inside a method (`record Score(...)`).

**Section 6: limits.** A record is implicitly `final`, cannot extend a class, cannot add instance fields, has no setters. Poor fit for JPA entities (need mutability and a no-arg constructor) and for objects with identity (two accounts with equal fields are not the same account).

## Key Rules

1. Records are for data carriers.
2. Validate and normalize in the compact constructor.
3. Copy mutable components defensively.
4. Accessors are `name()`, not `getName()`.

## Gotchas Recap

- `equals` compares **all** components, including mutable ones.
- A compact constructor that forgets to validate leaves the record invalid forever.
- Records are not a drop-in replacement for every class.

## Why This Structure Exists

The hand-written `OldPoint` sits next to the record so the saved boilerplate is something you can count.
