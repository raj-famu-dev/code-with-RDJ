// Tags: #Cpp #Basics #InputOutput | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _8_InputOutput
 * Teaches: iostream formatting with <iomanip>, sticky vs non-sticky
 * manipulators, and parsing text with std::istringstream. No keyboard
 * input: all "input" comes from built-in strings.
 */
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main() {
    std::cout << "===== SECTION 1: STREAMS AND cout vs cerr =====\n";
    std::cout << "cout is buffered stdout; cerr is unbuffered stderr (not shown below).\n";
    std::cout << "A newline '\\n' is cheap; std::endl also flushes, which is slow in loops.\n";
    std::cerr << "";   // writing to cerr is for diagnostics; empty here to keep stdout-only output
    std::cout << std::boolalpha << true << ' ' << std::noboolalpha << true << '\n';

    std::cout << "\n===== SECTION 2: FORMATTING WITH <iomanip> =====\n";
    double pi = 3.14159265358979;
    std::cout << "default:          " << pi << '\n';
    std::cout << "fixed, 2 places:  " << std::fixed << std::setprecision(2) << pi << '\n';
    std::cout << "fixed, 5 places:  " << std::setprecision(5) << pi << " (setprecision and fixed are STICKY)\n";
    std::cout << std::defaultfloat << std::setprecision(6);   // restore defaults: sticky state leaks
    std::cout << "scientific:       " << std::scientific << 12345.678 << std::defaultfloat << '\n';
    std::cout << "hex/oct/dec of 255: " << std::hex << 255 << ' ' << std::oct << 255 << ' ' << std::dec << 255 << '\n';
    std::cout << std::showbase << std::hex << "with showbase: " << 255 << std::noshowbase << std::dec << '\n';
    std::cout << "table:\n";
    std::cout << std::left << std::setw(10) << "item" << std::right << std::setw(8) << "price" << '\n';
    std::cout << std::setfill('-') << std::setw(18) << "" << std::setfill(' ') << '\n';
    struct Row { const char* name; double price; };
    const std::vector<Row> rows{{"coffee", 3.5}, {"bagel", 2.25}, {"juice", 12.0}};
    for (const auto& r : rows)
        std::cout << std::left << std::setw(10) << r.name << std::right << std::setw(8)
                  << std::fixed << std::setprecision(2) << r.price << '\n';
    std::cout << std::defaultfloat << std::setprecision(6);
    std::cout << "setw is NOT sticky: [" << std::setw(5) << 42 << "][" << 42 << "]\n";

    std::cout << "\n===== SECTION 3: PARSING WITH istringstream =====\n";
    std::istringstream csv("alice 30 4.5\nbob 25 3.0\ncarol 41 5.0\n");
    std::string name;
    int age;
    double score;
    double total = 0;
    while (csv >> name >> age >> score) {       // the stream converts to false at the first failed read
        std::cout << "parsed " << name << ", age " << age << ", score " << score << '\n';
        total += score;
    }
    std::cout << "total score = " << total << '\n';
    std::cout << "stream at end: eof=" << std::boolalpha << csv.eof() << ", fail=" << csv.fail() << '\n';

    std::cout << "\n===== SECTION 4: getline, SPLITTING AND BAD INPUT =====\n";
    std::istringstream lines("key=value\nname=RDJ\nbroken line\nlang=C++\n");
    std::string line;
    while (std::getline(lines, line)) {
        auto eq = line.find('=');
        if (eq == std::string::npos) {
            std::cout << "skipping malformed line: \"" << line << "\"\n";
            continue;
        }
        std::cout << "key=" << line.substr(0, eq) << " value=" << line.substr(eq + 1) << '\n';
    }
    // Trap: parsing a number from bad text does not throw; the stream fails.
    std::istringstream bad("12abc");
    int n = -1;
    bad >> n;
    std::string rest;
    bad >> rest;
    std::cout << "read '12abc' as int: n=" << n << ", leftover=\"" << rest << "\"\n";
    std::istringstream nonnum("abc");
    int m = 99;
    nonnum >> m;
    std::cout << "read 'abc' as int: m=" << m << ", fail=" << nonnum.fail() << " (m is set to 0 since C++11; always check the stream)\n";

    std::cout << "\n===== SECTION 5: BUILDING TEXT WITH ostringstream =====\n";
    std::ostringstream out;
    out << "id=" << std::setw(4) << std::setfill('0') << 7 << ";ok=" << std::boolalpha << true;
    std::cout << out.str() << '\n';
    return 0;
}
