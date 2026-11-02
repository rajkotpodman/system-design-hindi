"""
Search Autocomplete System using Top-K Cached Trie
Chapter 13: Design A Search Autocomplete System

Architecture:
- Trie data structure stores keywords and frequency.
- Top-K Optimization: Each TrieNode pre-caches its top-K most popular search queries.
  This transforms query time complexity from O(p + c + c log k) to O(p), where p is prefix length.
- Dynamic weight updates: As users type and click queries, node frequencies update
  and top-K caches percolate upwards.
"""

from heapq import nlargest
import threading
from typing import Dict, List, Optional, Tuple


class TrieNode:
    def __init__(self, top_k_size: int = 5):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_word: bool = False
        self.frequency: int = 0
        self.word: Optional[str] = None
        self.top_k_size = top_k_size
        # Pre-computed list of (query, frequency) sorted descending
        self.cached_top_k: List[Tuple[str, int]] = []

    def update_cached_top_k(self, word: str, frequency: int) -> None:
        """Update the node's cached top-K queries."""
        current_map = dict(self.cached_top_k)
        current_map[word] = frequency
        # Keep the top-k highest frequency items
        top_items = nlargest(self.top_k_size, current_map.items(), key=lambda x: (x[1], -len(x[0]), x[0]))
        self.cached_top_k = top_items


class SearchAutocompleteSystem:
    """
    High-performance Trie-based Autocomplete Engine.
    """

    def __init__(self, top_k_size: int = 5):
        self.top_k_size = top_k_size
        self.root = TrieNode(top_k_size=top_k_size)
        self._lock = threading.Lock()

    def insert(self, query: str, frequency: int = 1) -> None:
        """Insert or increment a query string with its frequency."""
        query = query.strip().lower()
        if not query:
            return

        with self._lock:
            # 1. Traverse and locate leaf to find existing frequency
            curr = self.root
            path: List[TrieNode] = [curr]
            for char in query:
                if char not in curr.children:
                    curr.children[char] = TrieNode(top_k_size=self.top_k_size)
                curr = curr.children[char]
                path.append(curr)

            curr.is_word = True
            curr.word = query
            curr.frequency += frequency
            final_freq = curr.frequency

            # 2. Update cached top-K along all prefix nodes along the path
            for node in path:
                node.update_cached_top_k(query, final_freq)

    def search(self, prefix: str, limit: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Return the top-K query completions for a given prefix in O(p) time.
        """
        prefix = prefix.strip().lower()
        if not prefix:
            return self.root.cached_top_k[:limit] if limit else self.root.cached_top_k

        curr = self.root
        for char in prefix:
            if char not in curr.children:
                return []
            curr = curr.children[char]

        results = curr.cached_top_k
        if limit is not None:
            results = results[:limit]
        return results

    def bulk_load(self, data: Dict[str, int]) -> None:
        """Batch load initial search terms and historical frequencies."""
        for query, freq in data.items():
            self.insert(query, freq)

