from pydantic import BaseModel
from typing import List

class TransactionSchema(BaseModel):
    sender: str
    recipient: str
    amount: float

class BlockAddRequest(BaseModel):
    transactions: List[TransactionSchema]

class UserRegisterRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TransactionCreateRequest(BaseModel):
    sender_username: str
    sender_password: str
    sender_address: str
    recipient_address: str
    amount: float

class User(BaseModel):
    username: str
    address: str
    password_hash: str

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"
