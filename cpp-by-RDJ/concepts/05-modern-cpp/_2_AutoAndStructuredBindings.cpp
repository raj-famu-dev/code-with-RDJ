// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * auto and decltype type deduction (including the "auto drops references and
 * const" trap), structured bindings for pairs, tuples, structs and arrays,
 * and range-for loops with bindings over a map.
 */
#include <array>
#include <iostream>
#include <map>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

struct Point {
    int x;
    int y;
};

std::pair<int, std::string> lookup(int id) {
    if (id == 1) return {1, "alice"};
    return {id, "unknown"};
}

std::tuple<std::string, int, double> student() { return {"Dana", 20, 3.75}; }

int main() {
    // ===== SECTION 1: auto DEDUCTION =====
    std::cout << "===== SECTION 1: auto DEDUCTION =====\n";
    auto i = 42;                 // int
    auto d = 3.14;               // double
    auto s = std::string("hi");  // std::string
    auto c = 'x';                // char
    auto f = 2.5f;               // float
    std::cout << std::boolalpha;
    std::cout << "auto i = 42      is int?    " << std::is_same_v<decltype(i), int> << "\n";
    std::cout << "auto d = 3.14    is double? " << std::is_same_v<decltype(d), double> << "\n";
    std::cout << "auto s = string  is string? " << std::is_same_v<decltype(s), std::string> << "\n";
    std::cout << "auto c = 'x'     is char?   " << std::is_same_v<decltype(c), char> << "\n";
    std::cout << "auto f = 2.5f    is float?  " << std::is_same_v<decltype(f), float> << "\n";
    auto lit = "text";           // const char*, NOT std::string
    std::cout << "auto lit = \"text\" is const char*? " << std::is_same_v<decltype(lit), const char*> << "\n";
    using namespace std::string_literals;
    auto str_lit = "text"s;      // the s suffix makes a std::string
    std::cout << "auto str_lit = \"text\"s is std::string? " << std::is_same_v<decltype(str_lit), std::string> << "\n";

    // ===== SECTION 2: auto TRAP, COPIES AND REFERENCES =====
    std::cout << "===== SECTION 2: auto TRAP, COPIES AND REFERENCES =====\n";
    std::vector<std::string> names = {"one", "two", "three"};
    auto first = names[0];       // TRAP: a COPY, not a reference
    first = "CHANGED";
    std::cout << "after changing the auto copy, names[0] = " << names[0] << "\n";
    auto& ref = names[0];        // auto& keeps it a reference
    ref = "CHANGED";
    std::cout << "after changing through auto&, names[0] = " << names[0] << "\n";
    const int k = 10;
    auto k2 = k;                 // auto drops top-level const
    std::cout << "auto k2 = k (k is const int): k2 is const? " << std::is_const_v<decltype(k2)> << "\n";
    const auto k3 = k;
    std::cout << "const auto k3 = k: k3 is const? " << std::is_const_v<decltype(k3)> << "\n";

    // ===== SECTION 3: decltype =====
    std::cout << "===== SECTION 3: decltype =====\n";
    int n = 5;
    int& nr = n;
    auto a1 = nr;                // int (reference dropped)
    decltype(nr) a2 = n;         // int& (decltype keeps the reference)
    a1 = 100;
    a2 = 200;
    std::cout << "a1 is a reference? " << std::is_reference_v<decltype(a1)> << ", a2 is a reference? "
              << std::is_reference_v<decltype(a2)> << "\n";
    std::cout << "n after a1=100 and a2=200: " << n << " (only a2 wrote through)\n";
    decltype(n + 1.5) sum = n + 1.5;  // decltype of an expression
    std::cout << "decltype(n + 1.5) is double? " << std::is_same_v<decltype(sum), double> << "\n";
    decltype(auto) da = nr;      // decltype(auto) keeps reference-ness
    std::cout << "decltype(auto) da = nr is int&? " << std::is_same_v<decltype(da), int&> << "\n";

    // ===== SECTION 4: STRUCTURED BINDINGS =====
    std::cout << "===== SECTION 4: STRUCTURED BINDINGS =====\n";
    auto [id, name] = lookup(1);
    std::cout << "pair:   id=" << id << " name=" << name << "\n";
    auto [sname, age, gpa] = student();
    std::cout << "tuple:  " << sname << " age " << age << " gpa " << gpa << "\n";
    Point p{3, 4};
    auto [px, py] = p;           // binds by member order
    std::cout << "struct: px=" << px << " py=" << py << "\n";
    std::array<int, 3> arr = {7, 8, 9};
    auto [e0, e1, e2] = arr;
    std::cout << "array:  " << e0 << " " << e1 << " " << e2 << "\n";
    auto& [rx, ry] = p;          // reference bindings modify the original
    rx = 30;
    ry = 40;
    std::cout << "after writing through auto& [rx, ry]: p = (" << p.x << ", " << p.y << ")\n";
    auto [cx, cy] = p;           // TRAP: no & means a copy of p
    cx = -1;
    std::cout << "copy binding cx=" << cx << " cy=" << cy << " (changing cx touches only the copy)\n";
    std::cout << "after changing a copy binding, p.x is still " << p.x << "\n";

    // ===== SECTION 5: RANGE-FOR WITH BINDINGS =====
    std::cout << "===== SECTION 5: RANGE-FOR WITH BINDINGS =====\n";
    std::map<std::string, int> scores = {{"carol", 88}, {"alice", 95}, {"bob", 72}};  // sorted by key
    for (const auto& [who, score] : scores) {
        std::cout << "  " << who << " -> " << score << "\n";
    }
    for (auto& [who, score] : scores) {
        score += 5;  // modify values in place
        (void)who;
    }
    std::cout << "after +5 curve:";
    for (const auto& [who, score] : scores) std::cout << " " << who << "=" << score;
    std::cout << "\n";
    auto [pos, inserted] = scores.insert({"alice", 0});  // insert returns pair<iterator,bool>
    std::cout << "insert existing key 'alice': inserted=" << inserted << " value kept=" << pos->second << "\n";
    std::vector<Point> pts = {{1, 2}, {3, 4}};
    int total = 0;
    for (const auto& [x, y] : pts) total += x * y;
    std::cout << "sum of x*y over points: " << total << "\n";
    return 0;
}
