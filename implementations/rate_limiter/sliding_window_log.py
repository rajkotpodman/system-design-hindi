"""
Sliding Window Log Rate Limiter
Chapter 4: Sliding Window Log Algorithm

Description:
Maintains an exact log of request timestamps. When a new request arrives:
1. Outdated timestamps older than (now - window_size) are pruned.
2. The count of active timestamps in the window is evaluated.
3. If the count is within limits, the new request's timestamp is appended to the log.
4. Otherwise, the request is rejected.

Pros: 100% accurate rate limiting without edge-burst vulnerabilities.
Cons: High memory consumption because every request timestamp is retained in memory.
"""

from collections import deque
import threading
import time
from typing import Deque, Dict, Optional
from implementations.rate_limiter.base import BaseRateLimiter, RateLimitResult


class SlidingWindowLogRateLimiter(BaseRateLimiter):
    """
    Sliding Window Log Rate Limiter.
    """

    def __init__(self, limit: int = 10, window_size_seconds: float = 1.0):
        """
        Args:
            limit: Maximum requests allowed in the rolling window.
            window_size_seconds: Window duration in seconds.
        """
        self.limit = limit
        self.window_size = float(window_size_seconds)
        self._logs: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            cutoff = now - self.window_size

            if key not in self._logs:
                self._logs[key] = deque()

            log = self._logs[key]

            # Discard timestamps outside the current window
            while log and log[0] <= cutoff:
                log.popleft()

            current_count = len(log)
            if current_count + tokens <= self.limit:
                for _ in range(tokens):
                    log.append(now)
                remaining = self.limit - len(log)
                oldest = log[0] if log else now
                reset_after = max(0.0, (oldest + self.window_size) - now)
                return RateLimitResult(
                    allowed=True,
                    limit=self.limit,
                    remaining=remaining,
                    reset_after=round(reset_after, 4),
                    retry_after=None,
                )
            else:
                oldest = log[0] if log else now
                retry_after = max(0.001, (oldest + self.window_size) - now)
                return RateLimitResult(
                    allowed=False,
                    limit=self.limit,
                    remaining=max(0, self.limit - current_count),
                    reset_after=round(retry_after, 4),
                    retry_after=round(retry_after, 4),
                )

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key:
                self._logs.pop(key, None)
            else:
                self._logs.clear()

