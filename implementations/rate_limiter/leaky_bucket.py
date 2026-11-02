"""
Leaky Bucket Rate Limiter
Chapter 4: Leaking Bucket Algorithm

Description:
Requests enter a buffer of fixed capacity (the bucket). The bucket leaks (discharges)
requests at a steady, fixed rate. If a request arrives when the bucket is full,
it overflows and is dropped or rejected.
"""

import threading
import time
from typing import Dict, Optional
from implementations.rate_limiter.base import BaseRateLimiter, RateLimitResult


class _LeakyBucketState:
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = float(capacity)
        self.leak_rate = float(leak_rate)  # requests leaked per second
        self.water_level = 0.0  # current pending requests
        self.last_leak_timestamp = time.time()
        self.lock = threading.Lock()

    def add(self, count: int = 1) -> RateLimitResult:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_leak_timestamp
            self.last_leak_timestamp = now

            # Leak water according to elapsed time
            self.water_level = max(0.0, self.water_level - elapsed * self.leak_rate)

            if self.water_level + count <= self.capacity:
                self.water_level += count
                remaining = int(self.capacity - self.water_level)
                return RateLimitResult(
                    allowed=True,
                    limit=int(self.capacity),
                    remaining=remaining,
                    reset_after=round(self.water_level / self.leak_rate, 4) if self.leak_rate > 0 else 0.0,
                    retry_after=None,
                )
            else:
                overflow = (self.water_level + count) - self.capacity
                retry_after = round(overflow / self.leak_rate, 4) if self.leak_rate > 0 else 1.0
                return RateLimitResult(
                    allowed=False,
                    limit=int(self.capacity),
                    remaining=0,
                    reset_after=round(self.water_level / self.leak_rate, 4) if self.leak_rate > 0 else 0.0,
                    retry_after=retry_after,
                )


class LeakyBucketRateLimiter(BaseRateLimiter):
    """
    Thread-safe multi-client Leaky Bucket Rate Limiter.
    """

    def __init__(self, capacity: int = 10, leak_rate: float = 2.0):
        """
        Args:
            capacity: Buffer capacity (maximum queue size).
            leak_rate: Requests discharged per second.
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self._states: Dict[str, _LeakyBucketState] = {}
        self._lock = threading.Lock()

    def _get_state(self, key: str) -> _LeakyBucketState:
        with self._lock:
            if key not in self._states:
                self._states[key] = _LeakyBucketState(self.capacity, self.leak_rate)
            return self._states[key]

    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        state = self._get_state(key)
        return state.add(tokens)

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key:
                self._states.pop(key, None)
            else:
                self._states.clear()

