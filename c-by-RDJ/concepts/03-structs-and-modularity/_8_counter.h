/* _8_counter.h — the INTERFACE. Declare, don't define.
   Include guards make double inclusion harmless. */
#ifndef COUNTER_H
#define COUNTER_H

/* extern: "this NAME exists, its storage is defined in some .c file." */
extern int counter_total(void);
extern void counter_reset(void);
extern void counter_bump(void);

#endif /* COUNTER_H */
