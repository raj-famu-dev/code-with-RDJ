// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// LinkedList<T>: a doubly linked list written from scratch (the idea behind std::list / Java's LinkedList).
// Every element lives in its own heap node (new / delete) holding `prev` and `next` pointers.
//
//   push_front / push_back / pop_front / pop_back   O(1)
//   insert / erase at an iterator                   O(1)  (finding the iterator is the O(n) part)
//   reverse                                         O(n), relinks nodes, never moves or copies a T
//   no operator[]: reaching the i-th element means walking i links
//
// Iterators stay valid when OTHER elements are inserted or erased (only the erased element's iterator dies).
// Rule of five is written out. Cleanup is a loop (not recursion), so a million-node list cannot overflow the stack.
#pragma once

#include <cstddef>
#include <initializer_list>
#include <iterator>
#include <type_traits>
#include <utility>

template <class T>
class LinkedList {
    struct Node {
        T value;
        Node* prev;
        Node* next;
        template <class... Args>
        Node(Node* p, Node* n, Args&&... args) : value(std::forward<Args>(args)...), prev(p), next(n) {}
    };

    template <bool Const>
    class Iter {
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = std::conditional_t<Const, const T*, T*>;
        using reference = std::conditional_t<Const, const T&, T&>;

        Iter() = default;

        // iterator -> const_iterator conversion only (never the other way)
        template <bool OtherConst>
            requires(Const && !OtherConst)
        Iter(const Iter<OtherConst>& other) : list_(other.list_), node_(other.node_) {}

        reference operator*() const { return node_->value; }
        pointer operator->() const { return &node_->value; }

        Iter& operator++() {
            node_ = node_->next;
            return *this;
        }
        Iter operator++(int) {
            Iter before = *this;
            node_ = node_->next;
            return before;
        }
        Iter& operator--() {
            node_ = node_ != nullptr ? node_->prev : list_->tail_;  // --end() is the last element
            return *this;
        }
        Iter operator--(int) {
            Iter before = *this;
            --*this;
            return before;
        }

        friend bool operator==(const Iter& a, const Iter& b) { return a.node_ == b.node_; }

    private:
        friend class LinkedList;
        template <bool>
        friend class Iter;
        Iter(const LinkedList* list, Node* node) : list_(list), node_(node) {}

        const LinkedList* list_ = nullptr;
        Node* node_ = nullptr;  // nullptr means end()
    };

public:
    using value_type = T;
    using size_type = std::size_t;
    using iterator = Iter<false>;
    using const_iterator = Iter<true>;

    LinkedList() noexcept = default;

    LinkedList(std::initializer_list<T> init) : LinkedList() {
        for (const T& v : init) push_back(v);
    }

    LinkedList(const LinkedList& other) : LinkedList() {
        for (const T& v : other) push_back(v);
    }

    LinkedList(LinkedList&& other) noexcept
        : head_(std::exchange(other.head_, nullptr)),
          tail_(std::exchange(other.tail_, nullptr)),
          size_(std::exchange(other.size_, 0)) {}

    LinkedList& operator=(const LinkedList& other) {
        if (this != &other) {
            LinkedList copy(other);
            swap(copy);
        }
        return *this;
    }

    LinkedList& operator=(LinkedList&& other) noexcept {
        if (this != &other) {
            LinkedList taken(std::move(other));
            swap(taken);
        }
        return *this;
    }

    ~LinkedList() { clear(); }

    // ----- access / size -----
    T& front() noexcept { return head_->value; }
    const T& front() const noexcept { return head_->value; }
    T& back() noexcept { return tail_->value; }
    const T& back() const noexcept { return tail_->value; }
    size_type size() const noexcept { return size_; }
    bool empty() const noexcept { return size_ == 0; }

    // ----- modifiers -----
    template <class... Args>
    T& emplace_back(Args&&... args) {
        Node* node = new Node(tail_, nullptr, std::forward<Args>(args)...);  // if T's ctor throws, `new` frees the memory
        if (tail_ != nullptr) tail_->next = node;
        else head_ = node;
        tail_ = node;
        ++size_;
        return node->value;
    }

    template <class... Args>
    T& emplace_front(Args&&... args) {
        Node* node = new Node(nullptr, head_, std::forward<Args>(args)...);
        if (head_ != nullptr) head_->prev = node;
        else tail_ = node;
        head_ = node;
        ++size_;
        return node->value;
    }

    void push_back(const T& v) { emplace_back(v); }
    void push_back(T&& v) { emplace_back(std::move(v)); }
    void push_front(const T& v) { emplace_front(v); }
    void push_front(T&& v) { emplace_front(std::move(v)); }

    void pop_front() noexcept { unlink(head_); }
    void pop_back() noexcept { unlink(tail_); }

    // Insert BEFORE `pos` (pos == end() appends). Returns an iterator to the new element.
    iterator insert(const_iterator pos, T value) {
        if (pos.node_ == nullptr) {
            emplace_back(std::move(value));
            return iterator(this, tail_);
        }
        Node* next = pos.node_;
        Node* node = new Node(next->prev, next, std::move(value));
        if (next->prev != nullptr) next->prev->next = node;
        else head_ = node;
        next->prev = node;
        ++size_;
        return iterator(this, node);
    }

    // Erase the element at `pos` (must not be end()). Returns the iterator that followed it.
    iterator erase(const_iterator pos) noexcept {
        Node* after = pos.node_->next;
        unlink(pos.node_);
        return iterator(this, after);
    }

    void clear() noexcept {
        Node* n = head_;
        while (n != nullptr) {
            Node* next = n->next;  // save BEFORE deleting: after delete, n->next is a dangling read
            delete n;
            n = next;
        }
        head_ = tail_ = nullptr;
        size_ = 0;
    }

    // Swap prev/next in every node, then swap head and tail. No T is touched.
    void reverse() noexcept {
        for (Node* n = head_; n != nullptr; n = n->prev) std::swap(n->prev, n->next);  // after the swap, prev == old next
        std::swap(head_, tail_);
    }

    void swap(LinkedList& other) noexcept {
        std::swap(head_, other.head_);
        std::swap(tail_, other.tail_);
        std::swap(size_, other.size_);
    }

    // ----- iteration -----
    iterator begin() noexcept { return iterator(this, head_); }
    iterator end() noexcept { return iterator(this, nullptr); }
    const_iterator begin() const noexcept { return const_iterator(this, head_); }
    const_iterator end() const noexcept { return const_iterator(this, nullptr); }
    const_iterator cbegin() const noexcept { return begin(); }
    const_iterator cend() const noexcept { return end(); }

    friend bool operator==(const LinkedList& a, const LinkedList& b) {
        if (a.size_ != b.size_) return false;
        for (Node *x = a.head_, *y = b.head_; x != nullptr; x = x->next, y = y->next) {
            if (!(x->value == y->value)) return false;
        }
        return true;
    }

private:
    void unlink(Node* node) noexcept {
        if (node->prev != nullptr) node->prev->next = node->next;
        else head_ = node->next;
        if (node->next != nullptr) node->next->prev = node->prev;
        else tail_ = node->prev;
        delete node;
        --size_;
    }

    Node* head_ = nullptr;
    Node* tail_ = nullptr;
    size_type size_ = 0;
};
