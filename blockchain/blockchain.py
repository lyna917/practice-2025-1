import hashlib
import time
import json
import os
import pickle


def hash_sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return json.dumps(self.__dict__, sort_keys=True)


class MerkleTree:
    @staticmethod
    def get_merkle_root(transactions):
        if not transactions:
            return None
        hashes = [hash_sha256(str(tx)) for tx in transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [hash_sha256(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
        return hashes[0]


class Block:
    def __init__(self, index, transactions, previous_hash, difficulty, data=None):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = MerkleTree.get_merkle_root(transactions)
        self.nonce = 0
        self.data = data
        self.hash = self.mine_block(difficulty)

    def calculate_hash(self):
        data_str = json.dumps(self.data, sort_keys=True) if isinstance(self.data, dict) else str(self.data)
        block_string = f"{self.index}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}{data_str}"
        return hash_sha256(block_string)

    def mine_block(self, difficulty):
        prefix = '0' * difficulty
        while True:
            hash_val = self.calculate_hash()
            if hash_val.startswith(prefix):
                return hash_val
            self.nonce += 1

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [str(tx) for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
            "data": self.data,
            "hash": self.hash,
        }


class Blockchain:
    def __init__(self, difficulty=4, storage_dir='blocks'):
        self.difficulty = difficulty
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.chain = self.load_chain()

    def create_genesis_block(self):
        return Block(0, [], "0" * 64, difficulty=1, data="Genesis Block")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions, data=None):
        prev_block = self.get_latest_block()
        tx_objs = [Transaction(**tx) for tx in transactions]
        new_block = Block(
            index=len(self.chain),
            transactions=tx_objs,
            previous_hash=prev_block.hash,
            difficulty=self.difficulty,
            data=data
        )
        self.chain.append(new_block)
        self.save_block(new_block)

    def to_dict(self):
        return [block.to_dict() for block in self.chain]

    def save_block(self, block):
        filename = os.path.join(self.storage_dir, f"{block.index}.blk")
        with open(filename, "wb") as f:
            pickle.dump(block, f)

    def load_chain(self):
        chain = []
        files = sorted(f for f in os.listdir(self.storage_dir) if f.endswith(".blk"))
        for filename in files:
            with open(os.path.join(self.storage_dir, filename), "rb") as f:
                block = pickle.load(f)
                chain.append(block)
        if not chain:
            genesis = self.create_genesis_block()
            self.save_block(genesis)
            return [genesis]
        return chain
