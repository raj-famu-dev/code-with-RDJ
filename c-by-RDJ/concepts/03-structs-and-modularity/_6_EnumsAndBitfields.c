// Tags: #C #Enums #Bitfields | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

/* An enum is a set of named int constants. The values are just ints. */
enum status { OK = 0, ERR_IO = 1, ERR_NET = 2, ERR_FATAL = 3 };

/* Without explicit values, they auto-increment from 0. */
enum color { RED, GREEN, BLUE };          /* 0, 1, 2 */

/* Bitfields: struct members measured in BITS. The compiler packs them
   into the enclosing storage unit — the C way to model hardware registers
   and flag sets. */
typedef struct {
    unsigned int enabled   : 1;    /* 1 bit  */
    unsigned int mode      : 2;    /* 2 bits: values 0-3 */
    unsigned int priority  : 3;    /* 3 bits: values 0-7 */
    unsigned int           : 2;    /* unnamed: 2 bits of padding */
    unsigned int reserved  : 4;    /* 4 bits */
} Reg32;                             /* total: 12 bits -> one 4-byte unit */

int main(void) {
    /* Enums are ints: comparable, printable, switchable */
    enum status s = ERR_NET;
    printf("status = %d\n", s);
    s = (s == ERR_NET) ? OK : ERR_FATAL;
    printf("after fix, status = %d\n", s);

    switch (s) {
    case OK:       printf("all good\n"); break;
    case ERR_IO:   printf("io problem\n"); break;
    case ERR_NET:  printf("net problem\n"); break;
    case ERR_FATAL: printf("fatal\n"); break;
    }

    /* Bitfields: set and read individual bit groups */
    Reg32 r = { 0 };
    r.enabled = 1;
    r.mode = 3;          /* binary 11 */
    r.priority = 5;      /* binary 101 */
    printf("enabled=%u mode=%u priority=%u\n", r.enabled, r.mode, r.priority);
    printf("sizeof(Reg32) = %zu (12 bits packed into one storage unit)\n", sizeof(Reg32));

    /* Overflowing a bitfield truncates silently: 5 needs 3 bits, 9 does not fit in 3.
       The warning is the lesson — suppressed only for this deliberate line. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Woverflow"
    r.priority = 9;      /* 9 = binary 1001; only the low 3 bits (001) survive */
#pragma GCC diagnostic pop
    printf("priority=9 stored as %u (truncated!)\n", r.priority);

    /* The enum+bitfield idiom: names for the bit meanings */
    enum { CAP_READ = 1, CAP_WRITE = 2, CAP_EXEC = 4 };   /* powers of two */
    unsigned caps = CAP_READ | CAP_EXEC;                   /* OR to combine */
    printf("caps: read=%d write=%d exec=%d\n",
           (caps & CAP_READ) != 0, (caps & CAP_WRITE) != 0, (caps & CAP_EXEC) != 0);
    return 0;
}
