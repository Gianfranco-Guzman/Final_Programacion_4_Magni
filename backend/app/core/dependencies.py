from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.db.base import get_session
from app.db.models.usuario import Usuario
from app.core.security import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> Usuario:
    """
    Dependencia para obtener el usuario actual desde el token JWT.
    Se usa en endpoints que requieren autenticación.

    Args:
        credentials: Credenciales HTTP Bearer
        session: Sesión de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Token inválido o expirado
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene información de usuario",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene un ID de usuario válido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Obtener usuario de la base de datos
    statement = select(Usuario).where(Usuario.id == user_id)
    user = session.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_role(*required_roles: str):
    """
    Dependencia para requerir que el usuario tenga uno de los roles especificados.
    Uso: @app.get("/admin", dependencies=[Depends(require_role("ADMIN"))])

    Args:
        required_roles: Nombres de roles requeridos

    Returns:
        Función decoradora que valida roles
    """
    async def verify_role(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        # TODO: Implementar en FASE 2 cuando tengamos relaciones cargadas
        # Por ahora retornamos el usuario directamente
        return current_user

    return verify_role
