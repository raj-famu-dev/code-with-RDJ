// Tags: #Cpp #Pointers #MemoryManagement #RAII | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _5_RAII
 * Teaches: Resource Acquisition Is Initialisation. A resource is acquired in
 * a constructor and released in the destructor, so cleanup happens on every
 * exit path, including exceptions. Builds a ScopeGuard and a FileHandle
 * wrapper (a temp file created and removed by this program).
 */
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

// ---------- ScopeGuard: run any callable when the scope ends ----------
template <typename F>
class ScopeGuard {
public:
    explicit ScopeGuard(F f) : f_(std::move(f)) {}
    ~ScopeGuard() { if (active_) f_(); }
    void dismiss() { active_ = false; }                 // "commit": cancel the cleanup
    ScopeGuard(const ScopeGuard&) = delete;             // one owner of the cleanup duty
    ScopeGuard& operator=(const ScopeGuard&) = delete;
private:
    F f_;
    bool active_ = true;
};

// ---------- FileHandle: owns a FILE* ----------
class FileHandle {
public:
    FileHandle(const std::string& path, const char* mode) : fp_(std::fopen(path.c_str(), mode)) {
        if (!fp_) throw std::runtime_error("cannot open " + path);   // constructor failure = no object, no leak
        std::cout << "  [FileHandle opened]\n";
    }
    ~FileHandle() {
        if (fp_) { std::fclose(fp_); std::cout << "  [FileHandle closed]\n"; }
    }
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& o) noexcept : fp_(std::exchange(o.fp_, nullptr)) {}   // ownership can MOVE
    FileHandle& operator=(FileHandle&& o) noexcept {
        if (this != &o) { if (fp_) std::fclose(fp_); fp_ = std::exchange(o.fp_, nullptr); }
        return *this;
    }
    void write_line(const std::string& s) { std::fputs((s + "\n").c_str(), fp_); }
    std::string read_line() {
        char buf[128];
        return std::fgets(buf, sizeof buf, fp_) ? std::string(buf) : std::string();
    }
private:
    std::FILE* fp_;
};

// Why RAII matters: the manual version leaks if anything between open and close throws.
void manual_style(const std::string& path, bool fail) {
    std::FILE* fp = std::fopen(path.c_str(), "w");
    if (!fp) return;
    std::fputs("manual\n", fp);
    if (fail) { std::fclose(fp); throw std::runtime_error("manual: had to remember to close before throwing"); }
    std::fclose(fp);   // forgotten on every new early return/throw added later
}

int main() {
    const std::string path = (std::filesystem::temp_directory_path() / "rdj_raii_demo.txt").string();

    std::cout << "===== SECTION 1: ScopeGuard =====\n";
    {
        ScopeGuard g([] { std::cout << "  guard ran: cleanup at scope exit\n"; });
        std::cout << "  doing work inside the scope\n";
    }
    {
        ScopeGuard first([] { std::cout << "  first created, runs LAST\n"; });
        ScopeGuard second([] { std::cout << "  second created, runs FIRST\n"; });
    }
    {
        ScopeGuard rollback([] { std::cout << "  rollback (not printed: committed)\n"; });
        std::cout << "  work succeeded, committing\n";
        rollback.dismiss();
    }

    std::cout << "\n===== SECTION 2: DESTRUCTORS RUN WHEN AN EXCEPTION FLIES =====\n";
    try {
        ScopeGuard g([] { std::cout << "  guard ran during stack unwinding\n"; });
        std::cout << "  about to throw\n";
        throw std::runtime_error("failure in the middle");
    } catch (const std::exception& e) {
        std::cout << "  caught: " << e.what() << '\n';
    }

    std::cout << "\n===== SECTION 3: FileHandle =====\n";
    {
        FileHandle out(path, "w");
        out.write_line("hello raii");
        out.write_line("second line");
    }   // closed and flushed here, no explicit close call
    {
        FileHandle in(path, "r");
        std::cout << "  read back: " << in.read_line();
        std::cout << "  read back: " << in.read_line();
    }
    try {
        FileHandle in(path, "r");
        throw std::logic_error("something went wrong while the file is open");
    } catch (const std::exception& e) {
        std::cout << "  caught: " << e.what() << " (file was closed before this catch ran)\n";
    }
    try {
        FileHandle missing("/nonexistent-dir-rdj/nope.txt", "r");
    } catch (const std::exception& e) {
        std::cout << "  constructor failure: " << e.what() << " (no handle, nothing to close)\n";
    }

    std::cout << "\n===== SECTION 4: MOVING OWNERSHIP =====\n";
    {
        FileHandle a(path, "r");
        FileHandle b = std::move(a);               // a is now empty; only b will close
        std::cout << "  moved; exactly one close will follow\n";
    }

    std::cout << "\n===== SECTION 5: THE MANUAL STYLE FOR COMPARISON =====\n";
    try { manual_style(path, true); } catch (const std::exception& e) { std::cout << "  " << e.what() << '\n'; }
    std::cout << "  (it only worked because the author wrote fclose twice; RAII needs it zero times)\n";

    ScopeGuard cleanup([&path] { std::filesystem::remove(path); std::cout << "\ntemp file removed by a ScopeGuard\n"; });
    return 0;
}
