// Tags: #Cpp #Concurrency #SystemsProgramming #LoopbackSocketsPosix | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * POSIX sockets on the loopback interface only (127.0.0.1): a TCP echo server
 * and client in ONE process, binding to port 0 so the OS picks a free port,
 * getsockname() to learn it, SO_RCVTIMEO receive timeouts, shutdown() vs
 * close(), and TCP's "byte stream, not messages" behaviour.
 * Nothing here ever leaves this machine. Compile with -pthread.
 */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <future>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>

// RAII wrapper: a file descriptor that is closed exactly once.
class Fd {
public:
    Fd() = default;
    explicit Fd(int fd) : fd_(fd) {}
    ~Fd() { reset(); }
    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;
    Fd(Fd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    Fd& operator=(Fd&& o) noexcept {
        if (this != &o) {
            reset();
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    int get() const { return fd_; }
    void reset() {
        if (fd_ >= 0) ::close(fd_);
        fd_ = -1;
    }

private:
    int fd_ = -1;
};

[[noreturn]] void fail(const std::string& what) { throw std::runtime_error(what + ": " + std::strerror(errno)); }

// Create a listening socket on 127.0.0.1, port 0 (the OS picks a free port). Returns the socket and the port.
std::pair<Fd, unsigned short> make_listener() {
    Fd s(::socket(AF_INET, SOCK_STREAM, 0));
    if (s.get() < 0) fail("socket");
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);  // 127.0.0.1 ONLY: not reachable from other machines
    addr.sin_port = htons(0);                       // 0 = "any free port"
    if (::bind(s.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) fail("bind");
    if (::listen(s.get(), 8) < 0) fail("listen");
    sockaddr_in bound{};
    socklen_t len = sizeof(bound);
    if (::getsockname(s.get(), reinterpret_cast<sockaddr*>(&bound), &len) < 0) fail("getsockname");
    return {std::move(s), ntohs(bound.sin_port)};
}

Fd connect_to(unsigned short port) {
    Fd c(::socket(AF_INET, SOCK_STREAM, 0));
    if (c.get() < 0) fail("socket");
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    if (::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr) != 1) fail("inet_pton");
    if (::connect(c.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) fail("connect");
    return c;
}

// send() may write fewer bytes than asked: loop until everything is sent.
void send_all(int fd, const std::string& data) {
    std::size_t sent = 0;
    while (sent < data.size()) {
        ssize_t n = ::send(fd, data.data() + sent, data.size() - sent, MSG_NOSIGNAL);  // no SIGPIPE if peer closed
        if (n < 0) {
            if (errno == EINTR) continue;
            fail("send");
        }
        sent += static_cast<std::size_t>(n);
    }
}

// Read until exactly 'count' bytes arrived, or the peer closed (returns what it got).
std::string recv_exact(int fd, std::size_t count) {
    std::string out;
    char buf[256];
    while (out.size() < count) {
        ssize_t n = ::recv(fd, buf, std::min(sizeof(buf), count - out.size()), 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            fail("recv");
        }
        if (n == 0) break;  // 0 means the peer closed its sending side
        out.append(buf, static_cast<std::size_t>(n));
    }
    return out;
}

// Read until the peer shuts down its sending side (EOF).
std::string recv_until_eof(int fd) {
    std::string out;
    char buf[256];
    for (;;) {
        ssize_t n = ::recv(fd, buf, sizeof(buf), 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            fail("recv");
        }
        if (n == 0) return out;
        out.append(buf, static_cast<std::size_t>(n));
    }
}

// The echo server: accepts 'connections' clients one after another and echoes every byte back until each hangs up.
// Returns an error message ("" on success) so the main thread can report it.
std::string run_echo_server(Fd& listener, int connections) {
    try {
        for (int i = 0; i < connections; ++i) {
            Fd client(::accept(listener.get(), nullptr, nullptr));
            if (client.get() < 0) fail("accept");
            char buf[256];
            for (;;) {
                ssize_t n = ::recv(client.get(), buf, sizeof(buf), 0);
                if (n < 0) {
                    if (errno == EINTR) continue;
                    fail("server recv");
                }
                if (n == 0) break;  // client finished sending
                send_all(client.get(), std::string(buf, static_cast<std::size_t>(n)));
            }
            // 'client' goes out of scope: close() is called by the Fd destructor
        }
        return "";
    } catch (const std::exception& e) {
        return e.what();
    }
}

int main() {
    std::cout << std::boolalpha;
    // ===== SECTION 1: LISTEN ON PORT 0 AND LEARN THE PORT =====
    std::cout << "===== SECTION 1: LISTEN ON PORT 0 AND LEARN THE PORT =====\n";
    auto [listener, port] = make_listener();
    std::cout << "bound to 127.0.0.1 with port 0; the OS chose a port; getsockname says it is nonzero: " << (port != 0) << "\n";
    std::cout << "(the actual port number differs every run, so it is not printed)\n";

    // The server runs in a second thread of THIS process; connections stay on the loopback interface.
    std::future<std::string> server_result = std::async(std::launch::async, run_echo_server, std::ref(listener), 2);

    // ===== SECTION 2: ECHO ROUND TRIP =====
    std::cout << "===== SECTION 2: ECHO ROUND TRIP =====\n";
    {
        Fd client = connect_to(port);
        for (const std::string msg : {"hello", "second message", "RDJ"}) {
            send_all(client.get(), msg);
            std::string echoed = recv_exact(client.get(), msg.size());
            std::cout << "sent \"" << msg << "\" -> echoed \"" << echoed << "\" matches: " << (echoed == msg) << "\n";
        }
        ::shutdown(client.get(), SHUT_WR);  // tell the server we are done sending
        std::cout << "after shutdown(SHUT_WR), recv returns EOF: " << recv_until_eof(client.get()).empty() << "\n";
    }  // client closed here by RAII

    // ===== SECTION 3: TCP IS A BYTE STREAM, NOT MESSAGES =====
    std::cout << "===== SECTION 3: TCP IS A BYTE STREAM, NOT MESSAGES =====\n";
    {
        Fd client = connect_to(port);
        send_all(client.get(), "AAAA");  // three separate send() calls...
        send_all(client.get(), "BBBB");
        send_all(client.get(), "CCCC");
        ::shutdown(client.get(), SHUT_WR);
        std::string all = recv_until_eof(client.get());  // ...read back as one continuous stream
        std::cout << "3 sends of 4 bytes came back as a stream of " << all.size() << " bytes: " << all << "\n";
        std::cout << "TRAP: one recv() is NOT one send(). Message boundaries are not preserved, so real protocols add a\n"
                     "      length prefix or a delimiter, and loops like recv_exact() / send_all() handle partial reads and writes.\n";
    }
    std::string server_error = server_result.get();  // the server handled its 2 connections and returned
    std::cout << "echo server finished both connections; error: \"" << server_error << "\"\n";

    // ===== SECTION 4: RECEIVE TIMEOUT WITH SO_RCVTIMEO =====
    std::cout << "===== SECTION 4: RECEIVE TIMEOUT WITH SO_RCVTIMEO =====\n";
    {
        auto [silent, silent_port] = make_listener();  // listens, but never accept()s or sends anything
        Fd client = connect_to(silent_port);           // the kernel completes the handshake from the backlog
        timeval tv{};
        tv.tv_sec = 0;
        tv.tv_usec = 150 * 1000;  // 150 ms
        if (::setsockopt(client.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) fail("setsockopt");
        char buf[16];
        ssize_t n = ::recv(client.get(), buf, sizeof(buf), 0);
        bool timed_out = (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK));
        std::cout << "recv() on a silent peer with a 150 ms timeout returned -1 with EAGAIN/EWOULDBLOCK: " << timed_out << "\n";
        std::cout << "(without SO_RCVTIMEO this recv() would block forever)\n";
    }

    // ===== SECTION 5: CONNECTION REFUSED AND close() =====
    std::cout << "===== SECTION 5: CONNECTION REFUSED AND close() =====\n";
    {
        unsigned short dead_port = 0;
        {
            auto [temp, p] = make_listener();
            dead_port = p;
        }  // listener closed here, so nothing listens on dead_port any more
        try {
            Fd c = connect_to(dead_port);
            std::cout << "unexpectedly connected\n";
        } catch (const std::runtime_error& e) {
            std::cout << "connecting to a closed loopback port failed: " << e.what() << "\n";
        }
    }
    std::cout << "close(fd) releases the descriptor; shutdown(fd, how) ends one or both directions but keeps the fd open.\n"
                 "TRAP: forgetting close() leaks descriptors (a process only gets a limited number); the Fd class prevents it.\n"
                 "TRAP: writing to a socket the peer already closed raises SIGPIPE and kills the process; MSG_NOSIGNAL turns it into an EPIPE error.\n";
    return 0;
}
