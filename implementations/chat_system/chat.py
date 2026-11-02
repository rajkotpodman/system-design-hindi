"""
Real-Time Chat & Presence System
Chapter 12: Design A Chat System

Architecture:
1. Presence Server:
   - Tracks online/offline/away status via heartbeats.
   - Publishes presence change events to friends/contacts.
2. Real-Time Message Routing:
   - Direct 1-on-1 messaging.
   - Group chat rooms.
   - Delivery status receipts: SENT -> DELIVERED -> READ.
3. Message Synchronization:
   - Monotonic message sequence per chat room.
"""

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import threading
import time
from typing import Dict, List, Optional, Set
import uuid


class DeliveryStatus(str, Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"


class UserStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    AWAY = "AWAY"


@dataclass
class ChatMessage:
    message_id: str
    channel_id: str
    sender_id: str
    recipient_id: Optional[str]  # None for group chat
    content: str
    timestamp: float
    sequence_id: int
    status: DeliveryStatus = DeliveryStatus.SENT


class PresenceServer:
    """Manages online heartbeats and friend notifications."""

    def __init__(self, heartbeat_timeout_seconds: float = 30.0):
        self.timeout = heartbeat_timeout_seconds
        # user_id -> last_heartbeat
        self._heartbeats: Dict[str, float] = {}
        self._lock = threading.Lock()

    def heartbeat(self, user_id: str) -> None:
        with self._lock:
            self._heartbeats[user_id] = time.time()

    def get_status(self, user_id: str) -> UserStatus:
        with self._lock:
            last = self._heartbeats.get(user_id)
            if not last:
                return UserStatus.OFFLINE
            if time.time() - last <= self.timeout:
                return UserStatus.ONLINE
            return UserStatus.OFFLINE

    def set_offline(self, user_id: str) -> None:
        with self._lock:
            self._heartbeats.pop(user_id, None)


class ChatService:
    """
    Real-time chat router and synchronization manager.
    """

    def __init__(self):
        self.presence = PresenceServer()
        # channel_id -> list of ChatMessage
        self._messages: Dict[str, List[ChatMessage]] = {}
        # channel_id -> set of member user_ids
        self._channels: Dict[str, Set[str]] = {}
        # channel_id -> current sequence
        self._sequence_counters: Dict[str, int] = {}
        self._lock = threading.Lock()

    def create_channel(self, channel_id: str, member_ids: List[str]) -> None:
        with self._lock:
            self._channels[channel_id] = set(member_ids)
            self._messages[channel_id] = []
            self._sequence_counters[channel_id] = 0

    def send_direct_message(self, sender_id: str, recipient_id: str, content: str) -> ChatMessage:
        """Route 1-to-1 direct message."""
        # Canonical 1-on-1 channel id
        channel_id = ":".join(sorted([sender_id, recipient_id]))
        with self._lock:
            if channel_id not in self._channels:
                self._channels[channel_id] = {sender_id, recipient_id}
                self._messages[channel_id] = []
                self._sequence_counters[channel_id] = 0

            self._sequence_counters[channel_id] += 1
            seq = self._sequence_counters[channel_id]

            # If recipient is online, status starts as DELIVERED, else SENT
            recipient_status = self.presence.get_status(recipient_id)
            status = DeliveryStatus.DELIVERED if recipient_status == UserStatus.ONLINE else DeliveryStatus.SENT

            msg = ChatMessage(
                message_id=f"msg_{uuid.uuid4().hex[:10]}",
                channel_id=channel_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content,
                timestamp=time.time(),
                sequence_id=seq,
                status=status,
            )
            self._messages[channel_id].append(msg)
            return msg

    def mark_read(self, message_id: str, channel_id: str) -> bool:
        with self._lock:
            for msg in self._messages.get(channel_id, []):
                if msg.message_id == message_id:
                    msg.status = DeliveryStatus.READ
                    return True
            return False

    def get_messages(self, channel_id: str, limit: int = 50) -> List[ChatMessage]:
        with self._lock:
            return list(self._messages.get(channel_id, []))[-limit:]

