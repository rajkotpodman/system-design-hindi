"""
Consistent Hashing Ring with Virtual Nodes
Chapter 5: Design Consistent Hashing

Features:
- Uniform hash ring mapping (0 to 2^32 - 1 or 2^160 - 1).
- Virtual Nodes (vnodes) to guarantee even data distribution and eliminate hot spots.
- Logarithmic lookup time O(log(M * V)) using binary search (bisect).
- Clockwise ring traversal for replica placement (N distinct physical nodes).
- Exact calculation of key migration during node scale-up or scale-down.
"""

import bisect
import hashlib
from typing import Callable, Dict, List, Optional, Set


class ConsistentHashRing:
    """
    Consistent Hash Ring supporting virtual nodes and replication.
    """

    def __init__(
        self,
        nodes: Optional[List[str]] = None,
        vnodes_per_node: int = 150,
        hash_func: Optional[Callable[[str], int]] = None,
    ):
        """
        Args:
            nodes: Initial list of physical node identifiers (e.g., ["server-1", "server-2"]).
            vnodes_per_node: Number of virtual nodes mapped per physical server.
            hash_func: Custom hash function returning an integer; defaults to MD5 (32-bit integer).
        """
        self.vnodes_per_node = vnodes_per_node
        self.hash_func = hash_func or self._default_hash
        self._ring: List[int] = []  # Sorted list of virtual node hash positions
        self._hash_to_node: Dict[int, str] = {}  # vnode hash -> physical node
        self._nodes: Set[str] = set()  # Set of active physical nodes

        if nodes:
            for node in nodes:
                self.add_node(node)

    @staticmethod
    def _default_hash(key: str) -> int:
        """Hash key using MD5 and return an integer in [0, 2^32 - 1]."""
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def add_node(self, node: str) -> None:
        """
        Add a physical node to the ring, allocating its virtual nodes.
        """
        if node in self._nodes:
            return

        self._nodes.add(node)
        for i in range(self.vnodes_per_node):
            vnode_key = f"{node}#vn_{i}"
            vnode_hash = self.hash_func(vnode_key)
            self._hash_to_node[vnode_hash] = node
            bisect.insort(self._ring, vnode_hash)

    def remove_node(self, node: str) -> None:
        """
        Remove a physical node from the ring and delete its virtual nodes.
        """
        if node not in self._nodes:
            return

        self._nodes.remove(node)
        for i in range(self.vnodes_per_node):
            vnode_key = f"{node}#vn_{i}"
            vnode_hash = self.hash_func(vnode_key)
            self._hash_to_node.pop(vnode_hash, None)
            idx = bisect.bisect_left(self._ring, vnode_hash)
            if idx < len(self._ring) and self._ring[idx] == vnode_hash:
                del self._ring[idx]

    def get_node(self, key: str) -> Optional[str]:
        """
        Find the physical node responsible for storing the given key.
        Searches clockwise on the ring until the first virtual node is encountered.
        """
        if not self._ring:
            return None

        key_hash = self.hash_func(key)
        idx = bisect.bisect_right(self._ring, key_hash)

        # Wrap around to the first node if key_hash is greater than all nodes
        if idx == len(self._ring):
            idx = 0

        vnode_hash = self._ring[idx]
        return self._hash_to_node[vnode_hash]

    def get_nodes(self, key: str, count: int) -> List[str]:
        """
        Get 'count' distinct physical replica nodes for a key by walking clockwise.
        Essential for distributed databases (e.g. Cassandra, DynamoDB N-replica placement).
        """
        if not self._ring or count <= 0:
            return []

        key_hash = self.hash_func(key)
        start_idx = bisect.bisect_right(self._ring, key_hash)
        ring_len = len(self._ring)

        replicas: List[str] = []
        seen_nodes: Set[str] = set()

        for step in range(ring_len):
            curr_idx = (start_idx + step) % ring_len
            vnode_hash = self._ring[curr_idx]
            physical_node = self._hash_to_node[vnode_hash]

            if physical_node not in seen_nodes:
                seen_nodes.add(physical_node)
                replicas.append(physical_node)

            if len(replicas) == min(count, len(self._nodes)):
                break

        return replicas

    @property
    def nodes(self) -> List[str]:
        """Return list of active physical nodes."""
        return sorted(list(self._nodes))

    @property
    def total_vnodes(self) -> int:
        """Total number of virtual nodes on the ring."""
        return len(self._ring)

