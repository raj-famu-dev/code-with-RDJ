# Project 01 — Console Calculator

**Status:** ⬜ Not started · **Needs:** `01-basics` only

## 📌 Project Description

A menu-driven console calculator that never crashes. It is the first real program in this repo, so the goal is clean structure: small methods, safe input, and honest error messages.

## 📋 Requirements

### Functional Requirements
1. **Basic operations** — add, subtract, multiply, divide, modulus
2. **Extra operations** — power, square root, percentage
3. **Division by zero and square root of a negative number** — detected and reported, never a crash or a silent `Infinity` / `NaN`
4. **History** — keep the last 10 calculations and let the user view them
5. **Memory** — store, recall, and clear a single value
6. **Exit** — clean shutdown, `Scanner` closed

### Non-Functional Requirements
- Menu loops until the user chooses to exit
- Any non-numeric input recovers with a clear message (use the `hasNextDouble()` pattern from `project-04`)
- Each operation is its own method; `main()` only routes
- Results are formatted consistently (no `3.0000000000000004` shown to the user)

## 🔍 Things to Decide and Document in the Project `.md`
- Why `double` instead of `float` or `int`, and what happens with `0.1 + 0.2`
- How you store the 10-item history using only what `01-basics` has taught (a fixed array and a counter)
- What the program does when the history is full

## ✅ Definition of Done
- [ ] `Calculator.java` plus `Calculator.md` (full walkthrough, same format as `project-04`)
- [ ] A self-check table mapping every requirement above to the code that meets it
- [ ] Five inputs you tried that broke it, and how you fixed each
- [ ] A "Possible Extensions" section

## 🚀 Possible Extensions
- Expression parsing (`2 + 3 * 4`) with correct operator precedence
- Replace the history array with an `ArrayList` after finishing `03-collections`
