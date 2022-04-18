# from uuid import uuid4

from blockchain import Blockchain
from verification import Verification

class Node:
    def __init__(self):
        self.id = 'Tim'
        self.blockchain = Blockchain(self.id)


    def listen_for_input(self): 
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transactions validity')
            print('q: Quit')

            choice = self.get_user_choice()

            if choice == '1':
                # Add transaction to blockchain
                tx_data = self.get_transaction_value()
                # Unpacking a tuple
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif choice == '2':
                self.blockchain.mine_block()
            elif choice == '3':
                self.print_blockchain_elements()
            elif choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('Invalid transactions found')
            elif choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')

            if not Verification.verify_chain(self.blockchain.chain):
                print('Invalid blockchain!')
                self.print_blockchain_elements()
                break

            print('Balance of {}: {:6.2f}'.format('Tim', self.blockchain.get_balance()))
        else:
            print('User left!')


        print('Done!')
    
    def get_transaction_value(self):
        """ Returns the transaction recipient and amount """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount


    def get_user_choice(self):
        return input('Your choice: ')


    def print_blockchain_elements(self):
        # Output the blockchain list to the console
        for block in self.blockchain.chain:
            print('Outputting Block')
            print(block)
        else:
            print('-' * 20)


node = Node()
node.listen_for_input()