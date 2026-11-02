"""
Vector Clock for Causality & Conflict Detection
Chapter 6: Design A Key-Value Store

Vector clocks track causality between concurrent writes across distributed nodes.
Format: {node_id: counter}
Relations:
- BEFORE: v1 happened before v2 (v1 is an ancestor of v2)
- AFTER: v1 happened after v2
- EQUAL: identical vector clocks
- CONCURRENT: neither clock dominates; concurrent conflict requiring reconciliation!
"""

from enum import Enum
from typing import Dict


class ClockRelation(str, Enum):
    EQUAL = "EQUAL"
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    CONCURRENT = "CONCURRENT"


class VectorClock:
    def __init__(self, clock_dict: Dict[str, int] = None):
        self.clock: Dict[str, int] = dict(clock_dict) if clock_dict else {}

    def increment(self, node_id: str) -> "VectorClock":
        """Increment current node's counter and return self."""
        self.clock[node_id] = self.clock.get(node_id, 0) + 1
        return self

    def copy(self) -> "VectorClock":
        return VectorClock(dict(self.clock))

    def merge(self, other: "VectorClock") -> "VectorClock":
        """Merge by taking the maximum counter for each node."""
        all_nodes = set(self.clock.keys()).union(other.clock.keys())
        merged = {
            node: max(self.clock.get(node, 0), other.clock.get(node, 0))
            for node in all_nodes
        }
        return VectorClock(merged)

    def compare(self, other: "VectorClock") -> ClockRelation:
        """Determine causal relationship between self and other."""
        all_nodes = set(self.clock.keys()).union(other.clock.keys())
        greater = False
        lesser = False

        for node in all_nodes:
            c1 = self.clock.get(node, 0)
            c2 = other.clock.get(node, 0)

            if c1 > c2:
                greater = True
            elif c1 < c2:
                lesser = True

        if greater and not lesser:
            return ClockRelation.AFTER
        elif lesser and not greater:
            return ClockRelation.BEFORE
        elif not greater and not lesser:
            return ClockRelation.EQUAL
        else:
            return ClockRelation.CONCURRENT

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clock)

    def __repr__(self) -> str:
        return f"VectorClock({self.clock})"

