from fastapi import APIRouter
from blockchain import Blockchain
from models import BlockAddRequest

router = APIRouter()
blockchain = Blockchain(difficulty=4)


@router.get("/chain")
def get_chain():
    return {"chain": blockchain.to_dict()}


@router.post("/mine")
def mine_block(req: BlockAddRequest):
    blockchain.add_block([tx.dict() for tx in req.transactions])
    return {"message": "Block mined successfully", "chain": blockchain.to_dict()}