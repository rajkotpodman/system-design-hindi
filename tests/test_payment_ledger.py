import pytest
from implementations.payment_system import (
    DoubleEntryLedger,
    AccountType,
    Posting,
    LedgerUnbalancedError,
    InsufficientFundsError,
    IdempotencyManager,
    ReconciliationEngine,
    SettlementRecord,
)


def test_double_entry_balance_invariant():
    ledger = DoubleEntryLedger()
    ledger.create_account("bank_cash", AccountType.ASSET)
    ledger.create_account("user_wallet", AccountType.LIABILITY)

    # Balanced entry: Debit Asset $100, Credit Liability $100
    entry = ledger.record_entry(
        description="Deposit",
        postings=[
            Posting("bank_cash", 10000, is_debit=True),
            Posting("user_wallet", 10000, is_debit=False),
        ],
    )
    assert len(ledger.journal) == 1
    assert ledger.get_account("bank_cash").balance_cents == 10000
    assert ledger.get_account("user_wallet").balance_cents == 10000

    # Unbalanced entry must raise error
    with pytest.raises(LedgerUnbalancedError):
        ledger.record_entry(
            description="Bad entry",
            postings=[
                Posting("bank_cash", 5000, is_debit=True),
                Posting("user_wallet", 4000, is_debit=False),
            ],
        )


def test_idempotency_manager():
    mgr = IdempotencyManager()
    assert mgr.try_acquire("key-1") is None
    # Second acquisition returns active record
    assert mgr.try_acquire("key-1") is not None

    mgr.commit("key-1", {"status": "ok"})
    rec = mgr.try_acquire("key-1")
    assert rec.status.value == "COMMITTED"


def test_reconciliation():
    internal_data = {"tx_1": 5000, "tx_2": 2000, "tx_3": 1000}
    settlement = [
        SettlementRecord("gw_1", "tx_1", 5000, 150, "SETTLED"),
        SettlementRecord("gw_2", "tx_2", 1800, 100, "SETTLED"),  # Mismatched amount
        SettlementRecord("gw_orphan", "tx_unknown", 3000, 90, "SETTLED"),  # Missing in internal
    ]
    report = ReconciliationEngine.reconcile(internal_data, settlement)
    assert report.total_matched == 1
    assert len(report.amount_mismatches) == 1
    assert len(report.missing_in_internal) == 1
    assert "tx_3" in report.missing_in_gateway

