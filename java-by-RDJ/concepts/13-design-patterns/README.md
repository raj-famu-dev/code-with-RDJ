<div align="center">

<img src="../../assets/modules/13-design-patterns.svg" alt="Design Patterns and SOLID: Observer, strategy, factory and friends. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-10-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Observer, strategy, factory and friends*

[Overview](#-overview) •
[Topics](#-topics) •
[Concept Notes](#-concept-notes) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 12](../12-build-tools/) · [Java Mastery Lab](../../README.md) · [Module 14](../14-dsa-in-java/) ➡

</div>

---

## 🎯 Overview

**Priority: LATER.** Patterns only make sense after you have written enough code to feel the problems they solve.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic. Each `.md` must state: problem, solution, trade-off.

**Module status:** ✅ Completed: written, run and explained (written with Claude, disclosed).

**Authorship:** Written with Claude (Sonnet 5.5), then compiled and verified. The first line of every file states its origin.

## 📚 Topics

| # | File | Status |
|---|---|:---:|
| 1 | `_1_SolidPrinciples` (one violation and its fix for each principle) | ✅ |
| 2 | `_2_Singleton` (three implementations, thread-safety trade-offs) | ✅ |
| 3 | `_3_Factory` | ✅ |
| 4 | `_4_Builder` | ✅ |
| 5 | `_5_Adapter` | ✅ |
| 6 | `_6_Decorator` | ✅ |
| 7 | `_7_Strategy` | ✅ |
| 8 | `_8_Observer` | ✅ |
| 9 | `_9_Command` | ✅ |
| 10 | `_10_RefactorBankSystem` (apply two patterns to `project-03`, show before and after) | ✅ |

## 📖 Concept Notes

A short explanation of every topic. The linked walkthrough has the full line-by-line breakdown, the traps and the gotchas.

### 1. Solid Principles

Five guidelines for code that must **change** over time. The file shows, for each letter, a **violation** and its **fix**.

**Problem:** code that is hard to change without breaking something else. **Solution:** the five principles below. **Trade-off:** they add classes and interfaces; if the code will never change, they add cost for no benefit.

📄 [`_1_SolidPrinciples.java`](./_1_SolidPrinciples.java) · 📝 [walkthrough](./_1_SolidPrinciples.md)

### 2. Singleton

**Problem:** some things should exist exactly once (a configuration, a pool, a logger). **Solution:** hide the constructor and hand out the single instance. **Trade-off:** it is a global variable in disguise: hard to test, hides dependencies, creates tight coupling. Dependency injection is often better.

📄 [`_2_Singleton.java`](./_2_Singleton.java) · 📝 [walkthrough](./_2_Singleton.md)

### 3. Factory

**Problem:** code scattered with `new EmailNotifier()` / `new SmsNotifier()` and if/else on a type string is welded to every concrete class; adding one means editing every place. **Solution:** callers ask a factory for "a notifier of kind X" and get back the **interface**. **Trade-off:** one more class and a layer of indirection; worth it only when creation logic is non-trivial or likely to grow.

📄 [`_3_Factory.java`](./_3_Factory.java) · 📝 [walkthrough](./_3_Factory.md)

### 4. Builder

**Problem:** a constructor with many parameters (some optional) is unreadable: `new UnreadablePizza("large", true, false, true, false)` (what do those booleans mean?), plus "telescoping constructors" for every combination. **Solution:** a separate `Builder` collects values with **named** methods, then `build()` creates the finished, immutable object after validating it. **Trade-off:** a second class and more code; for 2-3 required fields, or for records, a constructor or static factory is simpler.

📄 [`_4_Builder.java`](./_4_Builder.java) · 📝 [walkthrough](./_4_Builder.md)

### 5. Adapter

**Problem:** your code expects interface A; a legacy or third-party class (which you cannot or should not edit) offers the same capability through interface B. **Solution:** a small class that **implements A** and internally **calls B**, like a travel plug adapter. **Trade-off:** one more layer that can hide a poor fit (units, error handling, performance); if you can change the original class, change it instead.

📄 [`_5_Adapter.java`](./_5_Adapter.java) · 📝 [walkthrough](./_5_Adapter.md)

### 6. Decorator

**Problem:** you want optional extras in any combination (milk, sugar, logging, caching). With inheritance you would need a subclass per combination: `CoffeeWithMilkAndSugar`, and so on (an explosion). **Solution:** each extra is a small **wrapper** that implements the same interface, holds the thing it wraps, and adds its bit before or after delegating. Wrappers stack in any order. **Trade-off:** many tiny classes, debugging goes through layers, the **order** of wrappers can matter, and callers cannot tell which wrappers are present.

📄 [`_6_Decorator.java`](./_6_Decorator.java) · 📝 [walkthrough](./_6_Decorator.md)

### 7. Strategy

**Problem:** a class contains an if/else (or switch) choosing between several ways of doing the same job (shipping cost, discount, sorting); adding a way means editing that class. **Solution:** each way becomes a small object behind one interface, and the class receives the one to use. **Trade-off:** more types, and callers must choose. In Java a one-method strategy is just a **functional interface**, so a lambda is often all you need.

📄 [`_7_Strategy.java`](./_7_Strategy.java) · 📝 [walkthrough](./_7_Strategy.md)

### 8. Observer

**Problem:** when something happens (an order is placed), several other parts must react (email, stats, audit). If the source calls them directly it is welded to each of them. **Solution:** the source (publisher) keeps a list of listeners behind one small interface and notifies them; listeners register and unregister themselves. **Trade-off:** control flow becomes indirect (who runs when I fire this?), order may matter, a failing or slow listener can hurt everyone, and forgetting to unsubscribe leaks memory.

📄 [`_8_Observer.java`](./_8_Observer.java) · 📝 [walkthrough](./_8_Observer.md)

### 9. Command

**Problem:** with direct method calls (`editor.insert("x")`) the action vanishes after it runs: no undo, no history, no replay, no queueing. **Solution:** turn each action into an **object** with `execute()` and `undo()`; an invoker runs commands and keeps the history. **Trade-off:** one class per action, every command needs a correct undo, and undoing external effects (a sent email, a charged card) may be impossible.

📄 [`_9_Command.java`](./_9_Command.java) · 📝 [walkthrough](./_9_Command.md)

### 10. Refactor Bank System

**Problem:** a small bank where one class decides fees by if/else on account type **and** prints receipts **and** "emails" a manager. **Solution:** apply **Strategy** for fees and **Observer** for reactions. **Trade-off:** more types and indirection; for two account types and one print line the original would have been fine.

> Honest note: `projects/project-03-bank-system` is only a specification so far. This file is a **miniature** bank with the same ideas (account types, fees, history). When you build project-03, repeat this refactor on **your** code. Money is whole cents in a `long`, never `double`.

📄 [`_10_RefactorBankSystem.java`](./_10_RefactorBankSystem.java) · 📝 [walkthrough](./_10_RefactorBankSystem.md)

## 🧪 Exit Test

for any pattern, name a situation where using it would make the code worse.

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/13-design-patterns
javac -d out _*.java
java -cp out _1_SolidPrinciples
```

`out/` is git-ignored. Swap `_1_SolidPrinciples` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ completed (written, run and explained in a walkthrough) · 🔄 in progress · ⬜ not started.

✅ = completed: the `.java` file and its `.md` walkthrough are written, compiled and run. Each file's first line states who wrote it.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>Completed means written, run and explained in a walkthrough. These files were written with Claude (Sonnet 5.5) and say so in their first line.</sub>

⬅ [Module 12](../12-build-tools/) · [Java Mastery Lab](../../README.md) · [Module 14](../14-dsa-in-java/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
