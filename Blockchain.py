from time import time


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(11, "first block in the blockchain created by Aquasar")

    def new_block(self, proof, previous_hash=None):
        """create a new block"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

    def new_transaction(self, sender, recipient, amount):
        """add a new transaction to mempool"""
        self.current_transactions.append({'sender': sender, 'recipient': recipient, 'amount': amount})
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """hash a block"""
        pass

    @property
    def last_block(self):
        """return the last block of the blockchain"""
        pass
