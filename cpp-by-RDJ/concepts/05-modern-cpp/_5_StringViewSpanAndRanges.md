# `_5_StringViewSpanAndRanges.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::string_view` and `std::span` are non-owning "windows" onto existing memory: a pointer plus a length, with no copying. `std::ranges` and `std::views` let you chain operations (`filter`, `transform`, `take`) lazily, so nothing is computed until you iterate, similar in spirit to Java streams. Views make code both faster and more flexible, but they do not own what they point at, so they can dangle if the owner dies first.

## Full Line-by-Line Breakdown

### SECTION 1: string_view
`count_vowels(std::string_view)` accepts a `std::string`, a C string and a literal with no copies, which is why it is the best parameter type for read-only text. `substr` on a view is O(1) (it adjusts the pointer and length), and `remove_prefix` shrinks the window. TRAPS: a `string_view` is not guaranteed null-terminated, so passing `.data()` to a C function can read past the end; and a view must never outlive the string it points at. A view of a string literal is safe because literals live for the whole program.

Output from a real run:

```text
===== SECTION 1: string_view =====
vowels in std::string: 8
vowels in C string:    10
vowels in literal:     0
substr view: "education" size=9
after remove_prefix(10): "is the key"
starts_with("is")? true
TRAP: a string_view is NOT null-terminated, so never pass sv.data() to a C function expecting a C string.
TRAP: never return a view of a local (see dangling_view), and never keep one past its owner's life.
A view of a string literal is safe, literals live for the whole program: safe literal
```

### SECTION 2: std::span
`std::span<const int>` accepts a vector, a C array, or part of one, without copying; `subspan(2, 2)` is the middle two elements (3 + 4 = 7). A non-const `std::span<int>` writes through to the underlying vector (`zero_first_half`). TRAP (described, not run): a span is a pointer and a length, so if `push_back` reallocates the vector, an existing span points at freed memory.

Output from a real run:

```text
===== SECTION 2: std::span =====
sum_span(vector) = 21
sum_span(C array) = 60
sum of the middle two via subspan = 7
after zero_first_half(vec): 0 0 0 4 5 6
TRAP: push_back on the vector can reallocate and leave an existing span pointing at freed memory.
```

### SECTION 3: ranges VIEWS PIPELINE
`nums | views::filter(...) | views::transform(...)` builds a pipeline reading left to right: keep evens, then square them. Iterating it gives 4, 16, 36, 64, 100. `views::reverse | views::take(3)` takes the last three. `views::iota(1, 6)` generates 1..5. C++20 has no `ranges::to`, so the code collects into a vector with a loop. `std::ranges::sort(v)` is the range version of `std::sort` (no `begin()/end()` needed).

Output from a real run:

```text
===== SECTION 3: ranges VIEWS PIPELINE =====
squares of evens: 4 16 36 64 100
take(3) of reversed: 10 9 8
iota(1,6) = 1 2 3 4 5 
collected into a vector of size 5
ranges::sort: 1 2 5 9
```

### SECTION 4: LAZINESS
Views are lazy. Building the pipeline runs the transform zero times (`calls=0`). Reading the first element runs it once. Iterating 3 elements with `take(3)` runs it 3 more times, 4 in total (the first element was computed again because a view does not cache), and the other 7 elements are never touched. Laziness also makes infinite sources workable: `views::iota(1)` is unbounded but `take(5)` stops it after five even squares. TRAP: the view stores references to `nums` and to the lambda, so changing `nums[0]` changes what the view yields (1000 instead of 10), and a view over a temporary container dangles.

Output from a real run:

```text
===== SECTION 4: LAZINESS =====
built the view; transform calls so far: 0
first element 10; calls so far: 1
iterated 3 elements (sum 60); total calls: 4 (the other 7 never ran)
Infinite source is fine when lazy, first 5 even squares from iota(1): 4 16 36 64 100
TRAP: the view holds a reference to nums and the lambdas; changing nums changes what the view yields.
after nums[0]=100, *lazy.begin() = 1000
```

### SECTION 5: THE DANGLING VIEW BUG (opt-in)
This section is an opt-in bug demo. By default it is skipped and prints the fix. With `--dangling` the program calls `dangling_view()`, which returns a `string_view` of a local `std::string`. The string dies when the function returns, so reading the view is undefined behaviour. Running that under `-fsanitize=address` gave a real report: `AddressSanitizer: heap-use-after-free ... READ of size 46`. (The local string is made long on purpose so it lives on the heap; a short string would sit inside the stack object and hide the bug from AddressSanitizer.) The fix is to return a `std::string` by value or a view of storage that outlives the call.

Output from a real run:

```text
===== SECTION 5: THE DANGLING VIEW BUG (opt-in) =====
skipped; run with --dangling to read a view whose string was destroyed (use -fsanitize=address).
fix: return std::string by value, or a view of a longer-lived owner: returned views must ...
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `String.substring` creates a new String (copy in modern JDKs). | `string_view::substr` is a no-copy window; the owner must outlive it. |
| Arrays and `List` are separate types; `subList` is a view backed by the list. | `std::span` views any contiguous sequence (array, vector, std::array) uniformly. |
| `list.stream().filter(...).map(...)` is lazy until a terminal operation (`collect`, `forEach`). | `v \| views::filter(...) \| views::transform(...)` is lazy until you iterate it. |
| A stream can be consumed once; elements flow through a pipeline of objects. | A view can be iterated many times (and recomputes each time); it is a lightweight object, not a collection. |
| `Stream.iterate(1, x -> x + 1).limit(5)` | `views::iota(1) \| views::take(5)` |
| Garbage collector keeps referenced data alive, so views cannot dangle. | No GC: a view of a dead object is a dangling pointer (undefined behaviour). |

## Key Rules / Gotchas Recap
- Use `std::string_view` for read-only string parameters; return `std::string` when you must own the result.
- `string_view` is not null-terminated; do not hand `.data()` to C APIs.
- Never store a view or span longer than its owner lives; mutating or reallocating the owner can invalidate it.
- Views are lazy: no work until iteration, and the lambda runs again on each pass.
- Views do not own data; they reference the source container and the lambdas.
- C++20 has `ranges::sort`, `views::*`; `ranges::to` is C++23 (not available here).

## Why This Structure Exists
Parsing logs, network packets and model files without copying is a performance staple, and `string_view` / `span` are how modern C++ expresses it. Understanding dangling views is also a direct introduction to the use-after-free class of memory bugs that security work studies.
