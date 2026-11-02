"""
SkipList Data Structure & Real-Time Gaming Leaderboard
Chapter 25: Real-time Gaming Leaderboard

Redis ZSET is powered by a SkipList combined with a Hash Map.
- Hash Map: player_id -> score (O(1) lookup).
- SkipList: sorted by score descending, then player_id ascending.
  Provides O(log N) insertion, O(log N) rank calculation, and O(K + log N) range queries.
"""

from dataclasses import dataclass
import random
import threading
from typing import Dict, List, Optional, Tuple


@dataclass
class LeaderboardEntry:
    player_id: str
    score: float
    rank: int


class _SkipListNode:
    def __init__(self, player_id: str, score: float, level: int):
        self.player_id = player_id
        self.score = score
        # forward pointers at each level
        self.forward: List[Optional["_SkipListNode"]] = [None] * level
        # span[i]: distance (number of elements) spanned by forward[i] pointer
        self.span: List[int] = [0] * level


class SkipList:
    """
    Probabilistic SkipList supporting rank calculations (spanning tree).
    Sorted by (-score, player_id).
    """

    MAX_LEVEL = 32
    P = 0.25

    def __init__(self):
        self.header = _SkipListNode(player_id="", score=0.0, level=self.MAX_LEVEL)
        self.level = 1
        self.length = 0

    def _random_level(self) -> int:
        lvl = 1
        while random.random() < self.P and lvl < self.MAX_LEVEL:
            lvl += 1
        return lvl

    def _compare(self, score1: float, id1: str, score2: float, id2: str) -> int:
        # Descending by score; ascending by player_id
        if score1 > score2:
            return -1
        elif score1 < score2:
            return 1
        else:
            if id1 < id2:
                return -1
            elif id1 > id2:
                return 1
            return 0

    def insert(self, player_id: str, score: float) -> None:
        update = [None] * self.MAX_LEVEL
        rank = [0] * self.MAX_LEVEL

        curr = self.header
        for i in range(self.level - 1, -1, -1):
            rank[i] = rank[i + 1] if i + 1 < self.level else 0
            while curr.forward[i] and self._compare(curr.forward[i].score, curr.forward[i].player_id, score, player_id) < 0:
                rank[i] += curr.span[i]
                curr = curr.forward[i]
            update[i] = curr

        new_level = self._random_level()
        if new_level > self.level:
            for i in range(self.level, new_level):
                rank[i] = 0
                update[i] = self.header
                update[i].span[i] = self.length
            self.level = new_level

        new_node = _SkipListNode(player_id, score, new_level)
        for i in range(new_level):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

            new_node.span[i] = update[i].span[i] - (rank[0] - rank[i])
            update[i].span[i] = (rank[0] - rank[i]) + 1

        for i in range(new_level, self.level):
            update[i].span[i] += 1

        self.length += 1

    def delete(self, player_id: str, score: float) -> bool:
        update = [None] * self.MAX_LEVEL
        curr = self.header

        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and self._compare(curr.forward[i].score, curr.forward[i].player_id, score, player_id) < 0:
                curr = curr.forward[i]
            update[i] = curr

        target = curr.forward[0]
        if target and target.player_id == player_id and target.score == score:
            for i in range(self.level):
                if update[i].forward[i] == target:
                    update[i].span[i] += target.span[i] - 1
                    update[i].forward[i] = target.forward[i]
                else:
                    update[i].span[i] -= 1

            while self.level > 1 and self.header.forward[self.level - 1] is None:
                self.level -= 1

            self.length -= 1
            return True
        return False

    def get_rank(self, player_id: str, score: float) -> Optional[int]:
        """Returns 1-based rank of the element."""
        rank = 0
        curr = self.header
        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and self._compare(curr.forward[i].score, curr.forward[i].player_id, score, player_id) <= 0:
                rank += curr.span[i]
                if curr.forward[i].player_id == player_id:
                    return rank
                curr = curr.forward[i]
        return None

    def get_range(self, start_rank: int, count: int) -> List[Tuple[str, float, int]]:
        """Retrieve slice of nodes from 1-based start_rank."""
        if start_rank < 1 or count <= 0:
            return []

        curr = self.header
        accumulated = 0

        # Traverse to node at start_rank
        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and (accumulated + curr.span[i]) < start_rank:
                accumulated += curr.span[i]
                curr = curr.forward[i]

        curr = curr.forward[0]
        accumulated += 1

        results = []
        while curr and len(results) < count:
            results.append((curr.player_id, curr.score, accumulated))
            accumulated += 1
            curr = curr.forward[0]

        return results


class LeaderboardService:
    """
    Real-Time Gaming Leaderboard with Redis-like ZSET semantics.
    """

    def __init__(self):
        self._skiplist = SkipList()
        self._scores: Dict[str, float] = {}
        self._lock = threading.RLock()

    def update_score(self, player_id: str, score: float) -> LeaderboardEntry:
        """Add or update player score. If player exists, updates position."""
        with self._lock:
            if player_id in self._scores:
                old_score = self._scores[player_id]
                self._skiplist.delete(player_id, old_score)

            self._scores[player_id] = score
            self._skiplist.insert(player_id, score)
            rank = self._skiplist.get_rank(player_id, score) or 1

            return LeaderboardEntry(player_id=player_id, score=score, rank=rank)

    def increment_score(self, player_id: str, delta: float) -> LeaderboardEntry:
        """Increment existing score or initialize with delta."""
        with self._lock:
            current = self._scores.get(player_id, 0.0)
            return self.update_score(player_id, current + delta)

    def get_player(self, player_id: str) -> Optional[LeaderboardEntry]:
        """Fetch current score and rank of player."""
        with self._lock:
            if player_id not in self._scores:
                return None
            score = self._scores[player_id]
            rank = self._skiplist.get_rank(player_id, score)
            if rank is None:
                return None
            return LeaderboardEntry(player_id=player_id, score=score, rank=rank)

    def get_top_k(self, k: int = 10) -> List[LeaderboardEntry]:
        """Get top K players."""
        with self._lock:
            items = self._skiplist.get_range(1, k)
            return [
                LeaderboardEntry(player_id=pid, score=sc, rank=rk)
                for pid, sc, rk in items
            ]

    def get_around_player(self, player_id: str, radius: int = 2) -> List[LeaderboardEntry]:
        """Get players immediately above and below the given player."""
        with self._lock:
            player = self.get_player(player_id)
            if not player:
                return []
            start_rank = max(1, player.rank - radius)
            count = (radius * 2) + 1
            items = self._skiplist.get_range(start_rank, count)
            return [
                LeaderboardEntry(player_id=pid, score=sc, rank=rk)
                for pid, sc, rk in items
            ]

    @property
    def total_players(self) -> int:
        with self._lock:
            return len(self._scores)

