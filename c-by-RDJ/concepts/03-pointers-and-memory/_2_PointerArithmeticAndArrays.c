# Pointer Arithmetic and Arrays

In most expressions, an array name converts to a pointer to its first element. Adding i advances by i elements, not i bytes. Dereferencing cursor + i accesses the same element as values[i]. Pointer arithmetic is defined only within the same array object or one position past its end; the one-past pointer may not be dereferenced.

## Expected output

values[0] = 10 through values[3] = 40

## Practice

Modify the example, compile it with warnings enabled, run it, and explain the result. Test at least one boundary case and one invalid-input case where relevant.
