from fastapi import APIRouter, HTTPException
from blockchain import Blockchain
from models import BlockAddRequest, UserRegisterRequest, AuthRequest, BalanceRequest
from storage import register_user, get_user, authenticate, hash_password, users

router = APIRouter()
blockchain = Blockchain()


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


@router.post("/auth")
def auth(req: AuthRequest):
    address = authenticate(req.username, req.password)
    return {"address": address}


@router.post("/balance")
def get_balance(req: BalanceRequest):
    user = get_user_by_address(req.address)
    if not user or user.password_hash != hash_password(req.password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    balance = 0.0
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.sender == req.address:
                balance -= tx.amount
            elif tx.recipient == req.address:
                balance += tx.amount
    return {"balance": balance}


def get_user_by_address(address: str):
    for user in users.values():
        if user.address == address:
            return user
    return None
