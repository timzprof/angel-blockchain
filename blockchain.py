# Initializing our blockchain list
MINING_REWARD = 10

GENESIS_BLOCK = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
blockchain = [GENESIS_BLOCK]
open_transactions = []
owner = 'Tim'
participants = {'Tim'}

def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx  in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_sent = sum([tx[0] for tx in tx_sender if len(tx) > 0])
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


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last blockchain transaction

    Arguments:
        :recipient: The recipient of the coins
        :sender: The sender of the coins
        :amount: The amount of coins being sent
    """
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    # Reward participant for mining
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    open_transactions.append(reward_transaction)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }
    blockchain.append(block)
    return  True


def get_transaction_value():
    """ Returns the transaction recipient and amount """
    tx_recipient = input('Enter the recipient of the transaction:')
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
    return True


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Output the participants')
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
       if  mine_block():
           open_transactions = []
    elif choice == '3':
        print_blockchain_elements()
    elif choice == '4':
        print(participants)
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

    print(get_balance('Tim'))
else:
    print('User left!')


print('Done!')
