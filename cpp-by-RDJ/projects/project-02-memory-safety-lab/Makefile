# Project 02: memory safety lab. Targets: all, test, run, sanitize, clean, lab.
# Every buggy program is built WITH -fsanitize=address,undefined so the sanitizers can report it.
CXX      = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -Wpedantic -g
SAN      = -fsanitize=address,undefined
NAMES    = use_after_free heap_overflow leak double_free stack_overflow_array uninitialized_read
BUGGY    = $(addprefix bin/bugs/,$(NAMES))
FIXED    = $(addprefix bin/fixed/,$(NAMES))

.PHONY: all test run sanitize lab clean

all: $(BUGGY) $(FIXED) bin/lab_check

bin/bugs/%: bugs/%.cpp
	@mkdir -p bin/bugs
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ $<

bin/fixed/%: bugs/fixed/%.cpp
	@mkdir -p bin/fixed
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ $<

bin/lab_check: lab_check.cpp
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) -o $@ lab_check.cpp

bin/lab_check_san: lab_check.cpp
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ lab_check.cpp

# Runs every buggy program with --trigger and every fixed program, and checks the sanitizer's verdict.
test: all
	./bin/lab_check

# Fixed programs (clean) and, for the buggy ones, the harmless no-flag mode (the bug is NOT triggered).
run: all
	@for n in $(NAMES); do echo "--- fixed/$$n"; ./bin/fixed/$$n || exit 1; done
	@for n in $(NAMES); do echo "--- bugs/$$n (no --trigger: bug not run)"; ./bin/bugs/$$n || exit 1; done

# The checker itself, built with the sanitizers too (it must be clean), then run.
sanitize: all bin/lab_check_san
	./bin/lab_check_san

# Runs each buggy program under the sanitizers and rewrites RESULTS.md with the REAL reports (normalised).
lab: all
	./tools/lab.sh

clean:
	rm -rf bin
