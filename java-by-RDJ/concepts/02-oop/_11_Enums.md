# `_11_Enums.java`

## Concept
Enums — a fixed, named set of constants, optionally carrying their own fields, constructors, methods, and even constant-specific method implementations.

## Full Line-by-Line Breakdown

### `public class _11_Enums {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is An Enum?

**`Day today = Day.WEDNESDAY;`**
Assigns one of `Day`'s seven fixed constants to a variable. Notice the type is `Day` (the enum itself), not `String` or `int`.

---

### SECTION 2: Why Not Just Use Strings Or Ints Instead?
No executable code — just conceptual framing, with a commented-out example (`Day.WENDSDAY`) showing that a typo in an enum constant is a **compile error**, unlike a misspelled String literal which would compile fine but silently be wrong.

---

### SECTION 3: Comparing Enum Values

**`if (today == Day.WEDNESDAY)`**
Uses `==` to compare enum values — and unlike Strings, this is **safe and correct** for enums, since each constant (`Day.WEDNESDAY`) is a single, unique, shared instance that only ever exists once in memory.

**`today.equals(Day.WEDNESDAY)`**
Also works identically here — `.equals()` is available but `==` is the idiomatic convention for enums specifically.

---

### SECTION 4: Using Enums In A Switch Statement

**`switch (today) { case MONDAY, TUESDAY, ... -> ...; case SATURDAY, SUNDAY -> ...; }`**
The modern arrow-style switch (recap from `_5_ControlFlow.java`), now used with enum constants directly — notice cases reference `MONDAY`, `WEDNESDAY`, etc. **without** prefixing them as `Day.MONDAY` inside the switch body, since Java already knows the type being switched on.

---

### SECTION 5: Built-In Enum Methods

**`today.name()`**
Returns the exact constant name as a `String` — `"WEDNESDAY"`.

**`today.ordinal()`**
Returns the **zero-based position** of this constant in its declaration order — `WEDNESDAY` is the 3rd constant listed, so its ordinal is `2`.

**`Day.values()`**
Returns an array containing every constant in the enum, in declaration order — used here in a for-each loop to print all seven days along with each one's ordinal.

**`Day.valueOf("FRIDAY")`**
Converts a `String` into its matching enum constant — the commented-out `Day.valueOf("Frday")` (with a typo) would throw an `IllegalArgumentException` at runtime, since no exact match exists.

---

### SECTION 6: Enums With Fields And Constructors

**`Planet earth = Planet.EARTH;`**
Accesses one specific constant from the `Planet` enum — but unlike `Day`, each `Planet` constant carries its **own data** (gravity and distance from the sun).

**`earth.getGravity()` / `earth.getDistanceFromSun()`**
Calls getter methods defined on the enum itself, returning `EARTH`'s specific stored values.

**`for (Planet p : Planet.values()) { System.out.println(p + ": " + p.getGravity() + " m/s^2"); }`**
Loops through every planet constant, printing each one's own gravity value — proving each constant genuinely holds independent data, not just a shared label.

---

### SECTION 7: Enums With Their Own Methods

**`p.calculateWeight(70)`**
Calls a regular (non-getter) method defined on the `Planet` enum, using that specific constant's own `gravity` field internally to compute a weight-equivalent for a 70kg person on that planet.

---

### SECTION 8: Enums With Constant-Specific Method Bodies

**`for (TrafficLight light : TrafficLight.values()) { System.out.println(light + " means: " + light.getAction()); }`**
Loops through `RED`, `YELLOW`, `GREEN` — each one calling `getAction()`, but getting a **different** answer per constant (`"Stop"`, `"Slow down"`, `"Go"`), because each constant supplies its own override of that method body, defined right where the constant itself is declared.

---

### SECTION 9: When To Use Enums
No new code — a decision guide: use enums for a small, fixed, known set of values, for compile-time safety against typos, when each option needs its own data/behavior, or whenever you'd otherwise reach for "magic strings" or "magic numbers."

---

### The `Day` Enum

```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}
```
The simplest possible enum — just a fixed list of named constants, no fields or methods attached.

---

### The `Planet` Enum

```java
enum Planet {
    MERCURY(3.7, 57.9),
    VENUS(8.9, 108.2),
    EARTH(9.8, 149.6),
    MARS(3.7, 227.9);

    private final double gravity;
    private final double distanceFromSun;

    Planet(double gravity, double distanceFromSun) {
        this.gravity = gravity;
        this.distanceFromSun = distanceFromSun;
    }

    double getGravity() { return gravity; }
    double getDistanceFromSun() { return distanceFromSun; }

    double calculateWeight(double massOnEarthKg) {
        return massOnEarthKg * (gravity / 9.8);
    }
}
```
Each constant (`MERCURY(3.7, 57.9)`, etc.) calls the enum's own **constructor** with its own specific values the moment the enum class is loaded. The constructor here has no explicit access modifier — enum constructors are always implicitly private (or package-private); you could never write `new Planet(...)` yourself. `calculateWeight()` divides this constant's own `gravity` by Earth's standard gravity (`9.8`) to scale a given mass proportionally.

---

### The `TrafficLight` Enum

```java
enum TrafficLight {
    RED {
        @Override
        String getAction() { return "Stop"; }
    },
    YELLOW {
        @Override
        String getAction() { return "Slow down"; }
    },
    GREEN {
        @Override
        String getAction() { return "Go"; }
    };

    abstract String getAction();
}
```
`abstract String getAction();` declares that every constant **must** provide its own implementation — similar in spirit to an abstract method in `_8_AbstractClasses.java`. Each constant (`RED`, `YELLOW`, `GREEN`) then supplies its own `{ }` body immediately after its name, overriding `getAction()` with a completely different return value each time.

## Key Rules / Gotchas Recap

- Enum constructors are always implicitly private — you can never instantiate an enum constant yourself with `new`
- `ordinal()` reflects declaration order only — reordering constants shifts every ordinal value, so never rely on it for anything meaningful like database storage
- `valueOf()` throws `IllegalArgumentException` on no match — validate untrusted input before calling it
- `==` is safe and idiomatic for enum comparison, unlike Strings, since each constant is one unique shared instance

## Why This Structure Exists

Enums are the correct tool whenever a