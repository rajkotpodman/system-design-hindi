"""
High-Concurrency Digital Wallet Engine
Chapter 27: Digital Wallet

Features:
- Deadlock-Free Transfers: Employs strict lock-ordering (locking by sorted account_id).
- ACID Guarantees: All transfers are atomic; balance deductions and additions happen together.
- Invariant Checking: Strict checks ensure accounts never drop below zero.
- Complete Audit History: Every transfer emits an immutable transaction record.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from typing import Dict, List, Optional
import uuid


@dataclass
class WalletTransaction:
    tx_id: str
    from_account: Optional[str]
    to_account: Optional[str]
    amount_cents: int
    tx_type: str  # "DEPOSIT", "WITHDRAWAL", "TRANSFER"
    timestamp: str
    status: str  # "SUCCESS", "REJECTED"


class DigitalWalletService:
    """
    High-concurrency wallet system with dead-lock prevention.
    """

    def __init__(self):
        self._balances: Dict[str, int] = {}  # account_id -> balance_cents
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
        self._history: List[WalletTransaction] = []

    def _get_account_lock(self, account_id: str) -> threading.Lock:
        with self._global_lock:
            if account_id not in self._locks:
                self._locks[account_id] = threading.Lock()
            return self._locks[account_id]

    def create_wallet(self, account_id: str, initial_deposit_cents: int = 0) -> int:
        with self._global_lock:
            if account_id not in self._balances:
                self._balances[account_id] = 0
                self._locks[account_id] = threading.Lock()

        if initial_deposit_cents > 0:
            self.deposit(account_id, initial_deposit_cents)

        return self._balances[account_id]

    def get_balance(self, account_id: str) -> int:
        lock = self._get_account_lock(account_id)
        with lock:
            if account_id not in self._balances:
                raise ValueError(f"Wallet '{account_id}' does not exist.")
            return self._balances[account_id]

    def deposit(self, account_id: str, amount_cents: int) -> int:
        if amount_cents <= 0:
            raise ValueError("Deposit amount must be positive.")

        lock = self._get_account_lock(account_id)
        with lock:
            if account_id not in self._balances:
                self._balances[account_id] = 0
            self._balances[account_id] += amount_cents
            new_bal = self._balances[account_id]

            self._history.append(
                WalletTransaction(
                    tx_id=f"tx_{uuid.uuid4().hex[:10]}",
                    from_account=None,
                    to_account=account_id,
                    amount_cents=amount_cents,
                    tx_type="DEPOSIT",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="SUCCESS",
                )
            )
            return new_bal

    def withdraw(self, account_id: str, amount_cents: int) -> int:
        if amount_cents <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        lock = self._get_account_lock(account_id)
        with lock:
            if account_id not in self._balances:
                raise ValueError(f"Wallet '{account_id}' does not exist.")
            if self._balances[account_id] < amount_cents:
                raise ValueError("Insufficient balance.")

            self._balances[account_id] -= amount_cents
            new_bal = self._balances[account_id]

            self._history.append(
                WalletTransaction(
                    tx_id=f"tx_{uuid.uuid4().hex[:10]}",
                    from_account=account_id,
                    to_account=None,
                    amount_cents=amount_cents,
                    tx_type="WITHDRAWAL",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="SUCCESS",
                )
            )
            return new_bal

    def transfer(self, from_account: str, to_account: str, amount_cents: int) -> WalletTransaction:
        """
        Transfers funds atomically between two accounts.
        Enforces ordered locking to prevent deadlocks: always lock min(from, to) first!
        """
        if from_account == to_account:
            raise ValueError("Source and destination accounts must be distinct.")
        if amount_cents <= 0:
            raise ValueError("Transfer amount must be positive.")

        first_id, second_id = (
            (from_account, to_account) if from_account < to_account else (to_account, from_account)
        )

        first_lock = self._get_account_lock(first_id)
        second_lock = self._get_account_lock(second_id)

        # Acquire locks in deterministic alphabetical order
        with first_lock:
            with second_lock:
                if from_account not in self._balances:
                    raise ValueError(f"Account '{from_account}' does not exist.")
                if to_account not in self._balances:
                    raise ValueError(f"Account '{to_account}' does not exist.")

                if self._balances[from_account] < amount_cents:
                    tx = WalletTransaction(
                        tx_id=f"tx_{uuid.uuid4().hex[:10]}",
                        from_account=from_account,
                        to_account=to_account,
                        amount_cents=amount_cents,
                        tx_type="TRANSFER",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="REJECTED",
                    )
                    self._history.append(tx)
                    raise ValueError(f"Insufficient funds in account '{from_account}'.")

                self._balances[from_account] -= amount_cents
                self._balances[to_account] += amount_cents

                tx = WalletTransaction(
                    tx_id=f"tx_{uuid.uuid4().hex[:10]}",
                    from_account=from_account,
                    to_account=to_account,
                    amount_cents=amount_cents,
                    tx_type="TRANSFER",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="SUCCESS",
                )
                self._history.append(tx)
                return tx

    def get_history(self, account_id: Optional[str] = None) -> List[WalletTransaction]:
        with self._global_lock:
            if not account_id:
                return list(self._history)
            return [
                tx
                for tx in self._history
                if tx.from_account == account_id or tx.to_account == account_id
            ]

