// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: custom comparators for std::map / std::set / std::priority_queue
 * (strict weak ordering), and custom hash + equality for std::unordered_map.
 * Java parallels: Comparator.compare and equals()/hashCode().
 * Trap: a hash that disagrees with == silently makes lookups fail.
 */
#include <algorithm>
#include <cctype>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// ===== SECTION 1: comparators for ordered containers =====
struct CaseInsensitiveLess {
    bool operator()(const std::string& a, const std::string& b) const {
        return std::lexicographical_compare(a.begin(), a.end(), b.begin(), b.end(),
            [](unsigned char x, unsigned char y) { return std::tolower(x) < std::tolower(y); });
    }
};
struct Person {
    std::string name;
    int age;
};

// ===== SECTION 2: priority_queue with a comparator =====
struct Task {
    int priority;
    std::string label;
};
struct TaskLess {                                  // priority_queue is a MAX-heap on this "less"
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority) return a.priority < b.priority;
        return a.label > b.label;                  // tie-break: alphabetically earlier label comes out first
    }
};

// ===== SECTION 3: custom hash + equality =====
struct Point {
    int x, y;
    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
};
struct PointHash {
    std::size_t operator()(const Point& p) const noexcept {
        std::size_t h = std::hash<int>{}(p.x);
        h ^= std::hash<int>{}(p.y) + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);   // "hash combine": mixes both fields
        return h;
    }
};

// ===== SECTION 4: the inconsistent-hash trap =====
struct Tagged {
    int id;
    std::string note;                               // NOT part of equality
    bool operator==(const Tagged& o) const { return id == o.id; }
};
struct BadTaggedHash {                              // BUG: hashes a field that == ignores
    std::size_t operator()(const Tagged& t) const noexcept { return std::hash<int>{}(t.id) + std::hash<std::string>{}(t.note); }
};
struct GoodTaggedHash {                             // FIX: hash exactly the fields == uses
    std::size_t operator()(const Tagged& t) const noexcept { return std::hash<int>{}(t.id); }
};

int main() {
    std::cout << "===== SECTION 1: comparators for ordered containers =====\n";
    std::map<int, std::string, std::greater<int>> desc{{1, "one"}, {3, "three"}, {2, "two"}};
    std::cout << "map<int,..., std::greater> iterates:";
    for (const auto& [k, v] : desc) std::cout << " " << k << ":" << v;
    std::cout << "\n";
    std::set<std::string, CaseInsensitiveLess> names;
    for (const char* n : {"bob", "Alice", "BOB", "alice", "Carol"}) names.insert(n);
    std::cout << "case-insensitive set size = " << names.size() << ":";
    for (const auto& n : names) std::cout << " " << n;
    std::cout << " (\"BOB\" and \"alice\" were equal under the comparator, so they were not inserted)\n";
    auto byAge = [](const Person& a, const Person& b) { return a.age < b.age; };
    std::set<Person, decltype(byAge)> people(byAge);
    people.insert({"Ann", 30}); people.insert({"Ben", 25}); people.insert({"Cy", 30});
    std::cout << "set by age (lambda comparator) has " << people.size() << " people: Cy was dropped because age 30 already exists (equivalence = !(a<b) && !(b<a)).\n";
    std::cout << "Java: TreeSet(Comparator) behaves the same way: compare()==0 means duplicate.\n";
    std::cout << "Rule: comparators must be a strict weak ordering. `a.age <= b.age` breaks it (comp(x,x) must be false) and is undefined behaviour in std::sort/set.\n";

    std::cout << "\n===== SECTION 2: priority_queue with a comparator =====\n";
    std::priority_queue<int> maxHeap;
    for (int x : {4, 9, 1, 7}) maxHeap.push(x);
    std::cout << "default priority_queue<int> pops the LARGEST first:";
    while (!maxHeap.empty()) { std::cout << " " << maxHeap.top(); maxHeap.pop(); }
    std::cout << "\n";
    std::priority_queue<int, std::vector<int>, std::greater<int>> minHeap;
    for (int x : {4, 9, 1, 7}) minHeap.push(x);
    std::cout << "with std::greater it pops the SMALLEST first:";
    while (!minHeap.empty()) { std::cout << " " << minHeap.top(); minHeap.pop(); }
    std::cout << "\n";
    std::priority_queue<Task, std::vector<Task>, TaskLess> tasks;
    tasks.push({2, "write"}); tasks.push({5, "fix-bug"}); tasks.push({5, "deploy"}); tasks.push({1, "relax"});
    std::cout << "tasks by priority then label:";
    while (!tasks.empty()) { std::cout << " " << tasks.top().priority << "/" << tasks.top().label; tasks.pop(); }
    std::cout << "\n(Trap: the comparator's meaning is inverted vs sorting: 'less' puts the item at the BOTTOM, so max-heap pops the greatest.)\n";

    std::cout << "\n===== SECTION 3: custom hash + equality =====\n";
    std::unordered_map<Point, std::string, PointHash> grid;
    grid[{1, 2}] = "tree";
    grid[{3, 4}] = "rock";
    grid[{1, 2}] = "oak";                           // same key: overwrites
    std::cout << "size = " << grid.size() << ", grid[{1,2}] = " << grid.at({1, 2}) << ", contains {3,4}: " << std::boolalpha << grid.contains({3, 4})
              << ", contains {2,1}: " << grid.contains({2, 1}) << " (order of x,y matters)\n";
    std::cout << "hash of same value twice is equal: " << (PointHash{}({7, 8}) == PointHash{}({7, 8})) << ", hash({1,2}) != hash({2,1}): " << (PointHash{}({1, 2}) != PointHash{}({2, 1})) << "\n";
    std::cout << "Java parallel: equals(Object) <-> operator==, hashCode() <-> the hash functor. Contract: a == b implies hash(a) == hash(b).\n";
    std::cout << "(In C++ you can also specialize std::hash<Point> so no third template argument is needed.)\n";

    std::cout << "\n===== SECTION 4: the inconsistent-hash trap =====\n";
    std::unordered_set<Tagged, BadTaggedHash> bad;
    bad.insert({1, "first"});
    std::cout << "BadTaggedHash: contains({1, \"other\"}) = " << bad.contains({1, "other"}) << " (== says equal, but the hashes differ so the lookup looks in the wrong bucket)\n";
    std::unordered_set<Tagged, GoodTaggedHash> good;
    good.insert({1, "first"});
    std::cout << "GoodTaggedHash: contains({1, \"other\"}) = " << good.contains({1, "other"}) << " (hash uses only the fields that == uses)\n";
    return 0;
}
