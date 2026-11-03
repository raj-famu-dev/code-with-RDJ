// Tags: #Cpp #ModernCpp #OptionalVariantAny | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * std::optional (maybe a value), std::variant with std::visit (one of several
 * types, like a sealed interface), and std::any (anything, type-erased).
 */
#include <any>
#include <iostream>
#include <optional>
#include <string>
#include <typeinfo>
#include <variant>
#include <vector>

std::optional<int> parse_digit(char ch) {
    if (ch >= '0' && ch <= '9') return ch - '0';
    return std::nullopt;
}

struct Circle { double r; };
struct Rect { double w, h; };
struct Triangle { double base, height; };
using Shape = std::variant<Circle, Rect, Triangle>;

double area(const Shape& s) {
    return std::visit(
        [](const auto& shape) -> double {
            using T = std::decay_t<decltype(shape)>;
            if constexpr (std::is_same_v<T, Circle>) return 3.0 * shape.r * shape.r;  // pi approximated as 3 for tidy output
            else if constexpr (std::is_same_v<T, Rect>) return shape.w * shape.h;
            else return 0.5 * shape.base * shape.height;
        },
        s);
}

// overloaded{} idiom: build one visitor from several lambdas.
template <class... Ts> struct overloaded : Ts... { using Ts::operator()...; };
template <class... Ts> overloaded(Ts...) -> overloaded<Ts...>;

std::string describe(const Shape& s) {
    return std::visit(overloaded{
                          [](const Circle& c) { return "circle r=" + std::to_string(static_cast<int>(c.r)); },
                          [](const Rect& r) { return "rect " + std::to_string(static_cast<int>(r.w)) + "x" + std::to_string(static_cast<int>(r.h)); },
                          [](const Triangle&) { return std::string("triangle"); },
                      },
                      s);
}

int main() {
    std::cout << std::boolalpha;
    // ===== SECTION 1: std::optional =====
    std::cout << "===== SECTION 1: std::optional =====\n";
    for (char ch : {'7', 'x'}) {
        std::optional<int> r = parse_digit(ch);
        std::cout << "parse_digit('" << ch << "') has_value=" << r.has_value();
        if (r) std::cout << " value=" << *r;
        std::cout << " value_or(-1)=" << r.value_or(-1) << "\n";
    }
    std::optional<int> empty;
    try {
        std::cout << empty.value() << "\n";  // checked access throws
    } catch (const std::bad_optional_access& e) {
        std::cout << "empty.value() threw std::bad_optional_access\n";
    }
    std::cout << "TRAP: *empty is undefined behaviour (no check), so never dereference without testing.\n";
    std::optional<std::string> name = "RDJ";
    name.reset();
    std::cout << "after reset(), has_value=" << name.has_value() << "\n";
    name.emplace("Raj");
    std::cout << "after emplace, value=" << *name << " size=" << name->size() << "\n";

    // ===== SECTION 2: std::variant =====
    std::cout << "===== SECTION 2: std::variant =====\n";
    std::variant<int, double, std::string> v = 42;
    std::cout << "holds int? " << std::holds_alternative<int>(v) << ", index=" << v.index() << "\n";
    v = std::string("hello");
    std::cout << "now holds string? " << std::holds_alternative<std::string>(v) << ", index=" << v.index() << "\n";
    if (auto* sp = std::get_if<std::string>(&v)) std::cout << "get_if<string> -> " << *sp << "\n";
    if (auto* ip = std::get_if<int>(&v); ip == nullptr) std::cout << "get_if<int> -> nullptr (wrong alternative)\n";
    try {
        (void)std::get<int>(v);
    } catch (const std::bad_variant_access&) {
        std::cout << "std::get<int>(v) threw std::bad_variant_access\n";
    }
    std::variant<std::string, int> dflt;  // default-constructs the FIRST alternative
    std::cout << "TRAP: default variant<string,int> holds index " << dflt.index() << " (the first type), value=\""
              << std::get<0>(dflt) << "\"; put a cheap default type first, or use std::monostate.\n";

    // ===== SECTION 3: std::visit AND SEALED-STYLE SHAPES =====
    std::cout << "===== SECTION 3: std::visit AND SEALED-STYLE SHAPES =====\n";
    std::vector<Shape> shapes = {Circle{2}, Rect{3, 4}, Triangle{6, 5}};
    for (const auto& s : shapes) {
        std::cout << describe(s) << " area=" << area(s) << "\n";
    }
    std::cout << "A visitor must handle EVERY alternative or the program does not compile (like an exhaustive switch).\n";

    // ===== SECTION 4: std::any =====
    std::cout << "===== SECTION 4: std::any =====\n";
    std::any box = 10;
    std::cout << "holds int? " << (box.type() == typeid(int)) << ", value=" << std::any_cast<int>(box) << "\n";
    box = std::string("now a string");
    std::cout << "holds string? " << (box.type() == typeid(std::string)) << ", value=" << std::any_cast<std::string>(box) << "\n";
    try {
        (void)std::any_cast<int>(box);
    } catch (const std::bad_any_cast&) {
        std::cout << "any_cast<int> on a string threw std::bad_any_cast\n";
    }
    if (const auto* p = std::any_cast<double>(&box); p == nullptr) {
        std::cout << "pointer form any_cast<double>(&box) returned nullptr (no throw)\n";
    }
    box.reset();
    std::cout << "after reset, has_value=" << box.has_value() << "\n";
    std::cout << "Prefer variant when the set of types is known; any loses all compile-time checking.\n";
    return 0;
}
