"""
Twitter Snowflake 64-bit Distributed Unique ID Generator
Chapter 7: Design A Unique ID Generator In Distributed Systems

Structure of 64-bit Snowflake ID:
- 1 bit: Unused sign bit (always 0)
- 41 bits: Timestamp in milliseconds since custom epoch (~69 years)
- 5 bits: Datacenter ID (0 to 31 -> 32 datacenters)
- 5 bits: Worker / Machine ID (0 to 31 -> 32 machines per datacenter)
- 12 bits: Sequence counter (0 to 4095 -> 4096 IDs per millisecond per worker)

Throughput:
Up to 4,096,000 IDs per second per machine node.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import threading
import time


# Custom Epoch: Jan 1, 2024 00:00:00 UTC (in milliseconds)
DEFAULT_CUSTOM_EPOCH = 1704067200000


class ClockBackwardsError(Exception):
    """Raised when server system clock drifts backwards."""
    pass


@dataclass
class SnowflakeParts:
    id: int
    timestamp_ms: int
    utc_datetime: datetime
    datacenter_id: int
    worker_id: int
    sequence: int


class SnowflakeIDGenerator:
    """
    Thread-safe Twitter Snowflake ID Generator.
    """

    # Bit allocation
    UNUSED_BITS = 1
    TIMESTAMP_BITS = 41
    DATACENTER_ID_BITS = 5
    WORKER_ID_BITS = 5
    SEQUENCE_BITS = 12

    # Maximum values
    MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1  # 31
    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1          # 31
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1            # 4095

    # Bit shifts
    WORKER_ID_SHIFT = SEQUENCE_BITS
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

    def __init__(
        self,
        datacenter_id: int = 1,
        worker_id: int = 1,
        epoch: int = DEFAULT_CUSTOM_EPOCH,
    ):
        if not (0 <= datacenter_id <= self.MAX_DATACENTER_ID):
            raise ValueError(f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}")
        if not (0 <= worker_id <= self.MAX_WORKER_ID):
            raise ValueError(f"Worker ID must be between 0 and {self.MAX_WORKER_ID}")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.epoch = epoch

        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()

    def _current_timestamp_ms(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._current_timestamp_ms()
        while timestamp <= last_timestamp:
            time.sleep(0.0001)
            timestamp = self._current_timestamp_ms()
        return timestamp

    def generate(self) -> int:
        """
        Generate a unique 64-bit integer ID.
        """
        with self._lock:
            timestamp = self._current_timestamp_ms()

            # Handle clock backwards drift
            if timestamp < self._last_timestamp:
                drift = self._last_timestamp - timestamp
                if drift <= 5:
                    # Small drift: sleep and wait
                    timestamp = self._wait_next_millis(self._last_timestamp)
                else:
                    raise ClockBackwardsError(
                        f"Clock moved backwards by {drift}ms. Refusing to generate ID."
                    )

            if timestamp == self._last_timestamp:
                # Same millisecond: increment sequence
                self._sequence = (self._sequence + 1) & self.MAX_SEQUENCE
                if self._sequence == 0:
                    # Sequence exhausted for this millisecond: wait for next millisecond
                    timestamp = self._wait_next_millis(self._last_timestamp)
            else:
                # New millisecond: reset sequence counter to 0
                self._sequence = 0

            self._last_timestamp = timestamp

            # Bitwise packing
            snowflake_id = (
                ((timestamp - self.epoch) << self.TIMESTAMP_LEFT_SHIFT)
                | (self.datacenter_id << self.DATACENTER_ID_SHIFT)
                | (self.worker_id << self.WORKER_ID_SHIFT)
                | self._sequence
            )

            return snowflake_id

    def parse(self, snowflake_id: int) -> SnowflakeParts:
        """
        Deconstruct a Snowflake ID into its component parts.
        """
        sequence = snowflake_id & self.MAX_SEQUENCE
        worker_id = (snowflake_id >> self.WORKER_ID_SHIFT) & self.MAX_WORKER_ID
        datacenter_id = (snowflake_id >> self.DATACENTER_ID_SHIFT) & self.MAX_DATACENTER_ID
        timestamp_offset = snowflake_id >> self.TIMESTAMP_LEFT_SHIFT
        absolute_timestamp_ms = timestamp_offset + self.epoch
        dt = datetime.fromtimestamp(absolute_timestamp_ms / 1000.0, tz=timezone.utc)

        return SnowflakeParts(
            id=snowflake_id,
            timestamp_ms=absolute_timestamp_ms,
            utc_datetime=dt,
            datacenter_id=datacenter_id,
            worker_id=worker_id,
            sequence=sequence,
        )

