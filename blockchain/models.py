from pydantic import BaseModel
from typing import List


class TransactionSchema(BaseModel):
    sender: str
    recipient: str
    amount: float


class BlockAddRequest(BaseModel):
    transactions: List[TransactionSchema]