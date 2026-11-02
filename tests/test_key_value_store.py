import pytest
from implementations.key_value_store import VectorClock, ClockRelation, DistributedKVCluster


def test_vector_clock_causality():
    v1 = VectorClock({"node1": 1})
    v2 = VectorClock({"node1": 2})
    assert v1.compare(v2) == ClockRelation.BEFORE
    assert v2.compare(v1) == ClockRelation.AFTER

    # Concurrent clocks
    v_a = VectorClock({"node1": 2, "node2": 1})
    v_b = VectorClock({"node1": 1, "node2": 2})
    assert v_a.compare(v_b) == ClockRelation.CONCURRENT


def test_quorum_cluster_write_read_and_repair():
    cluster = DistributedKVCluster(
        node_ids=["node1", "node2", "node3"],
        n_replicas=3,
        w_quorum=2,
        r_quorum=2,
    )

    # 1. Quorum Write
    clock = cluster.put("key1", "value_initial")
    assert clock is not None

    # 2. Quorum Read
    val, read_clock, acks = cluster.get("key1")
    assert val == "value_initial"
    assert acks >= 2

    # 3. Simulate Stale Replica with an older clock
    cluster.nodes["node3"].put("key1", "stale_old_value", VectorClock())
    # Quorum Read detects stale replica and executes Read Repair
    repaired_val, _, _ = cluster.get("key1")
    assert repaired_val == "value_initial"
    # Verify node3 was repaired
    assert cluster.nodes["node3"].get("key1").value == "value_initial"

