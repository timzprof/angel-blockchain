from functools import reduce
import json
# import pickle

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

# Mining Reward
MINING_REWARD = 10

class Blockchain:
    def __init__(self, hosting_node_id):
        GENESIS_BLOCK = Block(0, '', [], 100, 0)
        # Initializing our blockchain list
        self.chain = [GENESIS_BLOCK] 
        # Unhandled Transacrtions
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self) -> None:
        try:
            with open('blockchain.txt', mode='r') as file:
                file_content = file.readlines()

                # Using JSON
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'],
                        block['previous_hash'],
                        converted_tx,
                        block['proof'],
                        block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1])
                self.__open_transactions = [
                    Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    for tx in open_transactions]

                # Pickling
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
        except (IOError, IndexError):
            print('File not found!')
        finally:
            print('Cleanup!')



    def save_data(self) -> None:
        try:
            with open('blockchain.txt', mode='w') as file:
                # Using JSON
                savable_chain = [block.__dict__ for block in [
                    Block(block_el.index, block_el.previous_hash, [
                        tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                    for block_el in self.__chain]]
                savable_tx = [tx.__dict__ for tx in self.__open_transactions]
                file.write(json.dumps(savable_chain))
                file.write('\n')
                file.write(json.dumps(savable_tx))

                # Pickling
                # save_data = {
                #     'chain': blockchain,
                #     'ot': open_transactions
                # }
                # file.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')


    def proof_of_work(self) -> int:
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof


    def get_balance(self) -> int:
        """ Calculate and return the balance of the hostig node user """
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions
                    if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount
                        for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)

        tx_recipient = [[tx.amount for tx in block.transactions
                        if tx.recipient == participant] for block in self.__chain]
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum +
                            sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)
        # amount_sent = sum([tx[0] for tx in tx_sender if len(tx) > 0])
        amount_received = sum([tx[0] for tx in tx_recipient if len(tx) > 0])
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, amount=1.0):
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

        transaction = Transaction(sender, recipient, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False


    def mine_block(self):
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        proof = self.proof_of_work()

        # Reward participant for mining
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)

        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        self.__chain.append(block)

        # Reset Open Transactions
        self.__open_transactions = []
        self.save_data()
