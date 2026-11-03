// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _7_StringsAndStringView
 * Teaches: std::string (mutable value type), small string optimisation
 * (SSO), std::string_view as a non-owning window, the dangling
 * string_view trap, and how this differs from Java's immutable String.
 */
#include <iostream>
#include <string>
#include <string_view>

// string_view parameters accept std::string, literals and substrings with no copy.
std::size_t count_char(std::string_view text, char c) {
    std::size_t n = 0;
    for (char ch : text) if (ch == c) ++n;
    return n;
}

// TRAP: returns a view into a local string that dies when the function returns.
// Kept here only as a description; calling it would be undefined behaviour.
//   std::string_view bad() { std::string s = "temporary"; return s; }
// FIX: return the owning std::string.
std::string good() { std::string s = "temporary"; return s; }

int main() {
    std::cout << "===== SECTION 1: std::string BASICS =====\n";
    std::string s = "Hello";
    s += ", World";
    s.push_back('!');
    std::cout << s << " (size " << s.size() << ")\n";
    s[0] = 'J';                          // strings are MUTABLE (Java Strings are not)
    std::cout << "after s[0] = 'J': " << s << '\n';
    std::cout << "substr(7, 5) = " << s.substr(7, 5) << ", find(\"World\") = " << s.find("World") << '\n';
    std::cout << "find(\"zzz\") == npos: " << std::boolalpha << (s.find("zzz") == std::string::npos) << '\n';
    std::string copy = s;                // deep copy of the characters
    copy[0] = 'H';
    std::cout << "copy: " << copy << " | original: " << s << " (independent)\n";
    std::cout << "== compares CONTENT: " << (std::string("a") == std::string("a")) << " (Java needs equals())\n";
    std::cout << "\"apple\" < \"banana\": " << (std::string("apple") < std::string("banana")) << '\n';

    std::cout << "\n===== SECTION 2: SMALL STRING OPTIMISATION (SSO) =====\n";
    // Short strings live INSIDE the string object, with no heap allocation.
    // Output below is a measurement of this library, not a language guarantee.
    std::string tiny = "hi";
    std::string longer(100, 'x');
    std::cout << "capacity of \"hi\" = " << tiny.capacity() << " (measurement: inline buffer in libstdc++)\n";
    std::cout << "capacity of a 100-char string = " << longer.capacity() << " (heap allocated)\n";
    std::cout << "sizeof(std::string) = " << sizeof(std::string) << " (measurement, same for short and long strings)\n";
    // Talking point: a tiny string stores its characters in a spare area of
    // the object itself; the heap is used only when the text outgrows that.

    std::cout << "\n===== SECTION 3: std::string_view =====\n";
    std::string owner = "banana bread";
    std::string_view whole = owner;                 // no copy
    std::string_view word = whole.substr(0, 6);     // no copy: pointer + length
    std::cout << "word = " << word << ", count of 'a' = " << count_char(word, 'a') << '\n';
    std::cout << "count_char with a literal: " << count_char("mississippi", 's') << '\n';
    owner[0] = 'B';                                  // view sees the change: it points at the same bytes
    std::cout << "after owner[0]='B', the view reads: " << word << " (it is a window, not a copy)\n";
    std::cout << "sizeof(string_view) = " << sizeof(std::string_view) << " (pointer + length; measurement)\n";

    std::cout << "\n===== SECTION 4: THE DANGLING string_view TRAP =====\n";
    std::string_view dangling;
    {
        std::string inner = "this string is longer than any small buffer so it lives on the heap";
        dangling = inner;
        std::cout << "inside scope the view is fine, size " << dangling.size() << '\n';
    }   // 'inner' destroyed here: 'dangling' now points at freed memory
    std::cout << "after scope the view is dangling (size " << dangling.size()
              << " is still stored, but reading it would be undefined behaviour; we do not read it)\n";
    dangling = std::string_view{};   // reset so the dead pointer is never used
    std::cout << "good() returns an owning string: " << good() << '\n';
    // Other classic traps: std::string_view v = std::string("temp");  // temp dies at the semicolon
    //                      std::string s2 = v + "x";                  // no operator+ for string_view
    std::cout << "string_view is not null-terminated; never pass v.data() to a C function expecting a C string.\n";

    std::cout << "\n===== SECTION 5: COMPARISON WITH JAVA String =====\n";
    std::cout << "Java: immutable, GC-managed, interned literals, == compares references.\n";
    std::cout << "C++ std::string: mutable value type, deep copy on assignment, == compares content.\n";
    std::cout << "Java substring() gives you a new safe String; string_view is a raw borrow that you must keep alive yourself.\n";
    return 0;
}
