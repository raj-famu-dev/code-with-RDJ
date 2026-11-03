// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Move semantics: lvalues vs rvalues, std::move, move constructor and move
 * assignment, a counter that proves moves avoid copies, and what a
 * moved-from object looks like.
 */
#include <cstddef>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

// A buffer that counts every copy and move so we can SEE what happens.
class Buffer {
public:
    static inline int copies = 0;
    static inline int moves = 0;

    explicit Buffer(std::size_t n) : data_(new int[n]()), size_(n) {}
    ~Buffer() { delete[] data_; }

    // Copy constructor: allocates new memory and copies every element.
    Buffer(const Buffer& other) : data_(new int[other.size_]), size_(other.size_) {
        for (std::size_t i = 0; i < size_; ++i) data_[i] = other.data_[i];
        ++copies;
    }
    // Move constructor: steals the pointer, leaves the source empty.
    Buffer(Buffer&& other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
        ++moves;
    }
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            Buffer tmp(other);  // copy-and-swap
            std::swap(data_, tmp.data_);
            std::swap(size_, tmp.size_);
        }
        return *this;
    }
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
            ++moves;
        }
        return *this;
    }

    std::size_t size() const { return size_; }
    bool empty() const { return data_ == nullptr; }

private:
    int* data_;
    std::size_t size_;
};

// Same idea as Buffer but WITHOUT noexcept on the move constructor.
struct Sloppy {
    static inline int copies = 0;
    static inline int moves = 0;
    Sloppy() = default;
    Sloppy(const Sloppy&) { ++copies; }
    Sloppy(Sloppy&&) { ++moves; }  // no noexcept: vector prefers COPY on growth
};

void reset_counters() { Buffer::copies = 0; Buffer::moves = 0; }
void report(const char* label) {
    std::cout << label << " -> copies=" << Buffer::copies << " moves=" << Buffer::moves << "\n";
}

// Overloads that reveal which kind of reference was bound.
void which(const std::string&) { std::cout << "  which(const std::string&)  [lvalue/const overload]\n"; }
void which(std::string&&) { std::cout << "  which(std::string&&)       [rvalue overload]\n"; }

Buffer make_buffer() { return Buffer(1000); }  // returned by value: elided or moved
Buffer pass_through(Buffer b) { return b; }     // by-value parameter

int main() {
    // ===== SECTION 1: LVALUES AND RVALUES =====
    std::cout << "===== SECTION 1: LVALUES AND RVALUES =====\n";
    std::string name = "RDJ";
    which(name);                        // has a name: lvalue
    which(std::string("temp"));         // temporary: rvalue
    which(std::move(name));             // std::move only CASTS to rvalue
    std::cout << "std::move did not move anything by itself; it is a cast.\n";

    // ===== SECTION 2: COPY vs MOVE CONSTRUCTION =====
    std::cout << "===== SECTION 2: COPY vs MOVE CONSTRUCTION =====\n";
    reset_counters();
    Buffer a(1000);
    Buffer b(a);              // copy
    report("after Buffer b(a)");
    Buffer c(std::move(a));   // move
    report("after Buffer c(std::move(a))");
    Buffer d = make_buffer(); // prvalue: guaranteed elision in C++17+
    report("after Buffer d = make_buffer()");
    std::cout << "sizes: b=" << b.size() << " c=" << c.size() << " d=" << d.size() << "\n";

    // ===== SECTION 3: MOVED-FROM STATE =====
    std::cout << "===== SECTION 3: MOVED-FROM STATE =====\n";
    std::cout << "a after being moved from: size=" << a.size() << " empty=" << std::boolalpha << a.empty() << "\n";
    std::string s = "hello world, this string is long enough to avoid small-string storage";
    std::string t = std::move(s);
    std::cout << "t = \"" << t.substr(0, 11) << "...\"\n";
    std::cout << "s.size() after move: " << s.size() << " (valid but unspecified; do not rely on it)\n";
    s = "assigned again";  // assigning to a moved-from object is always safe
    std::cout << "s after re-assignment: " << s << "\n";

    // ===== SECTION 4: MOVE ASSIGNMENT =====
    std::cout << "===== SECTION 4: MOVE ASSIGNMENT =====\n";
    reset_counters();
    Buffer x(10), y(20);
    x = y;                    // copy assignment
    report("after x = y");
    x = std::move(y);         // move assignment
    report("after x = std::move(y)");
    Buffer& alias = x;        // an alias hides the self-move from the compiler warning
    x = std::move(alias);     // self-move: guarded by this != &other, so it stays safe
    std::cout << "x.size() after self-move guard: " << x.size() << "\n";

    // ===== SECTION 5: vector GROWTH, noexcept TRAP =====
    std::cout << "===== SECTION 5: vector GROWTH, noexcept TRAP =====\n";
    reset_counters();
    {
        std::vector<Buffer> v;
        v.reserve(4);
        for (int i = 0; i < 4; ++i) v.emplace_back(100);
        report("4 emplace_back into reserved vector");
        v.emplace_back(100);  // exceeds capacity: reallocation relocates 4 elements
        report("5th emplace_back forced reallocation (noexcept move used)");
    }
    {
        std::vector<Sloppy> v;
        v.reserve(4);
        for (int i = 0; i < 4; ++i) v.emplace_back();
        v.emplace_back();
    }
    std::cout << "Sloppy (move not noexcept) -> copies=" << Sloppy::copies << " moves=" << Sloppy::moves
              << "  (vector copied the 4 old elements to keep the strong guarantee)\n";

    // ===== SECTION 6: BY-VALUE PARAMETERS AND RETURNS =====
    std::cout << "===== SECTION 6: BY-VALUE PARAMETERS AND RETURNS =====\n";
    reset_counters();
    Buffer p1(50);
    Buffer r1 = pass_through(p1);             // lvalue argument: copy in, then move out
    report("pass_through(lvalue)");
    reset_counters();
    Buffer r2 = pass_through(std::move(p1));  // rvalue argument: move in, then move out
    report("pass_through(std::move)");
    std::cout << "r1.size()=" << r1.size() << " r2.size()=" << r2.size() << "\n";

    // TRAP: std::move on a const object silently falls back to COPY.
    reset_counters();
    const Buffer cb(10);
    Buffer from_const(std::move(cb));
    report("TRAP: std::move(const Buffer)");
    std::cout << "A const object cannot be stolen from, so the copy constructor ran.\n";
    std::cout << "from_const.size()=" << from_const.size() << "\n";
    return 0;
}
