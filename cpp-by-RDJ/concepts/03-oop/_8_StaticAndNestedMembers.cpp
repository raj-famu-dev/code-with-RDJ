// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: static data members and static member functions (shared by all
 * objects), `inline static` (define in-class, no separate .cpp definition),
 * nested types, and `enum class` (scoped, strongly typed) vs unscoped enums
 * (names leak into the enclosing scope and convert to int silently).
 */
#include <iostream>
#include <string>
#include <vector>

// ===== SECTION 1: static members =====
class Widget {
public:
    Widget() { ++liveCount_; ++totalCreated; }
    ~Widget() { --liveCount_; }
    static int live() { return liveCount_; }          // static function: no `this`, can only touch statics
    static inline int totalCreated = 0;               // ===== SECTION 2: inline static (C++17) =====
    static constexpr int kMaxName = 16;               // static constexpr is implicitly inline
private:
    static inline int liveCount_ = 0;
};

// ===== SECTION 3: nested types =====
class Graph {
public:
    struct Edge { int from, to; };                    // nested type: Graph::Edge
    enum class Kind { Directed, Undirected };
    Graph(Kind k) : kind_(k) {}
    void add(int a, int b) { edges_.push_back({a, b}); }
    int degree(int node) const {
        int d = 0;
        for (const Edge& e : edges_) {
            if (e.from == node) ++d;
            if (kind_ == Kind::Undirected && e.to == node) ++d;
        }
        return d;
    }
private:
    Kind kind_;
    std::vector<Edge> edges_;
};

// ===== SECTION 4: enum class vs unscoped enum =====
enum Color { Red, Green, Blue };                      // unscoped: Red, Green, Blue are in the enclosing scope
enum class Fruit { Apple, Banana };                   // scoped: must write Fruit::Apple
enum class Level : unsigned char { Low = 1, High = 200 };   // underlying type chosen explicitly

// Trap: two unscoped enums in one scope collide on names (so Light uses trailing underscores), and unscoped converts to int silently.
enum Light { On_ = 1, Off_ = 0 };
std::string toString(Fruit f) { return f == Fruit::Apple ? "Apple" : "Banana"; }

int main() {
    std::cout << "===== SECTION 1: static members =====\n";
    std::cout << "live before: " << Widget::live() << "\n";
    {
        Widget a, b;
        std::cout << "live with 2 objects: " << Widget::live() << " (shared by the class, called without an object)\n";
        Widget c;
        std::cout << "live with 3 objects: " << Widget::live() << " via object c.live() = " << c.live() << "\n";
    }
    std::cout << "live after scope: " << Widget::live() << ", totalCreated: " << Widget::totalCreated << "\n";

    std::cout << "\n===== SECTION 2: inline static =====\n";
    std::cout << "Before C++17 a static data member needed `int Widget::totalCreated = 0;` in exactly one .cpp file.\n";
    std::cout << "With `static inline` the definition is in the class; kMaxName = " << Widget::kMaxName << " (static constexpr)\n";
    std::cout << "Trap avoided: without inline, defining a static in a header included twice gives a linker error (multiple definition).\n";

    std::cout << "\n===== SECTION 3: nested types =====\n";
    Graph::Edge e{1, 2};
    std::cout << "outside code must say Graph::Edge: {" << e.from << "," << e.to << "}\n";
    Graph dg(Graph::Kind::Directed), ug(Graph::Kind::Undirected);
    for (Graph* g : {&dg, &ug}) { g->add(1, 2); g->add(2, 3); }
    std::cout << "degree of node 2 in directed graph  : " << dg.degree(2) << "\n";
    std::cout << "degree of node 2 in undirected graph: " << ug.degree(2) << "\n";
    std::cout << "A nested class is only a namespace-like grouping: it has no hidden pointer to an outer object (unlike a Java inner class).\n";

    std::cout << "\n===== SECTION 4: enum class vs unscoped enum =====\n";
    Color c = Green;                                  // plain name leaked into scope
    int asInt = c;                                    // silent conversion to int
    std::cout << "unscoped Green converts to int silently: " << asInt << "\n";
    Fruit f = Fruit::Banana;
    std::cout << "enum class needs the scope and prints via a function: " << toString(f) << "\n";
    std::cout << "static_cast<int>(Fruit::Banana) = " << static_cast<int>(f) << " (conversion must be explicit)\n";
    std::cout << "`Fruit::Apple == 0` does not compile (enum class never converts to int on its own).\n";
    std::cout << "sizeof(Level) = " << sizeof(Level) << " byte (underlying type was chosen), High = " << static_cast<int>(Level::High) << "\n";
    std::cout << "Light is an unscoped enum: On_ = " << On_ << "; the unscoped Color Red == 0 compiles and is " << std::boolalpha << (Red == 0) << " (an enum silently acts like an int)\n";
    return 0;
}
