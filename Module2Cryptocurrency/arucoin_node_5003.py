# To be installed
#FLask
#Postman HTTP Client https://www.getpostman.com/
#requests library #pip install requests==2.18.4

#Module 2- Create a Cryptocurrency
import datetime #coz each block will have its own time stamp
import hashlib
import json # function used to encode the blocks before we hash them
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#request library will be used to connect nodes of the blockchain
#importedFlask class 
#jsonify to display the response of the request
#uuid4- to create address for each node
#urlparse-to parse the url of each node


'''Part 1- Building a block chain''' 
class Blockchain :
    
    def __init__(self):
        self.chain=[]#list containing different blocks
        self.transactions=[]#mempool
        self.create_block(proof = 1, previous_hash='0')#for genesis block
        self.nodes=set()

#creates block dictionary and appends it to the chain list
    def create_block(self, proof, previous_hash):
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'transactions':self.transactions#added the transactions into the block
            }#dictionary that defines each block
        self.transactions=[]#Emptying list after adding it to the block dict
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]#returns the last block of the chain
    
    #proof is prolly thr nonce
    def proof_of_work(self,previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof=True
            else:
                new_proof+=1
           
        return new_proof
    
    #hash func returns the cryptographic hash of the block
    #If sort_keys is true (default: False), then the output of dictionaries will be sorted by key. 
    #json.dumps() function converts a Python object into a json string.
    def hash(self, block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #FUNCTION THAT CHECKS IF A CHAIN IS Valid by checking if-
    #prevhash actually matches hash of prev block
    #if hashoperation of has '0000' in start
    #it checks this for each block
    def is_chain_valid(self,chain):
        previous_block=chain[0]
        block_index=1
        while block_index<len(chain):
            block=chain[block_index]
            if block['previous_hash']!=self.hash(previous_block):#if prevhash not equal to hash of previous block
                return False
            previous_proof=previous_block['proof']
            proof=block['proof']
            hash_operation=hashlib.sha256(str(proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]!='0000':
                return False
            previous_block=block
            block_index+=1
        return True 
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender, 
                                  'receiver':receiver, 
                                  'amount':amount})#appending a dictionary to transactions list
        previous_block=self.get_previous_block()
        return previous_block['index']+1#index of last block +1
    
    def add_node(self, address):
        parsed_url=urlparse(address)
        '''parsed_url cantains -->ParseResult(scheme='http', netloc='127.0.0.1:5000', path='/', params='', query='', fragment='')'''
        self.nodes.add(parsed_url.netloc)   
        
    def replace_chain(self):
        network = self.nodes #network that contains all the nodes all around the world 
        longest_chain = None
        max_length = len(self.chain)#length of the longest chain 
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
        #node=parse_url.netloc
        #each node has 127.0.0.1:5000,5001,5002, etc
            if response.status_code==200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length>max_length and self.is_chain_valid(chain):
                    max_length=length
                    longest_chain=chain
        if longest_chain:
             self.chain=longest_chain
             return True
        return False
                    


'''Part 2- Mining our blockchain'''
#Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#creating an address on port 5000
node_address=str(uuid4()).replace("-","")

#CREATING A BLOCKCHAIN
blockchain=Blockchain()#blochain obj of our very first blockchain class

#to start mining ur new block
#Minging a new block
@app.route("/mine_block",methods=['GET'])
#We then use the route() decorator to tell Flask what URL should trigger our function.
def mine_block():
    previous_block=blockchain.get_previous_block()
    previous_proof=previous_block['proof']
    proof=blockchain.proof_of_work(previous_proof)
    previous_hash=blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver="Saurabh", amount=1)
    block=blockchain.create_block(proof, previous_hash)
    response={'message':'Congratulations, u just mined a block!',
              'index':block['index'],
              'timestamp':block['timestamp'],
              'proof':block['proof'],
              'previous_hash':block['previous_hash'],
              'transactions':block['transactions']}
#now we just need to return the response
    return jsonify(response),200
# 200 -- --> OK HTTP status code

#second get request to
#Getting the full blockchain
#get_chain is name of our new request
@app.route("/get_chain",methods=['GET'])
#get_chain function just displays blockchain
def get_chain():
    response={'chain':blockchain.chain,
              'length':len(blockchain.chain)}
    return jsonify(response), 200

#running the app
#host = 0.0.0.0 to make the server publically available
#we will decentralize our blockchain in module 2

@app.route("/is_valid",methods=['GET'])
#get_chain function just displays blockchain
def is_valid():
    if blockchain.is_chain_valid(blockchain.chain):
        response={'message':'All good. The blockchain is valid'}
    else:    
        response={'message':'chain is NOT valid'}
    return jsonify(response), 200

#Adding a new transaction to the blockchain 
@app.route("/add_transaction",methods=['POST'])
def add_transaction():
#We will get the sender receiver and amount through the json file which we post in postman using
#get_json method
#variable json represents the json file itself
    json = request.get_json()
#Check if there are no missing keys 
    transaction_keys=["sender","receiver","amount"]
    if not all ( key in json for key in transaction_keys):
        return "Some elements of the transaction are missing!", 400
    index=blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response={'message':f'This transaction will be added to Block {index}'}
    return jsonify(response), 201
#The request has been fulfilled, resulting in the creation of a new resource so 201

'''Part3- Decentralizing our blockchain'''
#Two more requests
# 1) Connect the new nodes
# 2) Replace the chain on any node that is not up to date

#post request is a json file that contains the address of all the nodes
#json = {"nodes" : ["http://127.0.0.1:5000/", "http://127.0.0.1:5001/", "http://127.0.0.1:5001/"] }
@app.route("/connect_node",methods=['POST'])
def connect_node():
    json=request.get_json()
    nodes=json["nodes"]
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response={'message':'All the nodes are now connected. The arucoin contains the following nodes: ',
              'total_nodes':list(blockchain.nodes)}    
    return jsonify(response), 201

#Replacing the chain by the longest chain if needed 
@app.route("/replace_chain",methods=['GET'])
def replace_chain():
    if blockchain.replace_chain():
        response={'message':'The nodes had different chains so the chain was replaced.',
                  'new_chain':blockchain.chain}
    else:    
         response={'message':'All good. The chain is the longest one',
                  'actual_chain':blockchain.chain}
    return jsonify(response), 200



app.run(host='0.0.0.0',port=5003)
