"""
Consistent Hashing Simulator & Metrics Analysis
Chapter 5: Redistribution and Virtual Node Analysis

Compares Consistent Hashing against Naive Modulo Hashing:
1. Calculates key distribution variance across servers.
2. Measures key migration churn when a server is added or removed.
"""

from collections import Counter
import math
from typing import Any, Dict, List
from implementations.consistent_hashing.ring import ConsistentHashRing


class ConsistentHashSimulator:
    """
    Simulation suite for analyzing key distribution and churn.
    """

    @staticmethod
    def analyze_distribution(ring: ConsistentHashRing, keys: List[str]) -> Dict[str, Any]:
        """
        Calculates key counts per node and statistical metrics (std dev, variance).
        """
        counts = Counter()
        for k in keys:
            node = ring.get_node(k)
            if node:
                counts[node] += 1

        total_keys = len(keys)
        num_nodes = len(ring.nodes)
        if num_nodes == 0 or total_keys == 0:
            return {"counts": {}, "std_dev": 0.0, "mean": 0.0}

        mean = total_keys / num_nodes
        variance = sum((counts[n] - mean) ** 2 for n in ring.nodes) / num_nodes
        std_dev = math.sqrt(variance)

        distribution = {
            node: {
                "count": counts[node],
                "percentage": round((counts[node] / total_keys) * 100, 2),
            }
            for node in ring.nodes
        }

        return {
            "node_count": num_nodes,
            "total_keys": total_keys,
            "mean_per_node": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "coefficient_of_variation": round((std_dev / mean) * 100, 2) if mean > 0 else 0,
            "distribution": distribution,
        }

    @staticmethod
    def compare_node_churn(
        initial_nodes: List[str],
        new_node: str,
        keys: List[str],
        vnodes: int = 150,
    ) -> Dict[str, Any]:
        """
        Demonstrates the core theorem:
        - Consistent Hashing moves only ~1/(N+1) keys when a node is added.
        - Naive modulo hashing (hash % N) moves ~N/(N+1) keys (almost everything!).
        """
        # 1. Consistent Hashing evaluation
        ring = ConsistentHashRing(initial_nodes, vnodes_per_node=vnodes)
        initial_mapping = {k: ring.get_node(k) for k in keys}

        ring.add_node(new_node)
        new_mapping = {k: ring.get_node(k) for k in keys}

        consistent_moved = sum(
            1 for k in keys if initial_mapping[k] != new_mapping[k]
        )

        # 2. Naive Modulo Hashing evaluation
        n_orig = len(initial_nodes)
        n_new = n_orig + 1

        def naive_hash(key: str, n: int) -> int:
            return ConsistentHashRing._default_hash(key) % n

        naive_moved = sum(
            1 for k in keys if naive_hash(k, n_orig) != naive_hash(k, n_new)
        )

        total = len(keys)
        return {
            "total_keys": total,
            "consistent_hashing": {
                "keys_moved": consistent_moved,
                "percentage_moved": round((consistent_moved / total) * 100, 2),
                "theoretical_fraction": round((1.0 / n_new) * 100, 2),
            },
            "naive_modulo_hashing": {
                "keys_moved": naive_moved,
                "percentage_moved": round((naive_moved / total) * 100, 2),
                "theoretical_fraction": round(((n_new - 1) / n_new) * 100, 2),
            },
        }

