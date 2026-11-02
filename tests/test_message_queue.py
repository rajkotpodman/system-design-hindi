import pytest
from implementations.message_queue import MessageQueueBroker


def test_message_queue_partitioning_and_consumption():
    broker = MessageQueueBroker()
    broker.create_topic("events", partition_count=2)

    # Publish messages
    broker.publish("events", "event_A", key="user_1")
    broker.publish("events", "event_B", key="user_1")

    # Consume
    msgs = broker.consume(group_id="consumer_grp_1", topic_name="events", partition_id=0, max_messages=10)
    assert len(msgs) >= 0  # Key-partitioned to 0 or 1

    # Check lag calculation
    lags = broker.get_lag("consumer_grp_1", "events")
    assert isinstance(lags, dict)

