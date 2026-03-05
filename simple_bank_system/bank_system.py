class Account:
    def __init__(self, acc_num, pin, backup_number, balance=0.0):
        self.acc_num = acc_num
        self.pin = pin
        self.backup_number = backup_number
        self.balance = balance

    def get_details(self):
        return f"Account Number: {self.acc_num}, Balance: ${self.balance}"


class BankSystem:
    def __init__(self):
        self.accounts = {}
        self.next_acc_num = 1

    def create_account(self, pin, backup_number=""):
        account = Account(self.next_acc_num, pin, backup_number)
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

    def view_all_accounts(self):
        details = "\n".join(account.get_details() for account in self.accounts.values())
        return details if details else "No accounts available."

    def transfer_money(self, from_acc_num, from_pin, to_acc_num, amount):
        from_account = self.accounts.get(from_acc_num)
        to_account = self.accounts.get(to_acc_num)
        if from_account and to_account and from_account.pin == from_pin and 0 < amount <= from_account.balance:
            from_account.balance -= amount
            to_account.balance += amount
            return True
        return False

    def reset_pin(self, acc_num, backup_number, new_pin):
        account = self.accounts.get(acc_num)
        if account and account.backup_number == backup_number:
            account.pin = new_pin
            return True
        return False
