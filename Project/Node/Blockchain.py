import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from collections import Counter
import netifaces as ni

import requests
from flask import Flask, jsonify, request
#~ from flask_cors import CORS

usePort = input('Enter Port Number For Node:  ')


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block as a blockchain cannot be empty 
        self.new_block(previous_hash='1', proof=100)
    
    
    
    # responsible for adding new nodes to the list of neighbours
    def register_node(self, address, auto_add):
        if address:
            self.nodes.add(address)
            print(f'---  Node {address} added locally  ---')
            
            
            """
            Force resolve to check for longest valid blockchain from new node
            Add our address to the other nodes address list
            Force node to run resolve to check which va;id chain is longest and should be used
            """
            
            response = self.resolve_conflicts()
 
            if response is True:
                print('---  Loaded longer valid chain from new node address ---')
            
            else:
                print('---  No chain to download from other node  ---')
            
            """
            auto_add stores if it is the server that has made the request to add a node
            if so, no need to make request to add their information to the senders nodeList
            """
            if auto_add is False :
                ni.ifaddresses('eth0')
                ip = 'http://' + ni.ifaddresses('eth0')[ni.AF_INET][0]['addr'] + ':' + str(port)           
                response = requests.post(f'{address}/nodes/register?address={ip}&auto_add=True')
                print(response)
            
            
            return 'Node {address} added locally. Address shared and blockchain sysnced with new node'
            
        else:
            print(f'---  Invalid node address supplied by user  ---')
            return 'Invalid node address supplied'


    # function to read through chain and verify it has not been corrupted or has any double votes
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check if the last blocks hash is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check the last Proof of Work
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True
        
        
    # when called the node will request the chain of all known nodes
    # if chain recieved is valid and longer it will replace its own chain
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        cur_chain = self.chain

        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        
        # If this chain is invalid force retrieval of other longest chain
        response = self.valid_chain(cur_chain)

        if response is False:
            max_length = 0
 

        # retrieve and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # if a longer valid chain is discovered drop current chain and replace
        if new_chain:
            self.chain = new_chain
            return True

        return False



    # creates a new block to hold one or more transactions
    def new_block(self, proof, previous_hash):
        # initiate block with structure
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Clear current transactions as they are now in the block
        self.current_transactions = []
        
        # add block to chain
        self.chain.append(block)
        return block



    # adds a new transaction to the list of un mined transactions
    def new_transaction(self, sender, vote):      
        raw_chain = self.chain
        transactions = []
        
        for each in raw_chain:
            transactions.extend(each['transactions'])
        
        # check both the chain and transactions if the user has already voted
        voted_list = []
        for each in transactions:
            voted_list.extend([each['sender']])
            
        raw_unmined_transaction = self.current_transactions
    
        for each in raw_unmined_transaction:
            voted_list.extend([each['sender']])
        
            
        if sender not in voted_list:        
            self.current_transactions.append({
                'sender': sender,
                'vote': vote,
            })
            r = dict()
            r['success_code']  = 'True' 
            r['i'] = self.last_block['index'] + 1
            return r 
            
    
        else:
            r = dict()
            r['success_code']  = 'False' 
            r['i'] = ''
            return r 
            

    @property
    def last_block(self):
        return self.chain[-1]


    # Creates a SHA-256 hash of a Block
    @staticmethod
    def hash(block):
        # order hash dictionary for consistent hashing
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
        

    # proof of work to prove node correctly processed the request to prevent attacks
    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof
        
        
        
    def parse_data(self):
        # Check if chain is valid before sending
        response = self.valid_chain(self.chain)
        if response == False:
            return False
          
        raw_chain = self.chain
        transactions = []
    
        for each in raw_chain:
            transactions.extend(each['transactions'])
                
        vote_list = []
        
        for each in transactions:
            vote_list.extend(each['vote'])
        
        keys = list(Counter(vote_list).keys())
        values = list(Counter(vote_list).values())
        data = []
        
        i = 0
        while i < len(keys):
            this_key = keys[i]
            this_value = values[i]
            new_pair = {'option': this_key, 
                        'total': this_value}
            data.append(new_pair)
            
            i += 1

        return data


    def get_node_list(self):
        return str(list(self.nodes))
    
    
    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
       
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
        
        
        
    def clear_chain(self):
        self.chain = []
        # Re-create the genesis block
        self.new_block(previous_hash='1', proof=100)
        length = len(blockchain.chain)
    
        if length == 1:
            return True
        else:
            return False
        



# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()



"""
--- APP ROUTES ---
routes handle the incoming requests to the node
"""

@app.route('/mine', methods=['GET'])
def mine():
    # run the proof of work algorithm to get the next proof.
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)


    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    
    print('--- Mined Block(s) ---') 
       
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():

    # Check that the required fields are in the POST'ed data
    senderVal = request.args.get('sender')
    voteVal   = request.args.get('vote')
    if (senderVal is None or voteVal is None):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(senderVal, voteVal)
    
    success_code = index['success_code']
    i = index['i']
    
    if success_code == 'True':
        print(f'--- New Transaction ---     Added to Block: {i}  Sender: {senderVal}  Vote: {voteVal}')  

        response = {'message': f'Transaction will be added to Block {i}'}
        return jsonify(response), 201
    
    else:
        print(f'--- Failed Transaction ---     Sender: {senderVal} tried to vote again in Block: {i}')
        return jsonify('Error: You have already voted, your vote is already registered in the Blockchain or is waiting to be mined'), 401

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200
    

@app.route('/tobemined', methods=['GET'])
def to_be_mined():
    response = {
        'chain': blockchain.current_transactions,
        'length': len(blockchain.current_transactions),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    address = request.args.get('address')
    auto_add = request.args.get('auto_add')

    if auto_add == None:
        auto_add = False
        
    if address is None:
        return "Error: Please supply a valid list of nodes", 400

    else:
        blockchain.register_node(address, auto_add)

    response = {
        'message': 'New node have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/registerednodes', methods=['GET'])
def get_node_list():
    nodes = blockchain.get_node_list()
    return nodes, 200


@app.route('/verifychain', methods=['GET'])
def verify_chain():
    chain = blockchain.chain
    
    response = blockchain.valid_chain(chain)
    
    if response is True:
        
        print('--- Blockchain is verified ---')
        return jsonify(['--- Blockchain is verified ---'])
    else:
        print('---  WARNING  Blockchain is BROKEN ---')
        return jsonify(['--- Blockchain is Broken ---'])

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/getdata', methods=['GET'])
def get_data():
    
    data = blockchain.parse_data()
	
    if data == False:
        return jsonify('corrupt'), 400
    else:
        return jsonify(data), 200
	

@app.route('/resetchain', methods=['POST'])
def reset_chain():
	response = blockchain.clear_chain()
	return str(response)
	

@app.route('/setupchain', methods=['POST'])
def setup_chain():
    # Setup first block with data
    senderList = ['1', '2', '3']
    voteList = ['a', 'a', 'b']
    i = 0
    while i < len(senderList):
        senderVal = senderList[i]
        voteVal   = voteList[i]
        
    # Create a new Transaction
        index = blockchain.new_transaction(senderVal, voteVal)
        i +=1
    
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)


    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
        
    # Setup second block with data
    senderList = ['4', '5']
    voteList = ['a', 'b' ]
    i = 0
    while i < len(senderList):
        senderVal = senderList[i]
        voteVal   = voteList[i]
        
    # Create a new Transaction
        index = blockchain.new_transaction(senderVal, voteVal)
        i +=1 
    
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)


    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    
    print('--- Dummy Chain Set Up ---')
    
    return jsonify('--- Dummy Chain Set Up ---')
    
@app.route('/breakchain', methods=['GET'])
def break_chain():
   
    chain = blockchain.chain[1]['transactions'][0]  
    chain.update({'vote': 'c'})
    
    return jsonify(['Chain manually broken, vote changed from a to c'])
    





if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=usePort, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
