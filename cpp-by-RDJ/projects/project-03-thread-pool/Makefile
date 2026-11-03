# Project 03: thread pool. Targets: all, test, run, sanitize, clean (+ tsan, run once to check for data races).
CXX      = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -Wpedantic -O0 -g -pthread
SAN      = -fsanitize=address,undefined -fno-sanitize-recover=all
TSAN     = -fsanitize=thread
SAN_WORDS = 300000

.PHONY: all test run sanitize tsan tsan-raw tsan-repro clean

all: tests main

tests: tests.cpp thread_pool.hpp
	$(CXX) $(CXXFLAGS) -o $@ tests.cpp

main: main.cpp thread_pool.hpp
	$(CXX) $(CXXFLAGS) -o $@ main.cpp

tests_san: tests.cpp thread_pool.hpp
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ tests.cpp

main_san: main.cpp thread_pool.hpp
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ main.cpp

tests_tsan: tests.cpp thread_pool.hpp
	$(CXX) $(CXXFLAGS) $(TSAN) -o $@ tests.cpp

main_tsan: main.cpp thread_pool.hpp
	$(CXX) $(CXXFLAGS) $(TSAN) -o $@ main.cpp

test: tests
	./tests

run: main
	./main

sanitize: tests_san main_san
	./tests_san
	./main_san $(SAN_WORDS)

# ThreadSanitizer (data races), WITH tsan.supp: narrow suppressions for a known libstdc++ exception_ptr report
# (explained in tsan.supp and the README). Any OTHER race still fails this target.
tsan: tests_tsan main_tsan
	TSAN_OPTIONS="suppressions=tsan.supp" ./tests_tsan
	TSAN_OPTIONS="suppressions=tsan.supp" ./main_tsan $(SAN_WORDS)

# The same run WITHOUT suppressions. In this environment it prints the libstdc++ exception_ptr reports and a "-" in front
# of the command lets make continue, so you can read them. Its exit code is printed, never hidden.
tsan-raw: tests_tsan main_tsan
	-./tests_tsan; echo "tests_tsan (no suppressions) exit code: $$?"
	-./main_tsan $(SAN_WORDS) > /dev/null; echo "main_tsan (no suppressions) exit code: $$?"

# Minimal reproducer with NO ThreadPool: shows the exception_ptr report comes from libstdc++ + TSan, not from this pool.
tsan_repro: tsan_repro.cpp
	$(CXX) $(CXXFLAGS) $(TSAN) -o $@ tsan_repro.cpp

tsan-repro: tsan_repro
	-./tsan_repro; echo "tsan_repro (no ThreadPool involved) exit code: $$?"

clean:
	rm -f tests main tests_san main_san tests_tsan main_tsan tsan_repro *.o
