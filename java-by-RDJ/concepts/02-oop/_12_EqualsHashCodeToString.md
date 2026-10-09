# `_12_EqualsHashCodeToString.java`

## Concept
Overriding Java's default `equals()`, `hashCode()`, and `toString()` behavior for custom classes — and why the `equals()`/`hashCode()` contract is critical for correct behavior in `HashSet`/`HashMap`.

## Full Line-by-Line Breakdown

### `import java.util.HashSet;` / `import java.util.HashMap;`
Imports the two collection types used later to demonstrate why this topic matters in practice.

### `public class _12_EqualsHashCodeToString {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: The Default toString() Problem

**`PersonUnoverridden person1 = new PersonUnoverridden("Alice", 30);`**
Creates an object of a class that never overrides `toString()`.

**`System.out.println("Default toString(): " + person1);`**
Since `person1` is concatenated into a String, Java automatically calls its `toString()` method — but because none was written, it falls back to `Object`'s default implementation, printing something like `PersonUnoverridden@1b6d3586` (the class name plus a memory address hash). Recap of the exact same issue first seen in `_6_Inheritance.java`'s Section 10.

---

### SECTION 2: Overriding toString()

**`Person person2 = new Person("Bob", 25);`**
Creates an object of `Person` — a class that **does** override `toString()`.

**`System.out.println("Overridden toString(): " + person2);`**
Now prints something genuinely readable: `Person{name='Bob', age=25}` — because `toString()` was overridden to return exactly that format.

**`System.out.println("Concatenated directly: " + "Info -> " + person2);`**
Proves `toString()` is called **automatically** any time an object is concatenated into a String — you never explicitly write `.toString()` yourself for this to happen.

---

### SECTION 3: The Default equals() Problem

**`PersonUnoverridden p1 = new PersonUnoverridden("Charlie", 40);` / `PersonUnoverridden p2 = new PersonUnoverridden("Charlie", 40);`**
Two **separate** objects, but with identical field values.

**`p1.equals(p2)`**
Returns `false`. Since `PersonUnoverridden` never overrides `equals()`, it inherits `Object`'s default behavior — which is functionally identical to `==`: it only checks whether both variables point to the **exact same object in memory**. Since `p1` and `p2` are genuinely two different objects (even with matching data), this returns `false`.

---

### SECTION 4: Overriding equals() Properly

**`Person person3 = new Person("Dana", 28);` / `Person person4 = new Person("Dana", 28);`**
Two separate `Person` objects with identical field values.

**`person3.equals(person4)`**
Returns `true` this time — because `Person`'s overridden `equals()` (defined below) compares actual **field content** (`name` and `age`) rather than memory identity.

**`Person person5 = new Person("Dana", 99);` / `person3.equals(person5)`**
Returns `false` — the ages differ (`28` vs `99`), so despite sharing the same name, they're correctly identified as unequal.

---

### SECTION 5: The equals()/hashCode() Contract

**`person3.hashCode()` / `person4.hashCode()`**
Both print the **same** hash code value.

**`person3.hashCode() == person4.hashCode()`**
Returns `true`. This isn't a coincidence — it's a direct consequence of `hashCode()` being overridden using the exact same fields (`name`, `age`) that `equals()` compares. **The rule:** if two objects are `.equals()` to each other, they *must* produce the same `.hashCode()` — breaking this contract causes silent, hard-to-diagnose bugs in hash-based collections.

---

### SECTION 6: Why This Contract Matters — HashSet Demonstration

**`HashSet<PersonUnoverridden> unsafeSet = new HashSet<>();`**
A `HashSet` — a collection that's supposed to automatically prevent duplicate entries.

**`unsafeSet.add(new PersonUnoverridden("Eve", 22));` (twice)**
Adds what should logically be a "duplicate" (same name, same age) twice.

**`unsafeSet.size()`**
Prints `2`, **not** `1`. Since `PersonUnoverridden` never overrides `equals()`/`hashCode()`, the `HashSet` has no way to recognize these two objects as "the same" — it sees two entirely distinct objects with different memory addresses, so both get added.

**`HashSet<Person> safeSet = new HashSet<>();`** (same pattern, using `Person` instead)
**`safeSet.size()`**
Prints `1` this time — because `Person`'s properly overridden `equals()`/`hashCode()` allow the `HashSet` to correctly recognize the second addition as a genuine duplicate of the first, and reject it.

---

### SECTION 7: HashMap Also Depends On This Contract

**`HashMap<Person, String> personRoles = new HashMap<>();`**
A map using `Person` objects as **keys**.

**`personRoles.put(new Person("Frank", 35), "Manager");`**
Stores a value, keyed by a specific `Person` object.

**`String role = personRoles.get(new Person("Frank", 35));`**
Looks up using a **different** `Person` object instance — but one with identical field values.

**`role` prints `"Manager"`**
This lookup only succeeds because `Person`'s `equals()`/`hashCode()` let the `HashMap` recognize this new object as logically matching the original key, even though it's a completely separate object in memory. Without proper overrides, this lookup would return `null` instead, since the map would see it as a totally unrelated key.

---

### SECTION 8: The Standard Pattern For Overriding equals()
No new executable code — a pointer to `Person.equals()` below, outlining the three-step defensive pattern used there.

---

### SECTION 9: Objects.equals() And Objects.hash()
No new executable code — a pointer to `Person`'s implementation below, which uses these two null-safe helper utilities from `java.util.Objects`.

---

### The `PersonUnoverridden` Class

```java
class PersonUnoverridden {
    String name;
    int age;

    PersonUnoverridden(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```
A deliberately "plain" class — no `toString()`, `equals()`, or `hashCode()` overrides at all, relying entirely on `Object`'s defaults. Exists purely as a contrast to demonstrate the problems this whole topic solves.

---

### The `Person` Class

**`toString()` override:**
```java
@Override
public String toString() {
    return "Person{name='" + name + "', age=" + age + "}";
}
```
Returns a custom, readable String representation instead of the default memory-address format.

**`equals()` override — the standard defensive pattern:**
```java
@Override
public boolean equals(Object obj) {
    if (this == obj) {
        return true;
    }
    if (obj == null || getClass() != obj.getClass()) {
        return false;
    }
    Person other = (Person) obj;
    return this.age == other.age && java.util.Objects.equals(this.name, other.name);
}
```
- **Step 1:** `if (this == obj) return true;` — a fast-path shortcut: if it's literally the same object in memory, they're trivially equal, no further checks needed
- **Step 2:** `if (obj == null || getClass() != obj.getClass()) return false;` — rejects comparisons against `null` or against an object of a completely different class
- **Step 3:** `Person other = (Person) obj;` then compares the actual meaningful fields — `this.age == other.age` for the primitive, and `Objects.equals(this.name, other.name)` for the `String` field, which safely handles the case where either name might be `null` without needing a manual null check

**`hashCode()` override:**
```java
@Override
public int hashCode() {
    return java.util.Objects.hash(name, age);
}
```
`Objects.hash(name, age)` combines both fields into a single hash code — critically, using the **exact same fields** that `equals()` compares. This consistency is what satisfies the equals/hashCode contract; mismatched fields between the two methods is the most common way this contract gets accidentally broken.

## Key Rules / Gotchas Recap

- This is arguably the single most consequential override pair in Java — get it wrong, and hash-based collections (`HashSet`, `HashMap`) will silently misbehave rather than throwing an obvious error
- Never override `equals()` without also overriding `hashCode()` — the compiler doesn't force this, but breaking the contract creates notoriously hard-to-trace bugs
- `Objects.hash(field1, field2, ...)` should always use the exact same fields your `equals()` compares
- `toString()` is called automatically any time an object is printed or concatenated into a String — never called explicitly

## Why This Structure Exists

Without overriding these three methods, `==`-style content comparison fails on custom objects (the same issue Strings have, but now on your own classes), and printing an object shows an unreadable memory address. This topic sits deliberately right before `03-collections`, since `HashMap`/`HashSet` behavior depends entirely on getting `equals()`/`hashCode()` right — get this wrong, and collection-based code will fail in ways that are genuinely difficult to debug without understanding exactly why.