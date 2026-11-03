CC ?= cc
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -g
.PHONY: all clean
all: student-records
student-records: main.c
	$(CC) $(CFLAGS) $< -o $@
clean:
	rm -f student-records students.txt
