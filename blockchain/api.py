from fastapi import APIRouter, HTTPException
from blockchain import Blockchain
from models import BlockAddRequest, UserRegisterRequest, UserLoginRequest, TransactionCreateRequest
from storage import register_user, get_user, authenticate

router = APIRouter()
blockchain = Blockchain()
blockchain.load_blocks_from_disk()

@router.get("/chain")
def get_chain():
    return {"chain": blockchain.to_dict()}

@router.post("/mine")
def mine_block(req: BlockAddRequest):
    blockchain.add_block([tx.dict() for tx in req.transactions])
    blockchain.save_block_to_disk(blockchain.get_latest_block())
    return {"message": "Block mined successfully", "chain_length": len(blockchain.chain)}

@router.post("/register")
def register(req: UserRegisterRequest):
    try:
        user = register_user(req.username, req.password)
        # Адрес кошелька не создается на этапе регистрации
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(req: UserLoginRequest):
    user = authenticate(req.username, req.password)
    if user:
        return {"address": user.address}
    return {"address": ""}

@router.post("/transaction")
def create_transaction(req: TransactionCreateRequest):
    # Аутентификация отправителя
    user = authenticate(req.sender_username, req.sender_password)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")

    # Проверка баланса
    balance = blockchain.get_balance(user.address)
    if balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Добавление транзакции
    success = blockchain.add_transaction(req.sender_address, req.recipient_address, req.amount)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add transaction")
    
    return {"message": "Transaction successfully created"}

@router.get("/transactions/{wallet_address}")
def get_transactions(wallet_address: str):
    txs = blockchain.get_transactions_by_address(wallet_address)
    return {"transactions": txs}

@router.post("/balance")
def get_balance(req: UserLoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    balance = blockchain.get_balance(user.address)
    return {"balance": balance}
