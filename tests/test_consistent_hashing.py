import pytest
from implementations.consistent_hashing import ConsistentHashRing, ConsistentHashSimulator


def test_consistent_hash_ring():
    ring = ConsistentHashRing(nodes=["node-A", "node-B", "node-C"], vnodes_per_node=100)
    assert len(ring.nodes) == 3
    assert ring.total_vnodes == 300

    target = ring.get_node("user_12345")
    assert target in ["node-A", "node-B", "node-C"]

    # Replica placement
    replicas = ring.get_nodes("user_12345", count=2)
    assert len(replicas) == 2
    assert replicas[0] != replicas[1]


def test_node_addition_and_removal():
    ring = ConsistentHashRing(nodes=["node-A", "node-B"], vnodes_per_node=50)
    ring.add_node("node-C")
    assert "node-C" in ring.nodes

    ring.remove_node("node-A")
    assert "node-A" not in ring.nodes
    assert len(ring.nodes) == 2


def test_churn_simulator():
    keys = [f"key_{i}" for i in range(1000)]
    churn = ConsistentHashSimulator.compare_node_churn(
        initial_nodes=["node-1", "node-2"],
        new_node="node-3",
        keys=keys,
        vnodes=100,
    )
    # Consistent hashing should move substantially fewer keys than naive modulo
    assert churn["consistent_hashing"]["keys_moved"] < churn["naive_modulo_hashing"]["keys_moved"]

