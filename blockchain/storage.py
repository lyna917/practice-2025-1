import hashlib
import secrets
from models import User

users = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_address() -> str:
    return "ADDR_" + secrets.token_hex(16)

def register_user(username: str, password: str) -> User:
    if username in users:
        raise ValueError("Пользователь уже существует")
    address = generate_address()
    password_hash = hash_password(password)
    user = User(username=username, address=address, password_hash=password_hash)
    users[username] = user
    return user

def get_user(username: str) -> User:
    return users.get(username)

def authenticate_user(address: str, password: str) -> bool:
    for user in users.values():
        if user.address == address:
            return user.password_hash == hash_password(password)
    return False
