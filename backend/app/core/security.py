from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

import jwt
import bcrypt
from app.core.Config.config import get_settings

"""Este modulo tiene funciones para el manejo de seguridad, incluyendo hashing de contraseñas y generación/decodificación de tokens JWT."""

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
    subject: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:

    settings = get_settings()
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = subject.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"type": "access", "exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(subject: dict[str, Any], expires_delta: timedelta | None = None) -> str:

    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)

    to_encode = subject.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"type": "refresh", "exp": expire, "jti": str(uuid4())})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:

    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.InvalidTokenError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:

    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.InvalidTokenError:
        return None


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()
