// Tags: #C #FileIO #TextIO #Fgets #Sscanf | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <string.h>

int main(void) {
    /* WRITE: fprintf writes formatted text to any FILE*. */
    FILE *f = fopen("_2_demo.csv", "w");
    if (!f) { perror("fopen"); return 1; }
    fprintf(f, "id,name,gpa\n101,RDJ,3.75\n202,Raj,3.50\n");
    fclose(f);

    /* READ + PARSE: fgets for the line, sscanf for the fields.
       The newline issue: fgets keeps it; strcspn removes it. */
    FILE *in = fopen("_2_demo.csv", "r");
    if (!in) { perror("fopen"); return 1; }

    char line[128];
    int header = 1;
    while (fgets(line, sizeof line, in) != NULL) {
        if (header) { header = 0; continue; }

        int id;
        char name[32];
        double gpa;

        /* %31s bounds the string; the return COUNT is the validation */
        if (sscanf(line, "%d,%31[^,],%lf", &id, name, &gpa) == 3) {
            printf("parsed: id=%d name=%s gpa=%.2f\n", id, name, gpa);
        } else {
            printf("bad line: '%s'\n", line);
        }
    }
    fclose(in);
    return 0;
}
