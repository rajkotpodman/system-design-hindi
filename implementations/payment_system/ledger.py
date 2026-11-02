"""
Double-Entry Bookkeeping Ledger
Chapter 26: Payment System & Chapter 27: Digital Wallet

Fundamental Accounting Invariant:
For every transaction, the sum of debits MUST equal the sum of credits.
Total change in system balance is always zero:
    Sum(Debits) - Sum(Credits) == 0

Account Types:
- ASSET: (e.g., Bank account, Cash) - Debit increases, Credit decreases.
- LIABILITY: (e.g., User wallet deposits owed to users) - Credit increases, Debit decreases.
- REVENUE: (e.g., Processing fees earned) - Credit increases.
- EXPENSE: (e.g., Interchange fee paid) - Debit increases.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import threading
import time
from typing import Dict, List, Optional
import uuid


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


@dataclass
class Account:
    account_id: str
    account_type: AccountType
    currency: str = "USD"
    balance_cents: int = 0  # In integer cents to avoid floating-point errors!


@dataclass
class Posting:
    account_id: str
    amount_cents: int  # Positive for debit, negative for credit (or explicit debit/credit)
    is_debit: bool


@dataclass
class JournalEntry:
    entry_id: str
    description: str
    created_at: str
    postings: List[Posting]
    idempotency_key: Optional[str] = None


class LedgerUnbalancedError(Exception):
    """Raised when sum of debits does not equal sum of credits."""
    pass


class InsufficientFundsError(Exception):
    """Raised when an account does not have sufficient balance."""
    pass


class DoubleEntryLedger:
    """
    Immutable Double-Entry Bookkeeping Ledger.
    """

    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._journal: List[JournalEntry] = []
        self._lock = threading.Lock()

    def create_account(self, account_id: str, account_type: AccountType, currency: str = "USD") -> Account:
        with self._lock:
            if account_id in self._accounts:
                return self._accounts[account_id]
            account = Account(account_id=account_id, account_type=account_type, currency=currency, balance_cents=0)
            self._accounts[account_id] = account
            return account

    def get_account(self, account_id: str) -> Optional[Account]:
        with self._lock:
            return self._accounts.get(account_id)

    def record_entry(
        self,
        description: str,
        postings: List[Posting],
        idempotency_key: Optional[str] = None,
    ) -> JournalEntry:
        """
        Record an atomic balanced transaction.
        Invariant: Total Debits == Total Credits.
        """
        with self._lock:
            total_debits = sum(p.amount_cents for p in postings if p.is_debit)
            total_credits = sum(p.amount_cents for p in postings if not p.is_debit)

            if total_debits != total_credits:
                raise LedgerUnbalancedError(
                    f"Unbalanced entry! Total Debits ({total_debits}) != Total Credits ({total_credits})"
                )

            # Verify all accounts exist
            for p in postings:
                if p.account_id not in self._accounts:
                    raise ValueError(f"Account {p.account_id} does not exist.")

            # Apply balance mutations atomically
            for p in postings:
                acc = self._accounts[p.account_id]
                # In accounting:
                # ASSET/EXPENSE: Debit increases (+), Credit decreases (-)
                # LIABILITY/REVENUE: Credit increases (+), Debit decreases (-)
                if acc.account_type in (AccountType.ASSET, AccountType.EXPENSE):
                    if p.is_debit:
                        acc.balance_cents += p.amount_cents
                    else:
                        acc.balance_cents -= p.amount_cents
                else:  # LIABILITY, REVENUE
                    if not p.is_debit:
                        acc.balance_cents += p.amount_cents
                    else:
                        acc.balance_cents -= p.amount_cents

            entry = JournalEntry(
                entry_id=f"entry_{uuid.uuid4().hex[:12]}",
                description=description,
                created_at=datetime.now(timezone.utc).isoformat(),
                postings=postings,
                idempotency_key=idempotency_key,
            )
            self._journal.append(entry)
            return entry

    def transfer(
        self,
        source_account_id: str,
        dest_account_id: str,
        amount_cents: int,
        description: str = "Transfer",
        idempotency_key: Optional[str] = None,
    ) -> JournalEntry:
        """Convenience method for 1-to-1 fund transfer."""
        if amount_cents <= 0:
            raise ValueError("Transfer amount must be strictly positive.")

        with self._lock:
            source = self._accounts.get(source_account_id)
            if not source:
                raise ValueError(f"Source account {source_account_id} not found.")

            if source.balance_cents < amount_cents and source.account_type == AccountType.LIABILITY:
                raise InsufficientFundsError(
                    f"Account {source_account_id} has insufficient funds ({source.balance_cents} < {amount_cents})"
                )

        # For user liability accounts: transfer decreases source (debit) and increases dest (credit)
        postings = [
            Posting(account_id=source_account_id, amount_cents=amount_cents, is_debit=True),
            Posting(account_id=dest_account_id, amount_cents=amount_cents, is_debit=False),
        ]
        return self.record_entry(description=description, postings=postings, idempotency_key=idempotency_key)

    @property
    def journal(self) -> List[JournalEntry]:
        with self._lock:
            return list(self._journal)

