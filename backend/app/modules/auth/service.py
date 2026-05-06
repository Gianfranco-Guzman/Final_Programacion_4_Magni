from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.db.models.usuario import Usuario
from app.db.models.rol import Rol
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    UsuarioResponse,
    RolResponse,
)


class AuthService:
    """Servicio de autenticación"""

    @staticmethod
    def autenticar(email: str, password: str, session: Session) -> Usuario:
        """
        Autentica un usuario por email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            session: Sesión de base de datos
            
        Returns:
            Usuario autenticado
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        statement = select(Usuario).where(Usuario.email == email)
        user = session.exec(statement).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña inválidos",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
            )
        
        return user

    @staticmethod
    def crear_usuario(request: RegisterRequest, session: Session) -> Usuario:
        """
        Crea un nuevo usuario en el sistema.
        
        Args:
            request: Datos del registro
            session: Sesión de base de datos
            
        Returns:
            Usuario creado
            
        Raises:
            HTTPException: Si el email ya existe
        """
        # Verificar que el email no exista
        statement = select(Usuario).where(Usuario.email == request.email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email ya está registrado",
            )
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            email=request.email,
            password_hash=hash_password(request.password),
            nombre=request.nombre,
            is_active=True,
        )
        
        session.add(nuevo_usuario)
        session.commit()
        session.refresh(nuevo_usuario)
        
        # Asignar rol CLIENT por defecto
        client_rol = session.exec(
            select(Rol).where(Rol.nombre == "CLIENT")
        ).first()
        
        if client_rol:
            from app.db.models.usuario import UsuarioRol
            usuario_rol = UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=client_rol.id)
            session.add(usuario_rol)
            session.commit()
        
        return nuevo_usuario

    @staticmethod
    def obtener_usuario_con_roles(usuario_id: int, session: Session) -> UsuarioResponse:
        """
        Obtiene un usuario con sus roles asociados.
        
        Args:
            usuario_id: ID del usuario
            session: Sesión de base de datos
            
        Returns:
            UsuarioResponse con información del usuario y roles
        """
        statement = select(Usuario).where(Usuario.id == usuario_id)
        usuario = session.exec(statement).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        
        # TODO: Cargar roles desde UsuarioRol (FASE 2)
        # Por ahora retornamos lista vacía
        
        return UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            is_active=usuario.is_active,
            roles=[],
        )
