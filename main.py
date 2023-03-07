'''
this file contains the actual code !

Source code: https://github.com/dvf/blockchain/blob/master/blockchain.py
Project-based learning: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
'''

import hashlib # efficient hashing of file or a file-like object
import json # java-script object notation, storing and exchanging data
from time import time # time
from textwrap import dedent #to remove any common leading whitespace from every line in the input text
from uuid import uuid4 #generates randomUUID by using the crytographically generated secure number generator

from flask import Flask, jsonify, request #micro-framework

from urllib.parse import urlparse # consensus algorithm

class Blockchain(object):

    def __init__(self):
        self.chain = []
        # chain is array of dicts
        # array of blocks (dictionaries) , returned by new_block function
        self.current_transactions = []

        # creating genesis block
        self.new_block(previous_hash=1, proof=100)

        self.nodes = set() # will hold list of nodes

    def new_block(self, proof, previous_hash=None):
        # creates a new block and adds it to the chain
        """
                Create a new Block in the Blockchain
                :param proof: <int> The proof given by the Proof of Work algorithm
                :param previous_hash: (Optional) <str> Hash of previous Block
                :return: <dict> New Block
        """
        #block is a dictionary and new_block will return this data type
        block = {
                  'index':len(self.chain)+1,
                  'timestamp':time(),
                  'transactions':self.current_transactions,
                  'proof':proof,
                  'previous_hash': previous_hash or
                  self.hash(self.chain[-1]),
                  }

        # resetting the current list of transaction
        self.current_transactions=[]

        #adding element to the list
        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        # adds new transaction to the list

        """
               Creates a new transaction to go into the next mined Block
               :param sender: <str> Address of the Sender
               :param recipient: <str> Address of the Recipient
               :param amount: <int> Amount
               :return: <int> The index of the Block that will hold this transaction
        """

        # current_transaction is a list in __init__ function
        self.current_transactions.append({'sender':sender, 'recipient':recipient, 'amount':amount})
        return self.last_block['index']+1

    '''
    The @staticmethod is a built-in decorator that defines a static method in the class in Python.
    A static method doesn't receive any reference argument whether it is called by an instance of a
    class or by the class itself.
    '''
    @staticmethod
    def hash(block):
        # hashes a block
        """
                Creates a SHA-256 hash of a Block
                :param block: <dict> Block
                :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes

        '''
        This code takes a Python dictionary block and converts it into a JSON-formatted string using the 
        json.dumps() method. The sort_keys=True parameter specifies that the keys in the dictionary should be 
        sorted in alphabetical order when converting to a JSON string.

        The resulting JSON string is then encoded into a sequence of bytes using the encode() method. 
        This converts the Unicode string to a bytes object which can be transmitted over the network or saved 
        to a file.

        The resulting block_string variable will contain the JSON-formatted string representation of the block 
        dictionary in a sequence of bytes. This can be useful for transmitting the data over a network, 
        saving to a file, or other operations that require a byte representation of the data.
        '''

        block_string = json.dumps(block , sort_keys=True).encode()

        '''
        The hashlib module provides a secure way to hash data using various hashing algorithms. 
        In this code, the SHA-256 algorithm is used to create a hash of the block_string.

        The block_string is the JSON-formatted string representation of a Python dictionary 
        (in this case, the block dictionary) that has been encoded into bytes. The hashlib.sha256() method 
        takes this byte string as input and computes its SHA-256 hash value.

        The hexdigest() method is then called on the resulting hash object to convert the binary hash value
        into a hexadecimal string. This provides a human-readable representation of the hash value.

        The resulting value is a string that represents the SHA-256 hash of the block dictionary in hexadecimal 
        format. This hash value is typically used to verify the integrity of the data and ensure that it has 
        not been tampered with. It is a commonly used cryptographic hash function and is considered to be 
        highly secure.
        '''
        return hashlib.sha256(block_string).hexdigest()

    ''' It is used to give "special" functionality to certain methods to make them act as getters, setters, 
    or deleters when we define properties in a class
    '''
    @property
    def last_block(self):
        # return the last block in the chain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
                Simple Proof of Work Algorithm:
                 - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
                 - p is the previous proof, and p' is the new proof
                :param last_proof: <int>
                :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof+=1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):

        """
               Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
               :param last_proof: <int> Previous Proof
               :param proof: <int> Current Proof
               :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # part of consensus algorithm
    def register_node(self, address):
        """
                Add a new node to the list of nodes
                :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
                :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        # check if chain is valid by looping through each block and verifying both hash and the proof

        '''
                Determine if a given blockchain is valid
                :param chain: <list> A blockchain
                :return: <bool> True if valid, False if not
        '''

        last_block = chain[0]
        current_index = 1

        while current_index<len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n ---------- \n")

            #check that the hash of the block is correct
            if block['previous_hash']!=self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index+=1

        return True

    def resolve_conflicts(self):
        # loops through all our neighbouring nodes,

        '''
                This is our Consensus Algorithm, it resolves conflicts by replacing our chain
                with the longest one in the network.
                :return: <bool> True if our chain was replaced, False if not
        '''

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        for node in neighbours:
            response = request.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['Length']
                chain = response.json()['chain']

                # check if the length is longer and the chain is valid
                if length>max_length and self.valid_chain(chain):
                    max_length=length
                    new_chain=chain

        if new_chain:
            self.chain=new_chain
            return True

        return False

# Instantiate our Node
app = Flask(__name__)
#Generate a unique address
node_identifier = str(uuid4()).replace('-','')
#Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine',method=['GET'])
def mine():
    return "We'll mine a new block"

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    return "We'll add a new transaction"

@app.route('/chain',methods=['GET'])
def full_chain():
    response={'chain':blockchain.chain,'length':len(blockchain.chain)}
    return jsonify(response), 200

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    #check the required field are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message':f'transaction will be added to Block{index}'}
    return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine():
    # we run the proof of work algorithm to get next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # reward for finding the proof
    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {'message':'New Block forged',
                'index':block['index'],
                'transaction':block['transaction'],
                'proof':block['proof'],
                'previous_hash':block['previous_hash']
                }
    return jsonify(response), 200

# At this point, we’re done, and can start interacting with our blockchain.

@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values=request.get_json()
    # nodes is HTTP address
    nodes = values.get('nodes')
    if nodes is None :
        return "ERROR: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response={'message': 'New nodes have been added',
                  'total_nodes':list(blockchain.nodes)
                  }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response={'message':'Our chain is replaced',
                  'new_chain':blockchain.chain
                  }
    else:
        response={'message':'Our chain is authoritative',
                  'chain':blockchain.chain
                  }
    return jsonify(response), 200







