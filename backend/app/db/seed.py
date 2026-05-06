from sqlmodel import Session, select
from app.db.base import engine
from app.db.models.rol import Rol
from app.db.models.usuario import Usuario, UsuarioRol
from app.db.models.categoria import Categoria
from app.db.models.producto import Producto
from app.core.security import hash_password


def populate_seed_data() -> None:
    """
    Popula la base de datos con datos iniciales:
    - 4 Roles: ADMIN, CLIENT, STOCK, PEDIDOS
    - 1 Usuario admin para testing
    - 3 CategorÃ­as: Pizza, Bebidas, Postres
    - 10 Productos de ejemplo

    Solo ejecuta si los roles no existen.
    """
    session = Session(engine)

    try:
        # Verificar si los roles ya existen
        existing_roles = session.exec(select(Rol)).all()
        if existing_roles:
            print("âœ“ Datos seed ya existen")
            return

        # Crear roles
        roles_data = [
            Rol(nombre="ADMIN", descripcion="Administrador del sistema"),
            Rol(nombre="CLIENT", descripcion="Cliente final"),
            Rol(nombre="STOCK", descripcion="Gestor de inventario"),
            Rol(nombre="PEDIDOS", descripcion="Procesador de pedidos"),
        ]

        for rol in roles_data:
            session.add(rol)

        session.commit()

        # Obtener los roles creados
        admin_rol = session.exec(
            select(Rol).where(Rol.nombre == "ADMIN")).first()

        # Crear usuario admin
        admin_user = Usuario(
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            nombre="Administrador",
            is_active=True
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        # Asignar rol ADMIN al usuario admin
        if admin_rol:
            usuario_rol = UsuarioRol(
                usuario_id=admin_user.id, rol_id=admin_rol.id)
            session.add(usuario_rol)
            session.commit()

        # Crear categorÃ­as
        categorias_data = [
            Categoria(nombre="Pizza",
                      descripcion="Pizzas tradicionales y especiales"),
            Categoria(nombre="Bebidas",
                      descripcion="Bebidas frÃ­as y calientes"),
            Categoria(nombre="Postres", descripcion="Postres y dulces"),
        ]

        for categoria in categorias_data:
            session.add(categoria)

        session.commit()

        # Obtener las categorÃ­as creadas
        categoria_pizza = session.exec(
            select(Categoria).where(Categoria.nombre == "Pizza")
        ).first()
        categoria_bebidas = session.exec(
            select(Categoria).where(Categoria.nombre == "Bebidas")
        ).first()
        categoria_postres = session.exec(
            select(Categoria).where(Categoria.nombre == "Postres")
        ).first()

        # Crear productos
        productos_data = [
            # Pizzas
            Producto(
                nombre="Pizza ClÃ¡sica",
                descripcion="Pizza con salsa, queso y oregano",
                precio=299.99,
                stock_cantidad=50,
                categoria_id=categoria_pizza.id,
                codigo="PIZZA-001"
            ),
            Producto(
                nombre="Pizza Pepperoni",
                descripcion="Pizza con queso mozzarella y pepperoni",
                precio=349.99,
                stock_cantidad=45,
                categoria_id=categoria_pizza.id,
                codigo="PIZZA-002"
            ),
            Producto(
                nombre="Pizza Vegetariana",
                descripcion="Pizza con verduras frescas: tomate, cebolla, morrÃ³n",
                precio=329.99,
                stock_cantidad=40,
                categoria_id=categoria_pizza.id,
                codigo="PIZZA-003"
            ),
            Producto(
                nombre="Pizza BBQ",
                descripcion="Pizza con pollo, salsa BBQ y cebolla",
                precio=379.99,
                stock_cantidad=30,
                categoria_id=categoria_pizza.id,
                codigo="PIZZA-004"
            ),

            # Bebidas
            Producto(
                nombre="Coca Cola 2L",
                descripcion="Bebida gaseosa, botella de 2 litros",
                precio=89.99,
                stock_cantidad=120,
                categoria_id=categoria_bebidas.id,
                codigo="BEB-001"
            ),
            Producto(
                nombre="Agua Mineral",
                descripcion="Agua mineral sin gas, 1.5L",
                precio=49.99,
                stock_cantidad=200,
                categoria_id=categoria_bebidas.id,
                codigo="BEB-002"
            ),
            Producto(
                nombre="Cerveza Artesanal",
                descripcion="Cerveza artesanal premium, 355ml",
                precio=129.99,
                stock_cantidad=80,
                categoria_id=categoria_bebidas.id,
                codigo="BEB-003"
            ),

            # Postres
            Producto(
                nombre="Tiramisu",
                descripcion="Postre italiano clÃ¡sico con mascarpone",
                precio=149.99,
                stock_cantidad=25,
                categoria_id=categoria_postres.id,
                codigo="POST-001"
            ),
            Producto(
                nombre="Helado Vainilla",
                descripcion="Helado de vainilla, 500ml",
                precio=99.99,
                stock_cantidad=35,
                categoria_id=categoria_postres.id,
                codigo="POST-002"
            ),
            Producto(
                nombre="Brownie de Chocolate",
                descripcion="Brownie casero de chocolate con nueces",
                precio=79.99,
                stock_cantidad=50,
                categoria_id=categoria_postres.id,
                codigo="POST-003"
            ),
        ]

        for producto in productos_data:
            session.add(producto)

        session.commit()

        print("âœ“ Seed data poblado exitosamente")
        print(f"  - Roles creados: 4 (ADMIN, CLIENT, STOCK, PEDIDOS)")
        print(f"  - Usuario admin: admin@example.com / admin123")
        print(f"  - CategorÃ­as creadas: 3 (Pizza, Bebidas, Postres)")
        print(f"  - Productos creados: 10")

    except Exception as e:
        session.rollback()
        print(f"âœ— Error poblando seed data: {e}")
        raise
    finally:
        session.close()
