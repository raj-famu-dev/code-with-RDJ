// Tags: #Cpp #Project #DataStructures #DynamicArray | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DynamicArray<T>: a growable array written from scratch (the idea behind std::vector / Java's ArrayList).
// Storage comes ONLY from std::allocator<T> (raw, uninitialised memory); elements are built with
// std::construct_at and destroyed with std::destroy_at. No standard container is used inside.
//
//   size()      how many elements are alive       capacity()  how many fit before the next reallocation
//   growth      capacity doubles (4, 8, 16, ...)  => push_back is O(1) AMORTISED
//   push_back   O(1) amortised     insert/erase at an index  O(n)     operator[]  O(1)
//
// Rule of five: destructor, copy ctor, copy assign, move ctor, move assign are all written explicitly.
// Reallocation uses std::move_if_noexcept: elements are MOVED if their move constructor is noexcept,
// otherwise COPIED, so that a throwing move cannot leave the array half-relocated (strong guarantee).
#pragma once

#include <cstddef>
#include <initializer_list>
#include <memory>
#include <stdexcept>
#include <utility>

template <class T>
class DynamicArray {
public:
    using value_type = T;
    using size_type = std::size_t;
    using iterator = T*;
    using const_iterator = const T*;

    DynamicArray() noexcept = default;

    DynamicArray(std::initializer_list<T> init) : DynamicArray() {
        reserve(init.size());
        for (const T& v : init) emplace_back(v);
    }

    // Copy: deep copy. Delegating to the default ctor first means the destructor runs if a copy throws.
    DynamicArray(const DynamicArray& other) : DynamicArray() {
        reserve(other.size_);
        for (size_type i = 0; i < other.size_; ++i) emplace_back(other.data_[i]);
    }

    // Move: steal the buffer; the source becomes a valid empty array.
    DynamicArray(DynamicArray&& other) noexcept
        : data_(std::exchange(other.data_, nullptr)),
          size_(std::exchange(other.size_, 0)),
          capacity_(std::exchange(other.capacity_, 0)),
          reallocations_(std::exchange(other.reallocations_, 0)) {}

    DynamicArray& operator=(const DynamicArray& other) {
        if (this != &other) {
            DynamicArray copy(other);  // may throw: *this is untouched if it does
            swap(copy);
        }
        return *this;
    }

    DynamicArray& operator=(DynamicArray&& other) noexcept {
        if (this != &other) {
            DynamicArray taken(std::move(other));
            swap(taken);  // our old buffer is released when `taken` dies
        }
        return *this;
    }

    ~DynamicArray() { release(); }

    // ----- element access -----
    T& operator[](size_type i) noexcept { return data_[i]; }
    const T& operator[](size_type i) const noexcept { return data_[i]; }

    T& at(size_type i) {
        if (i >= size_) throw std::out_of_range("DynamicArray::at: index out of range");
        return data_[i];
    }
    const T& at(size_type i) const {
        if (i >= size_) throw std::out_of_range("DynamicArray::at: index out of range");
        return data_[i];
    }

    T& front() noexcept { return data_[0]; }
    const T& front() const noexcept { return data_[0]; }
    T& back() noexcept { return data_[size_ - 1]; }
    const T& back() const noexcept { return data_[size_ - 1]; }
    T* data() noexcept { return data_; }
    const T* data() const noexcept { return data_; }

    // ----- size -----
    size_type size() const noexcept { return size_; }
    size_type capacity() const noexcept { return capacity_; }
    bool empty() const noexcept { return size_ == 0; }
    size_type reallocation_count() const noexcept { return reallocations_; }

    // ----- modifiers -----
    void reserve(size_type wanted) {
        if (wanted > capacity_) adopt(allocate_checked(wanted), wanted, false);
    }

    template <class... Args>
    T& emplace_back(Args&&... args) {
        if (size_ == capacity_) {
            const size_type new_cap = capacity_ == 0 ? 4 : capacity_ * 2;
            T* fresh = allocate_checked(new_cap);
            // Build the NEW element first: `args` may refer to an element of this very array
            // (a.push_back(a[0])) and relocation would invalidate that reference.
            try {
                std::construct_at(fresh + size_, std::forward<Args>(args)...);
            } catch (...) {
                alloc_.deallocate(fresh, new_cap);
                throw;
            }
            adopt(fresh, new_cap, true);
        } else {
            std::construct_at(data_ + size_, std::forward<Args>(args)...);
        }
        ++size_;
        return data_[size_ - 1];
    }

    void push_back(const T& value) { emplace_back(value); }
    void push_back(T&& value) { emplace_back(std::move(value)); }

    void pop_back() noexcept {
        --size_;
        std::destroy_at(data_ + size_);
    }

    // Insert before position `index` (index == size() appends). Shifts the tail right: O(n).
    void insert(size_type index, T value) {
        if (index > size_) throw std::out_of_range("DynamicArray::insert: index out of range");
        if (index == size_) {
            emplace_back(std::move(value));
            return;
        }
        emplace_back(std::move(data_[size_ - 1]));  // new last slot, built from the old last element
        for (size_type i = size_ - 2; i > index; --i) data_[i] = std::move(data_[i - 1]);  // shift the tail right by one
        data_[index] = std::move(value);
    }

    // Remove the element at `index`, shifting the tail left: O(n).
    void erase(size_type index) {
        if (index >= size_) throw std::out_of_range("DynamicArray::erase: index out of range");
        for (size_type i = index; i + 1 < size_; ++i) data_[i] = std::move(data_[i + 1]);
        pop_back();
    }

    void clear() noexcept {
        while (size_ > 0) pop_back();
    }

    void swap(DynamicArray& other) noexcept {
        std::swap(data_, other.data_);
        std::swap(size_, other.size_);
        std::swap(capacity_, other.capacity_);
        std::swap(reallocations_, other.reallocations_);
    }

    // ----- iteration (plain pointers are valid random-access iterators) -----
    iterator begin() noexcept { return data_; }
    iterator end() noexcept { return data_ + size_; }
    const_iterator begin() const noexcept { return data_; }
    const_iterator end() const noexcept { return data_ + size_; }
    const_iterator cbegin() const noexcept { return data_; }
    const_iterator cend() const noexcept { return data_ + size_; }

    friend bool operator==(const DynamicArray& a, const DynamicArray& b) {
        if (a.size_ != b.size_) return false;
        for (size_type i = 0; i < a.size_; ++i) {
            if (!(a.data_[i] == b.data_[i])) return false;
        }
        return true;
    }

private:
    T* allocate_checked(size_type n) { return alloc_.allocate(n); }  // throws std::bad_alloc / length_error

    // Move (or copy, see header comment) the live elements into `fresh`, then make `fresh` the buffer.
    // `has_extra`: fresh[size_] already holds a newly built element that must be destroyed on failure.
    void adopt(T* fresh, size_type new_cap, bool has_extra) {
        size_type built = 0;
        try {
            for (; built < size_; ++built) std::construct_at(fresh + built, std::move_if_noexcept(data_[built]));
        } catch (...) {
            for (size_type i = 0; i < built; ++i) std::destroy_at(fresh + i);
            if (has_extra) std::destroy_at(fresh + size_);
            alloc_.deallocate(fresh, new_cap);
            throw;  // *this is unchanged: the strong guarantee
        }
        release();  // destroys old elements, frees old buffer; keeps size_ for us below
        data_ = fresh;
        capacity_ = new_cap;
        size_ = built;
        ++reallocations_;
    }

    // Destroy every element and free the buffer (size_ is preserved only because adopt() resets it).
    void release() noexcept {
        for (size_type i = 0; i < size_; ++i) std::destroy_at(data_ + i);
        if (data_ != nullptr) alloc_.deallocate(data_, capacity_);
        data_ = nullptr;
        capacity_ = 0;
        size_ = 0;
    }

    T* data_ = nullptr;
    size_type size_ = 0;
    size_type capacity_ = 0;
    size_type reallocations_ = 0;
    [[no_unique_address]] std::allocator<T> alloc_;
};
