# `_1_PointersAndAddresses.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A pointer is a variable that holds the memory address of another object. `&x` gives the address of `x`, `*p` follows a pointer to the object it points at, and `p + 1` moves to the next element of the same type. A pointer that points at nothing is `nullptr`, and dereferencing it is undefined behaviour. Pointers are how C++ talks to memory directly, and `std::vector` iterators, arrays and most of the standard library are built on them.

## Full Line-by-Line Breakdown

### SECTION 1: ADDRESS-OF AND DEREFERENCE
`int* p = &x;` stores the address of `x`. Writing through `*p` changes `x` itself (25, then 26 via the copy `q`). Copying a pointer copies the address, so `p == q` is true and both reach the same int; copying the value (`int y = x`) makes an independent number. Actual addresses are never printed because they differ on every run (address space layout randomisation); comparing pointers and printing what they point at is enough. `sizeof(int*)` is 8 bytes on this 64-bit machine (a measurement).

Output from a real run:

```text
===== SECTION 1: ADDRESS-OF AND DEREFERENCE =====
x = 10, *p = 10
after *p = 25, x = 25
p and q point to the same object: true, x = 26
copying the value leaves x alone: x = 26, y = 0
sizeof(int*) = 8 bytes (measurement: pointer width on this machine)
```

### SECTION 2: POINTER ARITHMETIC OVER AN ARRAY
An array name decays to a pointer to its first element. `*(begin + 2)` and `begin[2]` are identical: indexing is defined as pointer arithmetic. Adding 1 to an `int*` advances by `sizeof(int)` bytes automatically, and subtracting two pointers into the same array gives a count of ELEMENTS (5, not 20). `end = arr + 5` is a legal one-past-the-end pointer that you may compare against but never dereference; the loop `for (it = begin; it != end; ++it)` is exactly how STL iterators work. Going outside `[begin, end]` is undefined behaviour even without dereferencing. A C string walk shows the same idea stopping at the `'\0'` terminator.

Output from a real run:

```text
===== SECTION 2: POINTER ARITHMETIC OVER AN ARRAY =====
*(begin + 2) = 30, begin[2] = 30 (a[i] is *(a + i))
end - begin = 5 elements (not bytes)
sum via pointer walk = 150
after ++mid, *mid = 40 (ptr + 1 moves by sizeof(int) bytes automatically)
(mid - begin) = 3, begin < mid is true
walking a C string: A-B-C-end (stops at the null terminator)
```

### SECTION 3: nullptr AND NULL CHECKS
`nullptr` means "points at nothing"; a null pointer is false in a condition, and the lambda `safe_read` tests it before dereferencing, returning -1 for null. Dereferencing a null pointer is undefined behaviour (typically a crash). Use `nullptr`, not the old macro `NULL` (which is just 0 and can select the wrong overload).

Output from a real run:

```text
===== SECTION 3: nullptr AND NULL CHECKS =====
none == nullptr: true
a null pointer is false in a condition
safe_read(&x) = 26, safe_read(nullptr) = -1
```

### SECTION 4: const AND POINTERS
Read declarations right to left. `const int*` is a pointer to a const int: you may re-point it but not write through it. `int* const` is a const pointer to an int: you may write through it but not re-point it. The demo re-points the first and writes through the second.

Output from a real run:

```text
===== SECTION 4: const AND POINTERS =====
read through ptr_to_const: 9, after write via const_ptr other = 9
Read right to left: 'const int*' = pointer to const int; 'int* const' = const pointer to int.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| No pointers; object variables are references managed by the JVM | Explicit pointers (`T*`) holding raw addresses |
| `null` | `nullptr`; dereferencing it is undefined behaviour, not a `NullPointerException` |
| `arr[i]` always checked | `p[i]` is `*(p + i)`: unchecked |
| Cannot do arithmetic on references | `p + 1`, `p - q` are normal and powerful |
| Cannot print an address (only `hashCode`) | Addresses are real values, but printing them is rarely useful |
| Garbage collector frees memory | You (or a smart pointer) decide when memory is freed |

## Key Rules / Gotchas Recap
- `&x` is the address, `*p` is the object it points at.
- Copying a pointer copies the address, not the object.
- `ptr + n` moves by `n` elements, and `p - q` counts elements.
- One-past-the-end is a legal pointer value; anything beyond is undefined behaviour, and one-past-the-end must never be dereferenced.
- Always initialise pointers (`nullptr` if nothing) and check before dereferencing.
- Use `nullptr`, never `NULL` or `0`.
- `const int*` = pointer to const; `int* const` = const pointer.

## Why This Structure Exists
Pointers are the foundation of everything native: data structures, arrays, buffers, and calling C libraries from AI frameworks. They are also where memory-safety vulnerabilities live, so being precise about what a pointer points to, how far it may move, and when it may be null is core to both performance work and secure coding.
