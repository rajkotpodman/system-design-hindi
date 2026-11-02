"""
Fixed Window Counter Rate Limiter
Chapter 4: Fixed Window Counter Algorithm

Description:
Divides the timeline into fixed-size time intervals (e.g., 1-second, 60-second windows).
Assigns a counter for each window. Each request increments the counter.
If the counter exceeds the threshold, requests are dropped until the next window begins.
Note: Fixed window algorithm is prone to edge-of-window spikes where double the quota can pass.
"""

import math
import threading
import time
from typing import Dict, Optional, Tuple
from implementations.rate_limiter.base import BaseRateLimiter, RateLimitResult


class FixedWindowCounterRateLimiter(BaseRateLimiter):
    """
    Fixed Window Counter Rate Limiter.
    """

    def __init__(self, limit: int = 10, window_size_seconds: float = 1.0):
        """
        Args:
            limit: Maximum requests allowed per window.
            window_size_seconds: Window length in seconds (default: 1.0s).
        """
        self.limit = limit
        self.window_size = float(window_size_seconds)
        # key -> (window_index, count)
        self._counters: Dict[str, Tuple[int, int]] = {}
        self._lock = threading.Lock()

    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            current_window = int(math.floor(now / self.window_size))
            window_end = (current_window + 1) * self.window_size
            reset_after = max(0.0, window_end - now)

            last_window, count = self._counters.get(key, (current_window, 0))

            if last_window != current_window:
                # New window arrived, reset counter
                count = 0

            if count + tokens <= self.limit:
                new_count = count + tokens
                self._counters[key] = (current_window, new_count)
                return RateLimitResult(
                    allowed=True,
                    limit=self.limit,
                    remaining=self.limit - new_count,
                    reset_after=round(reset_after, 4),
                    retry_after=None,
                )
            else:
                self._counters[key] = (current_window, count)
                return RateLimitResult(
                    allowed=False,
                    limit=self.limit,
                    remaining=max(0, self.limit - count),
                    reset_after=round(reset_after, 4),
                    retry_after=round(reset_after, 4),
                )

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key:
                self._counters.pop(key, None)
            else:
                self._counters.clear()

