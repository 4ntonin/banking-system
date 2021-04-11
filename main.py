from random import randint
import sqlite3


class Bank:
    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.user_id = 0
        self.card_number = "400000"
        self.card_pin = ''
        self.balance = 0

    def drop_table(self):
        self.cur.execute('DROP TABLE IF EXISTS card;')

    def create_table(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
        self.conn.commit()

    def get_card_number(self):
        return self.card_number

    def get_card_pin(self):
        return self.card_pin

    def get_balance(self):
        return self.balance

    def luhn(self, cardnb=None):
        """
        Luhn algorithm to verify the validity of the card number
        :return: str (checksum of the card)
        """
        if not cardnb:
            cardnb = list(self.card_number)
        else:
            cardnb = list(cardnb)
        total = 0
        for i in range(15):
            if (i + 1) % 2 == 1:
                cardnb[i] = int(cardnb[i]) * 2
            if int(cardnb[i]) > 9:
                cardnb[i] = int(cardnb[i]) - 9
            total += int(cardnb[i])
        rest = total % 10
        if rest != 0:
            checksum = str(10 - rest)
        else:
            checksum = '0'
        return checksum

    def set_card_number(self):
        """adds 9 random digits to the card"""
        for i in range(9):
            self.card_number += str(randint(0, 9))
        self.card_number += self.luhn()

    def set_card_pin(self):
        """creates card pin"""
        for i in range(4):
            self.card_pin += str(randint(0, 9))

    def add_info(self):
        """adds account information to the table card"""
        self.cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (self.get_card_number(), self.get_card_pin()))
        self.conn.commit()

    def add_income(self, income):
        """adds income to the user's account"""
        self.balance += income
        self.cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.balance, self.card_number))
        self.conn.commit()

    def reset_account(self):
        """reset attributes"""
        self.card_number = "400000"
        self.card_pin = ''
        self.balance = 0

    def verification(self, number, pin):
        """verifies if the account exists"""
        for row in self.cur.execute('SELECT * FROM card'):
            if number in row and pin in row:
                self.user_id = row[0]
                self.card_number = row[1]
                self.card_pin = row[2]
                self.balance = row[3]
                return True
        return False

    def transfer_verification(self, number):
        """verifies if the transfer account exists"""
        for row in self.cur.execute('SELECT * FROM card'):
            if number in row:
                return True
        return False

    def transfer(self, cardnb, amount):
        """does transfer"""
        self.balance -= amount
        self.cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.balance, self.card_number))
        self.conn.commit()
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (amount, cardnb))
        self.conn.commit()

    def delete_account(self):
        """deletes the user's account"""
        self.cur.execute("DELETE FROM card WHERE id = ?", str(self.user_id))
        self.conn.commit()


if __name__ == '__main__':
    User = Bank()
    menu = 1
    User.drop_table()
    User.create_table()
    while menu != 0:
        menu = int(input("""
1. Create an account
2. Log into account
0. Exit
"""))
        if menu == 1:
            User.reset_account()
            print("Your card has been created")
            print("Your card number:")
            User.set_card_number()
            print(User.get_card_number())
            print("Your card PIN:")
            User.set_card_pin()
            print(User.get_card_pin())
            User.add_info()
        elif menu == 2:
            card_nb = str(input("Enter your card number: "))
            card_pin = str(input("Enter your PIN: "))
            verif = User.verification(card_nb, card_pin)
            if verif:
                print("You have successfully logged in!")
                while menu != 0 and menu != 5:
                    menu = int(input("""
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""))
                    if menu == 1:
                        print("Balance: ", User.get_balance())
                    elif menu == 2:
                        income = int(input("Enter income: "))
                        User.add_income(income)
                        print("Income was added!")
                    elif menu == 3:
                        transfer_card = str(input("Enter card number: "))
                        if User.luhn(transfer_card) != list(transfer_card)[-1]:
                            print("Probably you made a mistake in the card number. Please try again!")
                        elif not User.transfer_verification(transfer_card):
                            print("Such a card does not exist.")
                        elif transfer_card == User.get_card_number():
                            print("You can't transfer money to the same account!")
                        else:
                            transfer_amount = int(input("Enter how much money you want to transfer: "))
                            if User.get_balance() - transfer_amount < 0:
                                print("Not enough money!")
                            else:
                                User.transfer(transfer_card, transfer_amount)
                    elif menu == 4:
                        User.delete_account()
                        print("The account has been closed!")
                        menu = 5
                    elif menu == 5:
                        print("You have successfully logged out!")
            else:
                print("Wrong card number or PIN!")
    print("Bye!")
