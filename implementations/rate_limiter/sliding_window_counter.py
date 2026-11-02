"""
Sliding Window Counter Rate Limiter
Chapter 4: Sliding Window Counter Algorithm

Description:
Combines the memory efficiency of Fixed Window Counter with the smoothness of
Sliding Window Log. It approximates the number of requests in the sliding window using:

    estimated_requests = current_window_requests + (previous_window_requests * (1 - progress_in_current_window))

Pros:
- Low memory footprint: Only requires storing counts for current and previous windows.
- Smooths out traffic spikes at window boundaries.
- 99.9% accuracy for real-world traffic distributions.
"""

import math
import threading
import time
from typing import Dict, Optional, Tuple
from implementations.rate_limiter.base import BaseRateLimiter, RateLimitResult


class SlidingWindowCounterRateLimiter(BaseRateLimiter):
    """
    Sliding Window Counter Rate Limiter.
    """

    def __init__(self, limit: int = 10, window_size_seconds: float = 1.0):
        """
        Args:
            limit: Maximum requests allowed in the rolling window.
            window_size_seconds: Window duration in seconds.
        """
        self.limit = limit
        self.window_size = float(window_size_seconds)
        # key -> (current_window_idx, current_count, prev_count)
        self._windows: Dict[str, Tuple[int, int, int]] = {}
        self._lock = threading.Lock()

    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            current_window_idx = int(math.floor(now / self.window_size))
            window_start = current_window_idx * self.window_size
            window_end = window_start + self.window_size
            time_into_window = now - window_start
            window_progress = time_into_window / self.window_size  # 0.0 to 1.0

            stored_window, curr_count, prev_count = self._windows.get(
                key, (current_window_idx, 0, 0)
            )

            # Advance window state if time progressed
            if current_window_idx == stored_window:
                pass
            elif current_window_idx == stored_window + 1:
                # Exactly one window advanced
                prev_count = curr_count
                curr_count = 0
                stored_window = current_window_idx
            else:
                # More than one window advanced; both windows expired
                prev_count = 0
                curr_count = 0
                stored_window = current_window_idx

            # Weighted approximation of requests within the sliding window
            overlap_weight = 1.0 - window_progress
            estimated_count = curr_count + (prev_count * overlap_weight)

            if estimated_count + tokens <= self.limit:
                curr_count += tokens
                self._windows[key] = (stored_window, curr_count, prev_count)
                remaining = max(0, int(self.limit - (estimated_count + tokens)))
                reset_after = max(0.0, window_end - now)
                return RateLimitResult(
                    allowed=True,
                    limit=self.limit,
                    remaining=remaining,
                    reset_after=round(reset_after, 4),
                    retry_after=None,
                )
            else:
                self._windows[key] = (stored_window, curr_count, prev_count)
                reset_after = max(0.001, window_end - now)
                return RateLimitResult(
                    allowed=False,
                    limit=self.limit,
                    remaining=0,
                    reset_after=round(reset_after, 4),
                    retry_after=round(reset_after, 4),
                )

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key:
                self._windows.pop(key, None)
            else:
                self._windows.clear()

