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


class User(BaseModel):
    username: str
    address: str
    password_hash: str


class AuthRequest(BaseModel):
    username: str
    password: str


class BalanceRequest(BaseModel):
    address: str
    password: str
