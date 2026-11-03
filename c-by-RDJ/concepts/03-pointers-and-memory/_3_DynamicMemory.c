# Dynamic Memory Allocation

calloc requests storage for count zero-initialized integers. Always check for NULL before use. sizeof *values keeps the element type connected to the allocation. free releases allocated storage. Every successful allocation needs a clear owner responsible for releasing it exactly once. Avoid leaks, double frees and use-after-free errors.

## Expected output

10; 20; 30; 40; 50

## Practice

Modify the example, compile it with warnings enabled, run it, and explain the result. Test at least one boundary case and one invalid-input case where relevant.
