import pytest
from implementations.unique_id_generator import SnowflakeIDGenerator, Base62, TicketServer


def test_snowflake_uniqueness_and_ordering():
    gen = SnowflakeIDGenerator(datacenter_id=1, worker_id=2)
    ids = [gen.generate() for _ in range(1000)]

    # Check 100% uniqueness
    assert len(set(ids)) == 1000

    # Check monotonic increase
    for i in range(len(ids) - 1):
        assert ids[i] < ids[i + 1]


def test_snowflake_decomposition():
    gen = SnowflakeIDGenerator(datacenter_id=3, worker_id=4)
    uid = gen.generate()
    parts = gen.parse(uid)

    assert parts.datacenter_id == 3
    assert parts.worker_id == 4
    assert parts.timestamp_ms > 0


def test_base62_roundtrip():
    test_numbers = [0, 1, 61, 62, 1000, 99999999, 1234567890123456]
    for num in test_numbers:
        encoded = Base62.encode(num)
        decoded = Base62.decode(encoded)
        assert decoded == num


def test_ticket_server():
    server = TicketServer(server_id=1, step=2, start=1)
    assert server.next_id() == 1
    assert server.next_id() == 3
    assert server.next_id() == 5

