# `_6_ArraysAndVectors.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A C array is a fixed block of memory whose length the compiler forgets as soon as you pass it to a function (it "decays" to a pointer to the first element). `std::array` keeps the size in its type, and `std::vector` is a resizable array that owns a heap buffer: when it runs out of capacity it allocates a bigger one and moves everything. The most important behaviour to learn is that `operator[]` does no bounds checking, while `at()` throws.

## Full Line-by-Line Breakdown

### SECTION 1: C ARRAYS AND DECAY
In the scope where it is declared, `sizeof(c_arr)/sizeof(c_arr[0])` gives 5. As soon as the array becomes a pointer (assigned to a `const int*`, or passed to a function) its length is lost and `sizeof` reports the size of the pointer (8 bytes on this 64-bit platform: a measurement, not a language rule). `c_arr[2]` and `*(c_arr + 2)` are the same thing by definition, which is why indexing is just pointer arithmetic. g++ even warns if you write the sizeof trick inside a function, which is why the demo only prints the pointer size.

Output from a real run:

```text
===== SECTION 1: C ARRAYS AND DECAY =====
sizeof(c_arr)/sizeof(c_arr[0]) in the same scope = 5
sizeof(decayed pointer) = 8 (just a pointer; length is lost)
inside a function the same array is seen as sizeof = 8 (pointer size, so sizeof(arr)/sizeof(arr[0]) no longer gives 5)
c_arr[2] == *(c_arr + 2): true
```

### SECTION 2: std::array
`std::array<int, 5>` is a thin wrapper that keeps the length in the type, has `size()`, `front()`, `back()`, supports `==`, and copies by value (the copy is independent). A function template can take the size `N` as a parameter, so the length is never lost.

Output from a real run:

```text
===== SECTION 2: std::array =====
size() = 5, front = 10, back = 50
size_of_std_array(arr) = 5 (length is part of the type)
copy[0]=99 arr[0]=10 (independent)
arr == copy: false
```

### SECTION 3: vector GROWTH
A new vector has capacity 0. Every `push_back` that exceeds capacity allocates a bigger buffer and moves the elements. The printed growth (1, 2, 4, 8, 16, 32) is what libstdc++ does; the standard only promises that `push_back` is amortised constant time, so another library may grow differently. `reserve(20)` allocates once up front, so filling 20 elements causes no reallocation. `shrink_to_fit` is only a request. The trap on the last line: `vector<int>(3, 7)` means "3 elements, each 7" but `vector<int>{3, 7}` is the list of elements 3 and 7.

Output from a real run:

```text
===== SECTION 3: vector GROWTH =====
start: size=0 capacity=0
  push #1 reallocated: capacity now 1
  push #2 reallocated: capacity now 2
  push #3 reallocated: capacity now 4
  push #5 reallocated: capacity now 8
  push #9 reallocated: capacity now 16
  push #17 reallocated: capacity now 32
with reserve(20): size=20 capacity=20 (no reallocation while filling)
after shrink_to_fit (a non-binding request): capacity=20
vector<int>(3, 7) has 3 elements; vector<int>{3, 7} has 2
```

### SECTION 4: BOUNDS: operator[] vs at()
`small[2]` is fine. `small[3]` would be undefined behaviour (no check, silent memory corruption or garbage), so the demo does not run it. `small.at(3)` checks and throws `std::out_of_range`, which the code catches. Use `at()` or a range-for when the index comes from outside your control; use `[]` in hot loops whose bounds you have already proven.

Output from a real run:

```text
===== SECTION 4: BOUNDS: operator[] vs at() =====
small[2] = 3 (operator[] does no checking; small[3] would be undefined behaviour)
small.at(3) threw std::out_of_range (message text is library-specific)
Rule: use at() or a checked loop when the index comes from outside; use range-for when you can.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `int[] a = new int[5];` always bounds-checked (`ArrayIndexOutOfBoundsException`) | `int a[5]` unchecked; `std::array::at()` / `vector::at()` check, `[]` does not |
| `a.length` always available | C array: length lost when passed to a function; `std::array::size()` keeps it |
| `ArrayList<Integer>` holds references to boxed Integers | `std::vector<int>` holds the ints contiguously in memory: faster, cache-friendly |
| Arrays are heap objects, passed by reference | `std::array` and `std::vector` copy by value on assignment |
| `ArrayList` capacity management is hidden | `capacity()`, `reserve()`, `shrink_to_fit()` exposed |
| Out-of-bounds always throws | Out-of-bounds with `[]` is undefined behaviour |

## Key Rules / Gotchas Recap
- A C array decays to a pointer when passed; the size is lost.
- Prefer `std::array` for fixed size and `std::vector` for dynamic size.
- `operator[]` is unchecked (UB when out of range); `at()` throws `std::out_of_range`.
- `push_back` may reallocate: pointers, references and iterators into the vector then dangle.
- `reserve(n)` avoids repeated reallocation when you know the size.
- `vector<int>(3, 7)` vs `vector<int>{3, 7}` mean different things.

## Why This Structure Exists
Out-of-bounds access on arrays is the root of a large share of real-world memory-safety vulnerabilities, so knowing exactly which accessors check and which do not is core security knowledge. The contiguous, cache-friendly layout of `std::vector` is also why numerical and AI code stores tensors in it instead of lists of boxed objects.
