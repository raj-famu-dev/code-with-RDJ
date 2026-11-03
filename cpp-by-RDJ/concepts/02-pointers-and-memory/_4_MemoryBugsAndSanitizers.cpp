// Tags: #Cpp #Pointers #MemoryManagement #MemoryBugsSanitizers | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _4_MemoryBugsAndSanitizers
 * Teaches: the classic memory bugs (use-after-free, buffer overflow, leak,
 * double free, uninitialised read, plus signed overflow) as TOY code in this
 * file, and how AddressSanitizer / UndefinedBehaviorSanitizer find them.
 *
 *   Default run:           ./prog                -> only SAFE code runs, exit 0
 *   Trigger one toy bug:   ./prog --bug=<name>   -> names: use-after-free, overflow,
 *                          leak, double-free, uninit, signed-overflow
 *   Build with sanitizers: g++ -std=c++20 -g -fsanitize=address,undefined -o prog _4_MemoryBugsAndSanitizers.cpp
 *
 * Every bug is a few lines in your own process, shown and then fixed. There
 * is nothing here that attacks anything: the bugs only break this program.
 */
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

// [[gnu::noipa]] (GCC) stops the compiler from seeing through the bug and warning about it.
// That is also a hint about how hard these bugs are to spot statically.
[[gnu::noipa]] void release(int* p) { delete p; }
[[gnu::noipa]] void release_array(int* p) { delete[] p; }

// ---------- the toy bugs (each runs ONLY when asked for by name) ----------

void bug_use_after_free() {
    int* p = new int(42);
    release(p);
    std::cout << "reading freed memory: " << *p << '\n';        // BUG: p dangles
}

[[gnu::noipa]] void bug_overflow(int index) {
    int* buf = new int[4]{0, 1, 2, 3};
    buf[index] = 99;                                            // BUG when index is 4 or more
    std::cout << "wrote past the end\n";
    release_array(buf);
}

void bug_leak() {
    int* p = new int(7);                                        // BUG: never deleted
    std::cout << "allocated " << *p << " and forgot to free it\n";
}

void bug_double_free() {
    int* p = new int(1);
    release(p);
    release(p);                                                 // BUG: second delete of the same block
}

void bug_uninit() {
    int* data = new int[4];                                     // elements are NOT initialised (no braces)
    std::cout << "uninitialised value: " << data[0] << '\n';    // BUG: indeterminate value read
    release_array(data);
}

[[gnu::noipa]] void bug_signed_overflow(int v) {
    int big = v;
    int next = big + 1;                                         // BUG: signed overflow when v == INT_MAX
    std::cout << "next = " << next << '\n';
}

// ---------- the safe versions (the default run) ----------

void safe_demo() {
    std::cout << "===== SECTION 1: SAFE REPLACEMENTS FOR EACH BUG =====\n";
    // use-after-free -> let a smart pointer own the memory, never keep a raw copy past its life
    auto owned = std::make_unique<int>(42);
    std::cout << "use-after-free fix: unique_ptr owns it, value " << *owned << '\n';

    // buffer overflow -> vector + at() (or a range-for)
    std::vector<int> buf{0, 1, 2, 3};
    try {
        buf.at(4) = 99;
    } catch (const std::out_of_range&) {
        std::cout << "overflow fix: at(4) threw out_of_range instead of corrupting memory\n";
    }

    // leak -> RAII object frees at scope exit
    { auto temp = std::make_unique<int>(7); std::cout << "leak fix: freed automatically at scope end (" << *temp << ")\n"; }

    // double free -> single owner; the type system forbids a second delete
    auto a = std::make_unique<int>(1);
    auto b = std::move(a);
    std::cout << "double-free fix: after the move, a is " << (a ? "valid" : "null") << ", b owns the int\n";

    // uninitialised read -> always initialise: () or {} value-initialises
    std::vector<int> zeros(4);
    std::cout << "uninit fix: vector<int>(4) starts as zeros, first = " << zeros[0] << '\n';

    // signed overflow -> check, or widen the type
    int big = 2147483647;
    long long wide = static_cast<long long>(big) + 1;
    std::cout << "signed-overflow fix: widen first -> " << wide << '\n';

    std::cout << "\n===== SECTION 2: HOW TO SEE THE BUGS =====\n";
    std::cout << "Run with a flag, for example: ./prog --bug=use-after-free\n";
    std::cout << "Compile with -fsanitize=address,undefined -g to get a report instead of silent damage.\n";
    std::cout << "Without sanitizers these bugs are undefined behaviour: they may seem to work, crash, or corrupt data.\n";
    std::cout << "ASan finds: use-after-free, heap/stack/global overflow, double free, leaks (via LeakSanitizer).\n";
    std::cout << "UBSan finds: signed overflow, bad shifts, null deref, misaligned access. Neither finds uninit reads.\n";
}

int main(int argc, char** argv) {
    if (argc == 1) {
        safe_demo();
        return 0;
    }
    const std::string arg = argv[1];
    if (arg == "--bug=use-after-free") bug_use_after_free();
    else if (arg == "--bug=overflow") bug_overflow(4);
    else if (arg == "--bug=leak") bug_leak();
    else if (arg == "--bug=double-free") bug_double_free();
    else if (arg == "--bug=uninit") bug_uninit();
    else if (arg == "--bug=signed-overflow") bug_signed_overflow(2147483647);
    else {
        std::cerr << "unknown flag. Try --bug=use-after-free|overflow|leak|double-free|uninit|signed-overflow\n";
        return 2;
    }
    return 0;
}
