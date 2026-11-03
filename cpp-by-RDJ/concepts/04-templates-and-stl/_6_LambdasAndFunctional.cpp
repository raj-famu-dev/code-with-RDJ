// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: lambda syntax, captures by value and by reference, init-captures,
 * `mutable`, std::function (type-erased callable) and what a lambda really
 * is (an unnamed class with operator()). Includes the dangling-capture trap:
 * returning a lambda that captured a local BY REFERENCE is undefined
 * behaviour, so the broken version is guarded behind the flag:
 *     ./prog --trap   (run WITHOUT sanitizers; output is indeterminate)
 */
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// ===== SECTION 4 helpers: the dangling-capture trap =====
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-local-addr"
#pragma GCC diagnostic ignored "-Wdangling-reference"
std::function<int()> makeBrokenCounter() {
    int local = 41;
    return [&local]() { return local + 1; };           // BUG: `local` dies when this function returns
}
#pragma GCC diagnostic pop
std::function<int()> makeSafeCounter() {
    int local = 41;
    return [local]() { return local + 1; };            // FIX: capture by VALUE (a copy lives inside the lambda)
}

int main(int argc, char** argv) {
    bool trap = argc > 1 && std::string(argv[1]) == "--trap";

    std::cout << "===== SECTION 1: lambda syntax and capture by value / reference =====\n";
    int factor = 3;
    auto byValue = [factor](int x) { return x * factor; };       // copies factor at creation
    auto byRef = [&factor](int x) { return x * factor; };        // refers to the variable itself
    factor = 10;
    std::cout << "after factor = 10: byValue(2) = " << byValue(2) << " (still used 3), byRef(2) = " << byRef(2) << " (sees 10)\n";
    auto addAll = [=](int x) { return x + factor; };             // [=] captures everything used, by value
    auto addRef = [&](int x) { return x + factor; };             // [&] captures everything used, by reference
    std::cout << "addAll(1) = " << addAll(1) << ", addRef(1) = " << addRef(1) << "\n";
    std::cout << "sizeof captureless lambda is " << sizeof([] {}) << ", lambda capturing one int is " << sizeof(byValue) << " (a lambda is an object holding its captures)\n";

    std::cout << "\n===== SECTION 2: mutable and init-captures =====\n";
    int start = 5;
    auto counter = [n = start]() mutable { return ++n; };        // init-capture: new variable n inside the lambda
    std::cout << "counter() x3: " << counter() << " " << counter() << " " << counter() << "\n";
    std::cout << "outer `start` is untouched: " << start << " (mutable lets the lambda modify its OWN copy)\n";
    auto copy = counter;                                         // copying copies the captured state
    std::cout << "copy() = " << copy() << ", counter() = " << counter() << " (they now diverge)\n";
    auto owned = std::make_unique<std::string>("moved-in");
    auto holder = [p = std::move(owned)]() { return p->size(); };   // move-only capture (needs init-capture)
    std::cout << "unique_ptr moved into a lambda: size = " << holder() << ", original is null: " << std::boolalpha << (owned == nullptr) << "\n";

    std::cout << "\n===== SECTION 3: std::function =====\n";
    std::vector<std::function<int(int)>> ops;
    ops.push_back([](int x) { return x + 1; });
    ops.push_back([k = 4](int x) { return x * k; });
    struct Square { int operator()(int x) const { return x * x; } };      // a functor
    ops.push_back(Square{});
    ops.push_back(std::function<int(int)>([](int x) { return -x; }));
    for (std::size_t i = 0; i < ops.size(); ++i) std::cout << "ops[" << i << "](6) = " << ops[i](6) << "\n";
    std::function<int(int)> empty;
    try { empty(1); } catch (const std::bad_function_call&) { std::cout << "calling an empty std::function throws bad_function_call\n"; }
    std::cout << "std::function stores ANY callable with that signature (type erasure) at a cost: possible heap allocation and an indirect call.\n";
    std::cout << "For parameters you only call, prefer a template parameter (template <typename F>) which can be inlined.\n";

    std::cout << "\n===== SECTION 4: dangling-capture trap =====\n";
    auto safe = makeSafeCounter();
    std::cout << "makeSafeCounter()() = " << safe() << " (captured by value: correct)\n";
    if (trap) {
        auto broken = makeBrokenCounter();
        std::cout << "TRAP (--trap): makeBrokenCounter()() = " << broken() << " (reads a dead stack slot: undefined behaviour, any value is possible)\n";
    } else {
        std::cout << "makeBrokenCounter() is not called by default: it captures a local by reference and returns the lambda.\n";
        std::cout << "Run with --trap to call it (value is indeterminate; never rely on it).\n";
    }
    std::cout << "Rule: a lambda that outlives its creating scope (returned, stored, sent to a thread) must capture by value or by move.\n";
    return 0;
}
