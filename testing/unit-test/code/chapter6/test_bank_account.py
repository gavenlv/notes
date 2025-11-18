import pytest
from chapter6.bank_account import BankAccount, InsufficientFunds


def test_deposit():
    a = BankAccount()
    a.deposit(100)
    assert a.balance == 100


def test_withdraw_ok():
    a = BankAccount(100)
    a.withdraw(40)
    assert a.balance == 60


def test_withdraw_insufficient():
    a = BankAccount(50)
    with pytest.raises(InsufficientFunds):
        a.withdraw(100)


def test_invalid_amounts():
    a = BankAccount()
    with pytest.raises(ValueError):
        a.deposit(0)
    with pytest.raises(ValueError):
        a.withdraw(-1)
