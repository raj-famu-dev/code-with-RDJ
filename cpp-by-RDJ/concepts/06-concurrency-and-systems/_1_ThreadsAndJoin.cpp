// Tags: #Cpp #Concurrency #SystemsProgramming #ThreadsJoin | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * std::thread basics: starting threads, join, the "forgot to join" trap
 * (std::terminate), detach and its dangers, passing arguments (by-reference
 * needs std::ref), and std::jthread which joins automatically.
 * Compile with -pthread.
 */
#include <atomic>
#include <chrono>
#include <iostream>
#include <mutex>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

std::mutex print_mutex;  // so threads do not interleave characters on stdout

void say(const std::string& text) {
    std::lock_guard<std::mutex> lock(print_mutex);
    std::cout << text << "\n";
}

void add_to(int& target, int amount) { target += amount; }

void fill_square(std::vector<int>& out, std::size_t index) { out[index] = static_cast<int>(index * index); }

int main(int argc, char** argv) {
    // ===== SECTION 1: START AND JOIN =====
    std::cout << "===== SECTION 1: START AND JOIN =====\n";
    std::thread t([] { say("hello from a worker thread"); });
    std::cout << "joinable before join: " << std::boolalpha << t.joinable() << "\n";
    t.join();  // wait for the thread to finish
    std::cout << "joinable after join:  " << t.joinable() << "\n";
    std::cout << "hardware_concurrency is machine-specific, so not printed; calling it returns a hint only.\n";

    // ===== SECTION 2: MANY THREADS, DETERMINISTIC RESULT =====
    std::cout << "===== SECTION 2: MANY THREADS, DETERMINISTIC RESULT =====\n";
    std::vector<int> squares(8, -1);
    {
        std::vector<std::thread> pool;
        for (std::size_t i = 0; i < squares.size(); ++i) {
            // each thread writes ONLY its own element: no sharing, so no race
            pool.emplace_back(fill_square, std::ref(squares), i);
        }
        for (auto& th : pool) th.join();
    }
    std::cout << "squares:";
    for (int s : squares) std::cout << " " << s;
    std::cout << "\n";

    // ===== SECTION 3: PASSING ARGUMENTS, std::ref TRAP =====
    std::cout << "===== SECTION 3: PASSING ARGUMENTS, std::ref TRAP =====\n";
    int total = 0;
    // TRAP: std::thread COPIES its arguments. A plain 'add_to, total, 5' will not even compile
    // because the copy is an rvalue that cannot bind to int&. Wrap with std::ref to share the real variable.
    std::thread byref(add_to, std::ref(total), 5);
    byref.join();
    std::cout << "with std::ref the original changed: total = " << total << "\n";
    int copy_target = 0;
    std::thread bylambda([copy_target]() mutable { copy_target += 5; });  // captured by value: a private copy
    bylambda.join();
    std::cout << "by-value capture changes only the thread's own copy: copy_target = " << copy_target << "\n";
    std::string message = "moved into the thread";
    std::thread mover([m = std::move(message)] { say(m); });
    mover.join();
    std::cout << "message after being moved into the lambda has size " << message.size() << " (moved-from)\n";

    // ===== SECTION 4: FORGOT TO JOIN (opt-in) =====
    std::cout << "===== SECTION 4: FORGOT TO JOIN (opt-in) =====\n";
    std::cout << "Destroying a joinable std::thread calls std::terminate (the program aborts).\n";
    if (argc > 1 && std::string_view(argv[1]) == "--forget-join") {
        std::cout << "starting a thread and leaving scope without join(); expect abort (exit code 134)...\n" << std::flush;
        std::thread forgot([] {});
        // no join, no detach: ~thread() terminates the program
    } else {
        std::cout << "(skipped; run with --forget-join to see it)\n";
    }

    // ===== SECTION 5: DETACH =====
    std::cout << "===== SECTION 5: DETACH =====\n";
    std::atomic<bool> detached_done{false};
    std::thread bg([&detached_done] {
        detached_done = true;  // touches a variable owned by main: only safe because main waits below
    });
    bg.detach();  // bg is no longer joinable; nobody can wait for it through the thread object
    std::cout << "joinable after detach: " << bg.joinable() << "\n";
    while (!detached_done) std::this_thread::sleep_for(std::chrono::milliseconds(1));
    std::cout << "main waited using an atomic flag; detached thread finished.\n";
    std::cout << "TRAP: if main (or the function owning the variables) returns while a detached thread still uses them,\n"
                 "      the thread touches destroyed memory. Prefer join, or jthread, over detach.\n";

    // ===== SECTION 6: std::jthread =====
    std::cout << "===== SECTION 6: std::jthread =====\n";
    int jt_value = 0;
    {
        std::jthread jt([&jt_value] { jt_value = 42; });
        // no join() call: the jthread destructor joins when the scope ends (no terminate)
    }
    std::cout << "after the scope ended, the jthread had finished and set jt_value = " << jt_value << "\n";
    {
        std::jthread stoppable([](std::stop_token st) {
            while (!st.stop_requested()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
            say("stoppable jthread saw the stop request and exited cleanly");
        });
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        stoppable.request_stop();  // cooperative cancellation
    }
    std::cout << "jthread = thread + automatic join + cooperative stop_token.\n";
    return 0;
}
