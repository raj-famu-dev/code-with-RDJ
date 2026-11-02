> 📘 Reference material drafted with Claude. Not yet learned: retype `_1_SolidPrinciples.java`, break it on purpose, then rewrite this walkthrough in your own words.

# SOLID Principles

## Concept

Five guidelines for code that must **change** over time. The file shows, for each letter, a **violation** and its **fix**.

**Problem:** code that is hard to change without breaking something else. **Solution:** the five principles below. **Trade-off:** they add classes and interfaces; if the code will never change, they add cost for no benefit.

## Full Line-by-Line Breakdown

**S, Single Responsibility: one reason to change.** `BadReport` calculates, formats CSV **and** saves. Fix: `Calculator`, `CsvFormatter`, `Storage`, one job each:

```
  (saving to disk) 10.0,20.5, total=30.5
```

**O, Open/Closed: open for extension, closed for modification.** `BadAreaCalculator` needs an edit for every new shape. Fix: an interface `Shape` with `Circle`, `Rectangle`, and a `Square` added later with **no other class edited**: `total area with a Square added later = 13.14`.

**L, Liskov Substitution: a subtype must work wherever its parent does.** The classic trap, `MutableSquare extends MutableRectangle` (setting the width also sets the height):

```
MutableRectangle gives 10 (expected 10)
MutableSquare gives    4 (expected 10: the 'subtype' broke the contract)
```

Code written for "any rectangle" breaks. Fix: do not force the inheritance; both are `Shape`s.

**I, Interface Segregation: no forced methods.** A fat `FatWorker` interface forces `Robot.eat()` to throw `UnsupportedOperationException` ("robots do not eat"). Fix: small `Workable` and `Eatable`; `Human` implements both, `SlimRobot` only one.

**D, Dependency Inversion: depend on abstractions.** `BadAlertService` creates its own `SmsSender`. Fix: depend on `MessageSender` and **pass it in** (constructor injection). A `FakeSender` test double now captures messages: `test captured: [test alert]`.

## Key Rules

1. Many reasons to change in one class: split it.
2. Add behaviour by adding classes, not by editing a growing if/else.
3. Subtypes must keep the parent's promises.
4. Prefer several small interfaces to one big one.
5. Pass dependencies in; do not construct them inside.

## Gotchas Recap

- "A Square is a Rectangle" is true in maths, false for mutable objects.
- An interface with one implementation and no reason to change is ceremony.
- Splitting a 10-line class into five tiny ones can hurt readability.

## Why This Structure Exists

Each principle is a violation next to its fix, with output where it matters (Liskov's 10 versus 4), so you see the damage before the cure. Exit test: when did applying SOLID make the code worse? When nothing will change.
