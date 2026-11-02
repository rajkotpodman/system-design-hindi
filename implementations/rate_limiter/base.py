"""
Base interface and data models for Rate Limiting algorithms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_after: float  # seconds until rate limit resets or permits next request
    retry_after: Optional[float] = None  # seconds to wait if throttled


class BaseRateLimiter(ABC):
    """Abstract base class for all rate limiter algorithms."""

    @abstractmethod
    def allow_request(self, key: str, tokens: int = 1) -> RateLimitResult:
        """
        Check if a request is allowed under the rate limit for the given key.

        Args:
            key: Unique identifier for the client (e.g. IP address or user ID)
            tokens: Number of tokens/requests consumed (default 1)

        Returns:
            RateLimitResult containing decision and metadata
        """
        pass

    @abstractmethod
    def reset(self, key: Optional[str] = None) -> None:
        """Reset limits for a specific key or all keys if key is None."""
        pass

