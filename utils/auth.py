# book_app/utils/auth.py

import json
import os
import bcrypt
from pydantic import BaseModel, Field, EmailStr
from .logger import log_operation


DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")

class User(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserInDB(User):
    hashed_password: str

def get_users_db():
    """Carga la base de datos de usuarios desde el archivo JSON."""
    if not os.path.exists(USERS_FILE):
        return {} # Aunque siempre va a existir porque se crea inmediatamente después de iniciar el programa
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users_db(db):
    """Guarda la base de datos de usuarios en el archivo JSON."""
    with open(USERS_FILE, "w") as f:
        json.dump(db, f, indent=4)

def get_password_hash(password: str) -> str:
    """Hashea una contraseña usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username: str, email: str, password: str) -> bool:
    """Registra un nuevo usuario."""
    db = get_users_db()
    if username in db:
        log_operation(user=username, operation="REGISTER", result="Failure - User already exists")
        return False
    
    hashed_password = get_password_hash(password)
    db[username] = {"email": email, "hashed_password": hashed_password}
    save_users_db(db)
    log_operation(user=username, operation="REGISTER", result="Success")
    return True

def login_user(username: str, password: str) -> bool:
    """Inicia sesión con un usuario y contraseña."""
    db = get_users_db()
    user_data = db.get(username)
    
    if not user_data:
        log_operation(user=username, operation="LOGIN", result="Failure - User not found")
        return False
        
    if verify_password(password, user_data["hashed_password"]):
        log_operation(user=username, operation="LOGIN", result="Success")
        return True
    
    log_operation(user=username, operation="LOGIN", result="Failure - Invalid password")
    return False