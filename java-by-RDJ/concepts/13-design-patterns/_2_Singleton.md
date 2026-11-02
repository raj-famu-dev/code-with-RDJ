> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Singleton

## Concept

**Problem:** some things should exist exactly once (a configuration, a pool, a logger). **Solution:** hide the constructor and hand out the single instance. **Trade-off:** it is a global variable in disguise: hard to test, hides dependencies, creates tight coupling. Dependency injection is often better.

## Full Line-by-Line Breakdown

Four implementations, each with a private constructor that bumps a counter, so we can **prove** how many were built.

1. **Eager** (`EagerConfig`): `private static final INSTANCE = new ...`. Simple and thread-safe (class loading is safe); created even if never used.
2. **Lazy with double-checked locking** (`LazyConfig`). The naive `if (instance == null) instance = new ...` is **not** thread-safe: two threads can both see `null`. The fix needs a `volatile` field and two checks (one without the lock, one inside `synchronized`). Without `volatile` it can still break (see `05`).
3. **Initialization-on-demand holder** (`HolderConfig`): a nested `Holder` class loaded only on first use; the JVM guarantees safe class loading, so no locks are written by you. Lazy and thread-safe.
4. **Enum** (`EnumConfig.INSTANCE`): shortest and safest; the JVM guarantees one instance even against serialization and reflection tricks that can duplicate a normal class. It cannot extend another class.

**The race test.** 16 threads, released together by a `CountDownLatch`, fetch the three class-based singletons:

```
distinct objects seen across 16 racing threads (3 singletons): 3
constructor runs: eager=1, lazy=1, holder=1
```

Three singletons means three distinct objects in total, and each constructor ran once. (A correct result here is evidence, not proof: a race may need luck to appear.)

**The testing problem.** After `EnumConfig.INSTANCE.setMode("production")`, every later piece of code sees `production`. Tests that run afterwards inherit that state, so they are no longer independent.

## Key Rules

1. Make the constructor private.
2. Prefer the enum or holder idiom to hand-written locking.
3. Never write lazy initialization without thread-safety.
4. Keep singletons stateless or immutable when you can.

## Gotchas Recap

- Double-checked locking without `volatile` is broken.
- Singletons with mutable state leak between tests.
- Everything that calls `X.getInstance()` secretly depends on X.

## Why This Structure Exists

Four versions in order of how much the language does for you. Exit test: using a singleton as a convenient global `UserService`/`Database` makes code worse; pass it through the constructor instead.
