CC ?= cc
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -g
.PHONY: all clean
all: calculator
calculator: main.c
	$(CC) $(CFLAGS) $< -o $@
clean:
	rm -f calculator
