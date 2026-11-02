> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Builder

## Concept

**Problem:** a constructor with many parameters (some optional) is unreadable: `new UnreadablePizza("large", true, false, true, false)` (what do those booleans mean?), plus "telescoping constructors" for every combination. **Solution:** a separate `Builder` collects values with **named** methods, then `build()` creates the finished, immutable object after validating it. **Trade-off:** a second class and more code; for 2-3 required fields, or for records, a constructor or static factory is simpler.

## Full Line-by-Line Breakdown

**The product `Pizza`.** Final fields, a **private** constructor taking the builder, and a defensive `List.copyOf` of the toppings so the pizza is immutable. `Pizza.builder("large")` is the entry point and takes the **required** value.

**The nested `Builder`.** Each setter returns `this`, so calls chain:

```java
Pizza.builder("large").thinCrust().extraCheese().topping("mushrooms").topping("olives").build();
```

```
medium pizza, no toppings
large pizza, thin crust, extra cheese, toppings [mushrooms, olives]
small pizza, thin crust, toppings [ham, pineapple]
```

A builder can also be driven by loops and conditions (the `custom` example).

**Validation in one place.** `build()` checks the **whole** object before it exists:

```
rejected: unknown size 'gigantic'
rejected: too many toppings: 6 (max 5)
rejected: size is required
```

The last one comes from `Objects.requireNonNull` in the builder's constructor.

**Immutability.** A pizza built from a builder is not changed when the builder is used again: `first pizza is unaffected by later builder changes: small pizza, toppings [ham]`.

## Key Rules

1. Required values go in the entry point; optional ones become methods.
2. Validate in `build()`, not in the setters.
3. The product has a private constructor and immutable fields.
4. Copy mutable collections when building.

## Gotchas Recap

- Reusing one builder for several products can leak state between them unless `build()` copies.
- A builder that cannot reject invalid combinations is just verbose setters.
- Library tools (e.g. Lombok's `@Builder`) can generate this boilerplate in real projects.

## Why This Structure Exists

The unreadable constructor sits next to the builder so the improvement is visible. Exit test: `Point.builder().x(1).y(2).build()` is worse than `new Point(1, 2)`; and records already give named components.
