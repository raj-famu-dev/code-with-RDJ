# `_3_StackVsHeap.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Local variables live on the stack: they are created when execution reaches them and destroyed automatically, in reverse order, when the block ends. Objects created with `new` live on the heap: they stay alive until you explicitly `delete` them, whatever the scope. The stack is fast and tiny; the heap is flexible but you are responsible for freeing. Java hides this choice (all objects are on the heap, the GC frees them); C++ makes you decide.

## Full Line-by-Line Breakdown

### SECTION 1: AUTOMATIC (STACK) LIFETIME
`Tracker` prints from its constructor and destructor so lifetime is visible. Inside the block, `stack-A` is built and then `stack-B`; at the closing brace they are destroyed in REVERSE order (B then A) automatically, with no `delete` and no garbage collector.

Output from a real run:

```text
===== SECTION 1: AUTOMATIC (STACK) LIFETIME =====
entering block
  [ctor stack-A]
  [ctor stack-B]
leaving block (destructors run in REVERSE order automatically)
  [dtor stack-B]
  [dtor stack-A]
after block: both are gone
```

### SECTION 2: DYNAMIC (HEAP) LIFETIME WITH new/delete
`new Tracker(...)` allocates on the heap and runs the constructor; the object survives until `delete`, which runs the destructor and frees the memory. Setting the pointer to `nullptr` afterwards avoids leaving a dangling pointer. Arrays use `new int[4]` and MUST be freed with `delete[]`: mixing `delete` and `delete[]` is undefined behaviour. This raw `new`/`delete` is shown only to teach the mechanism; real code uses smart pointers (see `_6_SmartPointers`).

Output from a real run:

```text
===== SECTION 2: DYNAMIC (HEAP) LIFETIME WITH new/delete =====
  [ctor heap-1]
heap-1 still alive after no scope exit; name = heap-1
  [dtor heap-1]
deleted
sum of heap array = 10
```

### SECTION 3: WHERE THINGS LIVE (RELATIVE FACTS ONLY)
`stack_int` is a local in the current function's frame. `heap_int` is a pointer variable ALSO on the stack, but the `int` it points to is on the heap. No raw addresses are printed because they change every run; instead the demo prints sizes and one labelled measurement: a callee's local has a LOWER address than its caller's, because the stack grows downward on x86-64 Linux. That is a platform fact, not a language rule.

Output from a real run:

```text
===== SECTION 3: WHERE THINGS LIVE (RELATIVE FACTS ONLY) =====
stack_int is a variable (lives in this function's frame); *heap_int points into the heap
the pointer variable heap_int ITSELF is on the stack; what it points at is on the heap
sizeof(heap_int) = 8 bytes (measurement), sizeof(*heap_int) = 4
measurement: callee's local is at a LOWER address than the caller's (the stack grows downward on x86-64 Linux)
stack_int + *heap_int = 10
```

### SECTION 4: LEAK-PROOF PATTERN AND EXCEPTIONS
If an exception is thrown while a stack object exists, C++ unwinds the stack and runs its destructor before the `catch` runs (the dtor line appears before `caught`). Heap memory held by a raw pointer would NOT be freed in that case: `Tracker* t = new ...; might_throw(); delete t;` leaks if `might_throw()` throws. The fix is to let a stack object own the heap object (RAII), the subject of the next lessons.

Output from a real run:

```text
===== SECTION 4: LEAK-PROOF PATTERN AND EXCEPTIONS =====
  [ctor stack-guard]
  [dtor stack-guard]
caught: boom (the stack object was still destroyed first)
```

### SECTION 5: STACK SIZE LIMIT (DESCRIBED)
The stack is small (commonly about 8 MB on Linux; `ulimit -s` shows the limit). A huge local array or unbounded recursion overflows it and crashes. Large data belongs on the heap, and `std::vector` puts its elements there for you.

Output from a real run:

```text
===== SECTION 5: STACK SIZE LIMIT (DESCRIBED) =====
The stack is small (commonly about 8 MB on Linux; check with `ulimit -s`). A huge local array or
unbounded recursion overflows it. Large data belongs on the heap (std::vector does this for you).
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `new Foo()` always allocates on the heap | `Foo f;` on the stack; `new Foo` on the heap; you choose |
| Garbage collector frees unreachable objects | Stack objects die at the closing brace; heap objects live until `delete` |
| No destructors (`finalize` is deprecated and unreliable) | Destructors run deterministically and in reverse order |
| Forgetting to free is impossible | Forgetting `delete` is a memory leak; deleting twice is undefined behaviour |
| `StackOverflowError` for deep recursion | Stack overflow crashes the process (segfault) |
| Local primitives on the stack, objects on the heap | Both kinds of variable can be on either |

## Key Rules / Gotchas Recap
- Stack objects are destroyed automatically in reverse order of creation.
- Heap objects live until you `delete` them: every `new` needs exactly one `delete`, every `new[]` one `delete[]`.
- A raw pointer to a heap object leaks if an exception or early return skips the `delete`.
- The stack is small: put big data on the heap (use `std::vector`).
- Never print raw addresses in tests or logs: they change every run.
- Prefer smart pointers and containers over raw `new`.

## Why This Structure Exists
Where an object lives decides its speed, its lifetime and its failure modes. Stack allocation is why C++ can be fast enough for real-time and inference code, and heap lifetime errors (leaks, use-after-free) are the most common memory-safety bugs that security work looks for.
