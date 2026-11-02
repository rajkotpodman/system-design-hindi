"""
Distributed Redis Rate Limiter
Chapter 4: Distributed Environments & Race Condition Mitigation

Description:
In a multi-server/microservice environment, memory-based rate limiters cannot share state.
This module implements a Redis-backed Distributed Rate Limiter utilizing atomic Lua scripting.
Using Lua guarantees that checking the limit and incrementing the counter happen atomically
on the Redis server without distributed lock contention or race conditions.

Includes an in-memory mock client when Redis is not running locally.
"""

import time
from typing import Optional
from implementations.rate_limiter.base import BaseRateLimiter, RateLimitResult

# Canonical Redis Lua Script for Atomic Sliding Window Counter
SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local clear_before = now - window

-- Remove timestamps older than window
redis.call('ZREMRANGEBYSCORE', key, '-inf', clear_before)

-- Count requests currently in window
local current_requests = redis.call('ZCARD', key)

if current_requests < limit then
    -- Add unique member: timestamp + microsecond random
    redis.call('ZADD', key, now, ARGV[4])
    redis.call('EXPIRE', key, math.ceil(window))
    return {1, limit - current_requests - 1, 0}
else
    -- Find oldest entry in window to calculate retry_after
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 1
    if #oldest > 1 then
        retry_after = (tonumber(oldest[2]) + window) - now
    end
    if retry_after < 0 then retry_after = 0.1 end
    return {0, 0, retry_after}
end
"""


class DistributedRedisRateLimiter(BaseRateLimiter):
    """
    Redis-backed rate limiter for distributed clusters.
    """

    def __init__(
        self,
        redis_client=None,
        redis_url: str = "redis://localhost:6379/0",
        limit: int = 10,
        window_size_seconds: float = 1.0,
    ):
        self.limit = limit
        self.window_size = float(window_size_seconds)
        self.client = redis_client
        self._script = None

        if self.client is None:
            try:
                import redis
                self.client = redis.Redis.from_url(redis_url, decode_responses=True)
                self.client.ping()
            except Exception:
                # Fallback to internal in-memory sliding log simulator
                from implementations.rate_limiter.sliding_window_log import SlidingWindowLogRateLimiter
                self._fallback = SlidingWindowLogRateLimiter(limit=limit, window_size_seconds=window_size_seconds)
                self.client = None

        if self.client:
            self._script = self.client.register_script(SLIDING_WINDOW_LUA)

    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        if self.client is None:
            return self._fallback.allow_request(key, tokens)

        now = time.time()
        redis_key = f"rl:{key}"
        member_id = f"{now}:{time.perf_counter()}"

        try:
            res = self._script(
                keys=[redis_key],
                args=[now, self.window_size, self.limit, member_id],
            )
            allowed = bool(res[0])
            remaining = int(res[1])
            retry_after = float(res[2]) if not allowed else None
            return RateLimitResult(
                allowed=allowed,
                limit=self.limit,
                remaining=remaining,
                reset_after=float(res[2]),
                retry_after=retry_after,
            )
        except Exception:
            # Degrade gracefully to fallback if redis becomes unreachable
            from implementations.rate_limiter.sliding_window_log import SlidingWindowLogRateLimiter
            if not hasattr(self, "_fallback"):
                self._fallback = SlidingWindowLogRateLimiter(limit=self.limit, window_size_seconds=self.window_size)
            return self._fallback.allow_request(key, tokens)

    def reset(self, key: Optional[str] = None) -> None:
        if self.client is None:
            if hasattr(self, "_fallback"):
                self._fallback.reset(key)
            return

        try:
            if key:
                self.client.delete(f"rl:{key}")
            else:
                for k in self.client.scan_iter("rl:*"):
                    self.client.delete(k)
        except Exception:
            pass

