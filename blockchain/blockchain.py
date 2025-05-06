import hashlib
import json
import time


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

    def __repr__(self):
        return json.dumps(self.__dict__, indent=2, sort_keys=True, default=str)


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
        new_block = Block(len(self.chain), transactions, prev_block.hash, self.difficulty)
        self.chain.append(new_block)

    def is_valid(self):
        prefix = '0' * self.difficulty
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i - 1]
            if cur.hash != cur.calculate_hash():
                return False
            if not cur.hash.startswith(prefix):
                return False
            if cur.previous_hash != prev.hash:
                return False
        return True


# Пример использования
if __name__ == "__main__":
    blockchain = Blockchain(difficulty=4)
    tx1 = Transaction("Alice", "Bob", 10)
    tx2 = Transaction("Bob", "Charlie", 5)

    print("⛏ Майнинг блока 1...")
    blockchain.add_block([tx1, tx2])

    tx3 = Transaction("Charlie", "Alice", 2)
    print("⛏ Майнинг блока 2...")
    blockchain.add_block([tx3])

    for block in blockchain.chain:
        print(block)

    print("Цепочка валидна:", blockchain.is_valid())