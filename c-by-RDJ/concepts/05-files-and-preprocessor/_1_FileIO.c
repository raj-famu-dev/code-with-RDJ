# File Input and Output

fopen opens a stream. The w mode creates or truncates a text file. Check for NULL before using the stream. fprintf writes formatted text. Check write and close results because errors can be reported during either operation. The file is created in the program's current working directory. Extend this example to read it back with fgets.

## Expected output

Wrote c-lab-output.txt

## Practice

Modify the example, compile it with warnings enabled, run it, and explain the result. Test at least one boundary case and one invalid-input case where relevant.
