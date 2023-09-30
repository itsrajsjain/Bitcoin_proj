import hashlib
import datetime
import json
import qrcode
from time import time
from typing import List
class Node:
    def __init__(self, left, right, value: str, content, is_copied=False) -> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.content = content
        self.is_copied = is_copied

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()

    def __str__(self):
        return (str(self.value))

    def copy(self):
        return Node(self.left, self.right, self.value, self.content, True)
#class end
class TrustedThirdParty:
    """Representing a trusted third party to hold security deposits."""
    def __init__(self):
        self.deposits = {}  # Storing deposits with the depositor's name as the key

    def deposit(self, name, amount):
        """Deposit a security amount."""
        self.deposits[name] = int(amount)

    def get_deposit(self, name):
        """Retrieve the deposit amount for a given entity."""
        return int(self.deposits.get(name, 0))
    def deduction(self, name , amount):
        x =int(self.deposits.get(name, 0));
        self.deposits[name] =int(x)-amount;
#class end
class MerkleTree:
    def __init__(self, values: List[str]) -> None:
        self.__buildTree(values)
    def __buildTree(self, values: List[str]) -> None:
        leaves: List[Node] = [Node(None, None, Node.hash(e), e) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1].copy())
        self.root: Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes: List[Node]) -> Node:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1].copy())
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            return Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value), nodes[0].content+"+"+nodes[1].content)

        left: Node = self.__buildTreeRec(nodes[:half])
        right: Node = self.__buildTreeRec(nodes[half:])
        value: str = Node.hash(left.value + right.value)
        content: str = f'{left.content}+{right.content}'
        return Node(left, right, value, content)

    def printTree(self) -> None:
        self.__printTreeRec(self.root)

    def __printTreeRec(self, node: Node) -> None:
        if node != None:
            if node.left != None:
                print("Left: "+str(node.left))
                print("Right: "+str(node.right))
            else:
                print("Input")

            if node.is_copied:
                print('(Padding)')
            print("Value: "+str(node.value))
            print("Content: "+str(node.content))
            print("")
            self.__printTreeRec(node.left)
            self.__printTreeRec(node.right)

    def getRootHash(self) -> str:
        return self.root.value
#class end
class Transaction: 
    def __init__(self, product_id,product_name, distributor, client , amount):
        self.product_id = product_id
        self.product_name = product_name
        self.distributor = distributor
        self.client = client
        self.amount = amount
        self.distributor_confirmed = False
        self.client_confirmed = False

    def distributor_confirm(self):
        """Distributor confirms dispatching the product"""
        self.distributor_confirmed = True

    def client_confirm(self):
        """Client confirms receiving the product"""
        self.client_confirmed = True

    def is_confirmed(self):
        """Check if both distributor and client have confirmed"""
        return self.distributor_confirmed and self.client_confirmed
    def status(self):
        if self.is_confirmed()==True:
            return "received"
        elif self.distributor_confirmed==True:
            return "dispached"
        else : 
            return "not dispached"
#class end             
class Manufacturer:
    _instance = None

    def __new__(cls, name):
        """Ensure there's only one instance of Manufacturer (Singleton Pattern)."""
        if not isinstance(cls._instance, cls):
            cls._instance = super(Manufacturer, cls).__new__(cls)
            cls._instance.name = name
        else:
            print("There can be only one Manufacturer")
        return cls._instance
#class end
class Distributor:

    def __init__(self, name):
        self.name = name
        self.current_transaction = None
    def register(self, trusted_party, security_amount):
        """Register distributor and deposit a security amount."""
        trusted_party.deposit(self.name, security_amount)   
    def deliver(self, product, client,blockchain):
        if not self.current_transaction or self.current_transaction.is_confirmed():
            # Distributor can initiate a new delivery if there's no ongoing transaction or if the previous one is confirmed
            for transaction in blockchain.current_transactions:
                if transaction.distributor ==self.name and transaction.product_name==product:
                    self.current_transaction = transaction  
            print(f"{self.name} initiated delivery of {product} to {client}")
        else:
            print(f"{self.name} cannot initiate a new delivery until the previous transaction is confirmed by both parties.")
    def confirm_dispatch(self):
        if self.current_transaction and not self.current_transaction.distributor_confirmed:
            self.current_transaction.distributor_confirm()
            print(f"{self.name} confirmed the dispatch of {self.current_transaction.product_name} to {self.current_transaction.client}")
        else:
            print(f"{self.name} cannot confirm the dispatch. Either there's no ongoing transaction or it's already confirmed.")
 #class end   
#class end
class Client:
    def __init__(self, name):
        self.name = name
    def register(self, trusted_party, security_amount):
        """Register client and deposit a security amount."""
        trusted_party.deposit(self.name, security_amount)
    def confirm_receipt(self, transaction):
        if transaction and not transaction.client_confirmed:
            transaction.client_confirm()
            print(f"{self.name} confirmed the receipt of {transaction.product} from {transaction.distributor.name}")
        else:
            print(f"{self.name} cannot confirm the receipt. Either there's no ongoing transaction or it's already confirmed.")
#class end
class Blockchain:
    difficulty = 4

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        self.new_block(previous_hash="1", proof=100, merkle_root=None)

    def new_block(self, previous_hash, proof, merkle_root):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'proof': proof,
            'merkle_root': merkle_root
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True, default=str).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self,transact):
        
        self.current_transactions.append(transact)

    def register_node(self, address):
        self.nodes.add(address) 

    @staticmethod
    def proof_of_work(last_proof):
        proof = 0
        while Blockchain.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:Blockchain.difficulty] == "0" * Blockchain.difficulty

    def mine_block(self):
        # Calculate Merkle root for transactions in the current block
        transaction_hashes = [self.hash(tx) for tx in self.current_transactions]
        merkle_tree = MerkleTree(transaction_hashes)
        merkle_root = merkle_tree.getRootHash()

        # Mining (PoW)
        last_block = self.chain[-1]
        last_proof = last_block['proof']
        proof = self.proof_of_work(last_proof)

        # Create a new block
        previous_hash = self.hash(last_block)
        block = self.new_block(previous_hash, proof, merkle_root)

        return block
#class end
class QR:
    def __init__(self):
        self.transaction = None;
    def new_transaction(self,transact):
        self.transaction = transact
    def generate_qr_code(self):
        img = qrcode.make(f"product id: {self.transaction.product_id} product name: {self.transaction.product_name} product status: {self.transaction.status()}")
        img.save(f"{self.transaction.product_name}.png")
#class end
class SupplyChainSystem:
    def __init__(self):
        self.distributors = {}  # Using a dictionary to store distributor objects with their name as the key
        self.clients = {}
        self.trusted_party = TrustedThirdParty()

    def register_distributor(self, distributor_name,amount,trusted_party):
        if distributor_name not in self.distributors:
            distributor = Distributor(distributor_name)
            distributor.register(trusted_party,amount)
            self.distributors[distributor_name] = distributor
            print(f"Distributor {distributor_name} registered.")
            return distributor
        else:
            print(f"Distributor {distributor_name} already exists.")
            return self.distributors[distributor_name]

    def register_client(self, client_name,amount,trusted_party ):
        if client_name not in self.clients:
            client = Client(client_name)
            client.register(trusted_party,amount)
            self.clients[client_name] = client
            print(f"Client {client_name} registered.")
            return client
        else:
            print(f"Client {client_name} already exists.")
            return self.clients[client_name]

    def get_distributor(self, distributor_name):
        return self.distributors.get(distributor_name, None)

    def get_client(self, client_name):
        return self.clients.get(client_name, None)