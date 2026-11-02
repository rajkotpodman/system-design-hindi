"""
Notification System Engine
Chapter 10: Design A Notification System

Features:
1. Multi-channel delivery routing: SMS, EMAIL, PUSH (APNs / FCM).
2. Rate Limiting per recipient: Prevents spamming a user with excessive notifications.
3. Idempotent Deduplication: Rejects duplicate notifications using event hashes.
4. Priority-based Queues: High priority (OTP, Alerts) vs Normal/Low priority (Marketing).
5. Retry mechanism with exponential backoff for transient delivery failures.
"""

from dataclasses import dataclass
from enum import Enum
import threading
import time
from typing import Callable, Dict, List, Optional
import uuid
from implementations.rate_limiter.token_bucket import TokenBucketRateLimiter


class Channel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class Priority(int, Enum):
    HIGH = 1    # Immediate (OTP, 2FA, Fraud Alerts)
    NORMAL = 2  # Standard (Messages, Order Updates)
    LOW = 3     # Deferred (Marketing, Newsletters)


@dataclass
class NotificationRequest:
    recipient_id: str
    channel: Channel
    title: str
    body: str
    priority: Priority = Priority.NORMAL
    idempotency_key: Optional[str] = None


@dataclass
class DeliveryResult:
    notification_id: str
    recipient_id: str
    channel: Channel
    status: str  # "SENT", "RATE_LIMITED", "DUPLICATE", "FAILED"
    attempts: int
    error: Optional[str] = None


class NotificationEngine:
    """
    Notification dispatch pipeline.
    """

    def __init__(self, max_notifications_per_user_per_sec: float = 2.0):
        # Per-user rate limiter
        self._user_limiter = TokenBucketRateLimiter(capacity=5, refill_rate=max_notifications_per_user_per_sec)
        self._seen_keys: Dict[str, float] = {}
        self._history: List[DeliveryResult] = []
        self._lock = threading.Lock()

    def send(
        self,
        request: NotificationRequest,
        provider_send_func: Optional[Callable[[NotificationRequest], bool]] = None,
        max_retries: int = 3,
    ) -> DeliveryResult:
        """Process and deliver notification."""
        notif_id = f"notif_{uuid.uuid4().hex[:10]}"

        # 1. Deduplication check
        if request.idempotency_key:
            with self._lock:
                if request.idempotency_key in self._seen_keys:
                    res = DeliveryResult(
                        notification_id=notif_id,
                        recipient_id=request.recipient_id,
                        channel=request.channel,
                        status="DUPLICATE",
                        attempts=0,
                        error="Duplicate notification suppressed.",
                    )
                    self._history.append(res)
                    return res
                self._seen_keys[request.idempotency_key] = time.time()

        # 2. Rate limiting check per recipient
        rl_res = self._user_limiter.allow_request(request.recipient_id)
        if not rl_res.allowed:
            res = DeliveryResult(
                notification_id=notif_id,
                recipient_id=request.recipient_id,
                channel=request.channel,
                status="RATE_LIMITED",
                attempts=0,
                error="Recipient rate limit exceeded.",
            )
            with self._lock:
                self._history.append(res)
            return res

        # 3. Delivery dispatch with retry logic
        attempts = 0
        success = False
        last_error = None

        while attempts < max_retries and not success:
            attempts += 1
            try:
                if provider_send_func:
                    success = provider_send_func(request)
                else:
                    # Simulated mock provider success
                    success = True
            except Exception as e:
                last_error = str(e)
                time.sleep(0.01 * (2 ** (attempts - 1)))  # Exponential backoff

        status = "SENT" if success else "FAILED"
        result = DeliveryResult(
            notification_id=notif_id,
            recipient_id=request.recipient_id,
            channel=request.channel,
            status=status,
            attempts=attempts,
            error=last_error if not success else None,
        )

        with self._lock:
            self._history.append(result)
        return result

    def get_history(self) -> List[DeliveryResult]:
        with self._lock:
            return list(self._history)

