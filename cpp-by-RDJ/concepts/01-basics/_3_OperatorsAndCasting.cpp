// Tags: #Cpp #Basics #OperatorsCasting | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _3_OperatorsAndCasting
 * Teaches: arithmetic/bitwise/logical operators, integer division and
 * modulo with negatives, the increment forms, and why static_cast is
 * preferred over the C-style cast "(T)x".
 */
#include <cstdint>
#include <iostream>

int main() {
    std::cout << "===== SECTION 1: ARITHMETIC AND INTEGER DIVISION =====\n";
    int a = 7, b = 2;
    std::cout << "7 / 2 = " << a / b << " (integer division truncates toward zero)\n";
    std::cout << "-7 / 2 = " << -7 / b << ", -7 % 2 = " << -7 % b << " (remainder takes the sign of the dividend)\n";
    std::cout << "7.0 / 2 = " << 7.0 / b << " (one double operand makes it floating point)\n";
    // Trap: the division happens BEFORE the conversion to double.
    double wrong = a / b;
    double right = static_cast<double>(a) / b;
    std::cout << "double wrong = a / b  -> " << wrong << '\n';
    std::cout << "double right = static_cast<double>(a) / b -> " << right << '\n';

    std::cout << "\n===== SECTION 2: BITWISE, LOGICAL, SHORT-CIRCUIT =====\n";
    std::uint8_t flags = 0b0000'0101;
    flags |= 0b0000'1000;     // set bit 3
    flags &= static_cast<std::uint8_t>(~0b0000'0001);   // clear bit 0
    flags ^= 0b1000'0000;     // toggle bit 7
    std::cout << "flags = " << static_cast<int>(flags) << " (binary 10001100)\n";
    std::cout << "1 << 4 = " << (1 << 4) << ", 256 >> 3 = " << (256 >> 3) << '\n';
    int calls = 0;
    auto noisy = [&calls] { ++calls; return true; };
    bool r1 = false && noisy();   // right side never runs
    bool r2 = true || noisy();    // right side never runs
    std::cout << "short-circuit: calls = " << calls << " (r1=" << r1 << ", r2=" << r2 << ")\n";
    std::cout << "& vs &&: 6 & 3 = " << (6 & 3) << " but 6 && 3 = " << (6 && 3) << '\n';

    std::cout << "\n===== SECTION 3: INCREMENT AND ASSIGNMENT =====\n";
    int i = 5;
    int post = i++;    // value BEFORE the increment
    int pre = ++i;     // value AFTER the increment
    std::cout << "post = " << post << ", pre = " << pre << ", i = " << i << '\n';
    int x = 10;
    x += 5; x -= 3; x *= 2; x /= 4; x %= 4;
    std::cout << "compound assignments end at x = " << x << '\n';
    int t = 3;
    int tern = (t > 2) ? 100 : 200;
    std::cout << "ternary = " << tern << '\n';
    // Trap: never modify a variable twice in one expression (i = i++ + ++i
    // was undefined before C++17 and is still unreadable). Use separate statements.

    std::cout << "\n===== SECTION 4: static_cast VS THE C-STYLE CAST =====\n";
    double pi = 3.99;
    std::cout << "static_cast<int>(3.99) = " << static_cast<int>(pi) << " (truncates, does not round)\n";
    int big = 300;
    auto small = static_cast<std::uint8_t>(big);
    std::cout << "static_cast<uint8_t>(300) = " << static_cast<int>(small) << " (300 mod 256, defined for unsigned)\n";
    // Why C-style casts are bad: one syntax silently picks static_cast,
    // const_cast or reinterpret_cast, so a typo changes the meaning and
    // nothing warns you. It is also hard to grep for.
    const int locked = 7;
    const int* cp = &locked;
    // int* p = static_cast<int*>(cp);   // ERROR: static_cast refuses to drop const. Good.
    // int* p = (int*)cp;                // compiles silently and invites writing to a const object.
    std::cout << "static_cast refuses to drop const; (int*)cp would compile silently. Locked is still " << *cp << '\n';
    // reinterpret_cast is the loud, greppable tool for reading bytes of an object.
    std::uint32_t word = 0x01020304;
    auto* bytes = reinterpret_cast<const unsigned char*>(&word);   // char types may alias anything
    std::cout << "first byte of 0x01020304 in memory = " << static_cast<int>(bytes[0])
              << " (4 on little-endian machines)\n";
    return 0;
}
