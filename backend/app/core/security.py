from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
from app.core.config import get_settings


def hash_password(password: str) -> str:
    """
    Genera hash bcrypt de una contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash bcrypt de la contraseña
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash bcrypt almacenado
        
    Returns:
        True si la contraseña es válida, False en caso contrario
    """
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(
    subject: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un JWT access token.
    
    Args:
        subject: Datos a incluir en el token (ej: {"user_id": 1})
        expires_delta: Duración del token. Si no se proporciona usa ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        JWT token como string
    """
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
    """
    Decodifica y valida un JWT token.
    
    Args:
        token: JWT token como string
        
    Returns:
        Diccionario con el payload del token, o None si es inválido
    """
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
