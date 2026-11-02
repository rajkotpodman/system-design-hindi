import time
import pytest
from implementations.rate_limiter import (
    TokenBucketRateLimiter,
    LeakyBucketRateLimiter,
    FixedWindowCounterRateLimiter,
    SlidingWindowLogRateLimiter,
    SlidingWindowCounterRateLimiter,
)


def test_token_bucket():
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)
    # 3 initial tokens
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is True
    # 4th request within same second must be throttled
    res = limiter.allow_request("u1")
    assert res.allowed is False
    assert res.retry_after is not None
    assert res.retry_after > 0


def test_leaky_bucket():
    limiter = LeakyBucketRateLimiter(capacity=2, leak_rate=1.0)
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is False


def test_fixed_window():
    limiter = FixedWindowCounterRateLimiter(limit=2, window_size_seconds=1.0)
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is False


def test_sliding_window_log():
    limiter = SlidingWindowLogRateLimiter(limit=2, window_size_seconds=0.5)
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is False
    time.sleep(0.55)
    assert limiter.allow_request("u1").allowed is True


def test_sliding_window_counter():
    limiter = SlidingWindowCounterRateLimiter(limit=2, window_size_seconds=1.0)
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is True
    assert limiter.allow_request("u1").allowed is False

