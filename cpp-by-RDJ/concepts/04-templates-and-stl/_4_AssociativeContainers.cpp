// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: std::map / std::set (ordered, tree-based, O(log n)), std::unordered_map /
 * std::unordered_set (hash-based, average O(1)), std::multimap (duplicate keys),
 * the ordering-vs-hashing trade-off, and the operator[] insertion trap.
 * Unordered iteration order is unspecified, so the file sorts before printing.
 */
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

int main() {
    std::cout << "===== SECTION 1: map and set (ordered) =====\n";
    std::map<std::string, int> age{{"zoe", 31}, {"adam", 25}, {"mia", 40}};
    std::cout << "map iterates in KEY order:";
    for (const auto& [name, a] : age) std::cout << " " << name << "=" << a;
    std::cout << "\n";
    std::set<int> s{5, 1, 3, 3, 1};
    std::cout << "set of {5,1,3,3,1} keeps unique sorted values:";
    for (int x : s) std::cout << " " << x;
    std::cout << "\n";
    auto lo = s.lower_bound(2);
    std::cout << "lower_bound(2) in set = " << *lo << " (first element not less than 2: possible only because it is ordered)\n";
    auto r = age.insert({"mia", 99});
    std::cout << "insert({\"mia\",99}) did insert? " << std::boolalpha << r.second << ", mia is still " << age["mia"] << " (insert does not overwrite)\n";
    age.insert_or_assign("mia", 41);
    std::cout << "insert_or_assign overwrote: mia = " << age.at("mia") << "\n";

    std::cout << "\n===== SECTION 2: the operator[] insertion trap =====\n";
    std::map<std::string, int> stock{{"apple", 3}};
    std::cout << "size before: " << stock.size() << "\n";
    int pears = stock["pear"];                 // TRAP: reading with [] INSERTS pear = 0
    std::cout << "read stock[\"pear\"] = " << pears << ", size after: " << stock.size() << " (a lookup changed the map!)\n";
    std::cout << "contains(\"kiwi\") = " << stock.contains("kiwi") << ", size still " << stock.size() << " (contains/find do not insert)\n";
    auto it = stock.find("kiwi");
    std::cout << "find(\"kiwi\") == end(): " << (it == stock.end()) << "\n";
    try { stock.at("kiwi"); } catch (const std::out_of_range&) { std::cout << "at(\"kiwi\") throws out_of_range for missing keys\n"; }
    const std::map<std::string, int> frozen{{"a", 1}};
    std::cout << "frozen[\"b\"] would not compile on a const map; use at/find. Counting words idiom: ++counts[word] (the insertion IS wanted there).\n";

    std::cout << "\n===== SECTION 3: unordered_map and unordered_set (hashing) =====\n";
    std::unordered_map<std::string, int> h{{"zoe", 31}, {"adam", 25}, {"mia", 40}, {"leo", 12}};
    std::cout << "lookup h[\"mia\"] via find: " << h.find("mia")->second << ", size " << h.size() << "\n";
    std::vector<std::string> keys;
    for (const auto& kv : h) keys.push_back(kv.first);
    std::sort(keys.begin(), keys.end());
    std::cout << "iteration order of an unordered_map is unspecified; sorted keys:";
    for (const auto& k : keys) std::cout << " " << k;
    std::cout << "\n";
    std::unordered_set<int> us{3, 1, 3, 2};
    std::cout << "unordered_set of {3,1,3,2} has size " << us.size() << " (duplicates removed), contains(2) = " << us.contains(2) << "\n";
    std::cout << "load_factor <= max_load_factor: " << (h.load_factor() <= h.max_load_factor()) << " (rehashing keeps buckets roughly sized to the element count)\n";
    std::cout << "No lower_bound / range-by-order on unordered containers: hashing destroys order.\n";

    std::cout << "\n===== SECTION 4: multimap =====\n";
    std::multimap<std::string, std::string> tags;
    tags.insert({"cpp", "templates"});
    tags.insert({"cpp", "stl"});
    tags.insert({"java", "generics"});
    tags.insert({"cpp", "raii"});
    std::cout << "count(\"cpp\") = " << tags.count("cpp") << ", size = " << tags.size() << "\n";
    auto range = tags.equal_range("cpp");
    std::cout << "all values for cpp (insertion order kept among equal keys):";
    for (auto i = range.first; i != range.second; ++i) std::cout << " " << i->second;
    std::cout << "\n";
    std::cout << "multimap has no operator[] (which value would it mean?).\n";
    std::cout << "\nChoosing: ordered needs operator< (O(log n), sorted iteration, range queries); unordered needs hash + == (average O(1), no order).\n";
    return 0;
}
