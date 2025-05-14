import hashlib
import secrets
import pickle
import os
from models import User
from typing import Optional

USERS_FILE = "users.pkl"
users = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_address() -> str:
    return "ADDR_" + secrets.token_hex(16)

def save_users_to_disk():
    with open(USERS_FILE, "wb") as f:
        pickle.dump(users, f)

def load_users_from_disk():
    global users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "rb") as f:
            users = pickle.load(f)

def register_user(username: str, password: str) -> User:
    if username in users:
        raise ValueError("Пользователь уже существует")
    address = generate_address()
    password_hash = hash_password(password)
    user = User(username=username, address=address, password_hash=password_hash)
    users[username] = user
    save_users_to_disk()
    return user

def get_user(username: str) -> Optional[User]:
    return users.get(username)

def authenticate(username: str, password: str) -> Optional[User]:
    user = users.get(username)
    if user and user.password_hash == hash_password(password):
        return user
    return None

# Загружаем пользователей при импорте
load_users_from_disk()
