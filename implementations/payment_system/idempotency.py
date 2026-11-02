"""
Idempotency Manager & Reconciliation Engine
Chapter 26: Payment System

Components:
1. IdempotencyManager: Ensures that retried payment API calls do not double-charge customers.
   Tracks status transitions: STARTED -> COMMITTED / FAILED.
2. ReconciliationEngine: Matches internal payment journal entries with third-party payment
   gateway reports to identify discrepancies, orphan charges, or mismatched fees.
"""

from dataclasses import dataclass
from enum import Enum
import threading
import time
from typing import Any, Dict, List, Optional


class IdempotencyStatus(str, Enum):
    STARTED = "STARTED"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"


@dataclass
class IdempotencyRecord:
    key: str
    status: IdempotencyStatus
    response_data: Optional[Dict[str, Any]] = None
    created_at: float = 0.0


class IdempotencyManager:
    """
    In-memory idempotency state machine (simulating Redis/DB idempotency table).
    """

    def __init__(self, ttl_seconds: int = 86400):
        self.ttl = ttl_seconds
        self._store: Dict[str, IdempotencyRecord] = {}
        self._lock = threading.Lock()

    def try_acquire(self, key: str) -> Optional[IdempotencyRecord]:
        """
        Attempt to start execution with key.
        Returns None if key is acquired, or the existing record if already in progress or completed.
        """
        with self._lock:
            now = time.time()
            existing = self._store.get(key)
            if existing:
                if (now - existing.created_at) > self.ttl:
                    # Expired record, re-acquire
                    pass
                else:
                    return existing

            record = IdempotencyRecord(key=key, status=IdempotencyStatus.STARTED, created_at=now)
            self._store[key] = record
            return None

    def commit(self, key: str, response: Dict[str, Any]) -> None:
        with self._lock:
            if key in self._store:
                self._store[key].status = IdempotencyStatus.COMMITTED
                self._store[key].response_data = response

    def fail(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                self._store[key].status = IdempotencyStatus.FAILED


@dataclass
class SettlementRecord:
    gateway_tx_id: str
    internal_ref_id: str
    amount_cents: int
    fee_cents: int
    status: str


@dataclass
class ReconciliationReport:
    total_matched: int
    total_discrepancies: int
    missing_in_internal: List[SettlementRecord]
    missing_in_gateway: List[str]
    amount_mismatches: List[Dict[str, Any]]


class ReconciliationEngine:
    """
    Compares internal payment records with gateway settlement statements.
    """

    @staticmethod
    def reconcile(
        internal_records: Dict[str, int],  # internal_ref_id -> expected amount_cents
        settlement_records: List[SettlementRecord],
    ) -> ReconciliationReport:
        matched = 0
        missing_internal = []
        amount_mismatches = []
        seen_internal_ids = set()

        for st in settlement_records:
            ref_id = st.internal_ref_id
            seen_internal_ids.add(ref_id)

            if ref_id not in internal_records:
                missing_internal.append(st)
            else:
                expected_amt = internal_records[ref_id]
                if expected_amt != st.amount_cents:
                    amount_mismatches.append({
                        "ref_id": ref_id,
                        "expected_cents": expected_amt,
                        "settlement_cents": st.amount_cents,
                        "difference_cents": st.amount_cents - expected_amt,
                    })
                else:
                    matched += 1

        missing_gateway = [
            ref_id for ref_id in internal_records if ref_id not in seen_internal_ids
        ]

        return ReconciliationReport(
            total_matched=matched,
            total_discrepancies=len(missing_internal) + len(missing_gateway) + len(amount_mismatches),
            missing_in_internal=missing_internal,
            missing_in_gateway=missing_gateway,
            amount_mismatches=amount_mismatches,
        )

