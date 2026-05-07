from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
from app.core.config import get_settings


def hash_password(password: str) -> str:

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:

    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(
    subject: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:

    settings = get_settings()
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = subject.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:

    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.InvalidTokenError:
        return None
