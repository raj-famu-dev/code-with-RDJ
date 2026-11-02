> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Factory

## Concept

**Problem:** code scattered with `new EmailNotifier()` / `new SmsNotifier()` and if/else on a type string is welded to every concrete class; adding one means editing every place. **Solution:** callers ask a factory for "a notifier of kind X" and get back the **interface**. **Trade-off:** one more class and a layer of indirection; worth it only when creation logic is non-trivial or likely to grow.

## Full Line-by-Line Breakdown

**The products.** `Notifier` with `EmailNotifier`, `SmsNotifier` (truncates to 20 characters) and `PushNotifier` (needs a device token).

**Step 1: the problem.** `callerWithoutFactory` contains the if/else; copy it into five places and you have five places to edit.

**Step 2: simple (static) factory.** `NotifierFactory.create(kind)` is the only place that knows the classes. Unknown kinds throw `IllegalArgumentException`:

```
EMAIL -> Deployment finished successfully
SMS -> Deployment finished 
PUSH[device-42] -> Deployment finished successfully
unknown kind: unknown kind 'pigeon'
```

**Step 3: factory method.** The base class `Alert` has the shared workflow `raise(...)` and an abstract `createNotifier()`; subclasses decide the product:

```
[ALERT] SMS -> Database is down and
[ALERT] EMAIL -> 3 new signups today
```

**Step 4: registry of suppliers.** A `Map<String, Supplier<Notifier>>`: a new kind (`slack`) is **one line** with no edits to the factory (the Open/Closed idea from `_1`). The error message lists known kinds: `unknown kind 'fax'; known: [email, slack, sms]`.

## Key Rules

1. Callers should depend on the interface, not the concrete class.
2. Keep the "which class?" decision in one place.
3. A registry of `Supplier`s is the modern way to keep it open for extension.
4. Fail loudly on unknown kinds, and list the valid ones.

## Gotchas Recap

- A big `switch` in the factory still needs editing for each new kind (fine for small, fixed sets).
- Factories that return `null` for unknown input push the failure further away.
- Do not confuse the simple factory (a method), the factory method (inheritance) and the abstract factory (families of products).

## Why This Structure Exists

Three versions from simplest to most flexible. Exit test: a `UserFactory` whose only method is `return new User(name)` is pure ceremony: one product and no decision to hide.
