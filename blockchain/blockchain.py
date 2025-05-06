import hashlib
import time
import json


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
        hashes = [hash_sha256(str(tx)) for tx in transactions]
        if not hashes:
            return None
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            new_level = []
            for i in range(0, len(hashes), 2):
                new_hash = hash_sha256(hashes[i] + hashes[i + 1])
                new_level.append(new_hash)
            hashes = new_level
        return hashes[0]


class Block:
    def __init__(self, index, transactions, previous_hash, difficulty):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = MerkleTree.get_merkle_root(transactions)
        self.nonce = 0
        self.hash = self.mine_block(difficulty)

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}"
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
            "hash": self.hash,
        }


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty

    def create_genesis_block(self):
        return Block(0, [], "0" * 64, difficulty=1)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        prev_block = self.get_latest_block()
        tx_objs = [Transaction(**tx) for tx in transactions]
        new_block = Block(len(self.chain), tx_objs, prev_block.hash, self.difficulty)
        self.chain.append(new_block)

    def to_dict(self):
        return [block.to_dict() for block in self.chain]
