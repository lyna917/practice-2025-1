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

class AuthRequest(BaseModel):
    address: str
    password: str

class User(BaseModel):
    username: str
    address: str
    password_hash: str
