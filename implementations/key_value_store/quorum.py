"""
Distributed Quorum Key-Value Store
Chapter 6: Design A Key-Value Store

Key Concepts:
- Tunable Consistency: N (Replicas), W (Write Quorum), R (Read Quorum).
  - Strong Consistency: W + R > N (Guarantees read overlap with latest write).
  - High Write Availability: W = 1, R = N.
  - High Read Availability: W = N, R = 1.
- Partitioning: Consistent Hash Ring determines the N primary replicas.
- Versioning: Vector clocks identify the most up-to-date value.
- Read Repair: When a read detects a stale replica, it asynchronously repairs it with the freshest value!
"""

from dataclasses import dataclass
import threading
import time
from typing import Dict, List, Optional, Tuple
from implementations.consistent_hashing.ring import ConsistentHashRing
from implementations.key_value_store.vector_clock import VectorClock, ClockRelation


@dataclass
class StorageValue:
    value: str
    vector_clock: VectorClock
    timestamp: float


class KVNode:
    """A single physical node holding data partitions."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data: Dict[str, StorageValue] = {}
        self.is_healthy: bool = True
        self._lock = threading.Lock()

    def put(self, key: str, value: str, clock: VectorClock) -> StorageValue:
        with self._lock:
            if not self.is_healthy:
                raise ConnectionError(f"Node {self.node_id} is unreachable.")
            record = StorageValue(value=value, vector_clock=clock.copy(), timestamp=time.time())
            self.data[key] = record
            return record

    def get(self, key: str) -> Optional[StorageValue]:
        with self._lock:
            if not self.is_healthy:
                raise ConnectionError(f"Node {self.node_id} is unreachable.")
            return self.data.get(key)


class DistributedKVCluster:
    """
    Coordinator managing Quorum Reads & Writes across a cluster of KVNodes.
    """

    def __init__(self, node_ids: List[str], n_replicas: int = 3, w_quorum: int = 2, r_quorum: int = 2):
        self.n_replicas = n_replicas
        self.w_quorum = w_quorum
        self.r_quorum = r_quorum

        self.nodes: Dict[str, KVNode] = {nid: KVNode(nid) for nid in node_ids}
        self.ring = ConsistentHashRing(nodes=node_ids, vnodes_per_node=100)
        self._lock = threading.Lock()

    def put(self, key: str, value: str, client_clock: Optional[VectorClock] = None) -> VectorClock:
        """
        Execute Quorum Write.
        Requires acknowledgment from at least W replicas.
        """
        replica_node_ids = self.ring.get_nodes(key, count=self.n_replicas)
        if len(replica_node_ids) < self.w_quorum:
            raise ValueError(f"Insufficient nodes to achieve write quorum ({len(replica_node_ids)} < {self.w_quorum})")

        # Pick coordinator node (first replica)
        coord_id = replica_node_ids[0]
        clock = client_clock.copy() if client_clock else VectorClock()
        clock.increment(coord_id)

        acks = 0
        errors = []

        for nid in replica_node_ids:
            node = self.nodes[nid]
            try:
                node.put(key, value, clock)
                acks += 1
            except Exception as e:
                errors.append(str(e))

        if acks < self.w_quorum:
            raise RuntimeError(f"Write quorum failed. Acks: {acks}/{self.w_quorum}. Errors: {errors}")

        return clock

    def get(self, key: str) -> Tuple[Optional[str], VectorClock, int]:
        """
        Execute Quorum Read with Read Repair.
        Requires responses from at least R replicas.
        Returns (freshest_value, merged_clock, responses_count).
        """
        replica_node_ids = self.ring.get_nodes(key, count=self.n_replicas)
        responses: List[Tuple[str, StorageValue]] = []

        for nid in replica_node_ids:
            node = self.nodes[nid]
            try:
                val = node.get(key)
                if val:
                    responses.append((nid, val))
                else:
                    responses.append((nid, None))
            except Exception:
                pass

        valid_responses = [r for r in responses if r[1] is not None]
        if len(responses) < self.r_quorum:
            raise RuntimeError(f"Read quorum failed. Received {len(responses)}/{self.r_quorum} responses.")

        if not valid_responses:
            return None, VectorClock(), len(responses)

        # Find the latest value among quorum responses using Vector Clock comparison
        freshest_nid, freshest_record = valid_responses[0]
        stale_nodes = []

        for nid, record in valid_responses[1:]:
            relation = record.vector_clock.compare(freshest_record.vector_clock)
            if relation == ClockRelation.AFTER:
                stale_nodes.append(freshest_nid)
                freshest_nid = nid
                freshest_record = record
            elif relation == ClockRelation.BEFORE:
                stale_nodes.append(nid)

        # Read Repair: push the freshest record to any stale nodes identified in quorum
        for nid in stale_nodes:
            try:
                self.nodes[nid].put(key, freshest_record.value, freshest_record.vector_clock)
            except Exception:
                pass

        return freshest_record.value, freshest_record.vector_clock, len(responses)

