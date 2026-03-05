# bank_system.py
class Account:
    def __init__(self, acc_num, pin):
        self.acc_num = acc_num
        self.pin = pin
        self.balance = 0.0

class BankSystem:
    def __init__(self):
        self.accounts = {}
        self.next_acc_num = 1

    def create_account(self, pin):
        account = Account(self.next_acc_num, pin)
        self.accounts[self.next_acc_num] = account
        self.next_acc_num += 1
        return account.acc_num

    def delete_account(self, acc_num, pin):
        account = self.accounts.get(acc_num)
        if account and account.pin == pin:
            del self.accounts[acc_num]
            return True
        return False

    def deposit(self, acc_num, amount, pin):
        account = self.accounts.get(acc_num)
        if account and account.pin == pin and amount > 0:
            account.balance += amount
            return account.balance
        return None

    def withdraw(self, acc_num, amount, pin):
        account = self.accounts.get(acc_num)
        if account and account.pin == pin and 0 < amount <= account.balance:
            account.balance -= amount
            return account.balance
        return None

    def show_balance(self, acc_num, pin):
        account = self.accounts.get(acc_num)
        if account and account.pin == pin:
            return account.balance
        return None
