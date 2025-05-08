import hashlib
import time
import json
import os
import pickle
from models import Transaction

def hash_sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

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
        self.pending_transactions = []
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
    def __init__(self, difficulty=3):
        self.chain = []
        self.difficulty = difficulty
        self.blocks_dir = "blocks"
        self.pending_transactions = []
        os.makedirs(self.blocks_dir, exist_ok=True)

    def create_genesis_block(self):
        return Block(0, [], "0" * 64, difficulty=1, data="Genesis Block")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        tx = Transaction(sender, recipient, amount)
        self.pending_transactions.append(tx)

        #Если накопилось 2 транзакций — майним блок
        if len(self.pending_transactions) >= 2:
            self.mine_pending_transactions()
            self.save_block_to_disk(self.get_latest_block())
            print("[INFO] Автоматический майнинг блока выполнен.")

        return True

    def mine_pending_transactions(self):
        if not self.pending_transactions:
            return None

        previous_hash = self.chain[-1].hash if self.chain else "0" * 64
        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=previous_hash,
            difficulty=self.difficulty,
            data=None
        )
        self.chain.append(block)
        self.pending_transactions.clear()
        return block

    def credit_balance(self, address, amount):
        return self.add_transaction("SYSTEM", address, amount)

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        return balance

    def get_transactions_by_address(self, address):
        txs = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    txs.append(str(tx))
        return txs

    def save_block_to_disk(self, block):
        path = os.path.join(self.blocks_dir, f"{block.index}.blk")
        with open(path, "wb") as f:
            pickle.dump(block, f)

    def load_blocks_from_disk(self):
        files = sorted(os.listdir(self.blocks_dir), key=lambda x: int(x.split('.')[0]))
        for filename in files:
            path = os.path.join(self.blocks_dir, filename)
            with open(path, "rb") as f:
                block = pickle.load(f)
                self.chain.append(block)
        if not self.chain:
            genesis = self.create_genesis_block()
            self.chain.append(genesis)
            self.save_block_to_disk(genesis)
        is_valid, message = self.validate_chain()
        if not is_valid:
            raise ValueError(f"Blockchain integrity check failed: {message}")
        else:
            print("[INFO] Blockchain validated successfully.")

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False, f"Hash mismatch at block {current.index}"
            if current.previous_hash != previous.hash:
                return False, f"Previous hash mismatch at block {current.index}"
            expected_merkle_root = MerkleTree.get_merkle_root(current.transactions)
            if current.merkle_root != expected_merkle_root:
                return False, f"Invalid Merkle Root at block {current.index}"
        return True, "Blockchain is valid"

    def to_dict(self):
        return [block.to_dict() for block in self.chain]
