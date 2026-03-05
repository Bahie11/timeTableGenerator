import tkinter as tk
from tkinter import simpledialog 
from tkinter import messagebox
from bank_system import BankSystem

class BankApp:
    def __init__(self, root):
        self.root = root
        self.bank = BankSystem()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Bank System")
        self.root.geometry("400x300")

        tk.Button(self.root, text="Create Account", command=self.create_account).pack(pady=5)
        tk.Button(self.root, text="Delete Account", command=self.delete_account).pack(pady=5)
        tk.Button(self.root, text="Deposit", command=self.deposit).pack(pady=5)
        tk.Button(self.root, text="Withdraw", command=self.withdraw).pack(pady=5)
        tk.Button(self.root, text="Show Balance", command=self.show_balance).pack(pady=5)

    def create_account(self):
        pin = self.get_pin("Enter a 4-digit PIN for the new account:")
        if pin:
            acc_num = self.bank.create_account(pin)
            messagebox.showinfo("Success", f"Account created with number: {acc_num}")

    def delete_account(self):
        acc_num, pin = self.get_acc_num_and_pin()
        if acc_num and pin and self.bank.delete_account(acc_num, pin):
            messagebox.showinfo("Success", "Account deleted successfully")
        else:
            messagebox.showerror("Error", "Invalid account number or PIN")

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

    def show_balance(self):
        acc_num, pin = self.get_acc_num_and_pin()
        if acc_num and pin:
            balance = self.bank.show_balance(acc_num, pin)
            if balance is not None:
                messagebox.showinfo("Balance", f"Your balance: ${balance}")
            else:
                messagebox.showerror("Error", "Invalid account number or PIN")

    def get_pin(self, prompt):
        pin = tk.simpledialog.askinteger("PIN", prompt, minvalue=1000, maxvalue=9999)
        return pin

    def get_acc_num_and_pin(self):
        acc_num = tk.simpledialog.askinteger("Account Number", "Enter account number:")
        pin = self.get_pin("Enter PIN:")
        return acc_num, pin

    def get_amount(self, prompt):
        amount = tk.simpledialog.askfloat("Amount", prompt, minvalue=0.01)
        return amount

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
