# Project 01: data structures from scratch. Targets: all, test, run, sanitize, clean (+ lint, used by test).
CXX      = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -Wpedantic -O0 -g
SAN      = -fsanitize=address,undefined -fno-sanitize-recover=all
HEADERS  = dynamic_array.hpp linked_list.hpp hash_map.hpp min_heap.hpp

.PHONY: all test run sanitize lint clean

all: tests main

tests: tests.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ tests.cpp

main: main.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ main.cpp

tests_san: tests.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ tests.cpp

main_san: main.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) $(SAN) -o $@ main.cpp

# The headers must not use standard containers (comments are stripped before searching).
lint:
	@bad=0; for f in $(HEADERS); do \
	  if sed 's://.*$$::' $$f | grep -nE 'std::(vector|list|forward_list|deque|map|set|multimap|multiset|unordered_[a-z]+|array|string|queue|stack|priority_queue)\b|#include <(vector|list|forward_list|deque|map|set|unordered_map|unordered_set|array|string|queue|stack)>'; then \
	    echo "lint: standard container found in $$f"; bad=1; fi; \
	done; \
	if [ $$bad -eq 0 ]; then echo "lint: no standard containers in the headers"; else exit 1; fi

test: tests lint
	./tests

run: main
	./main

sanitize: tests_san main_san
	./tests_san
	./main_san > /dev/null && echo "sanitize: main ran clean under ASan+UBSan"

clean:
	rm -f tests main tests_san main_san *.o
