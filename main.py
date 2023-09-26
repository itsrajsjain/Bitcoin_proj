import hashlib
import json
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
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }
        self.current_transactions.append(transaction)

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

# Create the blockchain
blockchain = Blockchain()

# Register nodes
blockchain.register_node("Node1")
blockchain.register_node("Node2")

# Create new transactions
blockchain.new_transaction("Manufacturer", "Distributor1", 10)
blockchain.new_transaction("Manufacturer", "Distributor2", 20)
blockchain.new_transaction("Distributor1", "Client1", 5)

# Mine the block with transactions
mined_block = blockchain.mine_block()

# Print blockchain details
print("Blockchain:")
for block in blockchain.chain:
    print("\nBlock:", block['index'])
    print("Timestamp:", block['timestamp'])
    print("Previous Hash:", block['previous_hash'])
    print("Proof:", block['proof'])
    print("Merkle Root:", block['merkle_root'])
    print("Transactions:", block['transactions'])

# Print registered nodes
print("\nRegistered Nodes:")
for node in blockchain.nodes:
    print(node)

