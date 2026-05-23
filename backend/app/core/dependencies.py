from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.db.models.usuario import Usuario
from app.core.security import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    uow: SqlModelUnitOfWork = Depends(get_uow)
) -> Usuario:
    
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

    statement = select(Usuario).where(Usuario.id == user_id)
    user = uow.session.exec(statement).first()

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

    async def verify_role(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        user_roles = [r.nombre for r in current_user.roles]
        
        # Si no se requieren roles específicos, solo estar autenticado
        if not required_roles:
            return current_user
            
        # Verificar si el usuario tiene al menos uno de los roles requeridos
        has_role = any(role in user_roles for role in required_roles)
        
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos suficientes. Se requiere uno de los siguientes roles: {', '.join(required_roles)}"
            )
            
        return current_user

    return verify_role
