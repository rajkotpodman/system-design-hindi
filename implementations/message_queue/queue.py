"""
Distributed Message Queue (Kafka-style Partitioned Log Architecture)
Chapter 19: Distributed Message Queue

Core Concepts:
1. Topic: Category or feed name to which messages are published.
2. Partitions: Shards of a topic providing horizontal scalability and ordering guarantees within each partition.
3. Commit Log: Ordered, immutable sequence of messages assigned sequential offsets (0, 1, 2...).
4. Consumer Groups: Multiple consumers coordinate to read partitions without duplicate processing.
   Partitions are rebalanced across active consumers in the group.
5. Offset Tracking: Each consumer group maintains its own read progress per partition.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import threading
from typing import Dict, List, Optional


@dataclass
class Message:
    offset: int
    key: Optional[str]
    payload: str
    timestamp: str


class Partition:
    """An append-only ordered commit log."""

    def __init__(self, partition_id: int):
        self.partition_id = partition_id
        self._log: List[Message] = []
        self._lock = threading.Lock()

    def append(self, key: Optional[str], payload: str) -> Message:
        with self._lock:
            offset = len(self._log)
            msg = Message(
                offset=offset,
                key=key,
                payload=payload,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log.append(msg)
            return msg

    def read_from(self, offset: int, max_messages: int = 10) -> List[Message]:
        with self._lock:
            if offset >= len(self._log):
                return []
            return self._log[offset : offset + max_messages]

    @property
    def latest_offset(self) -> int:
        with self._lock:
            return len(self._log)


class Topic:
    def __init__(self, name: str, partition_count: int = 3):
        self.name = name
        self.partition_count = partition_count
        self.partitions = [Partition(i) for i in range(partition_count)]

    def get_partition_for_key(self, key: Optional[str]) -> Partition:
        if not key:
            # Round-robin or random
            return self.partitions[0]
        # Consistent partition hashing
        digest = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)
        part_idx = digest % self.partition_count
        return self.partitions[part_idx]


class MessageQueueBroker:
    """
    Message Broker orchestrating topics, publishing, and consumer groups.
    """

    def __init__(self):
        self._topics: Dict[str, Topic] = {}
        # consumer_group -> topic -> partition_id -> committed_offset
        self._offsets: Dict[str, Dict[str, Dict[int, int]]] = {}
        self._lock = threading.Lock()

    def create_topic(self, topic_name: str, partition_count: int = 3) -> Topic:
        with self._lock:
            if topic_name not in self._topics:
                self._topics[topic_name] = Topic(topic_name, partition_count)
            return self._topics[topic_name]

    def publish(self, topic_name: str, payload: str, key: Optional[str] = None) -> Message:
        """Publish a message to a topic."""
        with self._lock:
            if topic_name not in self._topics:
                self._topics[topic_name] = Topic(topic_name)
            topic = self._topics[topic_name]

        partition = topic.get_partition_for_key(key)
        return partition.append(key, payload)

    def consume(
        self,
        group_id: str,
        topic_name: str,
        partition_id: int,
        max_messages: int = 5,
        auto_commit: bool = True,
    ) -> List[Message]:
        """
        Poll messages for a consumer group on a specific partition.
        """
        with self._lock:
            if topic_name not in self._topics:
                return []
            topic = self._topics[topic_name]
            if partition_id >= topic.partition_count:
                return []

            # Retrieve current committed offset for this group
            group_map = self._offsets.setdefault(group_id, {}).setdefault(topic_name, {})
            current_offset = group_map.get(partition_id, 0)

        partition = topic.partitions[partition_id]
        messages = partition.read_from(current_offset, max_messages)

        if messages and auto_commit:
            with self._lock:
                # Commit offset of next unread message
                next_offset = messages[-1].offset + 1
                self._offsets[group_id][topic_name][partition_id] = next_offset

        return messages

    def commit_offset(self, group_id: str, topic_name: str, partition_id: int, offset: int) -> None:
        """Explicitly commit offset for at-least-once processing semantics."""
        with self._lock:
            self._offsets.setdefault(group_id, {}).setdefault(topic_name, {})[partition_id] = offset

    def get_lag(self, group_id: str, topic_name: str) -> Dict[int, int]:
        """Calculate consumer lag across all partitions."""
        with self._lock:
            if topic_name not in self._topics:
                return {}
            topic = self._topics[topic_name]
            lag_map = {}
            for i, p in enumerate(topic.partitions):
                latest = p.latest_offset
                committed = self._offsets.get(group_id, {}).get(topic_name, {}).get(i, 0)
                lag_map[i] = max(0, latest - committed)
            return lag_map

