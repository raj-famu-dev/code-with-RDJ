// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * std::chrono durations and clocks, std::mt19937 with a fixed seed (the same
 * numbers every run), and std::filesystem used inside a temporary directory
 * that is created and removed by the program.
 */
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <algorithm>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

// RAII: create a fixed-name temp directory and delete it on scope exit.
class TempDir {
public:
    TempDir() : path_(fs::temp_directory_path() / "cpp_by_rdj_chrono_demo") {
        fs::remove_all(path_);  // start clean if a previous run was killed
        fs::create_directories(path_);
    }
    ~TempDir() {
        std::error_code ec;  // destructors must not throw: use the error_code overload
        fs::remove_all(path_, ec);
    }
    TempDir(const TempDir&) = delete;
    TempDir& operator=(const TempDir&) = delete;
    const fs::path& path() const { return path_; }

private:
    fs::path path_;
};

int main() {
    // ===== SECTION 1: chrono DURATIONS =====
    std::cout << "===== SECTION 1: chrono DURATIONS =====\n";
    auto d1 = 90min;
    auto d2 = 30s;
    auto total = d1 + d2;  // common type is seconds
    std::cout << "90min + 30s = " << total.count() << " seconds\n";
    std::cout << "as minutes (duration_cast truncates): " << std::chrono::duration_cast<std::chrono::minutes>(total).count() << "\n";
    std::chrono::duration<double, std::ratio<3600>> hours_f = total;  // floating-point duration converts implicitly
    std::cout << "as fractional hours: " << std::fixed << std::setprecision(4) << hours_f.count() << "\n";
    std::cout << "1500ms in seconds (int, truncated): " << std::chrono::duration_cast<std::chrono::seconds>(1500ms).count() << "\n";
    std::cout << "TRAP: duration_cast<seconds>(1500ms) is 1, not 1.5; integer durations truncate toward zero.\n";
    std::cout << "2h == 120min? " << std::boolalpha << (2h == 120min) << "\n";
    std::cout << "sizeof(std::chrono::nanoseconds) = " << sizeof(std::chrono::nanoseconds) << " bytes (just an integer)\n";

    // ===== SECTION 2: CLOCKS (MEASUREMENT) =====
    std::cout << "===== SECTION 2: CLOCKS (MEASUREMENT) =====\n";
    auto start = std::chrono::steady_clock::now();
    std::uint64_t acc = 0;
    for (std::uint64_t i = 0; i < 1000000; ++i) acc += i * i;
    auto stop = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);
    std::cout << "loop result (deterministic): " << acc << "\n";
    std::cout << "MEASUREMENT (varies every run, do not rely on it): elapsed >= 0 us? " << (elapsed.count() >= 0) << "\n";
    std::cout << "Use steady_clock to time code (never goes backwards); system_clock is wall time and can jump.\n";
    std::cout << "steady_clock is_steady=" << std::chrono::steady_clock::is_steady
              << ", system_clock is_steady=" << std::chrono::system_clock::is_steady << "\n";
    std::chrono::system_clock::time_point epoch{};
    std::cout << "default system_clock time_point is the epoch: seconds since epoch = "
              << std::chrono::duration_cast<std::chrono::seconds>(epoch.time_since_epoch()).count() << "\n";

    // ===== SECTION 3: mt19937 WITH A FIXED SEED =====
    std::cout << "===== SECTION 3: mt19937 WITH A FIXED SEED =====\n";
    std::mt19937 rng(42);
    std::cout << "first 5 raw outputs (seed 42):";
    for (int i = 0; i < 5; ++i) std::cout << " " << rng();
    std::cout << "\n";
    rng.seed(42);
    std::cout << "after re-seeding with 42, first output again: " << rng() << "\n";
    std::mt19937 rng2(2024);
    std::uniform_int_distribution<int> dice(1, 6);
    std::cout << "ten dice rolls (seed 2024):";
    for (int i = 0; i < 10; ++i) std::cout << " " << dice(rng2);
    std::cout << "\n";
    std::vector<int> deck = {1, 2, 3, 4, 5, 6, 7, 8};
    std::mt19937 shuffler(7);
    std::shuffle(deck.begin(), deck.end(), shuffler);
    std::cout << "shuffle with seed 7 (std::shuffle order is implementation-specific, so this is libstdc++ only):";
    for (int x : deck) std::cout << " " << x;
    std::cout << "\n";
    std::cout << "TRAP: std::random_device gives a different seed each run, so output is not reproducible;"
              << " use it only to pick a seed you then log.\n";
    std::cout << "TRAP: mt19937 raw values are fixed by the standard, but distributions (uniform_int_distribution) are"
              << " NOT guaranteed identical across compilers.\n";
    std::cout << "mt19937 is NOT cryptographically secure; never use it for passwords or keys.\n";

    // ===== SECTION 4: filesystem IN A TEMP DIRECTORY =====
    std::cout << "===== SECTION 4: filesystem IN A TEMP DIRECTORY =====\n";
    fs::path root_copy;
    {
        TempDir tmp;
        root_copy = tmp.path();
        std::cout << "temp dir exists: " << fs::exists(tmp.path()) << "\n";
        fs::create_directories(tmp.path() / "logs" / "2024");
        {
            std::ofstream(tmp.path() / "notes.txt") << "hello filesystem\n";
            std::ofstream(tmp.path() / "logs" / "a.log") << "line1\nline2\n";
            std::ofstream(tmp.path() / "logs" / "2024" / "b.log") << "x";
        }
        std::cout << "notes.txt size: " << fs::file_size(tmp.path() / "notes.txt") << " bytes\n";
        std::cout << "is_directory(logs): " << fs::is_directory(tmp.path() / "logs")
                  << ", is_regular_file(notes.txt): " << fs::is_regular_file(tmp.path() / "notes.txt") << "\n";
        std::vector<std::string> found;
        for (const auto& entry : fs::recursive_directory_iterator(tmp.path())) {
            found.push_back(fs::relative(entry.path(), tmp.path()).generic_string() + (entry.is_directory() ? "/" : ""));
        }
        std::sort(found.begin(), found.end());  // directory order is unspecified: sort for stable output
        std::cout << "recursive listing (sorted):\n";
        for (const auto& f : found) std::cout << "  " << f << "\n";
        fs::rename(tmp.path() / "notes.txt", tmp.path() / "renamed.txt");
        std::cout << "after rename: notes.txt exists=" << fs::exists(tmp.path() / "notes.txt")
                  << ", renamed.txt exists=" << fs::exists(tmp.path() / "renamed.txt") << "\n";
        fs::path p = "dir/sub/file.tar.gz";
        std::cout << "path parts: filename=" << p.filename().string() << " stem=" << p.stem().string()
                  << " extension=" << p.extension().string() << " parent=" << p.parent_path().string() << "\n";
        std::error_code ec;
        auto missing_size = fs::file_size(tmp.path() / "does_not_exist", ec);
        std::cout << "error_code overload on a missing file: failed=" << static_cast<bool>(ec)
                  << ", returned " << missing_size << " (no exception thrown)\n";
        try {
            (void)fs::file_size(tmp.path() / "does_not_exist");
        } catch (const fs::filesystem_error&) {
            std::cout << "throwing overload raised std::filesystem::filesystem_error\n";
        }
    }
    std::cout << "after the TempDir went out of scope, directory still exists? " << fs::exists(root_copy) << "\n";
    return 0;
}
