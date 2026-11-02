"""
URL Shortener Service
Chapter 8: Design A URL Shortener

Architecture:
1. Distributed ID Generation: Twitter Snowflake produces 64-bit monotonically increasing IDs.
2. Short Code Generation: Base62 encodes the 64-bit ID into a 7-8 char string.
3. Multi-tier Caching:
   - Bloom Filter quickly discards non-existent codes without hitting cache or disk.
   - LRU In-Memory Cache answers hot reads in microseconds.
   - Persistent store holds long URLs, metadata, and expiration.
4. Analytics: Tracks total clicks, creation timestamp, last accessed timestamp.
"""

from dataclasses import dataclass
import threading
import time
from typing import Dict, List, Optional
from implementations.unique_id_generator.snowflake import SnowflakeIDGenerator
from implementations.unique_id_generator.base62 import Base62
from implementations.url_shortener.bloom_filter import BloomFilter
from implementations.url_shortener.lru_cache import LRUCache


@dataclass
class URLMetadata:
    short_code: str
    long_url: str
    created_at: float
    expires_at: Optional[float] = None
    click_count: int = 0
    last_accessed: Optional[float] = None


class URLShortenerService:
    """
    End-to-end URL Shortening Engine.
    """

    def __init__(
        self,
        base_domain: str = "https://short.io/",
        cache_capacity: int = 10_000,
        bloom_expected: int = 100_000,
    ):
        self.base_domain = base_domain.rstrip("/") + "/"
        self._id_generator = SnowflakeIDGenerator(datacenter_id=1, worker_id=1)
        self._cache = LRUCache(capacity=cache_capacity)
        self._bloom = BloomFilter(expected_elements=bloom_expected)
        self._db: Dict[str, URLMetadata] = {}
        self._reverse_lookup: Dict[str, str] = {}  # long_url -> short_code
        self._lock = threading.Lock()

    def shorten(
        self,
        long_url: str,
        custom_alias: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> URLMetadata:
        """
        Create a shortened URL for long_url. If already shortened, return existing metadata.
        """
        if not long_url.startswith(("http://", "https://")):
            long_url = "https://" + long_url

        with self._lock:
            # Check if long_url already has an active short code
            if not custom_alias and long_url in self._reverse_lookup:
                existing_code = self._reverse_lookup[long_url]
                entry = self._db.get(existing_code)
                if entry and (entry.expires_at is None or entry.expires_at > time.time()):
                    return entry

            now = time.time()
            expires_at = (now + ttl_seconds) if ttl_seconds else None

            if custom_alias:
                if custom_alias in self._db:
                    raise ValueError(f"Custom alias '{custom_alias}' is already in use.")
                short_code = custom_alias
            else:
                # Generate unique ID via Snowflake, then encode via Base62
                snowflake_id = self._id_generator.generate()
                short_code = Base62.encode(snowflake_id)

            metadata = URLMetadata(
                short_code=short_code,
                long_url=long_url,
                created_at=now,
                expires_at=expires_at,
                click_count=0,
                last_accessed=None,
            )

            self._db[short_code] = metadata
            self._reverse_lookup[long_url] = short_code
            self._bloom.add(short_code)
            self._cache.put(short_code, long_url)

            return metadata

    def resolve(self, short_code: str) -> Optional[str]:
        """
        Resolve a short code into the original long URL and increment click metrics.
        Returns None if not found or expired.
        """
        # Step 1: Bloom filter pre-check (eliminates 99% of invalid requests)
        if not self._bloom.contains(short_code):
            return None

        # Step 2: Check LRU cache
        cached_url = self._cache.get(short_code)

        with self._lock:
            metadata = self._db.get(short_code)
            if not metadata:
                return None

            # Step 3: Check TTL expiration
            if metadata.expires_at and metadata.expires_at <= time.time():
                # Expired: evict from cache and db
                self._cache.delete(short_code)
                self._db.pop(short_code, None)
                self._reverse_lookup.pop(metadata.long_url, None)
                return None

            # Update click analytics
            metadata.click_count += 1
            metadata.last_accessed = time.time()

            if not cached_url:
                self._cache.put(short_code, metadata.long_url)

            return metadata.long_url

    def get_metadata(self, short_code: str) -> Optional[URLMetadata]:
        """Fetch metadata and analytics for a short code."""
        with self._lock:
            entry = self._db.get(short_code)
            if entry and (entry.expires_at is None or entry.expires_at > time.time()):
                return entry
            return None

    def get_all(self, limit: int = 50) -> List[URLMetadata]:
        with self._lock:
            return list(self._db.values())[:limit]

