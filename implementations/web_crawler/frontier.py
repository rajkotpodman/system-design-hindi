"""
URL Frontier with Politeness & Deduplication
Chapter 9: Design A Web Crawler

Key Components:
1. URL Deduplication: Ensures every URL is crawled at most once.
2. Politeness Manager: Distributes URLs into per-host queues with minimum inter-request delay
   to prevent overloading remote web servers.
3. Priority Scheduler: High-authority domains (e.g. Wikipedia, news) are given priority.
4. Content Deduplication: Checks content hash (MD5/SimHash) to eliminate mirrored web pages.
"""

from collections import deque
from dataclasses import dataclass
import hashlib
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse
from implementations.url_shortener.bloom_filter import BloomFilter


@dataclass
class CrawlTask:
    url: str
    priority: int = 1  # Lower number = higher priority
    depth: int = 0


class URLFrontier:
    """
    Politeness-aware URL Frontier.
    """

    def __init__(self, politeness_delay_seconds: float = 0.5):
        self.delay = politeness_delay_seconds
        # host -> deque of CrawlTask
        self._host_queues: Dict[str, deque] = {}
        # host -> timestamp of last download
        self._last_download_time: Dict[str, float] = {}
        # Seen URLs filter
        self._seen_urls = BloomFilter(expected_elements=500_000)
        # Seen Content hashes (MD5)
        self._seen_content_hashes: Set[str] = set()

    def add_url(self, task: CrawlTask) -> bool:
        """
        Add a URL to the frontier.
        Returns True if newly added, False if duplicate.
        """
        # Normalize URL
        url = task.url.strip()
        if self._seen_urls.contains(url):
            return False

        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if not host:
            return False

        self._seen_urls.add(url)
        if host not in self._host_queues:
            self._host_queues[host] = deque()

        self._host_queues[host].append(task)
        return True

    def get_next_task(self) -> Optional[CrawlTask]:
        """
        Polls the next eligible URL task respecting per-host politeness delays.
        """
        now = time.time()
        for host, q in list(self._host_queues.items()):
            if not q:
                continue

            last_time = self._last_download_time.get(host, 0.0)
            if now - last_time >= self.delay:
                task = q.popleft()
                self._last_download_time[host] = now
                return task

        return None

    def is_content_duplicate(self, content: str) -> bool:
        """Verify if HTML content was already downloaded previously."""
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        if content_hash in self._seen_content_hashes:
            return True
        self._seen_content_hashes.add(content_hash)
        return False

    @property
    def total_pending(self) -> int:
        return sum(len(q) for q in self._host_queues.values())

