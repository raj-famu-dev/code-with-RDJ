// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _3_StackVsHeap
 * Teaches: automatic (stack) storage vs dynamic (heap) storage, new/delete
 * and new[]/delete[], object lifetime, and why Java programmers must now
 * decide where an object lives. Raw addresses are never printed; only
 * relative facts (ordering, byte distance) labelled as measurements.
 */
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

// An object that announces its birth and death so lifetime is visible.
struct Tracker {
    std::string name;
    explicit Tracker(std::string n) : name(std::move(n)) { std::cout << "  [ctor " << name << "]\n"; }
    ~Tracker() { std::cout << "  [dtor " << name << "]\n"; }
    Tracker(const Tracker&) = delete;
    Tracker& operator=(const Tracker&) = delete;
};

// Returns the address of a local in a nested call, converted to an integer
// ONLY so we can compare ordering. The number itself is never printed.
std::uintptr_t local_address_in_callee() {
    int local = 0;
    return reinterpret_cast<std::uintptr_t>(&local);
}

int main() {
    std::cout << "===== SECTION 1: AUTOMATIC (STACK) LIFETIME =====\n";
    {
        std::cout << "entering block\n";
        Tracker a("stack-A");
        Tracker b("stack-B");
        std::cout << "leaving block (destructors run in REVERSE order automatically)\n";
    }
    std::cout << "after block: both are gone\n";

    std::cout << "\n===== SECTION 2: DYNAMIC (HEAP) LIFETIME WITH new/delete =====\n";
    Tracker* heap_one = new Tracker("heap-1");     // you decide when it dies
    std::cout << "heap-1 still alive after no scope exit; name = " << heap_one->name << '\n';
    delete heap_one;                               // destructor runs here
    heap_one = nullptr;                            // defensive: no dangling pointer left behind
    std::cout << "deleted\n";
    int* numbers = new int[4]{1, 2, 3, 4};         // array form
    int total = 0;
    for (int i = 0; i < 4; ++i) total += numbers[i];
    std::cout << "sum of heap array = " << total << '\n';
    delete[] numbers;                              // TRAP: new[] must pair with delete[], not delete
    numbers = nullptr;
    // Pairing rules: new <-> delete, new[] <-> delete[]. Mixing them is undefined behaviour.

    std::cout << "\n===== SECTION 3: WHERE THINGS LIVE (RELATIVE FACTS ONLY) =====\n";
    int stack_int = 5;
    int* heap_int = new int(5);
    std::cout << "stack_int is a variable (lives in this function's frame); *heap_int points into the heap\n";
    std::cout << "the pointer variable heap_int ITSELF is on the stack; what it points at is on the heap\n";
    std::cout << "sizeof(heap_int) = " << sizeof(heap_int) << " bytes (measurement), sizeof(*heap_int) = " << sizeof(*heap_int) << '\n';
    std::uintptr_t here = reinterpret_cast<std::uintptr_t>(&stack_int);
    std::uintptr_t deeper = local_address_in_callee();
    std::cout << "measurement: callee's local is at a " << (deeper < here ? "LOWER" : "HIGHER")
              << " address than the caller's (the stack grows downward on x86-64 Linux)\n";
    std::cout << "stack_int + *heap_int = " << stack_int + *heap_int << '\n';
    delete heap_int;

    std::cout << "\n===== SECTION 4: LEAK-PROOF PATTERN AND EXCEPTIONS =====\n";
    // Described trap: with raw new/delete, an exception between them skips delete.
    //   Tracker* t = new Tracker("leaky"); might_throw(); delete t;   // leak if might_throw throws
    // Fix: let a stack object own the heap object (RAII). unique_ptr is shown properly in _6.
    try {
        Tracker guard("stack-guard");
        throw std::runtime_error("boom");
    } catch (const std::exception& e) {
        std::cout << "caught: " << e.what() << " (the stack object was still destroyed first)\n";
    }

    std::cout << "\n===== SECTION 5: STACK SIZE LIMIT (DESCRIBED) =====\n";
    std::cout << "The stack is small (commonly about 8 MB on Linux; check with `ulimit -s`). A huge local array or\n";
    std::cout << "unbounded recursion overflows it. Large data belongs on the heap (std::vector does this for you).\n";
    return 0;
}
