from fastapi import APIRouter, HTTPException, Query
from blockchain import Blockchain
from models import BlockAddRequest, UserRegisterRequest, AuthRequest
from storage import register_user, get_user, authenticate_user

router = APIRouter()
blockchain = Blockchain()
blockchain.generate_initial_blocks(5)

@router.get("/chain")
def get_chain():
    return {"chain": blockchain.to_dict()}

@router.post("/mine")
def mine_block(req: BlockAddRequest):
    blockchain.add_block([tx.dict() for tx in req.transactions])
    return {"message": "Block mined successfully", "chain_length": len(blockchain.chain)}

@router.post("/register")
def register(req: UserRegisterRequest):
    try:
        user = register_user(req.username, req.password)
        data = {
            "type": "user_registration",
            "username": user.username,
            "address": user.address,
            "password_hash": user.password_hash
        }
        blockchain.add_block([], data=str(data))
        return {"message": "User registered", "address": user.address}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/block/{index}")
def get_block(index: int):
    if index < 0 or index >= len(blockchain.chain):
        raise HTTPException(status_code=404, detail="Block not found")
    return blockchain.chain[index].to_dict()

@router.post("/store-data/")
def store_data(data: str):
    blockchain.add_block([], data=data)
    return {"message": "Data stored in new block", "block_index": len(blockchain.chain) - 1}

@router.get("/transactions/by-address")
def get_transactions(address: str = Query(..., description="Крипто-адрес")):
    txs = blockchain.get_transactions_by_address(address)
    return {"address": address, "transactions": txs, "count": len(txs)}

@router.post("/balance")
def get_balance(auth: AuthRequest):
    if not authenticate_user(auth.address, auth.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    balance = blockchain.get_balance(auth.address)
    return {"address": auth.address, "balance": balance}
