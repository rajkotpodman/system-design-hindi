import pytest
from implementations.search_autocomplete import SearchAutocompleteSystem


def test_search_autocomplete():
    trie = SearchAutocompleteSystem(top_k_size=3)
    trie.bulk_load({
        "apple": 100,
        "app store": 250,
        "application": 80,
        "banana": 500,
    })

    res = trie.search("app")
    assert len(res) == 3
    # Top result should be "app store" because of higher frequency
    assert res[0][0] == "app store"
    assert res[0][1] == 250

    # Non-existent prefix
    assert trie.search("xyz") == []


def test_dynamic_frequency_increment():
    trie = SearchAutocompleteSystem(top_k_size=2)
    trie.insert("python", 10)
    trie.insert("pytorch", 20)

    # Currently pytorch (20) > python (10)
    assert trie.search("py")[0][0] == "pytorch"

    # Increment python by 50 -> 60 total
    trie.insert("python", 50)
    assert trie.search("py")[0][0] == "python"

