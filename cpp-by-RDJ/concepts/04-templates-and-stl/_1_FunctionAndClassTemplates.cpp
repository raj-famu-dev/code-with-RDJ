// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: function templates and template argument deduction, class templates
 * (a generic Stack<T>), class template argument deduction (CTAD), explicit
 * specialization, and the instantiation model: the compiler generates a
 * separate copy of the code for every distinct T (unlike Java, which erases T).
 */
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <string>
#include <vector>

// ===== SECTION 1: a function template and deduction =====
template <typename T>
T maxOf(T a, T b) { return (b < a) ? a : b; }

// ===== SECTION 2: a class template =====
template <typename T>
class Stack {
public:
    void push(T v) { items_.push_back(std::move(v)); }
    T pop() {
        if (items_.empty()) throw std::underflow_error("pop on empty Stack");
        T v = std::move(items_.back());
        items_.pop_back();
        return v;
    }
    const T& top() const { return items_.back(); }
    bool empty() const { return items_.empty(); }
    std::size_t size() const { return items_.size(); }
private:
    std::vector<T> items_;
};

// ===== SECTION 3: instantiation: one generated copy per type =====
template <typename T>
int& instantiationCounter() { static int calls = 0; return calls; }   // a separate static per T
template <typename T>
void touch() { ++instantiationCounter<T>(); }

// ===== SECTION 4: specialization: the const char* pointer-compare trap =====
template <typename T>
bool lessThan(T a, T b) { return a < b; }
template <>
bool lessThan<const char*>(const char* a, const char* b) { return std::strcmp(a, b) < 0; }   // compare TEXT, not addresses

int main() {
    std::cout << "===== SECTION 1: a function template and deduction =====\n";
    std::cout << "maxOf(3, 7)         = " << maxOf(3, 7) << "   (T deduced as int)\n";
    std::cout << "maxOf(2.5, 1.5)     = " << maxOf(2.5, 1.5) << " (T deduced as double)\n";
    std::cout << "maxOf<std::string>(\"pear\", \"apple\") = " << maxOf<std::string>("pear", "apple") << " (explicit T)\n";
    std::cout << "maxOf(1, 2.5) does NOT compile: one argument says int, the other double, so deduction fails.\n";
    std::cout << "Fix: maxOf<double>(1, 2.5) = " << maxOf<double>(1, 2.5) << " (explicit T converts the int)\n";

    std::cout << "\n===== SECTION 2: a class template =====\n";
    Stack<int> si;
    si.push(1); si.push(2); si.push(3);
    std::cout << "Stack<int> top = " << si.top() << ", pop = " << si.pop() << ", size now " << si.size() << "\n";
    Stack<std::string> ss;
    ss.push("alpha"); ss.push("beta");
    std::cout << "Stack<std::string> pop = " << ss.pop() << ", then " << ss.pop() << "\n";
    try { ss.pop(); } catch (const std::underflow_error& e) { std::cout << "empty pop: " << e.what() << "\n"; }
    std::vector v{4, 5};                 // CTAD (C++17): no <int> written; the compiler deduces std::vector<int>
    std::pair p{1, 2.5};                 // CTAD: std::pair<int, double>
    std::cout << "CTAD: `std::vector v{4, 5};` deduces std::vector<int>, size " << v.size() << "; `std::pair p{1, 2.5};` deduces pair<int,double>: "
              << p.first << "," << p.second << "\n";
    std::cout << "is_same<decltype(v), std::vector<int>>: " << std::boolalpha << std::is_same_v<decltype(v), std::vector<int>> << "\n";

    std::cout << "\n===== SECTION 3: instantiation: one generated copy per type =====\n";
    touch<int>(); touch<int>(); touch<int>();
    touch<double>();
    touch<std::string>(); touch<std::string>();
    std::cout << "calls recorded for int: " << instantiationCounter<int>() << ", double: " << instantiationCounter<double>()
              << ", std::string: " << instantiationCounter<std::string>() << "\n";
    std::cout << "Each type got its own function with its own static variable. Java generics would have ONE method for all of them.\n";
    std::cout << "sizeof(Stack<int>) = " << sizeof(Stack<int>) << ", sizeof(Stack<std::string>) = " << sizeof(Stack<std::string>)
              << " (both equal: each just holds one vector; the element code differs, not the handle)\n";

    std::cout << "\n===== SECTION 4: specialization: the const char* pointer-compare trap =====\n";
    const char first[] = "banana";
    const char second[] = "apple";
    const char* p1 = first;
    const char* p2 = second;
    std::cout << "Generic lessThan<const char*> would compare ADDRESSES (meaningless). Specialized version compares text.\n";
    std::cout << "lessThan(p1 = \"banana\", p2 = \"apple\") = " << std::boolalpha << lessThan(p1, p2) << " (strcmp: banana is not less than apple)\n";
    std::cout << "lessThan(p2, p1) = " << lessThan(p2, p1) << "\n";
    std::cout << "lessThan(3, 4) = " << lessThan(3, 4) << " (generic version)\n";
    return 0;
}
