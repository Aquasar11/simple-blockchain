import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests as requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(11, "first block in the blockchain created by Aquasar")
        self.nodes = set()

    def register_node(self, address):
        """register a node into blockchain"""
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """check a given chain and validate it"""
        current_index = 0
        last_block = chain[current_index]
        current_index += 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """check all blockchain nodes and determine the chosen chain"""
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            res = requests.get(f'http://{node}/chain')

            if res.status_code == 200:
                length = res.json()['length']
                chain = res.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

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


app = Flask(__name__)
node_id = str(uuid4())
blockchain = Blockchain()


@app.route('/mine')
def mine():
    """mine a block and add it to blockchain"""
    previous_block = blockchain.last_block
    previous_proof = previous_block['proof']

    blockchain.new_transaction('protocol', 'Ali', 100)
    new_proof = blockchain.proof_of_work(previous_proof)

    previous_hash = blockchain.hash(previous_block)
    new_block = blockchain.new_block(new_proof, previous_hash)
    res = {
        'message': "new block created",
        'index': new_block['index'],
        'trxs': new_block['transactions'],
        'proof': new_proof,
        'hash': blockchain.hash(new_block)
    }

    return jsonify(res), 200


@app.route('/trxs/new', methods=['POST'])
def new_trx():
    """add a new transaction by getting sender, recipient and amount"""
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    if not all(k in values for k in ['sender', 'recipient', 'amount']):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain')
def full_chain():
    """returns the full chain"""
    res = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(res), 200


@app.route('/nodes/register', methods=['POST'])
def register_node():
    value = request.get_json()

    nodes = value.get('nodes')
    for node in nodes:
        blockchain.register_node(node)

    res = {
        'message': "nodes added",
        'total nodes': list(blockchain.nodes)
    }

    return jsonify(res), 201


@app.route('/consensus')
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        res = {
            'message': "chain replaced",
            'new chain': blockchain.chain
        }
    else:
        res = {
            'message': "chain didn't replaced in this machine",
            'new chain': blockchain.chain
        }

    return jsonify(res), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)
