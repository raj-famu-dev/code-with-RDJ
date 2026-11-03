# Error Handling and Debugging

strtol converts text to long and reports where parsing stopped. Set errno to zero before the call so a range error can be detected. end equal to input means no digits were converted. A non-null character at end means extra characters remain. Compile with -Wall -Wextra -Wpedantic -Wconversion -Wshadow -g and test malformed and very large inputs.

## Expected output

Parsed value: 1234

## Practice

Modify the example, compile it with warnings enabled, run it, and explain the result. Test at least one boundary case and one invalid-input case where relevant.
