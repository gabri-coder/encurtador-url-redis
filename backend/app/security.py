import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

SECRET_KEY = os.getenv("SECRET_KEY", "DEV_ONLY_CHANGE_THIS_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": subject, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    subject = payload.get("sub")
    if not subject:
        raise jwt.InvalidTokenError("Token sem identificador.")
    return subject
