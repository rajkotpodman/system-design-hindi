"""
News Feed System (Fan-Out on Write & Fan-Out on Read)
Chapter 11: Design A News Feed System

Architecture:
1. Feed Publishing:
   - Normal users: Fan-out on Write (Push model) -> Injects post_id into followers' feed caches.
   - Celebrity users (high follower count): Fan-out on Read (Pull model) -> Posts are fetched
     and merged dynamically when a follower opens their feed to avoid write amplification.
2. Feed Retrieval:
   - Merges pre-computed push feed cache with celebrity pull posts.
   - Sorts feed items by creation timestamp descending.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import threading
import time
from typing import Dict, List, Optional, Set
import uuid


@dataclass
class Post:
    post_id: str
    user_id: str
    content: str
    created_at: float


class NewsFeedService:
    """
    Hybrid push/pull news feed pipeline.
    """

    def __init__(self, celebrity_threshold: int = 5):
        self.celebrity_threshold = celebrity_threshold
        # user_id -> set of followers
        self._followers: Dict[str, Set[str]] = {}
        # user_id -> set of followed users
        self._following: Dict[str, Set[str]] = {}
        # user_id -> list of Post objects authored by user
        self._user_posts: Dict[str, List[Post]] = {}
        # user_id -> pre-computed timeline of Post objects (Fan-out cache)
        self._feed_cache: Dict[str, List[Post]] = {}
        self._lock = threading.Lock()

    def follow(self, follower_id: str, followee_id: str) -> None:
        with self._lock:
            self._followers.setdefault(followee_id, set()).add(follower_id)
            self._following.setdefault(follower_id, set()).add(followee_id)

    def unfollow(self, follower_id: str, followee_id: str) -> None:
        with self._lock:
            if followee_id in self._followers:
                self._followers[followee_id].discard(follower_id)
            if follower_id in self._following:
                self._following[follower_id].discard(followee_id)

    def is_celebrity(self, user_id: str) -> bool:
        return len(self._followers.get(user_id, set())) >= self.celebrity_threshold

    def create_post(self, user_id: str, content: str) -> Post:
        """
        Publish a post and execute fan-out according to author follower status.
        """
        post = Post(
            post_id=f"post_{uuid.uuid4().hex[:10]}",
            user_id=user_id,
            content=content,
            created_at=time.time(),
        )

        with self._lock:
            self._user_posts.setdefault(user_id, []).append(post)

            # Fan-out on Write (Push) only if user is NOT a celebrity
            if not self.is_celebrity(user_id):
                followers = self._followers.get(user_id, set())
                for fid in followers:
                    cache = self._feed_cache.setdefault(fid, [])
                    cache.insert(0, post)
                    if len(cache) > 800:
                        cache.pop()

        return post

    def get_feed(self, user_id: str, limit: int = 20) -> List[Post]:
        """
        Retrieve news feed:
        1. Fetch pre-computed posts from push cache.
        2. Pull recent posts from followed celebrities (Fan-out on Read).
        3. Merge and rank by timestamp descending.
        """
        with self._lock:
            cached_posts = list(self._feed_cache.get(user_id, []))
            followed = self._following.get(user_id, set())

            celebrity_posts: List[Post] = []
            for target_id in followed:
                if self.is_celebrity(target_id):
                    recent = self._user_posts.get(target_id, [])[-limit:]
                    celebrity_posts.extend(recent)

        # Merge and sort
        combined = cached_posts + celebrity_posts
        # Deduplicate
        seen = set()
        unique = []
        for p in combined:
            if p.post_id not in seen:
                seen.add(p.post_id)
                unique.append(p)

        unique.sort(key=lambda p: p.created_at, reverse=True)
        return unique[:limit]

