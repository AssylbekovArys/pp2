class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def deposit(self, deposit_):
        self.balance+=deposit_
    def withdraw(self, withdraw_):
        if withdraw_<=self.balance:
            self.balance -= withdraw_
            return True
        return False
    def Show(self):
        return self.balance

ac1 = Account("Bob", 200)
ac1.deposit(200)
print(ac1.Show())
ac1.withdraw(300)
print(ac1.Show())
ac1.withdraw(200)
print(ac1.Show())