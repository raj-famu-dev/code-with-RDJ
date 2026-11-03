# `_6_SmartPointers.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Smart pointers are small RAII objects that own heap memory and free it automatically. `std::unique_ptr` has exactly one owner and cannot be copied (only moved). `std::shared_ptr` allows several owners and frees the object when the last one goes away, tracked with a reference count. `std::weak_ptr` observes a shared object without owning it, which is how you break reference cycles. With these, modern C++ code almost never writes `new` or `delete`.

## Full Line-by-Line Breakdown

### SECTION 1: unique_ptr (SOLE OWNER)
`std::make_unique<Widget>("U1")` allocates and wraps in one step (prefer it to `new`). You can lend the object with a plain reference (`just_use(*w)`) while keeping ownership. Moving transfers ownership: after `std::move`, the original is null. `take_ownership(std::move(moved))` hands the widget to the callee, and it is destroyed when the callee returns, before "back in caller" is printed. Copying a `unique_ptr` is a compile error, which is what enforces single ownership. `make_unique<int[]>(3)` creates an array that is value-initialised (zeros) and freed with `delete[]` automatically.

Output from a real run:

```text
===== SECTION 1: unique_ptr (SOLE OWNER) =====
  [Widget U1 created]
  using it: U1
  callee only borrows U1
  after move, original is null
  callee owns U1 and will destroy it
  [Widget U1 destroyed]
  back in caller
  unique_ptr<int[]> arr[0] = 5, arr[1] = 0 (make_unique value-initialises)
```

### SECTION 2: shared_ptr AND use_count
A new `shared_ptr` has count 1. Copying it (`b = a`, and copies inside a vector) raises the count to 4, and the count drops back to 1 when the inner scope ends. The object is destroyed only when the LAST owner is gone. `make_shared` allocates the object and its count together in one block. The trap in the comment: building two `shared_ptr`s from the same raw pointer gives two independent counts, so the object is deleted twice. Always copy an existing `shared_ptr`.

Output from a real run:

```text
===== SECTION 2: shared_ptr AND use_count =====
  [Widget S1 created]
  use_count after creation: 1
  use_count with b and a 2-element vector: 4
  use_count after the inner scope: 1
  leaving scope: last owner releases it
  [Widget S1 destroyed]
```

### SECTION 3: weak_ptr
A `weak_ptr` does not increase the count: `use_count` stays 1 while the observer exists. `lock()` returns a `shared_ptr` if the object is still alive (a temporary owner for the duration you use it) or an empty one if it is gone. After the owner leaves its scope the widget is destroyed, `expired()` is true, and `lock()` returns null, so checking the result is mandatory.

Output from a real run:

```text
===== SECTION 3: weak_ptr =====
  [Widget W1 created]
  use_count (weak does not count): 1
  lock() succeeded, name = W1
  [Widget W1 destroyed]
  expired after owner died: true
  lock() now returns null, so the check is mandatory
```

### SECTION 4: A REFERENCE CYCLE LEAKS (TRAP)
`x` points to `y` and `y` points to `x`, both with `shared_ptr`. Each object is therefore owned by the other as well as by its local variable, so both counts are 2. When the locals go away the counts only fall to 1, never 0, so neither destructor would ever run: a leak the garbage-collected world calls a cycle (Java's GC handles cycles; reference counting cannot). To keep this demo leak-free (it must also pass LeakSanitizer), the code breaks the cycle by hand with `reset()` before the scope ends, and then both destructors run.

Output from a real run:

```text
===== SECTION 4: A REFERENCE CYCLE LEAKS (TRAP) =====
  x use_count = 2, y use_count = 2 (each held by the other)
  if we just left the scope, neither destructor would run: a leak
  broke the cycle manually; now leaving scope
  [BadNode y destroyed]
  [BadNode x destroyed]
```

### SECTION 5: FIX WITH weak_ptr
In `GoodNode` the forward link `next` owns (`shared_ptr`) and the back link `prev` observes (`weak_ptr`), so there is no ownership cycle. `head` has count 1 (only its variable), `tail` has count 2 (its variable and `head->next`). On scope exit both objects are destroyed with no manual step.

Output from a real run:

```text
===== SECTION 5: FIX WITH weak_ptr =====
  head use_count = 1, tail use_count = 2
  leaving scope: both destructors run (no leak)
  [GoodNode head destroyed]
  [GoodNode tail destroyed]

Rule: default to unique_ptr; use shared_ptr only for true shared ownership; use weak_ptr for back-references.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Every object reference is managed by the GC | Smart pointers are opt-in libraries; plain `T*` is unmanaged |
| Cycles are collected automatically | `shared_ptr` cycles leak; break them with `weak_ptr` |
| Shared ownership is the default | `unique_ptr` (exclusive) is the default; `shared_ptr` only when truly shared |
| `WeakReference<T>` / `get()` may return null | `weak_ptr<T>::lock()` returns an empty `shared_ptr` |
| No notion of "ownership" in the type system | `unique_ptr` in a signature means "I take it", `T&`/`T*` means "I borrow" |
| Object freed at an unpredictable time | Freed deterministically when the last owner dies |

## Key Rules / Gotchas Recap
- Default to `std::unique_ptr`; it costs nothing extra over a raw pointer.
- Create with `std::make_unique` / `std::make_shared`, not `new`.
- `unique_ptr` is move-only; `std::move` it to transfer ownership; the source becomes null.
- Pass `T&` or `T*` to functions that only use the object; pass a `unique_ptr` by value to transfer ownership.
- `shared_ptr` copies bump an atomic reference count (a small cost); never create two from the same raw pointer.
- A `shared_ptr` cycle is a leak: use `weak_ptr` for back-references and always `lock()` and check before use.
- `use_count()` is for learning and debugging, not for program logic.

## Why This Structure Exists
Ownership expressed in types is how large C++ code bases avoid leaks and use-after-free without a garbage collector, and it is how inference runtimes manage model weights and buffers. Smart pointers also make code review and security audit easier: any raw `new`/`delete` stands out as something to examine.
