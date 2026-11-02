# `_6_ExceptionChaining.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
Exception chaining wraps a low-level exception inside a higher-level one **while keeping the original as the cause**. The caller sees a meaningful message, and you can still find the real problem.

## Full Line-by-Line Breakdown

### The helper code
- `ConfigException` has two constructors; the second takes a `Throwable cause` and passes it to `super(message, cause)`.
- `readPort(String)`: the low level; `Integer.parseInt` throws `NumberFormatException`.
- `loadPortGood`: catches it and throws `new ConfigException("Invalid port setting: '" + text + "'", e)`: **cause kept**.
- `loadPortBad`: throws `new ConfigException("Invalid port setting")`: **cause thrown away**.
- `printCauseChain(Throwable)`: walks `getCause()` in a loop, indenting each level.

### SECTION 1: Why chaining exists
Each layer speaks its own language (file layer: `IOException`, config layer: "invalid setting"). A higher layer should translate, but the original technical cause is what you need to debug.

### SECTION 2: The good way
```
-> ConfigException: Invalid port setting: '80a'
  -> NumberFormatException: For input string: "80a"
```
`getCause()` is a `NumberFormatException`.

### SECTION 3: Trap: losing the cause
```
-> ConfigException: Invalid port setting
getCause() is null
```
Nothing says **which** text failed or why. This turns a five-minute bug into a two-hour one.

### SECTION 4: Wrapping a checked exception in an unchecked one
Useful when an interface does not allow `throws`. Output shows `RuntimeException: Could not complete request` caused by `IOException: socket closed`. Always pass the cause.

### SECTION 5: Rules of thumb
Pass the original as the cause whenever you translate. Do not log **and** rethrow at every layer (the same error shows many times); log in one place, usually the top. `printStackTrace()` prints the whole chain with `Caused by:` lines.

## Key Rules / Gotchas Recap
- `new SomeException("msg", cause)` or `initCause`; never drop the cause
- Read stack traces to the **bottom** `Caused by:` to find the root cause
- Translate for the caller, preserve for the developer

## Why This Structure Exists
Layered programs need layered errors, but the debugging information lives at the bottom layer. Chaining lets both coexist.
