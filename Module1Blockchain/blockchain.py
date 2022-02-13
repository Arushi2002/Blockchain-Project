#module 1- Create a blockchain
import datetime #coz each block will have its own time stamp
import hashlib
import json # function used to encode the blocks before we hash them
from flask import Flask, jsonify
#importedFlask class 
#jsonify to display the response of the request

#Part 1- Building a block chain 
class Blockchain :
    
    def __init__(self):
        self.chain=[]#list containing different blocks
        self.create_block(proof = 1, previous_hash='0')#for genesis block

#creates block dictionary and appends it to the chain list
    def create_block(self, proof, previous_hash):
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash
            }#dictionary that defines each block
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
    '''If sort_keys is true (default: False), then the output of dictionaries will be sorted by key. '''
    '''json.dumps() function converts a Python object into a json string.'''
    def hash(self, block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #FUNCTION THAT CHECKS IF A CHAIN IS Valid by checking if-
    #prevhash actually matches hash of prev block
    #if hashoperation of has '0000' in start
    #it checks this for each block
    def is_chain_vaild(self,chain):
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
    


#Part 2- Mining our blockchain
# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


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
    block=blockchain.create_block(proof, previous_hash)
    response={'message':'Congratulations, u just mined a block!',
              'index':block['index'],
              'timestamp':block['timestamp'],
              'proof':block['proof'],
              'previous_hash':block['previous_hash']}
    #now we just need to return the response
    return jsonify(response),200
#200---->OK HTTP status code


#second get request to
#Getting the full blockchain
#get_chai  is name of our new request
@app.route("/get_chain",methods=['GET'])
#get_chain function just displays blockchain
def get_chain():
    response={'chain':blockchain.chain,
              'length':len(blockchain.chain)}
    return jsonify(response), 200

#running the app
#host=0.0.0.0 to make the server publically available
#we will decentralize our blockchain in module 2

@app.route("/is_valid",methods=['GET'])
#get_chain function just displays blockchain
def is_valid():
    if blockchain.is_chain_vaild(blockchain.chain):
        response={'message':'chain is valid'}
    else:    
        response={'message':'chain is NOT valid'}
    return jsonify(response), 200

app.run(host='0.0.0.0',port=5000)
    
