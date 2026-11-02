import pytest
from implementations.digital_wallet import DigitalWalletService


def test_wallet_deposit_and_transfer():
    wallet = DigitalWalletService()
    wallet.create_wallet("Alice", 10000)
    wallet.create_wallet("Bob", 5000)

    # Transfer $30 from Alice to Bob
    tx = wallet.transfer("Alice", "Bob", 3000)
    assert tx.status == "SUCCESS"
    assert wallet.get_balance("Alice") == 7000
    assert wallet.get_balance("Bob") == 8000


def test_wallet_insufficient_funds():
    wallet = DigitalWalletService()
    wallet.create_wallet("Alice", 1000)
    wallet.create_wallet("Bob", 1000)

    with pytest.raises(ValueError, match="Insufficient funds"):
        wallet.transfer("Alice", "Bob", 5000)

    # Balances must remain unchanged
    assert wallet.get_balance("Alice") == 1000
    assert wallet.get_balance("Bob") == 1000

