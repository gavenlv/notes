class InsufficientFunds(Exception):
    pass


class BankAccount:
    def __init__(self, balance: float = 0.0):
        self.balance = float(balance)

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("withdraw amount must be positive")
        if amount > self.balance:
            raise InsufficientFunds("not enough balance")
        self.balance -= amount
