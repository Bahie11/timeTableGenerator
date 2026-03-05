import tkinter as tk
from tkinter import simpledialog, messagebox
from bank_system import BankSystem, Account

class BankApp:
    def __init__(self, root):
        self.root = root
        self.bank = BankSystem()  # Initialize BankSystem
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Bank System")
        self.root.geometry("400x300")

        tk.Button(self.root, text="Create Account", command=self.create_account).pack()
        tk.Button(self.root, text="View All Accounts", command=self.view_all_accounts).pack()
        tk.Button(self.root, text="Transfer Money", command=self.transfer_money).pack()
        tk.Button(self.root, text="Deposit", command=self.deposit).pack()
        tk.Button(self.root, text="Withdraw", command=self.withdraw).pack()
        tk.Button(self.root, text="View Balance", command=self.view_balance).pack()
        tk.Button(self.root, text="Reset PIN", command=self.reset_pin).pack()

    def create_account(self):
        pin = simpledialog.askinteger("PIN", "Enter a 4-digit PIN:")
        backup_number = simpledialog.askstring("Backup Number", "Enter a backup number (e.g., phone number):")  # Ask for backup number
        if pin and backup_number:
            acc_num = self.bank.create_account(pin, backup_number)  # Pass backup number to create_account
            messagebox.showinfo("Success", f"Account created successfully! Account Number: {acc_num}")
        else:
            messagebox.showerror("Error", "Account creation failed. Please provide both PIN and backup number.")

    def view_all_accounts(self):
        all_accounts_details = self.bank.view_all_accounts()
        messagebox.showinfo("All Accounts", all_accounts_details)

    def transfer_money(self):
        from_acc = simpledialog.askinteger("Transfer", "Enter your Account Number:")
        from_pin = simpledialog.askinteger("Transfer", "Enter your PIN:")
        to_acc = simpledialog.askinteger("Transfer", "Enter target Account Number:")
        amount = simpledialog.askfloat("Transfer", "Enter amount to transfer:")
        if self.bank.transfer_money(from_acc, from_pin, to_acc, amount):
            messagebox.showinfo("Success", "Transfer successful!")
        else:
            messagebox.showerror("Error", "Transfer failed. Check account details and balance.")

    def reset_pin(self):
        acc_num = simpledialog.askinteger("Reset PIN", "Enter your Account Number:")
        backup_number = simpledialog.askstring("Reset PIN", "Enter your Backup Number:")
        new_pin = simpledialog.askinteger("Reset PIN", "Enter a new 4-digit PIN:")
        if self.bank.reset_pin(acc_num, backup_number, new_pin):
            messagebox.showinfo("Success", "PIN reset successfully!")
        else:
            messagebox.showerror("Error", "PIN reset failed. Check backup number and account.")

    def view_balance(self):
        acc_num = simpledialog.askinteger("View Balance", "Enter your Account Number:")
        pin = simpledialog.askinteger("View Balance", "Enter your PIN:")
        balance = self.bank.show_balance(acc_num, pin)
        if balance is not None:
            messagebox.showinfo("Balance", f"Your balance: ${balance}")
        else:
            messagebox.showerror("Error", "Invalid account number or PIN.")

    def deposit(self):
        acc_num, pin = self.get_acc_num_and_pin()
        if acc_num and pin:
            amount = self.get_amount("Enter deposit amount:")
            if amount and self.bank.deposit(acc_num, amount, pin) is not None:
                messagebox.showinfo("Success", f"${amount} deposited successfully")
            else:
                messagebox.showerror("Error", "Deposit failed")

    def withdraw(self):
        acc_num, pin = self.get_acc_num_and_pin()
        if acc_num and pin:
            amount = self.get_amount("Enter withdrawal amount:")
            if amount and self.bank.withdraw(acc_num, amount, pin) is not None:
                messagebox.showinfo("Success", f"${amount} withdrawn successfully")
            else:
                messagebox.showerror("Error", "Withdrawal failed or insufficient balance")

    def get_acc_num_and_pin(self):
        acc_num = simpledialog.askinteger("Account Number", "Enter account number:")
        pin = self.get_pin("Enter PIN:")
        return acc_num, pin

    def get_amount(self, prompt):
        amount = simpledialog.askfloat("Amount", prompt, minvalue=0.01)
        return amount

    def get_pin(self, prompt):
        pin = simpledialog.askinteger("PIN", prompt, minvalue=1000, maxvalue=9999)
        return pin

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
