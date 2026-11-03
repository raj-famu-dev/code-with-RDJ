// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// HashMap<K, V, Hash, KeyEqual>: a hash table with SEPARATE CHAINING, written from scratch
// (the idea behind std::unordered_map / Java's HashMap; see java-by-RDJ 14-dsa-in-java/_4_HashMapWithChaining).
//
//   buckets_   an array of Node* (from std::allocator); each slot is the head of a singly linked chain
//   index      mix(hash(key)) & (bucket_count - 1)   (bucket_count is always a power of two)
//   rehash     when (size + 1) / bucket_count would exceed 0.75, the bucket array DOUBLES and every node is
//              relinked into the new array (nodes are NOT reallocated, so references to elements stay valid;
//              iterators do not, exactly as with std::unordered_map)
//
//   find / insert / erase / operator[]   O(1) on average, O(n) worst case (every key in one chain)
//   iteration                            O(bucket_count + size), in bucket order (NOT insertion order)
//
// Rule of five is written out. Iterators are forward iterators (iterator and const_iterator).
// Only std::allocator, new and delete are used for memory: no standard container is used inside.
#pragma once

#include <algorithm>
#include <cstddef>
#include <functional>
#include <iterator>
#include <memory>
#include <stdexcept>
#include <tuple>
#include <type_traits>
#include <utility>

template <class K, class V, class Hash = std::hash<K>, class KeyEqual = std::equal_to<K>>
class HashMap {
    struct Node {
        std::pair<const K, V> kv;
        std::size_t hash;
        Node* next;
        template <class... Args>
        Node(std::size_t h, Node* n, Args&&... args) : kv(std::forward<Args>(args)...), hash(h), next(n) {}
    };

    template <bool Const>
    class Iter {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = std::pair<const K, V>;
        using difference_type = std::ptrdiff_t;
        using pointer = std::conditional_t<Const, const value_type*, value_type*>;
        using reference = std::conditional_t<Const, const value_type&, value_type&>;

        Iter() = default;

        template <bool OtherConst>
            requires(Const && !OtherConst)
        Iter(const Iter<OtherConst>& other) : map_(other.map_), node_(other.node_) {}

        reference operator*() const { return node_->kv; }
        pointer operator->() const { return &node_->kv; }

        Iter& operator++() {
            advance();
            return *this;
        }
        Iter operator++(int) {
            Iter before = *this;
            advance();
            return before;
        }

        friend bool operator==(const Iter& a, const Iter& b) { return a.node_ == b.node_; }

    private:
        friend class HashMap;
        template <bool>
        friend class Iter;
        Iter(const HashMap* map, Node* node) : map_(map), node_(node) {}

        // Next node in the same chain, else the head of the next non-empty bucket, else end().
        void advance() {
            if (node_->next != nullptr) {
                node_ = node_->next;
                return;
            }
            std::size_t b = (node_->hash & (map_->bucket_count_ - 1)) + 1;
            node_ = nullptr;
            for (; b < map_->bucket_count_; ++b) {
                if (map_->buckets_[b] != nullptr) {
                    node_ = map_->buckets_[b];
                    return;
                }
            }
        }

        const HashMap* map_ = nullptr;
        Node* node_ = nullptr;  // nullptr means end()
    };

public:
    using key_type = K;
    using mapped_type = V;
    using value_type = std::pair<const K, V>;
    using size_type = std::size_t;
    using iterator = Iter<false>;
    using const_iterator = Iter<true>;

    HashMap() = default;  // allocates nothing until the first insert

    explicit HashMap(const Hash& hash, const KeyEqual& eq = KeyEqual()) : hash_(hash), eq_(eq) {}

    HashMap(const HashMap& other) : HashMap(other.hash_, other.eq_) {
        reserve(other.size_);
        for (const value_type& kv : other) insert(kv.first, kv.second);
    }

    HashMap(HashMap&& other) noexcept
        : buckets_(std::exchange(other.buckets_, nullptr)),
          bucket_count_(std::exchange(other.bucket_count_, 0)),
          size_(std::exchange(other.size_, 0)),
          rehashes_(std::exchange(other.rehashes_, 0)),
          hash_(std::move(other.hash_)),
          eq_(std::move(other.eq_)) {}

    HashMap& operator=(const HashMap& other) {
        if (this != &other) {
            HashMap copy(other);
            swap(copy);
        }
        return *this;
    }

    HashMap& operator=(HashMap&& other) noexcept {
        if (this != &other) {
            HashMap taken(std::move(other));
            swap(taken);
        }
        return *this;
    }

    ~HashMap() { release(); }

    // ----- size and statistics -----
    size_type size() const noexcept { return size_; }
    bool empty() const noexcept { return size_ == 0; }
    size_type bucket_count() const noexcept { return bucket_count_; }
    double load_factor() const noexcept {
        return bucket_count_ == 0 ? 0.0 : static_cast<double>(size_) / static_cast<double>(bucket_count_);
    }
    static constexpr double max_load_factor() noexcept { return 0.75; }
    size_type rehash_count() const noexcept { return rehashes_; }

    size_type bucket_size(size_type bucket) const noexcept {
        size_type n = 0;
        for (const Node* p = buckets_[bucket]; p != nullptr; p = p->next) ++n;
        return n;
    }
    size_type longest_chain() const noexcept {
        size_type longest = 0;
        for (size_type b = 0; b < bucket_count_; ++b) longest = std::max(longest, bucket_size(b));
        return longest;
    }
    size_type buckets_in_use() const noexcept {
        size_type used = 0;
        for (size_type b = 0; b < bucket_count_; ++b) used += buckets_[b] != nullptr ? 1 : 0;
        return used;
    }

    // ----- lookup -----
    iterator find(const K& key) { return iterator(this, find_node(key)); }
    const_iterator find(const K& key) const { return const_iterator(this, find_node(key)); }
    bool contains(const K& key) const { return find_node(key) != nullptr; }
    size_type count(const K& key) const { return contains(key) ? 1 : 0; }

    V& at(const K& key) {
        Node* n = find_node(key);
        if (n == nullptr) throw std::out_of_range("HashMap::at: key not found");
        return n->kv.second;
    }
    const V& at(const K& key) const {
        const Node* n = find_node(key);
        if (n == nullptr) throw std::out_of_range("HashMap::at: key not found");
        return n->kv.second;
    }

    // ----- modifiers -----
    // Insert only if the key is absent (an existing value is NOT overwritten), like std::unordered_map::insert.
    std::pair<iterator, bool> insert(K key, V value) {
        const std::size_t h = mix(hash_(key));
        if (Node* existing = find_node(key, h)) return {iterator(this, existing), false};
        grow_if_needed();
        Node* node = new Node(h, nullptr, std::move(key), std::move(value));
        link(node);
        return {iterator(this, node), true};
    }

    // Insert, or overwrite the value if the key exists. Returns true if a NEW key was added.
    bool insert_or_assign(K key, V value) {
        const std::size_t h = mix(hash_(key));
        if (Node* existing = find_node(key, h)) {
            existing->kv.second = std::move(value);
            return false;
        }
        grow_if_needed();
        link(new Node(h, nullptr, std::move(key), std::move(value)));
        return true;
    }

    // Find the value for `key`, inserting a default-constructed V first if needed.
    V& operator[](const K& key) {
        const std::size_t h = mix(hash_(key));
        if (Node* existing = find_node(key, h)) return existing->kv.second;
        grow_if_needed();
        Node* node = new Node(h, nullptr, std::piecewise_construct, std::forward_as_tuple(key), std::tuple<>());
        link(node);
        return node->kv.second;
    }

    // Remove `key`. Returns true if something was removed.
    bool erase(const K& key) {
        if (bucket_count_ == 0) return false;
        const std::size_t h = mix(hash_(key));
        Node** link_to_node = &buckets_[h & (bucket_count_ - 1)];  // pointer to the pointer that points at the node
        while (*link_to_node != nullptr) {
            Node* n = *link_to_node;
            if (n->hash == h && eq_(n->kv.first, key)) {
                *link_to_node = n->next;  // unlink (works for head and middle alike)
                delete n;
                --size_;
                return true;
            }
            link_to_node = &n->next;
        }
        return false;
    }

    void clear() noexcept {
        for (size_type b = 0; b < bucket_count_; ++b) {
            Node* n = buckets_[b];
            while (n != nullptr) {
                Node* next = n->next;
                delete n;
                n = next;
            }
            buckets_[b] = nullptr;
        }
        size_ = 0;
    }

    // Make room for `n` entries without triggering a rehash on the way.
    void reserve(size_type n) {
        size_type wanted = bucket_count_ == 0 ? kInitialBuckets : bucket_count_;
        while (n * 4 > wanted * 3) wanted *= 2;
        if (wanted > bucket_count_) rehash(wanted);
    }

    void swap(HashMap& other) noexcept {
        using std::swap;
        swap(buckets_, other.buckets_);
        swap(bucket_count_, other.bucket_count_);
        swap(size_, other.size_);
        swap(rehashes_, other.rehashes_);
        swap(hash_, other.hash_);
        swap(eq_, other.eq_);
    }

    // ----- iteration -----
    iterator begin() noexcept { return iterator(this, first_node()); }
    iterator end() noexcept { return iterator(this, nullptr); }
    const_iterator begin() const noexcept { return const_iterator(this, first_node()); }
    const_iterator end() const noexcept { return const_iterator(this, nullptr); }
    const_iterator cbegin() const noexcept { return begin(); }
    const_iterator cend() const noexcept { return end(); }

private:
    static constexpr size_type kInitialBuckets = 8;

    // Spread the bits: std::hash<int> is the identity, and a bitmask only looks at the LOW bits.
    static std::size_t mix(std::size_t h) noexcept {
        h ^= h >> 32;
        h ^= h >> 16;
        return h;
    }

    Node* find_node(const K& key) const { return find_node(key, mix(hash_(key))); }

    Node* find_node(const K& key, std::size_t h) const {
        if (bucket_count_ == 0) return nullptr;
        for (Node* n = buckets_[h & (bucket_count_ - 1)]; n != nullptr; n = n->next) {
            if (n->hash == h && eq_(n->kv.first, key)) return n;  // compare the cheap stored hash first
        }
        return nullptr;
    }

    Node* first_node() const noexcept {
        for (size_type b = 0; b < bucket_count_; ++b) {
            if (buckets_[b] != nullptr) return buckets_[b];
        }
        return nullptr;
    }

    void grow_if_needed() {
        if (bucket_count_ == 0) rehash(kInitialBuckets);
        else if ((size_ + 1) * 4 > bucket_count_ * 3) rehash(bucket_count_ * 2);
    }

    // Push `node` onto the FRONT of its chain: O(1).
    void link(Node* node) noexcept {
        Node*& head = buckets_[node->hash & (bucket_count_ - 1)];
        node->next = head;
        head = node;
        ++size_;
    }

    void rehash(size_type new_count) {
        Node** fresh = bucket_alloc_.allocate(new_count);  // may throw: nothing has changed yet
        for (size_type i = 0; i < new_count; ++i) std::construct_at(fresh + i, nullptr);
        for (size_type b = 0; b < bucket_count_; ++b) {
            Node* n = buckets_[b];
            while (n != nullptr) {
                Node* next = n->next;  // save before relinking
                Node*& head = fresh[n->hash & (new_count - 1)];
                n->next = head;  // the stored hash is reused: no need to call Hash again
                head = n;
                n = next;
            }
        }
        if (buckets_ != nullptr) bucket_alloc_.deallocate(buckets_, bucket_count_);
        buckets_ = fresh;
        bucket_count_ = new_count;
        ++rehashes_;
    }

    void release() noexcept {
        clear();
        if (buckets_ != nullptr) bucket_alloc_.deallocate(buckets_, bucket_count_);
        buckets_ = nullptr;
        bucket_count_ = 0;
    }

    Node** buckets_ = nullptr;
    size_type bucket_count_ = 0;
    size_type size_ = 0;
    size_type rehashes_ = 0;
    [[no_unique_address]] Hash hash_{};
    [[no_unique_address]] KeyEqual eq_{};
    [[no_unique_address]] std::allocator<Node*> bucket_alloc_;
};
