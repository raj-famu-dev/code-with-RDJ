> 📘 Reference material drafted with Claude. Not yet learned: retype `_1_VarAndTextBlocks.java`, break it on purpose, then rewrite this walkthrough in your own words.

# var and Text Blocks

## Concept

`var` (Java 10) lets the compiler infer a **local** variable's type. Text blocks (Java 15) are multi-line strings without `\n` and `\"` noise.

## Full Line-by-Line Breakdown

**Section 1: `var` is still static typing.** `var count = 10;` is an `int` forever (`count = "text"` would not compile). It is not JavaScript's `var`.

```
count is Integer, name is String, prices is ArrayList
```

(The program boxes `count` to print its class, hence `Integer`.)

**Section 2: where `var` helps.** The type is obvious or very long: `var concise = new HashMap<String, List<Integer>>();` writes the type once instead of twice. Also useful in `for (var entry : map.entrySet())`.

**Section 3: where `var` hurts.**
- When the right-hand side hides the type (`var result = compute();`).
- `var bigger = 1;` is an `int`, not a `long`: say `long wanted = 1;` when you mean it.
- `var list = new ArrayList<>();` is `ArrayList<Object>` (the diamond has nothing to infer from), so a mixed list compiles: `[1, mixed]`.
- Not allowed: no initializer, `null`, a lambda without a target type, array initializers, and fields, parameters or return types (locals only).
- Names carry more weight: `customers` beats `data`.

**Section 4: text blocks.** Open with `"""` + a newline, close with `"""`. The JSON example equals the old escaped string (`true`).

**Section 5: indentation.** The compiler removes the **common** leading whitespace, including the closing `"""` line. Moving the closing delimiter left keeps more indentation (`[    kept four spaces]`).

**Section 6: special escapes.** A trailing `\` joins lines (no newline); `\s` is a space that is not stripped (trailing spaces are otherwise removed: 3 vs 6 characters); `\"""` is a literal triple quote.

**Section 7: `formatted()`** fills `%s`/`%d` placeholders.

**Section 8: rule of thumb.** Use `var` when the type is obvious from the right-hand side. Text blocks for JSON/SQL/HTML, but never glue user input into SQL (still injection, see `10-jdbc-sql`).

## Key Rules

1. `var` is for locals with an initializer.
2. Use it when the line already tells the reader the type.
3. The closing `"""` position controls indentation.
4. Names matter more when you use `var`.

## Gotchas Recap

- `var x = 1;` is `int`.
- `var x = new ArrayList<>();` is `ArrayList<Object>`.
- Trailing spaces inside a text block vanish unless you write `\s`.

## Why This Structure Exists

Each feature is shown with its best use and its misuse, which is what the exit test asks for.
