"""
Token Bucket Rate Limiter
Chapter 4: Token Bucket Algorithm

Description:
Tokens are refilled into a bucket of fixed capacity at a constant refill rate.
Each incoming request requires 1 or more tokens. If enough tokens exist in the bucket,
they are consumed and the request is permitted. Otherwise, the request is dropped/rejected.
"""

import threading
import time
from typing import Dict, Optional
from implementations.rate_limiter.base import BaseRateLimiter, RateLimitResult


class _Bucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)  # tokens per second
        self.tokens = float(capacity)
        self.last_refill_timestamp = time.time()
        self.lock = threading.Lock()

    def consume(self, count: int = 1) -> RateLimitResult:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill_timestamp
            self.last_refill_timestamp = now

            # Add newly accumulated tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

            if self.tokens >= count:
                self.tokens -= count
                remaining = int(self.tokens)
                return RateLimitResult(
                    allowed=True,
                    limit=int(self.capacity),
                    remaining=remaining,
                    reset_after=0.0,
                    retry_after=None,
                )
            else:
                deficit = count - self.tokens
                retry_after = round(deficit / self.refill_rate, 4) if self.refill_rate > 0 else 1.0
                return RateLimitResult(
                    allowed=False,
                    limit=int(self.capacity),
                    remaining=int(self.tokens),
                    reset_after=retry_after,
                    retry_after=retry_after,
                )


class TokenBucketRateLimiter(BaseRateLimiter):
    """
    Thread-safe multi-client Token Bucket Rate Limiter.
    """

    def __init__(self, capacity: int = 10, refill_rate: float = 2.0):
        """
        Args:
            capacity: Maximum bucket capacity (maximum burst size).
            refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: Dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, key: str) -> _Bucket:
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = _Bucket(self.capacity, self.refill_rate)
            return self._buckets[key]

    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        bucket = self._get_bucket(key)
        return bucket.consume(tokens)

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()

