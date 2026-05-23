from sqlmodel import Session, select
from app.db.base import engine
from app.db.models.usuario import Usuario
from app.core.security import hash_password, verify_password

session = Session(engine)
user = session.exec(select(Usuario).where(Usuario.email == 'admin@foodstore.com')).first()
if user:
    print(f"Email: {user.email}")
    print(f"Hash actual: {user.password_hash}")
    print(f"Verifica admin1234: {verify_password('admin1234', user.password_hash)}")
    print(f"Verifica admin123: {verify_password('admin123', user.password_hash)}")

    nuevo_hash = hash_password('admin1234')
    user.password_hash = nuevo_hash
    session.add(user)
    session.commit()
    print(f"\nHash actualizado: {nuevo_hash}")
    print(f"Verifica despues de actualizar: {verify_password('admin1234', user.password_hash)}")
else:
    print("Usuario no encontrado")
session.close()
