// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// Demo of ThreadPool, ending with a parallel word count over generated in-memory text (no files).
//   usage: ./main [word_count]       (default 2,000,000 words; smaller is faster under sanitizers)
//
// Counts, results and the correctness check are deterministic (seeded std::mt19937, only `%` on its output).
// Wall-clock times are MEASUREMENTS: they differ per machine and per run and are labelled as such.
// The program exits 1 if the pooled word count differs from the sequential one.

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <future>
#include <random>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

#include "thread_pool.hpp"

using WordCounts = std::unordered_map<std::string_view, std::size_t>;

static void section(const char* title) { std::printf("\n===== %s =====\n", title); }

// ---------- text generation (deterministic) ----------
static std::string generate_text(std::size_t word_count, unsigned seed) {
    std::mt19937 rng(seed);
    std::vector<std::string> vocabulary;
    for (int i = 0; i < 2000; ++i) {
        std::string w;
        const std::size_t length = 3 + rng() % 7;
        for (std::size_t k = 0; k < length; ++k) w.push_back(static_cast<char>('a' + rng() % 26));
        vocabulary.push_back(w + std::to_string(i));  // the suffix keeps all 2000 words distinct
    }
    std::string text;
    text.reserve(word_count * 8);
    for (std::size_t i = 0; i < word_count; ++i) {
        // skew toward low indices (min of two draws) so some words are much more frequent than others
        const std::size_t index = std::min(rng() % vocabulary.size(), rng() % vocabulary.size());
        text += vocabulary[index];
        text.push_back(rng() % 17 == 0 ? '\n' : ' ');
    }
    return text;
}

// ---------- word counting on a slice of the text ----------
static bool is_separator(char c) { return c == ' ' || c == '\n'; }

static WordCounts count_words(std::string_view slice) {
    WordCounts counts;
    std::size_t i = 0;
    while (i < slice.size()) {
        while (i < slice.size() && is_separator(slice[i])) ++i;
        const std::size_t start = i;
        while (i < slice.size() && !is_separator(slice[i])) ++i;
        if (i > start) ++counts[slice.substr(start, i - start)];
    }
    return counts;
}

// Cut the text into `chunks` slices whose edges fall on separators, so no word is split between two slices.
static std::vector<std::string_view> split_on_boundaries(std::string_view text, std::size_t chunks) {
    std::vector<std::string_view> slices;
    std::size_t begin = 0;
    for (std::size_t c = 1; c <= chunks && begin < text.size(); ++c) {
        std::size_t end = c == chunks ? text.size() : text.size() * c / chunks;
        if (end < begin) end = begin;
        while (end < text.size() && !is_separator(text[end])) ++end;  // extend to the end of the current word
        slices.push_back(text.substr(begin, end - begin));
        begin = end;
    }
    return slices;
}

using Clock = std::chrono::steady_clock;
static double elapsed_ms(Clock::time_point from) { return std::chrono::duration<double, std::milli>(Clock::now() - from).count(); }

int main(int argc, char** argv) {
    const std::size_t word_count = argc > 1 ? static_cast<std::size_t>(std::strtoull(argv[1], nullptr, 10)) : 2'000'000;
    const unsigned cores = std::thread::hardware_concurrency();
    std::printf("ThreadPool demo. std::thread::hardware_concurrency() on this machine = %u (a measurement of THIS machine)\n", cores);

    // ===== SECTION 1: submit and futures =====
    section("SECTION 1: submit returns a future; results are read in submission order");
    {
        ThreadPool pool(4);
        std::vector<std::future<int>> futures;
        for (int i = 1; i <= 8; ++i) futures.push_back(pool.submit([](int n) { return n * n; }, i));
        std::printf("squares of 1..8 via 4 workers:");
        for (auto& f : futures) std::printf(" %d", f.get());
        std::printf("\n");
    }

    // ===== SECTION 2: exceptions travel through the future =====
    section("SECTION 2: an exception thrown inside a task is rethrown by future.get()");
    {
        ThreadPool pool(2);
        auto failing = pool.submit([]() -> int { throw std::runtime_error("task failed on purpose"); });
        try {
            (void)failing.get();
        } catch (const std::runtime_error& e) {
            std::printf("caught in the caller: %s\n", e.what());
        }
        auto after = pool.submit([] { return 7; });
        std::printf("the pool still works afterwards: %d\n", after.get());
    }

    // ===== SECTION 3: graceful shutdown =====
    section("SECTION 3: shutdown() lets queued tasks finish");
    {
        std::atomic<int> done{0};
        {
            ThreadPool pool(2);
            for (int i = 0; i < 100; ++i) (void)pool.submit([&done] { ++done; });
        }  // destructor -> shutdown(): drains the queue, then joins
        std::printf("100 tasks submitted, pool destroyed immediately, tasks completed = %d\n", done.load());
    }

    // ===== SECTION 4: parallel word count =====
    section("SECTION 4: parallel word count over generated in-memory text");
    const std::string text = generate_text(word_count, 2024);
    std::printf("generated %zu words, %zu bytes of text (seed 2024)\n", word_count, text.size());

    auto t0 = Clock::now();
    const WordCounts sequential = count_words(text);
    const double sequential_ms = elapsed_ms(t0);

    const std::size_t workers = cores == 0 ? 2 : cores;
    const std::size_t chunks = workers * 4;  // more slices than threads: evens out uneven chunk costs
    double pooled_ms = 0;
    WordCounts pooled;
    {
        ThreadPool pool(workers);
        t0 = Clock::now();
        const std::vector<std::string_view> slices = split_on_boundaries(text, chunks);
        std::vector<std::future<WordCounts>> parts;
        for (std::string_view s : slices) parts.push_back(pool.submit(count_words, s));
        for (auto& part : parts) {
            for (const auto& [word, n] : part.get()) pooled[word] += n;  // merge on the calling thread
        }
        pooled_ms = elapsed_ms(t0);
        std::printf("pool: %zu worker threads, text cut into %zu slices\n", pool.thread_count(), slices.size());
    }

    const bool equal = sequential == pooled;
    std::size_t total = 0;
    for (const auto& kv : pooled) total += kv.second;
    std::printf("CORRECTNESS: sequential result == pooled result : %s\n", equal ? "yes" : "NO (BUG)");
    std::printf("total words counted = %zu (expected %zu), distinct words = %zu\n", total, word_count, pooled.size());

    std::vector<std::pair<std::string_view, std::size_t>> top(pooled.begin(), pooled.end());
    std::sort(top.begin(), top.end(), [](const auto& a, const auto& b) { return a.second != b.second ? a.second > b.second : a.first < b.first; });
    std::printf("top 3 words:");
    for (std::size_t i = 0; i < 3 && i < top.size(); ++i) std::printf(" %.*s=%zu", static_cast<int>(top[i].first.size()), top[i].first.data(), top[i].second);
    std::printf("\n");

    std::printf("MEASUREMENT (varies per machine and per run, not a result): sequential = %.1f ms, pooled = %.1f ms\n", sequential_ms, pooled_ms);
    if (pooled_ms > 0) {
        std::printf("MEASUREMENT: sequential/pooled time ratio on this run = %.2f (%u hardware threads reported)\n", sequential_ms / pooled_ms, cores);
    }
    return equal && total == word_count ? 0 : 1;
}
