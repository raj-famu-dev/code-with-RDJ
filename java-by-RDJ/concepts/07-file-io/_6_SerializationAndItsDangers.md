> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Serialization and Its Dangers

## Concept

**Serialization** turns an object (and everything it references) into bytes and back. A class opts in with the marker interface `Serializable`. It is convenient, and a long-standing source of security problems, so the main lesson is **when not to use it**. This file contains no attack code.

## Full Line-by-Line Breakdown

**Classes.** `User` has a `serialVersionUID` (a version stamp: a mismatch on load gives `InvalidClassException`), an `Address` field (must be `Serializable` too), a `transient` password (never written), and a `readObject` that re-validates.

**Section 2: round trip (in memory with byte arrays).**

```
    (constructor ran for ada)
serialized to 226 bytes
deserializing:
name = ada, age = 36, city = London
same object? false (a different object with equal content)
transient password after reading: null  (never saved)
```

Note: **no** constructor line appears during deserialization. The constructor is skipped, so its checks are skipped too. (The byte count can differ on other JDKs.)

**Section 3: not everything serializes.** A field of a non-serializable type gives `NotSerializableException: NotSerializableThing`. The compile output warns about that field: that one `[serial]` warning is deliberate.

**Section 4: `readObject` validation.** A user with `age = -5` is rejected on the way in: `readObject rejected the data: age cannot be negative`.

**Section 6: the danger.** `ObjectInputStream` loads whatever class the bytes name and runs its deserialization code **before** your cast `(User) in.readObject()`. Attackers have exploited this for years (a vulnerability class known as CWE-502). Rules:
1. Never deserialize data from outside your trust boundary (network, uploads, cookies, user-supplied files).
2. Prefer JSON or CSV (`_5`) to exchange data.
3. If you must use it, set an allow-list filter.

**Section 7: `ObjectInputFilter` allow-list (Java 9+).** The pattern lists permitted classes and ends with `!*` to reject everything else. The filter runs before objects are created:

```
filter allowed the expected classes: ada
filter rejected an unexpected class: InvalidClassException
```

**Section 8: other reasons to avoid it.** The format is tied to your class layout, exposes private fields, and is hard to evolve. Modern teams use JSON, Protocol Buffers or a database.

## Key Rules

1. Never deserialize untrusted bytes.
2. `transient` fields are not saved (they come back as `null`/`0`).
3. Constructors do not run on deserialization: re-validate in `readObject`.
4. Declare `serialVersionUID` explicitly.
5. Prefer JSON/CSV/DB; if you must, use an allow-list filter.

## Gotchas Recap

- The cast does not protect you: it happens after the dangerous work.
- A `final` field marked `transient` stays `null` after loading.
- Changing a class (adding fields) can break old saved files.

## Why This Structure Exists

It shows the mechanics first, then the failure modes, then the defence, so you learn serialization as something to be treated with caution, not a convenient save button.
