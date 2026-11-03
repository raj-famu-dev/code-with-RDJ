// Tags: #Cpp #Templates #STL #TemplateTraitsSFINAE | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: <type_traits> (queries and transformations), `if constexpr`
 * (compile-time branches), classic SFINAE with std::enable_if and a
 * detection idiom (void_t), and compile-time checks with static_assert.
 * SFINAE = "Substitution Failure Is Not An Error": a template whose signature
 * fails to substitute is silently removed from the overload set.
 * In modern C++20 prefer concepts (previous files) where you can.
 */
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

// ===== SECTION 1: type traits =====
template <typename T>
void inspect(const char* name) {
    std::cout << "  " << name << ": integral=" << std::is_integral_v<T> << " floating=" << std::is_floating_point_v<T>
              << " pointer=" << std::is_pointer_v<T> << " const=" << std::is_const_v<T> << " sizeof=" << sizeof(T) << "\n";
}

// ===== SECTION 2: if constexpr =====
template <typename T>
std::string kind(const T& v) {
    if constexpr (std::is_integral_v<T>) return "integer " + std::to_string(v);
    else if constexpr (std::is_floating_point_v<T>) return "float " + std::to_string(v);
    else if constexpr (std::is_same_v<T, std::string>) return "string \"" + v + "\"";
    else return "something else";                // note: branches NOT taken are not even compiled for this T
}
template <typename T>
auto describeSize(const T& v) {                    // v.size() only exists in the branch where it is valid
    if constexpr (requires { v.size(); }) return v.size();
    else return static_cast<std::size_t>(1);
}

// ===== SECTION 3: SFINAE =====
template <typename T, typename = void>
struct HasSize : std::false_type {};              // default: no size()
template <typename T>
struct HasSize<T, std::void_t<decltype(std::declval<T>().size())>> : std::true_type {};   // chosen only if size() is valid

template <typename T>
std::enable_if_t<std::is_integral_v<T>, std::string> pretty(T v) { return "int-like:" + std::to_string(v); }
template <typename T>
std::enable_if_t<!std::is_integral_v<T> && HasSize<T>::value, std::string> pretty(const T& v) { return "sized:" + std::to_string(v.size()); }
template <typename T>
std::enable_if_t<!std::is_integral_v<T> && !HasSize<T>::value, std::string> pretty(const T&) { return "opaque"; }
struct Blob {};

// ===== SECTION 4: compile-time checks =====
template <typename T>
struct Wrapper {
    static_assert(std::is_copy_constructible_v<T>, "Wrapper<T> requires a copyable T");
    T value;
};
static_assert(std::is_same_v<std::remove_reference_t<int&>, int>);
static_assert(std::is_same_v<std::remove_cv_t<const volatile int>, int>);
static_assert(std::is_same_v<std::conditional_t<(sizeof(int) >= 4), long, short>, long>);
static_assert(HasSize<std::vector<int>>::value && !HasSize<int>::value);
static_assert(std::is_trivially_copyable_v<int> && !std::is_trivially_copyable_v<std::string>);

int main() {
    std::cout << std::boolalpha;
    std::cout << "===== SECTION 1: type traits =====\n";
    inspect<int>("int");
    inspect<double>("double");
    inspect<const char*>("const char*");
    inspect<const long>("const long");
    std::cout << "remove_reference_t<int&> is int: " << std::is_same_v<std::remove_reference_t<int&>, int> << ", decay_t<const int&> is int: " << std::is_same_v<std::decay_t<const int&>, int> << "\n";
    std::cout << "Traits are compile-time functions on TYPES: ::value (bool) or ::type / _t (a type).\n";

    std::cout << "\n===== SECTION 2: if constexpr =====\n";
    std::cout << kind(42) << " | " << kind(2.5) << " | " << kind(std::string("hi")) << " | " << kind(Blob{}) << "\n";
    std::cout << "describeSize(vector of 3) = " << describeSize(std::vector<int>{1, 2, 3}) << ", describeSize(7) = " << describeSize(7) << "\n";
    std::cout << "A plain `if` here would not compile for int (7.size() is an error); `if constexpr` discards the branch at compile time.\n";

    std::cout << "\n===== SECTION 3: SFINAE =====\n";
    std::cout << "HasSize<std::string>=" << HasSize<std::string>::value << " HasSize<int>=" << HasSize<int>::value << " HasSize<Blob>=" << HasSize<Blob>::value << "\n";
    std::cout << pretty(5) << " | " << pretty(std::string("abcd")) << " | " << pretty(Blob{}) << "\n";
    std::cout << "Each pretty() overload whose enable_if is false fails substitution and silently drops out; exactly one remains.\n";
    std::cout << "If NO overload remains you get 'no matching function' (a long error): the pain that concepts were created to fix.\n";

    std::cout << "\n===== SECTION 4: compile-time checks =====\n";
    Wrapper<int> w{9};
    Wrapper<std::string> ws{"copyable"};
    std::cout << "Wrapper<int> value = " << w.value << ", Wrapper<std::string> value = " << ws.value << "\n";
    std::cout << "Wrapper<std::unique_ptr<int>> would stop compilation with the message: \"Wrapper<T> requires a copyable T\".\n";
    std::cout << "5 static_assert lines at file scope were checked by the compiler; a false one would prevent this program from existing.\n";
    return 0;
}
