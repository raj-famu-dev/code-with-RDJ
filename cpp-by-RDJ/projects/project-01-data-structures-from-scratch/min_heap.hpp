// Tags: #Cpp #Project #DataStructures #MinHeap | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// MinHeap<T, Less>: a binary min-heap (a priority queue whose top() is the SMALLEST element), from scratch.
// The tree lives in a plain array (our own DynamicArray, not a standard container):
//   parent(i) = (i - 1) / 2     left(i) = 2i + 1     right(i) = 2i + 2
// Heap property: no child is smaller than its parent. The root (index 0) is therefore the minimum.
//
//   push    O(log n)  append at the end, then SIFT UP while smaller than the parent
//   pop     O(log n)  move the last element to the root, then SIFT DOWN toward the smaller child
//   top     O(1)
//   build from n items   O(n)  (heapify: sift down every non-leaf, last to first)
//
// `Less` is the ordering: the element for which Less says "smaller than everything else" is on top.
// With std::greater<T> you get a MAX-heap. The heap copies and moves like DynamicArray (rule of zero).
#pragma once

#include <cstddef>
#include <functional>
#include <initializer_list>
#include <stdexcept>
#include <utility>

#include "dynamic_array.hpp"

template <class T, class Less = std::less<T>>
class MinHeap {
public:
    using value_type = T;
    using size_type = std::size_t;

    MinHeap() = default;
    explicit MinHeap(Less less) : less_(std::move(less)) {}

    // Heapify: O(n), cheaper than n separate pushes (O(n log n)).
    MinHeap(std::initializer_list<T> items, Less less = Less()) : less_(std::move(less)) {
        for (const T& v : items) items_.push_back(v);
        build();
    }
    explicit MinHeap(DynamicArray<T> items, Less less = Less()) : items_(std::move(items)), less_(std::move(less)) { build(); }

    size_type size() const noexcept { return items_.size(); }
    bool empty() const noexcept { return items_.empty(); }
    void clear() noexcept { items_.clear(); }

    const T& top() const {
        if (items_.empty()) throw std::out_of_range("MinHeap::top: heap is empty");
        return items_[0];
    }

    void push(T value) {
        items_.push_back(std::move(value));
        sift_up(items_.size() - 1);
    }

    template <class... Args>
    void emplace(Args&&... args) {
        push(T(std::forward<Args>(args)...));
    }

    // Remove and return the smallest element.
    T pop() {
        if (items_.empty()) throw std::out_of_range("MinHeap::pop: heap is empty");
        T smallest = std::move(items_[0]);
        if (items_.size() > 1) items_[0] = std::move(items_.back());
        items_.pop_back();
        if (!items_.empty()) sift_down(0);
        return smallest;
    }

private:
    void build() {
        // Indices n/2 .. n-1 are leaves (already valid heaps of one element); fix the rest bottom-up.
        for (size_type i = items_.size() / 2; i-- > 0;) sift_down(i);
    }

    void sift_up(size_type i) {
        while (i > 0) {
            const size_type parent = (i - 1) / 2;
            if (!less_(items_[i], items_[parent])) break;
            std::swap(items_[i], items_[parent]);
            i = parent;
        }
    }

    void sift_down(size_type i) {
        const size_type n = items_.size();
        for (;;) {
            const size_type left = 2 * i + 1;
            const size_type right = left + 1;
            size_type smallest = i;
            if (left < n && less_(items_[left], items_[smallest])) smallest = left;
            if (right < n && less_(items_[right], items_[smallest])) smallest = right;
            if (smallest == i) return;
            std::swap(items_[i], items_[smallest]);
            i = smallest;
        }
    }

    DynamicArray<T> items_;
    Less less_{};
};
