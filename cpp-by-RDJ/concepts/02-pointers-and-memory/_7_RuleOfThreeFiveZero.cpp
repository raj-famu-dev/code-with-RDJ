// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _7_RuleOfThreeFiveZero
 * Teaches: what the compiler generates for you, why a class that owns heap
 * memory needs a custom destructor + copy + move (Rule of Three / Five),
 * and why the best answer is usually the Rule of Zero.
 *
 * The WRONG class has a real shallow-copy bug. By default the demo detaches
 * the copy so nothing is freed twice. Run with --bug=shallow-copy to let the
 * double free happen (meant for -fsanitize=address; it deliberately crashes).
 */
#include <algorithm>
#include <cstring>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

// ---------- WRONG: owns memory, but only the destructor is written ----------
class WrongBuffer {
public:
    explicit WrongBuffer(std::size_t n, int fill) : size_(n), data_(new int[n]) { std::fill(data_, data_ + n, fill); }
    ~WrongBuffer() { delete[] data_; }
    // The implicitly generated copy constructor copies the POINTER, not the array: two owners, one block.
    int* raw() const { return data_; }
    int at(std::size_t i) const { return data_[i]; }
    void set(std::size_t i, int v) { data_[i] = v; }
    void detach_for_demo() { data_ = nullptr; }   // lets the demo skip the double free; never do this in real code
private:
    std::size_t size_;
    int* data_;
};

// ---------- RIGHT (Rule of Five): every special member written out ----------
class Buffer {
public:
    static inline int copies = 0, moves = 0;
    explicit Buffer(std::size_t n = 0, int fill = 0) : size_(n), data_(n ? new int[n] : nullptr) {
        std::fill(data_, data_ + n, fill);
    }
    ~Buffer() { delete[] data_; }                                                  // 1. destructor
    Buffer(const Buffer& o) : size_(o.size_), data_(o.size_ ? new int[o.size_] : nullptr) {   // 2. copy ctor: DEEP copy
        std::copy(o.data_, o.data_ + o.size_, data_);
        ++copies;
    }
    Buffer& operator=(const Buffer& o) {                                           // 3. copy assignment
        if (this != &o) {                                                          // self-assignment guard
            Buffer tmp(o);                                                         // copy first: if it throws, *this is untouched
            std::swap(size_, tmp.size_);
            std::swap(data_, tmp.data_);                                           // tmp's destructor frees the old block
        }
        return *this;
    }
    Buffer(Buffer&& o) noexcept : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) { ++moves; }   // 4. move ctor: steal
    Buffer& operator=(Buffer&& o) noexcept {                                       // 5. move assignment
        if (this != &o) {
            delete[] data_;
            size_ = std::exchange(o.size_, 0);
            data_ = std::exchange(o.data_, nullptr);
            ++moves;
        }
        return *this;
    }
    int at(std::size_t i) const { return data_[i]; }
    void set(std::size_t i, int v) { data_[i] = v; }
    std::size_t size() const { return size_; }
private:
    std::size_t size_;
    int* data_;
};

// Same as Buffer but the move constructor is NOT noexcept: vector will refuse to use it when it reallocates.
class SlowMover {
public:
    static inline int copies = 0, moves = 0;
    SlowMover() : data_(new int(0)) {}
    ~SlowMover() { delete data_; }
    SlowMover(const SlowMover& o) : data_(new int(*o.data_)) { ++copies; }
    SlowMover(SlowMover&& o) : data_(std::exchange(o.data_, nullptr)) { ++moves; }   // no noexcept
    SlowMover& operator=(const SlowMover&) = delete;
private:
    int* data_;
};
class FastMover {
public:
    static inline int copies = 0, moves = 0;
    FastMover() : data_(new int(0)) {}
    ~FastMover() { delete data_; }
    FastMover(const FastMover& o) : data_(new int(*o.data_)) { ++copies; }
    FastMover(FastMover&& o) noexcept : data_(std::exchange(o.data_, nullptr)) { ++moves; }
    FastMover& operator=(const FastMover&) = delete;
private:
    int* data_;
};

// ---------- BEST (Rule of Zero): let members manage themselves ----------
class Document {
public:
    Document(std::string title, std::vector<int> pages) : title_(std::move(title)), pages_(std::move(pages)) {}
    const std::string& title() const { return title_; }
    std::size_t page_count() const { return pages_.size(); }
private:
    std::string title_;            // owns its memory
    std::vector<int> pages_;       // owns its memory
    // No destructor, no copy, no move written: the compiler-generated ones do the right thing.
};

template <typename T>
void count_vector_growth(const char* label) {
    T::copies = 0; T::moves = 0;
    std::vector<T> v;
    for (int i = 0; i < 4; ++i) v.push_back(T());
    std::cout << "  " << label << ": copies=" << T::copies << " moves=" << T::moves << " after 4 push_backs (includes reallocations)\n";
}

int main(int argc, char** argv) {
    const bool trigger_bug = argc > 1 && std::string(argv[1]) == "--bug=shallow-copy";

    std::cout << "===== SECTION 1: THE BUG (RULE OF THREE VIOLATED) =====\n";
    {
        WrongBuffer original(3, 1);
        WrongBuffer copy = original;               // compiler-generated copy: copies the pointer
        copy.set(0, 99);
        std::cout << "  wrote 99 through the copy; original.at(0) = " << original.at(0) << " (shared block, not a copy)\n";
        std::cout << "  both point at the same array: " << std::boolalpha << (original.raw() == copy.raw()) << '\n';
        if (!trigger_bug) {
            copy.detach_for_demo();
            std::cout << "  detached the copy so destruction is safe. Without that, both destructors would delete[] the same block.\n";
        } else {
            std::cout << "  --bug=shallow-copy given: letting both destructors run (double free)\n";
        }
    }

    std::cout << "\n===== SECTION 2: RULE OF FIVE DONE RIGHT =====\n";
    Buffer a(3, 7);
    Buffer b = a;                                  // copy constructor
    b.set(0, 1);
    std::cout << "  deep copy: a.at(0) = " << a.at(0) << ", b.at(0) = " << b.at(0) << '\n';
    Buffer c(2, 0);
    c = a;                                         // copy assignment
    std::cout << "  copy assignment: c.size() = " << c.size() << ", c.at(2) = " << c.at(2) << '\n';
    c = c;                                         // self-assignment must be safe
    std::cout << "  self-assignment survived: c.size() = " << c.size() << '\n';
    std::cout << "  copies so far = " << Buffer::copies << ", moves so far = " << Buffer::moves << '\n';

    std::cout << "\n===== SECTION 3: COPY vs MOVE =====\n";
    Buffer big(1000, 5);
    Buffer stolen = std::move(big);                // move constructor: steals the block, O(1)
    std::cout << "  after move: stolen.size() = " << stolen.size() << ", big.size() = " << big.size() << " (moved-from is valid but empty)\n";
    std::cout << "  copies = " << Buffer::copies << ", moves = " << Buffer::moves << '\n';
    Buffer target(1, 0);
    target = std::move(stolen);                    // move assignment
    std::cout << "  move assignment: target.size() = " << target.size() << ", stolen.size() = " << stolen.size() << '\n';
    // Trap: using a moved-from object's CONTENT is a logic bug. Only assign to it or destroy it.

    std::cout << "\n===== SECTION 4: noexcept MATTERS FOR vector =====\n";
    count_vector_growth<SlowMover>("move ctor NOT noexcept");
    count_vector_growth<FastMover>("move ctor noexcept    ");
    std::cout << "  vector only moves on reallocation if the move cannot throw; otherwise it copies to keep its guarantee.\n";

    std::cout << "\n===== SECTION 5: RULE OF ZERO =====\n";
    Document d1("Notes", {1, 2, 3});
    Document d2 = d1;                              // generated copy: deep, correct
    Document d3 = std::move(d2);                   // generated move: cheap, correct
    std::cout << "  d1: " << d1.title() << " with " << d1.page_count() << " pages; d3: " << d3.title() << " with " << d3.page_count() << " pages\n";
    std::cout << "  Rule of Zero: hold std::string / std::vector / smart pointers and write none of the five.\n";
    std::cout << "  Rule of Three/Five: if you write ANY of destructor, copy, move, write (or delete) all of them.\n";
    return 0;
}
