"""
Bloom Filter Implementation
Chapter 8: URL Shortener & Cache Pre-checking

A space-efficient probabilistic data structure used to test whether an element
is a member of a set. False positive matches are possible, but false negatives
are impossible. If Bloom Filter says "NO", the short URL definitely does not exist,
preventing expensive database queries.
"""

import hashlib
import math
from typing import List


class BloomFilter:
    """
    Bloom filter with dynamic bit array sizing based on expected capacity and target error rate.
    """

    def __init__(self, expected_elements: int = 100_000, false_positive_rate: float = 0.01):
        if not (0 < false_positive_rate < 1):
            raise ValueError("False positive rate must be between 0 and 1.")

        self.expected_elements = expected_elements
        self.false_positive_rate = false_positive_rate

        # Optimal bit array size m = - (n * ln(p)) / (ln(2)^2)
        self.bit_size = int(
            math.ceil(
                -1 * (expected_elements * math.log(false_positive_rate)) / (math.log(2) ** 2)
            )
        )

        # Optimal number of hash functions k = (m / n) * ln(2)
        self.num_hashes = int(
            math.ceil((self.bit_size / expected_elements) * math.log(2))
        )

        self._byte_size = (self.bit_size + 7) // 8
        self._bit_array = bytearray(self._byte_size)
        self._count = 0

    def _get_hashes(self, item: str) -> List[int]:
        """
        Generate k distinct hash values using double hashing:
        hash_i(x) = (hash1(x) + i * hash2(x)) % bit_size
        """
        raw = item.encode("utf-8")
        h1 = int(hashlib.md5(raw).hexdigest()[:8], 16)
        h2 = int(hashlib.sha256(raw).hexdigest()[:8], 16) or 1

        indices = []
        for i in range(self.num_hashes):
            idx = (h1 + i * h2) % self.bit_size
            indices.append(idx)
        return indices

    def add(self, item: str) -> None:
        """Add an item into the bloom filter."""
        for idx in self._get_hashes(item):
            byte_idx = idx // 8
            bit_offset = idx % 8
            self._bit_array[byte_idx] |= 1 << bit_offset
        self._count += 1

    def contains(self, item: str) -> bool:
        """
        Check if item might be present.
        Returns False -> guaranteed NOT present.
        Returns True -> probably present.
        """
        for idx in self._get_hashes(item):
            byte_idx = idx // 8
            bit_offset = idx % 8
            if not (self._bit_array[byte_idx] & (1 << bit_offset)):
                return False
        return True

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    @property
    def element_count(self) -> int:
        return self._count

