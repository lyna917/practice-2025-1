import hashlib
import time
import json
import os
import pickle

BLOCKS_DIR = "blocks"

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
            new_level = []
            for i in range(0, len(hashes), 2):
                new_hash = hash_sha256(hashes[i] + hashes[i + 1])
                new_level.append(new_hash)
            hashes = new_level

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
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain = self.load_blocks_from_files()
        if not self.chain:
            genesis = self.create_genesis_block()
            self.chain = [genesis]
            self.save_block_to_file(genesis)

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
        self.save_block_to_file(new_block)

    def save_block_to_file(self, block):
        os.makedirs(BLOCKS_DIR, exist_ok=True)
        filename = os.path.join(BLOCKS_DIR, f"{block.index:08d}.blk")
        with open(filename, "wb") as f:
            pickle.dump(block, f)

    def load_blocks_from_files(self):
        if not os.path.exists(BLOCKS_DIR):
            return []

        files = sorted(os.listdir(BLOCKS_DIR))
        chain = []

        for filename in files:
            path = os.path.join(BLOCKS_DIR, filename)
            with open(path, "rb") as f:
                block = pickle.load(f)

                # Проверка связности
                if chain and block.previous_hash != chain[-1].hash:
                    raise ValueError(f"Нарушена целостность цепочки в блоке {filename}")
                chain.append(block)

        return chain

    def to_dict(self):
        return [block.to_dict() for block in self.chain]

    def generate_initial_blocks(self, count=1000):
        for i in range(count):
            self.add_block([], data={"type": "init", "index": i})