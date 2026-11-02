import time
import pytest
from implementations.web_crawler import URLFrontier, CrawlTask
from implementations.notification_system import (
    NotificationEngine,
    NotificationRequest,
    Channel,
    Priority,
)
from implementations.news_feed import NewsFeedService
from implementations.chat_system import ChatService, UserStatus
from implementations.object_storage import ObjectStorageService
from implementations.stock_exchange import OrderBook, OrderSide
from implementations.proximity_service import ProximityService, Place, haversine_distance_km
from implementations.hotel_reservation import HotelReservationService


def test_web_crawler_frontier():
    frontier = URLFrontier(politeness_delay_seconds=0.1)
    assert frontier.add_url(CrawlTask("https://en.wikipedia.org/wiki/System_design")) is True
    # Duplicate URL rejected
    assert frontier.add_url(CrawlTask("https://en.wikipedia.org/wiki/System_design")) is False

    task = frontier.get_next_task()
    assert task is not None
    assert "System_design" in task.url


def test_notification_engine():
    engine = NotificationEngine(max_notifications_per_user_per_sec=10.0)
    req = NotificationRequest(
        recipient_id="user_123",
        channel=Channel.EMAIL,
        title="Welcome",
        body="Welcome to System Design!",
        idempotency_key="welcome_event_1",
    )
    res = engine.send(req)
    assert res.status == "SENT"

    # Duplicate suppression
    res_dup = engine.send(req)
    assert res_dup.status == "DUPLICATE"


def test_news_feed_hybrid_push_pull():
    feed = NewsFeedService(celebrity_threshold=3)
    # Alice is normal user, Elon is celebrity (threshold 3)
    feed.follow("Bob", "Alice")
    feed.follow("Bob", "Elon")
    feed.follow("Charlie", "Elon")
    feed.follow("Diana", "Elon")

    assert feed.is_celebrity("Elon") is True
    assert feed.is_celebrity("Alice") is False

    feed.create_post("Alice", "Hello from Alice!")
    feed.create_post("Elon", "Hello from Elon!")

    bob_feed = feed.get_feed("Bob")
    assert len(bob_feed) == 2


def test_chat_and_presence():
    chat = ChatService()
    chat.presence.heartbeat("Alice")
    assert chat.presence.get_status("Alice") == UserStatus.ONLINE

    msg = chat.send_direct_message("Alice", "Bob", "Hello Bob!")
    assert msg.sender_id == "Alice"
    assert msg.content == "Hello Bob!"


def test_object_storage_deduplication():
    store = ObjectStorageService(chunk_size=512)
    chunk = b"X" * 512
    data1 = chunk * 4 + b"1"
    data2 = chunk * 4 + b"2"

    store.put_object("b", "f1", data1)
    store.put_object("b", "f2", data2)

    stats = store.get_storage_stats()
    assert stats["saved_bytes"] > 0
    assert store.get_object("b", "f1") == data1


def test_stock_exchange_matching():
    book = OrderBook(symbol="MSFT")
    book.place_limit_order(OrderSide.SELL, 200.0, 50)
    order, trades = book.place_limit_order(OrderSide.BUY, 205.0, 50)

    assert len(trades) == 1
    assert trades[0].price == 200.0
    assert trades[0].quantity == 50
    assert order.remaining_quantity == 0


def test_proximity_haversine():
    # Distance between New York (40.7128, -74.0060) and London (51.5074, -0.1278) ~ 5570 km
    d = haversine_distance_km(40.7128, -74.0060, 51.5074, -0.1278)
    assert 5500 < d < 5600

    service = ProximityService()
    service.add_place(Place("p1", "Central Park Coffee", 40.785091, -73.968285, "cafe"))
    results = service.search_nearby(40.785000, -73.968000, radius_km=1.0)
    assert len(results) == 1


def test_hotel_reservation():
    service = HotelReservationService(hold_duration_seconds=60)
    service.set_inventory("hotel_1", "deluxe", "2026-12-01", total_rooms=1)

    assert service.get_available_rooms("hotel_1", "deluxe", "2026-12-01") == 1
    res = service.reserve_hold("user_1", "hotel_1", "deluxe", "2026-12-01", "2026-12-02")
    assert res.status.value == "PENDING"

    # Now 0 available
    assert service.get_available_rooms("hotel_1", "deluxe", "2026-12-01") == 0

    confirmed = service.confirm_reservation(res.reservation_id)
    assert confirmed.status.value == "CONFIRMED"

