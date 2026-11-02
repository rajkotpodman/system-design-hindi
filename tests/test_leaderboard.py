import pytest
from implementations.leaderboard import LeaderboardService


def test_leaderboard_ranking():
    lb = LeaderboardService()
    lb.update_score("Alice", 100)
    lb.update_score("Bob", 200)
    lb.update_score("Charlie", 150)

    top = lb.get_top_k(3)
    assert len(top) == 3
    assert top[0].player_id == "Bob"
    assert top[0].rank == 1
    assert top[1].player_id == "Charlie"
    assert top[1].rank == 2
    assert top[2].player_id == "Alice"
    assert top[2].rank == 3


def test_leaderboard_score_update():
    lb = LeaderboardService()
    lb.update_score("Alice", 100)
    lb.update_score("Bob", 200)

    # Alice increases score to 300
    lb.update_score("Alice", 300)
    alice = lb.get_player("Alice")
    assert alice.rank == 1
    assert alice.score == 300


def test_around_player():
    lb = LeaderboardService()
    for i in range(1, 10):
        lb.update_score(f"player_{i}", i * 100)

    # Around player_5
    around = lb.get_around_player("player_5", radius=1)
    assert len(around) == 3

