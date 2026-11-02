> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Observer

## Concept

**Problem:** when something happens (an order is placed), several other parts must react (email, stats, audit). If the source calls them directly it is welded to each of them. **Solution:** the source (publisher) keeps a list of listeners behind one small interface and notifies them; listeners register and unregister themselves. **Trade-off:** control flow becomes indirect (who runs when I fire this?), order may matter, a failing or slow listener can hurt everyone, and forgetting to unsubscribe leaks memory.

## Full Line-by-Line Breakdown

**The pieces.** `OrderPlaced` (a record event), `OrderListener` (one method), `OrderService` (the subject). It uses a `CopyOnWriteArrayList` so a listener can unsubscribe during notification, and **catches `RuntimeException` per listener** so one failure does not stop the others.

**Listeners.** `EmailReceipt`, `SalesStats`, `FraudCheck` (throws for totals over 1000).

```
--- no listeners ---                      (nothing happens, and that is fine)
--- three listeners ---
  email: receipt for A-2 total 50.0
  email: receipt for A-3 total 2500.0
  (listener failed: order A-3 flagged as suspicious, continuing)
```

The failing `FraudCheck` did not stop the email or the stats.

**Lambdas as listeners.** `OrderListener auditor = e -> audit.add(e.orderId());` gives `audit log: [A-4]`.

**Unsubscribing.** After `unsubscribe(email)` the next order prints no email line. Final: `stats: 4 orders, revenue 2565.00` (orders A-2, A-3, A-4, A-5; A-1 had no listeners).

**A generic `Topic<T>`** with `Consumer<T>` subscribers shows the idea in a few lines (`reader 1 got: Java 21 released`, `reader 2 got: JAVA 21 RELEASED`).

**Where you have seen it.** GUI listeners, `PropertyChangeListener`, Spring's event publisher, `Flow.Publisher`. `java.util.Observable` is deprecated since Java 9: do not use it.

## Key Rules

1. The publisher knows only the listener interface.
2. Protect the notification loop from a failing listener.
3. Always provide a way to unsubscribe.
4. Do not depend on listener order unless you enforce it.

## Gotchas Recap

- Exceptions inside listeners can silently disappear if caught carelessly.
- Listeners that never unsubscribe keep objects alive.
- Notifications run on the publisher's thread: a slow listener blocks the publisher.

## Why This Structure Exists

Stages go from none, to several, to failing, to removed, so each risk in the trade-off is demonstrated. Exit test: if only one thing ever reacts, call it directly; the pattern hides a simple call.
