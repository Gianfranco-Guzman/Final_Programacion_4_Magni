from sqlmodel import Session, select
from app.db.base import engine
from app.db.models.rol import Rol
from app.db.models.usuario import Usuario, UsuarioRol
from app.db.models.categoria import Categoria
from app.db.models.producto import Producto
from app.core.security import hash_password


def populate_seed_data() -> None:
    session = Session(engine)

    try:
        existing_roles = session.exec(select(Rol)).all()
        if existing_roles:
            print("Datos seed ya existen")
            return

        roles_data = [
            Rol(nombre="ADMIN", descripcion="Administrador del sistema"),
            Rol(nombre="CLIENT", descripcion="Cliente final"),
            Rol(nombre="STOCK", descripcion="Gestor de inventario"),
            Rol(nombre="PEDIDOS", descripcion="Procesador de pedidos"),
        ]
        for rol in roles_data:
            session.add(rol)
        session.commit()

        admin_rol = session.exec(select(Rol).where(Rol.nombre == "ADMIN")).first()

        admin_user = Usuario(
            email="admin@foodstore.com",
            password_hash=hash_password("admin123"),
            nombre="Administrador",
            is_active=True,
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        if admin_rol:
            session.add(UsuarioRol(usuario_id=admin_user.id, rol_id=admin_rol.id))
            session.commit()

        categorias_data = [
            Categoria(nombre="Pizzas", descripcion="Pizzas tradicionales y especiales"),
            Categoria(nombre="Bebidas", descripcion="Bebidas frias y calientes"),
            Categoria(nombre="Postres", descripcion="Postres y dulces"),
            Categoria(nombre="Entradas", descripcion="Entradas y snacks"),
        ]
        for cat in categorias_data:
            session.add(cat)
        session.commit()

        pizzas = session.exec(select(Categoria).where(Categoria.nombre == "Pizzas")).first()
        bebidas = session.exec(select(Categoria).where(Categoria.nombre == "Bebidas")).first()
        postres = session.exec(select(Categoria).where(Categoria.nombre == "Postres")).first()
        entradas = session.exec(select(Categoria).where(Categoria.nombre == "Entradas")).first()

        productos_data = [
            Producto(nombre="Pizza Clasica", descripcion="Pizza con salsa, queso y oregano", precio=299.99, stock_cantidad=50, categoria_id=pizzas.id, codigo="PIZZA-001"),
            Producto(nombre="Pizza Pepperoni", descripcion="Pizza con queso mozzarella y pepperoni", precio=349.99, stock_cantidad=45, categoria_id=pizzas.id, codigo="PIZZA-002"),
            Producto(nombre="Pizza Vegetariana", descripcion="Pizza con verduras frescas: tomate, cebolla, morron", precio=329.99, stock_cantidad=40, categoria_id=pizzas.id, codigo="PIZZA-003"),
            Producto(nombre="Pizza BBQ", descripcion="Pizza con pollo, salsa BBQ y cebolla", precio=379.99, stock_cantidad=30, categoria_id=pizzas.id, codigo="PIZZA-004"),
            Producto(nombre="Pizza 4 Quesos", descripcion="Pizza con mozzarella, brie, parmesano y roquefort", precio=399.99, stock_cantidad=25, categoria_id=pizzas.id, codigo="PIZZA-005"),
            Producto(nombre="Coca Cola 2L", descripcion="Bebida gaseosa, botella de 2 litros", precio=89.99, stock_cantidad=120, categoria_id=bebidas.id, codigo="BEB-001"),
            Producto(nombre="Agua Mineral", descripcion="Agua mineral sin gas, 1.5L", precio=49.99, stock_cantidad=200, categoria_id=bebidas.id, codigo="BEB-002"),
            Producto(nombre="Cerveza Artesanal", descripcion="Cerveza artesanal premium, 355ml", precio=129.99, stock_cantidad=80, categoria_id=bebidas.id, codigo="BEB-003"),
            Producto(nombre="Jugo de Naranja", descripcion="Jugo natural exprimido, 500ml", precio=79.99, stock_cantidad=60, categoria_id=bebidas.id, codigo="BEB-004"),
            Producto(nombre="Tiramisu", descripcion="Postre italiano clasico con mascarpone", precio=149.99, stock_cantidad=25, categoria_id=postres.id, codigo="POST-001"),
            Producto(nombre="Helado Vainilla", descripcion="Helado de vainilla artesanal, 500ml", precio=99.99, stock_cantidad=35, categoria_id=postres.id, codigo="POST-002"),
            Producto(nombre="Brownie de Chocolate", descripcion="Brownie casero con nueces", precio=79.99, stock_cantidad=50, categoria_id=postres.id, codigo="POST-003"),
            Producto(nombre="Cheesecake", descripcion="Cheesecake de frutos rojos", precio=169.99, stock_cantidad=20, categoria_id=postres.id, codigo="POST-004"),
            Producto(nombre="Empanadas x6", descripcion="Empanadas de carne cortada a cuchillo", precio=199.99, stock_cantidad=40, categoria_id=entradas.id, codigo="ENT-001"),
            Producto(nombre="Papas Fritas", descripcion="Papas fritas crocantes con ketchup y mayo", precio=89.99, stock_cantidad=70, categoria_id=entradas.id, codigo="ENT-002"),
            Producto(nombre="Tabla de Fiambres", descripcion="Seleccion de fiambres y quesos importados", precio=349.99, stock_cantidad=15, categoria_id=entradas.id, codigo="ENT-003"),
        ]
        for p in productos_data:
            session.add(p)
        session.commit()

        print("Seed data poblado: 4 roles, admin@foodstore.local, 4 categorias, 16 productos")

    except Exception as e:
        session.rollback()
        print(f"Error en seed: {e}")
        raise
    finally:
        session.close()
