// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * File I/O with std::ofstream / std::ifstream: text vs binary, reading line by
 * line, checking for errors, RAII closing, and a temporary directory that the
 * program deletes at the end. No -pthread needed for this file.
 */
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>

namespace fs = std::filesystem;

// RAII temp directory: removed when it goes out of scope, even if an exception is thrown.
class TempDir {
public:
    TempDir() : path_(fs::temp_directory_path() / "cpp_by_rdj_fstream_demo") {
        fs::remove_all(path_);
        fs::create_directories(path_);
    }
    ~TempDir() {
        std::error_code ec;
        fs::remove_all(path_, ec);
    }
    TempDir(const TempDir&) = delete;
    TempDir& operator=(const TempDir&) = delete;
    const fs::path& path() const { return path_; }

private:
    fs::path path_;
};

struct Record {  // a plain struct is safe to write as raw bytes ONLY because it has no pointers
    std::int32_t id;
    double score;
};

bool write_lines(const fs::path& file, const std::vector<std::string>& lines) {
    std::ofstream out(file);  // text mode, truncates by default
    if (!out) return false;
    for (const auto& l : lines) out << l << '\n';
    return static_cast<bool>(out);  // true only if every write succeeded
}

std::vector<std::string> read_lines(const fs::path& file) {
    std::ifstream in(file);
    if (!in) throw std::runtime_error("cannot open " + file.filename().string());
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(in, line)) lines.push_back(line);  // the loop condition IS the read
    return lines;
}

int main() {
    std::cout << std::boolalpha;
    TempDir tmp;

    // ===== SECTION 1: WRITING AND READING TEXT =====
    std::cout << "===== SECTION 1: WRITING AND READING TEXT =====\n";
    const fs::path text_file = tmp.path() / "notes.txt";
    std::cout << "write_lines ok: " << write_lines(text_file, {"first line", "second line", "", "fourth line"}) << "\n";
    auto lines = read_lines(text_file);
    std::cout << "read back " << lines.size() << " lines:\n";
    for (std::size_t i = 0; i < lines.size(); ++i) std::cout << "  [" << i << "] \"" << lines[i] << "\"\n";
    std::cout << "file size on disk: " << fs::file_size(text_file) << " bytes\n";
    {
        std::ofstream app(text_file, std::ios::app);  // append instead of truncate
        app << "appended line\n";
    }  // closed here by the destructor: RAII, no close() needed
    std::cout << "lines after append: " << read_lines(text_file).size() << "\n";
    std::ifstream whole(text_file);
    std::stringstream buffer;
    buffer << whole.rdbuf();  // slurp the entire file into a string
    std::cout << "whole-file read length: " << buffer.str().size() << " characters\n";
    std::ifstream words_in(text_file);
    std::string word;
    int words = 0;
    while (words_in >> word) ++words;  // operator>> splits on whitespace
    std::cout << "word count via operator>>: " << words << "\n";

    // ===== SECTION 2: BINARY VS TEXT =====
    std::cout << "===== SECTION 2: BINARY VS TEXT =====\n";
    const fs::path bin_file = tmp.path() / "records.bin";
    const std::vector<Record> records = {{1, 91.5}, {2, 78.25}, {3, 100.0}};
    {
        std::ofstream out(bin_file, std::ios::binary);
        for (const auto& r : records) out.write(reinterpret_cast<const char*>(&r), sizeof(Record));
    }
    std::cout << "sizeof(Record) = " << sizeof(Record) << " (includes padding), file size = " << fs::file_size(bin_file) << " bytes\n";
    {
        std::ifstream in(bin_file, std::ios::binary);
        Record r{};
        std::cout << "read back:";
        while (in.read(reinterpret_cast<char*>(&r), sizeof(Record))) std::cout << " (" << r.id << ", " << r.score << ")";
        std::cout << "\n";
    }
    const fs::path num_text = tmp.path() / "number.txt";
    {
        std::ofstream out(num_text);
        out << 1234567;  // text: one character per digit
    }
    const fs::path num_bin = tmp.path() / "number.bin";
    {
        std::ofstream out(num_bin, std::ios::binary);
        std::int32_t v = 1234567;
        out.write(reinterpret_cast<const char*>(&v), sizeof(v));  // binary: always 4 bytes
    }
    std::cout << "the number 1234567 takes " << fs::file_size(num_text) << " bytes as text and " << fs::file_size(num_bin)
              << " bytes as binary\n";
    std::cout << "TRAP: binary files written this way are tied to this machine's byte order, padding and type sizes;\n"
                 "      they are not a portable file format. Never write structs that contain pointers or std::string.\n";
    std::cout << "TRAP: on Windows, text mode translates \\n to \\r\\n; on Linux it makes no difference. Use std::ios::binary for raw bytes.\n";

    // ===== SECTION 3: ERROR CHECKING =====
    std::cout << "===== SECTION 3: ERROR CHECKING =====\n";
    std::ifstream missing(tmp.path() / "nope.txt");
    std::cout << "opening a missing file -> is_open: " << missing.is_open() << ", operator bool: " << static_cast<bool>(missing) << "\n";
    try {
        (void)read_lines(tmp.path() / "nope.txt");
    } catch (const std::runtime_error& e) {
        std::cout << "read_lines threw: " << e.what() << "\n";
    }
    std::ifstream in(text_file);
    std::string first;
    in >> first;
    std::cout << "state after a good read: good=" << in.good() << " eof=" << in.eof() << " fail=" << in.fail() << "\n";
    std::ifstream numbers(text_file);
    int n = 0;
    numbers >> n;  // the file starts with "first", not a number
    std::cout << "reading an int from text 'first': failbit set: " << numbers.fail() << ", n = " << n << "\n";
    std::ifstream tiny(num_bin, std::ios::binary);
    char two[2];
    tiny.read(two, 2);
    char ten[10];
    tiny.read(ten, 10);  // only 2 bytes remain
    std::cout << "asked for 10 bytes with 2 left: gcount=" << tiny.gcount() << ", eof=" << tiny.eof() << ", fail=" << tiny.fail() << "\n";
    std::cout << "TRAP: 'while (!in.eof()) { getline(in, s); use(s); }' processes a bogus last item; test the READ itself:\n"
                 "      'while (getline(in, s)) { use(s); }'.\n";
    std::ofstream impossible(tmp.path() / "no_such_dir" / "file.txt");
    std::cout << "writing into a missing directory -> opened: " << impossible.is_open() << " (fstream never creates directories)\n";

    // ===== SECTION 4: RAII AND EXCEPTIONS =====
    std::cout << "===== SECTION 4: RAII AND EXCEPTIONS =====\n";
    const fs::path raii_file = tmp.path() / "raii.txt";
    try {
        std::ofstream out(raii_file);
        out << "written before the failure\n";
        throw std::runtime_error("something failed mid-write");
    } catch (const std::runtime_error& e) {
        std::cout << "caught: " << e.what() << "\n";
    }
    std::cout << "ofstream destructor still flushed and closed it; file has " << fs::file_size(raii_file) << " bytes\n";
    {
        std::ifstream strict;  // opt in to exceptions on failure
        strict.exceptions(std::ios::failbit);
        try {
            strict.open(tmp.path() / "nope.txt");
        } catch (const std::ios_base::failure&) {
            std::cout << "with exceptions(failbit) enabled, opening a missing file threw std::ios_base::failure\n";
        }
    }
    std::cout << "TRAP: the destructor closes the file but cannot report a failed flush; for data you cannot lose, call\n"
                 "      out.flush() or out.close() yourself and check the stream afterwards.\n";
    std::cout << "files in the temp directory before cleanup: ";
    int count = 0;
    for (const auto& e : fs::directory_iterator(tmp.path())) {
        (void)e;
        ++count;
    }
    std::cout << count << "\n";
    return 0;
}
