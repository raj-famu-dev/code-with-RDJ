# Headers and the Preprocessor

The preprocessor handles directives before compilation. include makes declarations from a header available. define creates a macro replacement. ARRAY_LENGTH is intended for actual arrays, not pointers. Parentheses reduce precedence surprises. A macro such as SQUARE(i++) may evaluate its argument more than once; prefer a function when a macro is not necessary.

## Expected output

Count: 3; Square of 5: 25

## Practice

Modify the example, compile it with warnings enabled, run it, and explain the result. Test at least one boundary case and one invalid-input case where relevant.
