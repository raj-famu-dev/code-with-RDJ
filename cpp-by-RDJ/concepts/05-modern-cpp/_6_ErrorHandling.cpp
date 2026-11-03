// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Error handling in C++: exceptions, noexcept, error codes, a tiny Result<T,E>
 * type (std::expected is C++23 and NOT in g++ 13), and the three exception
 * safety guarantees (basic, strong, no-throw).
 */
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <variant>
#include <vector>

// ---------- a tiny Result type (what std::expected does in C++23) ----------
template <class T, class E>
class Result {
public:
    static Result ok(T value) { return Result(std::in_place_index<0>, std::move(value)); }
    static Result fail(E error) { return Result(std::in_place_index<1>, std::move(error)); }
    bool has_value() const { return data_.index() == 0; }
    explicit operator bool() const { return has_value(); }
    const T& value() const { return std::get<0>(data_); }
    const E& error() const { return std::get<1>(data_); }
    T value_or(T fallback) const { return has_value() ? std::get<0>(data_) : std::move(fallback); }

private:
    template <class... Args>
    explicit Result(Args&&... args) : data_(std::forward<Args>(args)...) {}
    std::variant<T, E> data_;
};

enum class ParseError { Empty, NotANumber, OutOfRange };
std::string_view to_string(ParseError e) {
    switch (e) {
        case ParseError::Empty: return "Empty";
        case ParseError::NotANumber: return "NotANumber";
        case ParseError::OutOfRange: return "OutOfRange";
    }
    return "?";
}

Result<int, ParseError> parse_percent(const std::string& text) {
    if (text.empty()) return Result<int, ParseError>::fail(ParseError::Empty);
    for (char c : text)
        if (c < '0' || c > '9') return Result<int, ParseError>::fail(ParseError::NotANumber);
    int n = std::stoi(text);
    if (n > 100) return Result<int, ParseError>::fail(ParseError::OutOfRange);
    return Result<int, ParseError>::ok(n);
}

// ---------- the same job with an exception and with an error code ----------
int parse_percent_throwing(const std::string& text) {
    auto r = parse_percent(text);
    if (!r) throw std::invalid_argument("bad percent '" + text + "': " + std::string(to_string(r.error())));
    return r.value();
}

bool parse_percent_code(const std::string& text, int& out) {  // C-style: bool + out-parameter
    auto r = parse_percent(text);
    if (!r) return false;
    out = r.value();
    return true;
}

// ---------- exception safety ----------
struct Tracer {  // counts live objects so we can see destructors run
    static inline int alive = 0;
    Tracer() { ++alive; }
    Tracer(const Tracer&) { ++alive; }
    ~Tracer() { --alive; }
};

// Adding an item fails (throws) when the item is empty.
void add_checked(std::vector<std::string>& list, const std::string& item) {
    if (item.empty()) throw std::invalid_argument("empty item");
    list.push_back(item);
}

// BASIC guarantee only: if a later item throws, 'dst' keeps the items already added (valid, no leaks, but changed).
void append_basic(std::vector<std::string>& dst, const std::vector<std::string>& src) {
    for (const auto& item : src) add_checked(dst, item);
}

// STRONG guarantee: build a copy, then swap (commit) only after everything succeeded.
void append_strong(std::vector<std::string>& dst, const std::vector<std::string>& src) {
    std::vector<std::string> tmp = dst;  // dst is untouched until the commit
    for (const auto& item : src) add_checked(tmp, item);
    dst.swap(tmp);                       // noexcept commit
}

// NO-THROW guarantee: swap and destructors must never throw.
void swap_nothrow(int& a, int& b) noexcept {
    int t = a;
    a = b;
    b = t;
}

int risky_cleanup_demo(bool fail) {
    std::unique_ptr<Tracer> guard = std::make_unique<Tracer>();  // RAII frees on any exit path
    if (fail) throw std::runtime_error("failed after acquiring a resource");
    return 0;
}

void might_throw() { throw std::runtime_error("boom"); }
void promise_not_to_throw() noexcept {}

int main(int argc, char** argv) {
    // ===== SECTION 1: EXCEPTIONS =====
    std::cout << "===== SECTION 1: EXCEPTIONS =====\n";
    try {
        std::cout << "parse '42' -> " << parse_percent_throwing("42") << "\n";
        std::cout << "parse 'abc' -> " << parse_percent_throwing("abc") << "\n";
        std::cout << "not reached\n";
    } catch (const std::invalid_argument& e) {
        std::cout << "caught invalid_argument: " << e.what() << "\n";
    }
    try {
        std::vector<int> v(3);
        (void)v.at(10);  // checked access throws; operator[] would be undefined behaviour
    } catch (const std::out_of_range& e) {
        std::cout << "vector::at threw std::out_of_range (message is implementation specific)\n";
        (void)e;
    }
    try {
        try {
            might_throw();
        } catch (const std::exception& e) {
            std::cout << "inner caught '" << e.what() << "' and rethrows with a bare 'throw;'\n";
            throw;  // rethrow the SAME exception, no slicing
        }
    } catch (const std::runtime_error& e) {
        std::cout << "outer caught runtime_error: " << e.what() << "\n";
    }
    std::cout << "TRAP: catch by const reference. 'catch (std::exception e)' by value would slice a derived exception.\n";
    std::cout << "Stack unwinding runs destructors: ";
    try {
        risky_cleanup_demo(true);
    } catch (const std::exception&) {
        std::cout << "Tracer::alive after unwinding = " << Tracer::alive << " (0 means the unique_ptr cleaned up)\n";
    }

    // ===== SECTION 2: noexcept =====
    std::cout << "===== SECTION 2: noexcept =====\n";
    std::cout << std::boolalpha;
    std::cout << "noexcept(promise_not_to_throw()) = " << noexcept(promise_not_to_throw()) << "\n";
    std::cout << "noexcept(might_throw())          = " << noexcept(might_throw()) << "\n";
    std::cout << "is_nothrow_move_constructible<std::string> = " << std::is_nothrow_move_constructible_v<std::string> << "\n";
    std::cout << "TRAP: if a noexcept function lets an exception escape, std::terminate is called (the program aborts).\n";
    if (argc > 1 && std::string_view(argv[1]) == "--terminate") {
        std::cout << "calling a noexcept function that throws now; expect the process to abort...\n" << std::flush;
        void (*thrower)() = might_throw;  // call through a pointer so the compiler cannot warn
        auto bad = [thrower]() noexcept { thrower(); };
        bad();
    } else {
        std::cout << "(skipped; run with --terminate to watch std::terminate happen, exit code is 134)\n";
    }

    // ===== SECTION 3: ERROR CODES AND Result<T,E> =====
    std::cout << "===== SECTION 3: ERROR CODES AND Result<T,E> =====\n";
    int out = -1;
    std::cout << "error-code style: parse_percent_code(\"55\", out) -> " << parse_percent_code("55", out) << ", out=" << out << "\n";
    std::cout << "error-code style: parse_percent_code(\"\", out)   -> " << parse_percent_code("", out)
              << ", out stays " << out << " (caller can forget to check the bool)\n";
    for (const std::string text : {"75", "", "12x", "250"}) {
        auto r = parse_percent(text);
        if (r) std::cout << "Result \"" << text << "\" -> ok " << r.value() << "\n";
        else std::cout << "Result \"" << text << "\" -> error " << to_string(r.error()) << "\n";
    }
    std::cout << "value_or: " << parse_percent("abc").value_or(-1) << "\n";
    std::cout << "Use exceptions for rare, truly exceptional failures; use Result/codes where failure is routine "
                 "(parsing user input) or exceptions are banned (kernels, embedded, hot loops).\n";

    // ===== SECTION 4: EXCEPTION SAFETY GUARANTEES =====
    std::cout << "===== SECTION 4: EXCEPTION SAFETY GUARANTEES =====\n";
    const std::vector<std::string> src = {"c", "", "e"};  // the empty string makes the 2nd item fail
    {
        std::vector<std::string> dst = {"a", "b"};
        try {
            append_basic(dst, src);
        } catch (const std::invalid_argument&) {
        }
        std::cout << "basic guarantee:  dst was {a,b}; after the failed append it has " << dst.size()
                  << " elements (the 'c' stayed: changed, but valid)\n";
    }
    {
        std::vector<std::string> dst = {"a", "b"};
        try {
            append_strong(dst, src);
        } catch (const std::invalid_argument&) {
        }
        std::cout << "strong guarantee: dst was {a,b}; after the failed append it has " << dst.size()
                  << " elements (rolled back, as if nothing happened)\n";
    }
    int a = 1, b = 2;
    swap_nothrow(a, b);
    std::cout << "nothrow guarantee: swap_nothrow(1,2) -> " << a << "," << b << " (never throws, so it can be the commit step)\n";
    std::cout << "Levels: no-throw > strong (all or nothing) > basic (valid, no leaks) > none (leaks/corruption).\n";
    std::cout << "Destructors are implicitly noexcept: never throw from one.\n";
    return 0;
}
