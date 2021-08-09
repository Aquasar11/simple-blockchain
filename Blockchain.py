import hashlib
import json
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
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """add a new transaction to mempool"""
        self.current_transactions.append({'sender': sender, 'recipient': recipient, 'amount': amount})
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """return sha256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """return the last block of the blockchain"""
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof):
        """check the proof and return a boolean as a result"""
        guess_proof = f"{proof}{last_proof}".encode()
        guess_proof_hash = hashlib.sha256(guess_proof).hexdigest()
        return guess_proof_hash[:4] == '0000'

    def proof_of_work(self, last_proof):
        """"
        Simple Proof of Work Algorithm:
        Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
        p is the previous proof, and p' is the new proof
        """
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof
