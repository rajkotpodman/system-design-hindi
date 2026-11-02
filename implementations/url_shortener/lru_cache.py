"""
LRU Cache for Hot URLs
Chapter 8: Caching Layer for URL Shortener

Maintains a bounded in-memory cache of the most recently accessed URL mappings.
Uses an internal doubly linked list + hash map (via collections.OrderedDict)
to achieve O(1) reads and O(1) evictions.
"""

from collections import OrderedDict
import threading
from typing import Optional


class LRUCache:
    def __init__(self, capacity: int = 10_000):
        self.capacity = capacity
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            if key not in self._cache:
                return None
            self._cache.move_to_end(key)
            return self._cache[key]

    def put(self, key: str, value: str) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self.capacity:
                self._cache.popitem(last=False)

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

