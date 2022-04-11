from functools import reduce
from collections import OrderedDict
import json
# import pickle

from hash_util import hash_block, hash_string_256

# Mining Reward
MINING_REWARD = 10

GENESIS_BLOCK = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}

# Initializing our blockchain list
blockchain = [GENESIS_BLOCK]
# Unhandled Transacrtions
open_transactions = []
owner = 'Tim'
participants = {'Tim'}


def load_data():
    with open('blockchain.txt', mode='r') as file:
        file_content = file.readlines()
        global blockchain
        global open_transactions

        # Using JSON
        blockchain = json.loads(file_content[0][:-1])
        blockchain = [{
            'previous_hash': block['previous_hash'],
            'index': block['index'],
            'proof':  block['proof'],
            'transactions': [
                OrderedDict([
                    ('sender', tx['sender']),
                    ('recipient', tx['recipient']),
                    ('amount', tx['amount'])
                ])
                for tx in block['transactions']]
        } for block in blockchain]
        open_transactions = json.loads(file_content[1])
        open_transactions = [
            OrderedDict([
                ('sender', tx['sender']),
                ('recipient', tx['recipient']),
                ('amount', tx['amount'])
            ])
            for tx in open_transactions]

        # Pickling
        # blockchain = file_content['chain']
        # open_transactions = file_content['ot']


# Load data from blockchain file
load_data()

def save_data():
    with open('blockchain.txt', mode='w') as file:
        # Using JSON
        file.write(json.dumps(blockchain))
        file.write('\n')
        file.write(json.dumps(open_transactions))
        
        # Pickling 
        # save_data = {
        #     'chain': blockchain,
        #     'ot': open_transactions
        # }
        # file.write(pickle.dumps(save_data))        


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)

    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum +
                         sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)
    # amount_sent = sum([tx[0] for tx in tx_sender if len(tx) > 0])
    amount_received = sum([tx[0] for tx in tx_recipient if len(tx) > 0])
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last blockchain transaction

    Arguments:
        :recipient: The recipient of the coins
        :sender: The sender of the coins
        :amount: The amount of coins being sent
    """
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }

    transaction = OrderedDict([
        ('sender', sender),
        ('recipient', recipient),
        ('amount', amount)
    ])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)

    proof = proof_of_work()
    # Reward participant for mining
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }

    reward_transaction = OrderedDict([
        ('sender', 'MINING'),
        ('recipient', owner),
        ('amount', MINING_REWARD)
    ])

    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns the transaction recipient and amount """
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return tx_recipient, tx_amount


def get_user_choice():
    return input('Your choice: ')


def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    """ Verify the current blockchain """
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False
    return True


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Output the participants')
    print('5: Check transactions validity')
    print('h: Manipulate the chain')
    print('q: Quit')

    choice = get_user_choice()

    if choice == '1':
        # Add transaction to blockchain
        tx_data = get_transaction_value()
        # Unpacking a tuple
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif choice == '3':
        print_blockchain_elements()
    elif choice == '4':
        print(participants)
    elif choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('Invalid transactions found')
    elif choice == 'h':
        # Make sure that you don't try to "hack" the blockchain
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [
                    {'sender': 'Chris', 'recipient': 'Tim', 'amount': 1000}
                ]
            }
    elif choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')

    if not verify_chain():
        print('Invalid blockchain!')
        print_blockchain_elements()
        break

    print('Balance of {}: {:6.2f}'.format('Tim', get_balance('Tim')))
else:
    print('User left!')


print('Done!')
