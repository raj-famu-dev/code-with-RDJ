# `_2_TextIO.c`

## Concept
The text-file pattern: write with `fprintf`, read with `fgets`, parse with `sscanf` — each layer bounded and checked. This trio is the C equivalent of Python's `with open()` + `for line in f`, with the discipline made explicit.

## The Code

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *f = fopen("_2_demo.csv", "w");
    if (!f) { perror("fopen"); return 1; }
    fprintf(f, "id,name,gpa\n101,RDJ,3.75\n202,Raj,3.50\n");
    fclose(f);

    FILE *in = fopen("_2_demo.csv", "r");
    if (!in) { perror("fopen"); return 1; }

    char line[128];
    int header = 1;
    while (fgets(line, sizeof line, in) != NULL) {
        if (header) { header = 0; continue; }

        int id;
        char name[32];
        double gpa;

        if (sscanf(line, "%d,%31[^,],%lf", &id, name, &gpa) == 3) {
            printf("parsed: id=%d name=%s gpa=%.2f\n", id, name, gpa);
        } else {
            printf("bad line: '%s'\n", line);
        }
    }
    fclose(in);
    return 0;
}
```

## Line-by-Line Breakdown

### `fprintf(f, ...)` — printf to a stream
Same format mini-language as `printf`, destination as the first argument. All formatted output (`printf`, `fprintf`, `sprintf`, `snprintf`) is one function family.

### `fgets(line, sizeof line, in)`
The bounded line reader: at most `sizeof line - 1` bytes, stops at `'\n'` **which it keeps**, returns NULL at EOF. `while (fgets(...))` is the canonical whole-file loop.

### `sscanf(line, "%d,%31[^,],%lf", &id, name, &gpa)`
Parse the *string*, not the stream:
- `%d` — the id
- `%31[^,]` — "up to 31 chars that are NOT a comma" (bounded!) into `name` — the CSV-safe alternative to `%s`
- `%lf` — the gpa (note: `scanf` needs `%lf` for `double`, while `printf` uses `%f` — asymmetric and a classic bug)

### The return count is the validation
`sscanf` returns the number of successful conversions — 3 means every field landed. Anything less means the line didn't match; the demo prints it instead of trusting garbage values. **Never use the variables after a short parse.**

### Buffering (why text I/O is fast)
`fprintf` writes to an in-memory buffer; the library flushes to the OS in big blocks (and fully on `fclose`). This is why an un-closed write loses data — the bytes may still be in the buffer.

## Traps
- `fgets` keeps the `'\n'` — strip it (`line[strcspn(line, "\n")] = '\0';`) or your last field has a hidden newline.
- Lines longer than the buffer are split across reads — size your buffer or check `strchr(line, '\n')` to detect truncation.
- `fscanf` on a stream has the Module-01 `scanf` pitfalls; parse lines, not streams.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _2_TextIO.c && ./demo
```

## Why This Structure Exists
Read-a-line-then-parse splits the two failure modes cleanly: `fgets` can't overflow (bounded), and `sscanf`'s return count validates the format. Together they give C what higher-level languages bake into `csv.reader` — with every decision visible.
