from sqlmodel import Session, select
from app.db.base import engine
from app.db.models.usuario import Usuario, UsuarioRol
from app.db.models.rol import Rol

session = Session(engine)

user = session.exec(select(Usuario).where(Usuario.email == 'admin@foodstore.com')).first()
if user:
    print(f"Usuario: {user.email} (ID: {user.id})")

    roles_query = select(Rol).join(UsuarioRol).where(UsuarioRol.usuario_id == user.id)
    roles = session.exec(roles_query).all()

    if roles:
        print(f"Roles: {[r.nombre for r in roles]}")
    else:
        print("Roles: NINGUNO - El usuario no tiene roles asignados!")

        admin_rol = session.exec(select(Rol).where(Rol.nombre == 'ADMIN')).first()
        if admin_rol:
            print(f"\nAsignando rol ADMIN (ID: {admin_rol.id})...")
            session.add(UsuarioRol(usuario_id=user.id, rol_id=admin_rol.id))
            session.commit()
            print("Rol ADMIN asignado!")
        else:
            print("No existe el rol ADMIN en la BD!")
else:
    print("Usuario no encontrado")

session.close()
