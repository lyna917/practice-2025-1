from fastapi import APIRouter, HTTPException, status
from blockchain import Blockchain
from models import BlockAddRequest, UserRegisterRequest, UserLoginRequest, TransactionCreateRequest
from storage import register_user, get_user, authenticate

router = APIRouter()
blockchain = Blockchain()
blockchain.load_blocks_from_disk()

@router.get(
    "/chain",
    status_code=status.HTTP_200_OK,
    summary="Get full blockchain",
    description="Возвращает всю цепочку блоков.",
    responses={
        200: {"description": "Цепочка блоков успешно получена"},
        500: {"description": "Внутренняя ошибка сервера"},
    }
)
def get_chain():
    return {"chain": blockchain.to_dict()}

@router.post(
    "/mine",
    status_code=status.HTTP_201_CREATED,
    summary="Mine new block",
    description="Создает новый блок с переданными транзакциями.",
    responses={
        201: {"description": "Блок успешно создан"},
        400: {"description": "Неверные входные данные"},
        500: {"description": "Ошибка при майнинге блока"},
    }
)
def mine_block(req: BlockAddRequest):
    try:
        blockchain.add_block([tx.dict() for tx in req.transactions])
        blockchain.save_block_to_disk(blockchain.get_latest_block())
        return {"message": "Block mined successfully", "chain_length": len(blockchain.chain)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Mining failed")

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Создает нового пользователя без адреса кошелька.",
    responses={
        201: {"description": "Пользователь успешно зарегистрирован"},
        400: {"description": "Пользователь уже существует"},
    }
)
def register(req: UserRegisterRequest):
    try:
        user = register_user(req.username, req.password)
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Проверяет логин и пароль. Возвращает адрес кошелька или пустую строку.",
    responses={
        200: {"description": "Аутентификация успешна"},
        401: {"description": "Неверные учетные данные"},
    }
)
def login(req: UserLoginRequest):
    user = authenticate(req.username, req.password)
    if user:
        return {"address": user.address}
    return {"address": ""}

@router.post(
    "/transaction",
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction",
    description="Создает транзакцию после аутентификации и проверки баланса.",
    responses={
        201: {"description": "Транзакция успешно создана"},
        400: {"description": "Недостаточно средств или ошибка данных"},
        401: {"description": "Ошибка аутентификации"},
    }
)
def create_transaction(req: TransactionCreateRequest):
    user = authenticate(req.sender_username, req.sender_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    balance = blockchain.get_balance(user.address)
    if balance < req.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    success = blockchain.add_transaction(req.sender_address, req.recipient_address, req.amount)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add transaction")
    
    return {"message": "Transaction successfully created"}

@router.get(
    "/transactions/{wallet_address}",
    status_code=status.HTTP_200_OK,
    summary="Get transactions for a wallet",
    description="Возвращает список всех транзакций по адресу кошелька.",
    responses={
        200: {"description": "Список транзакций получен"},
        404: {"description": "Кошелек не найден (если нужно добавить такую проверку)"},
    }
)
def get_transactions(wallet_address: str):
    txs = blockchain.get_transactions_by_address(wallet_address)
    return {"transactions": txs}

@router.post(
    "/balance",
    status_code=status.HTTP_200_OK,
    summary="Get wallet balance",
    description="Возвращает баланс кошелька после проверки логина и пароля.",
    responses={
        200: {"description": "Баланс успешно получен"},
        401: {"description": "Неверные учетные данные"},
    }
)
def get_balance(req: UserLoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    balance = blockchain.get_balance(user.address)
    return {"balance": balance}
