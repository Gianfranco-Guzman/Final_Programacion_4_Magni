from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.base import engine
from app.db.models import (
    Categoria,
    DetallePedido,
    DireccionEntrega,
    EstadoPedido,
    FormaPago,
    HistorialEstadoPedido,
    Ingrediente,
    Pedido,
    Pago,
    Producto,
    ProductoCategoria,
    ProductoDetalle,
    Rol,
    UnidadMedidaCatalogo,
    Usuario,
    UsuarioRol,
)
from app.modules.productos.service import ProductoService


ROLES_SEED = [
    {"nombre": "ADMIN", "descripcion": "Administrador del sistema"},
    {"nombre": "CLIENT", "descripcion": "Cliente final"},
    {"nombre": "STOCK", "descripcion": "Gestor de inventario"},
    {"nombre": "PEDIDOS", "descripcion": "Operador de pedidos y caja"},
]

USUARIOS_SEED = [
    {
        "email": "admin@foodstore.com",
        "password": "Admin1234!",
        "nombre": "Admin",
        "apellido": "FoodStore",
        "celular": "3510000001",
        "roles": ["ADMIN"],
    },
    {
        "email": "cliente@foodstore.com",
        "password": "cliente123",
        "nombre": "Clara",
        "apellido": "Cliente",
        "celular": "3510000002",
        "roles": ["CLIENT"],
    },
    {
        "email": "stock@foodstore.com",
        "password": "stock123",
        "nombre": "Sergio",
        "apellido": "Stock",
        "celular": "3510000003",
        "roles": ["STOCK"],
    },
    {
        "email": "pedidos@foodstore.com",
        "password": "pedidos123",
        "nombre": "Paula",
        "apellido": "Pedidos",
        "celular": "3510000004",
        "roles": ["PEDIDOS"],
    },
]

FORMAS_PAGO_SEED = [
    {"codigo": "MERCADOPAGO", "nombre": "MERCADOPAGO", "descripcion": "Pago mediante MercadoPago", "activo": True},
    {"codigo": "EFECTIVO", "nombre": "EFECTIVO", "descripcion": "Pago en efectivo al recibir el pedido", "activo": True},
    {"codigo": "TRANSFERENCIA", "nombre": "TRANSFERENCIA", "descripcion": "Transferencia bancaria o billetera virtual", "activo": True},
]

ESTADOS_PEDIDO_SEED = [
    {"codigo": "PENDIENTE", "nombre": "PENDIENTE", "descripcion": "Pedido recibido, pendiente de confirmación", "orden": 1, "es_terminal": False},
    {"codigo": "CONFIRMADO", "nombre": "CONFIRMADO", "descripcion": "Pedido confirmado y esperando preparación", "orden": 2, "es_terminal": False},
    {"codigo": "EN_PREP", "nombre": "EN_PREP", "descripcion": "Pedido en preparación", "orden": 3, "es_terminal": False},
    {"codigo": "EN_CAMINO", "nombre": "EN_CAMINO", "descripcion": "Pedido en camino al cliente", "orden": 4, "es_terminal": False},
    {"codigo": "ENTREGADO", "nombre": "ENTREGADO", "descripcion": "Pedido entregado al cliente", "orden": 5, "es_terminal": True},
    {"codigo": "CANCELADO", "nombre": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
]

UNIDADES_MEDIDA_SEED = [
    {"nombre": "kilogramo", "simbolo": "kg", "tipo": "peso"},
    {"nombre": "gramo", "simbolo": "g", "tipo": "peso"},
    {"nombre": "litro", "simbolo": "L", "tipo": "volumen"},
    {"nombre": "mililitro", "simbolo": "ml", "tipo": "volumen"},
    {"nombre": "unidad", "simbolo": "ud", "tipo": "contable"},
    {"nombre": "porciones", "simbolo": "por", "tipo": "contable"},
]

INGREDIENTES_SEED = [
    {"nombre": "Queso Mozzarella", "descripcion": "Queso mozzarella fresco", "es_alergeno": True, "stock_actual": 5000, "stock_minimo": 1000, "costo_unitario": 15.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Salsa de Tomate", "descripcion": "Salsa de tomate natural", "es_alergeno": False, "stock_actual": 10000, "stock_minimo": 2000, "costo_unitario": 8.50, "unidad_medida": "MILILITRO", "permite_fraccion": True},
    {"nombre": "Pepperoni", "descripcion": "Rodajas de pepperoni picante", "es_alergeno": False, "stock_actual": 3000, "stock_minimo": 500, "costo_unitario": 25.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Orégano", "descripcion": "Orégano seco", "es_alergeno": False, "stock_actual": 500, "stock_minimo": 100, "costo_unitario": 5.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Cebolla", "descripcion": "Cebolla fresca", "es_alergeno": False, "stock_actual": 100, "stock_minimo": 20, "costo_unitario": 3.50, "unidad_medida": "UNIDAD", "permite_fraccion": True},
    {"nombre": "Morron", "descripcion": "Morrón rojo y verde", "es_alergeno": False, "stock_actual": 80, "stock_minimo": 15, "costo_unitario": 5.00, "unidad_medida": "UNIDAD", "permite_fraccion": True},
    {"nombre": "Pollo", "descripcion": "Pollo desmenuzado", "es_alergeno": False, "stock_actual": 8000, "stock_minimo": 2000, "costo_unitario": 18.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Salsa BBQ", "descripcion": "Salsa barbacoa ahumada", "es_alergeno": False, "stock_actual": 5000, "stock_minimo": 1000, "costo_unitario": 12.00, "unidad_medida": "MILILITRO", "permite_fraccion": True},
    {"nombre": "Brie", "descripcion": "Queso brie importado", "es_alergeno": True, "stock_actual": 2000, "stock_minimo": 500, "costo_unitario": 35.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Parmesano", "descripcion": "Queso parmesano rallado", "es_alergeno": True, "stock_actual": 3000, "stock_minimo": 500, "costo_unitario": 22.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Roquefort", "descripcion": "Queso roquefort", "es_alergeno": True, "stock_actual": 1500, "stock_minimo": 300, "costo_unitario": 40.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Tomate", "descripcion": "Tomate fresco", "es_alergeno": False, "stock_actual": 100, "stock_minimo": 20, "costo_unitario": 2.50, "unidad_medida": "UNIDAD", "permite_fraccion": True},
    {"nombre": "Lechuga", "descripcion": "Lechuga criolla", "es_alergeno": False, "stock_actual": 60, "stock_minimo": 10, "costo_unitario": 3.00, "unidad_medida": "UNIDAD", "permite_fraccion": True},
    {"nombre": "Mascarpone", "descripcion": "Queso mascarpone", "es_alergeno": True, "stock_actual": 2000, "stock_minimo": 500, "costo_unitario": 30.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Cafe", "descripcion": "Café espresso", "es_alergeno": False, "stock_actual": 5000, "stock_minimo": 1000, "costo_unitario": 1.50, "unidad_medida": "MILILITRO", "permite_fraccion": True},
    {"nombre": "Chocolate", "descripcion": "Chocolate amargo", "es_alergeno": True, "stock_actual": 3000, "stock_minimo": 500, "costo_unitario": 20.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Vainilla", "descripcion": "Extracto de vainilla", "es_alergeno": False, "stock_actual": 1000, "stock_minimo": 200, "costo_unitario": 25.00, "unidad_medida": "MILILITRO", "permite_fraccion": True},
    {"nombre": "Nueces", "descripcion": "Nueces picadas", "es_alergeno": True, "stock_actual": 2000, "stock_minimo": 500, "costo_unitario": 18.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Frutos Rojos", "descripcion": "Mezcla de frutos rojos", "es_alergeno": False, "stock_actual": 2500, "stock_minimo": 500, "costo_unitario": 22.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Carne", "descripcion": "Carne cortada a cuchillo", "es_alergeno": False, "stock_actual": 5000, "stock_minimo": 1000, "costo_unitario": 15.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Empanada Masa", "descripcion": "Masa para empanadas", "es_alergeno": True, "stock_actual": 200, "stock_minimo": 50, "costo_unitario": 3.00, "unidad_medida": "UNIDAD", "permite_fraccion": True},
    {"nombre": "Papa", "descripcion": "Papas frescas", "es_alergeno": False, "stock_actual": 10000, "stock_minimo": 2000, "costo_unitario": 2.50, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Ketchup", "descripcion": "Salsa ketchup", "es_alergeno": False, "stock_actual": 3000, "stock_minimo": 500, "costo_unitario": 6.00, "unidad_medida": "MILILITRO", "permite_fraccion": True},
    {"nombre": "Mayonesa", "descripcion": "Mayonesa casera", "es_alergeno": True, "stock_actual": 2000, "stock_minimo": 500, "costo_unitario": 8.00, "unidad_medida": "MILILITRO", "permite_fraccion": True},
    {"nombre": "Fiambres", "descripcion": "Selección de fiambres", "es_alergeno": False, "stock_actual": 3000, "stock_minimo": 500, "costo_unitario": 28.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
    {"nombre": "Quesos Importados", "descripcion": "Variedad de quesos importados", "es_alergeno": True, "stock_actual": 2000, "stock_minimo": 500, "costo_unitario": 45.00, "unidad_medida": "GRAMO", "permite_fraccion": True},
]


def populate_seed_data() -> None:
    session = Session(engine)

    try:
        roles = _seed_roles(session)
        usuarios = _seed_usuarios(session, roles)
        direcciones = _seed_direcciones(session, usuarios)
        _seed_unidades_medida(session)
        categorias = _seed_categorias(session)
        ingredientes = _seed_ingredientes(session)
        productos = _seed_productos(session, categorias)
        _seed_producto_categorias(session, productos, categorias)
        _seed_producto_ingredientes(session, productos, ingredientes)
        formas_pago = _seed_formas_pago(session)
        _seed_estados_pedido(session)
        _seed_pedidos_demo(session, usuarios, direcciones, formas_pago, productos)

        session.commit()
        print(
            "Seed data poblado/actualizado: roles, usuarios demo, categorías, ingredientes, productos, direcciones, formas de pago, estados y pedidos de ejemplo"
        )
    except Exception as e:
        session.rollback()
        print(f"Error en seed: {e}")
        raise
    finally:
        session.close()


def _seed_roles(session: Session) -> dict[str, Rol]:
    roles: dict[str, Rol] = {}
    for role_data in ROLES_SEED:
        rol = session.exec(select(Rol).where(Rol.nombre == role_data["nombre"])).first()
        if not rol:
            rol = Rol(**role_data)
            session.add(rol)
            session.flush()
        else:
            rol.descripcion = role_data["descripcion"]
            session.add(rol)
            session.flush()
        roles[rol.nombre] = rol
    return roles


def _seed_usuarios(session: Session, roles: dict[str, Rol]) -> dict[str, Usuario]:
    usuarios: dict[str, Usuario] = {}
    for user_data in USUARIOS_SEED:
        usuario = session.exec(select(Usuario).where(Usuario.email == user_data["email"])).first()
        password_hash = hash_password(user_data["password"])

        if not usuario:
            usuario = Usuario(
                email=user_data["email"],
                password_hash=password_hash,
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                celular=user_data["celular"],
                is_active=True,
                deleted_at=None,
            )
            session.add(usuario)
            session.flush()
        else:
            usuario.password_hash = password_hash
            usuario.nombre = user_data["nombre"]
            usuario.apellido = user_data["apellido"]
            usuario.celular = user_data["celular"]
            usuario.is_active = True
            usuario.deleted_at = None
            usuario.updated_at = datetime.now(timezone.utc)
            session.add(usuario)
            session.flush()

        _sync_usuario_roles(session, usuario, user_data["roles"], roles)
        usuarios[usuario.email] = usuario

    return usuarios


def _sync_usuario_roles(
    session: Session,
    usuario: Usuario,
    desired_roles: list[str],
    roles: dict[str, Rol],
) -> None:
    current_relations = session.exec(
        select(UsuarioRol).where(UsuarioRol.usuario_id == usuario.id)
    ).all()
    current_role_ids = {relation.rol_id for relation in current_relations}
    desired_role_ids = {roles[role_name].id for role_name in desired_roles if role_name in roles}

    for relation in current_relations:
        if relation.rol_id not in desired_role_ids:
            session.delete(relation)

    for role_id in desired_role_ids:
        if role_id not in current_role_ids:
            session.add(UsuarioRol(usuario_id=usuario.id, rol_id=role_id))

    session.flush()


def _seed_direcciones(session: Session, usuarios: dict[str, Usuario]) -> dict[str, DireccionEntrega]:
    direcciones_seed = [
        {
            "email": "cliente@foodstore.com",
            "etiqueta": "Casa",
            "linea1": "San Martín 456",
            "linea2": "Depto 2B",
            "ciudad": "Córdoba",
            "latitud": -31.4167,
            "longitud": -64.1833,
            "es_principal": True,
        },
        {
            "email": "cliente@foodstore.com",
            "etiqueta": "Trabajo",
            "linea1": "Av. Colón 1250",
            "linea2": "Piso 4",
            "ciudad": "Córdoba",
            "latitud": -31.4072,
            "longitud": -64.1888,
            "es_principal": False,
        },
    ]

    direcciones: dict[str, DireccionEntrega] = {}
    for data in direcciones_seed:
        usuario = usuarios[data["email"]]
        direccion = session.exec(
            select(DireccionEntrega).where(
                (DireccionEntrega.usuario_id == usuario.id)
                & (DireccionEntrega.etiqueta == data["etiqueta"])
            )
        ).first()

        if not direccion:
            direccion = DireccionEntrega(
                usuario_id=usuario.id,
                etiqueta=data["etiqueta"],
                linea1=data["linea1"],
                linea2=data["linea2"],
                ciudad=data["ciudad"],
                latitud=data["latitud"],
                longitud=data["longitud"],
                es_principal=data["es_principal"],
                deleted_at=None,
            )
            session.add(direccion)
            session.flush()
        else:
            direccion.linea1 = data["linea1"]
            direccion.linea2 = data["linea2"]
            direccion.ciudad = data["ciudad"]
            direccion.latitud = data["latitud"]
            direccion.longitud = data["longitud"]
            direccion.es_principal = data["es_principal"]
            direccion.deleted_at = None
            direccion.updated_at = datetime.now(timezone.utc)
            session.add(direccion)
            session.flush()

        direcciones[f'{data["email"]}:{data["etiqueta"]}'] = direccion

    _normalize_principal_direcciones(session, usuarios["cliente@foodstore.com"].id)
    return direcciones


def _normalize_principal_direcciones(session: Session, usuario_id: int) -> None:
    direcciones = session.exec(
        select(DireccionEntrega)
        .where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        .order_by(DireccionEntrega.created_at.asc())
    ).all()

    principal_asignada = False
    for direccion in direcciones:
        should_be_principal = direccion.etiqueta == "Casa" and not principal_asignada
        if should_be_principal:
            principal_asignada = True
        direccion.es_principal = should_be_principal
        direccion.updated_at = datetime.now(timezone.utc)
        session.add(direccion)

    session.flush()


def _seed_categorias(session: Session) -> dict[str, Categoria]:
    categorias_seed = [
        {"nombre": "Pizzas", "descripcion": "Pizzas tradicionales y especiales", "parent": None},
        {"nombre": "Bebidas", "descripcion": "Bebidas frías y calientes", "parent": None},
        {"nombre": "Postres", "descripcion": "Postres y dulces", "parent": None},
        {"nombre": "Entradas", "descripcion": "Entradas y snacks", "parent": None},
        {"nombre": "Pizzas Clásicas", "descripcion": "Pizzas tradicionales", "parent": "Pizzas"},
        {"nombre": "Pizzas Especiales", "descripcion": "Combinaciones especiales de la casa", "parent": "Pizzas"},
        {"nombre": "Bebidas Frías", "descripcion": "Gaseosas, aguas y jugos", "parent": "Bebidas"},
        {"nombre": "Postres Fríos", "descripcion": "Postres refrigerados y helados", "parent": "Postres"},
    ]

    categorias: dict[str, Categoria] = {}
    for categoria_data in categorias_seed:
        categoria = session.exec(
            select(Categoria).where(Categoria.nombre == categoria_data["nombre"])
        ).first()
        parent_id = None
        if categoria_data["parent"]:
            parent_id = categorias[categoria_data["parent"]].id

        if not categoria:
            categoria = Categoria(
                nombre=categoria_data["nombre"],
                descripcion=categoria_data["descripcion"],
                parent_id=parent_id,
                deleted_at=None,
            )
            session.add(categoria)
            session.flush()
        else:
            categoria.descripcion = categoria_data["descripcion"]
            categoria.parent_id = parent_id
            categoria.deleted_at = None
            categoria.updated_at = datetime.now(timezone.utc)
            session.add(categoria)
            session.flush()

        categorias[categoria.nombre] = categoria

    return categorias


def _seed_ingredientes(session: Session) -> dict[str, Ingrediente]:
    ingredientes: dict[str, Ingrediente] = {}
    for ingrediente_data in INGREDIENTES_SEED:
        ingrediente = session.exec(
            select(Ingrediente).where(Ingrediente.nombre == ingrediente_data["nombre"])
        ).first()
        if not ingrediente:
            ingrediente = Ingrediente(**ingrediente_data)
            session.add(ingrediente)
            session.flush()
        else:
            ingrediente.descripcion = ingrediente_data["descripcion"]
            ingrediente.es_alergeno = ingrediente_data["es_alergeno"]
            ingrediente.stock_actual = ingrediente_data["stock_actual"]
            ingrediente.stock_minimo = ingrediente_data["stock_minimo"]
            ingrediente.costo_unitario = ingrediente_data["costo_unitario"]
            ingrediente.unidad_medida = ingrediente_data["unidad_medida"]
            ingrediente.permite_fraccion = ingrediente_data.get("permite_fraccion", False)
            ingrediente.deleted_at = None
            ingrediente.updated_at = datetime.now(timezone.utc)
            session.add(ingrediente)
            session.flush()

        ingredientes[ingrediente.nombre] = ingrediente
    return ingredientes


def _seed_productos(session: Session, categorias: dict[str, Categoria]) -> dict[str, Producto]:
    productos_seed = [
        {"codigo": "PIZZA-001", "nombre": "Pizza Clásica", "descripcion": "Pizza con salsa, queso y orégano", "precio": 299.99, "categoria": "Pizzas Clásicas", "disponible": True},
        {"codigo": "PIZZA-002", "nombre": "Pizza Pepperoni", "descripcion": "Pizza con queso mozzarella y pepperoni", "precio": 349.99, "categoria": "Pizzas Especiales", "disponible": True},
        {"codigo": "PIZZA-003", "nombre": "Pizza Vegetariana", "descripcion": "Pizza con verduras frescas: tomate, cebolla y morrón", "precio": 329.99, "categoria": "Pizzas Clásicas", "disponible": True},
        {"codigo": "PIZZA-004", "nombre": "Pizza BBQ", "descripcion": "Pizza con pollo, salsa BBQ y cebolla", "precio": 379.99, "categoria": "Pizzas Especiales", "disponible": True},
        {"codigo": "PIZZA-005", "nombre": "Pizza 4 Quesos", "descripcion": "Pizza con mozzarella, brie, parmesano y roquefort", "precio": 399.99, "categoria": "Pizzas Especiales", "disponible": True},
        {"codigo": "BEB-001", "nombre": "Coca Cola 2L", "descripcion": "Bebida gaseosa, botella de 2 litros", "precio": 89.99, "categoria": "Bebidas Frías", "disponible": True},
        {"codigo": "BEB-002", "nombre": "Agua Mineral", "descripcion": "Agua mineral sin gas, 1.5L", "precio": 49.99, "categoria": "Bebidas Frías", "disponible": True},
        {"codigo": "BEB-003", "nombre": "Cerveza Artesanal", "descripcion": "Cerveza artesanal premium, 355ml", "precio": 129.99, "categoria": "Bebidas Frías", "disponible": True},
        {"codigo": "BEB-004", "nombre": "Jugo de Naranja", "descripcion": "Jugo natural exprimido, 500ml", "precio": 79.99, "categoria": "Bebidas Frías", "disponible": False},
        {"codigo": "POST-001", "nombre": "Tiramisú", "descripcion": "Postre italiano clásico con mascarpone", "precio": 149.99, "categoria": "Postres Fríos", "disponible": True},
        {"codigo": "POST-002", "nombre": "Helado Vainilla", "descripcion": "Helado de vainilla artesanal, 500ml", "precio": 99.99, "categoria": "Postres Fríos", "disponible": True},
        {"codigo": "POST-003", "nombre": "Brownie de Chocolate", "descripcion": "Brownie casero con nueces", "precio": 79.99, "categoria": "Postres", "disponible": True},
        {"codigo": "POST-004", "nombre": "Cheesecake", "descripcion": "Cheesecake de frutos rojos", "precio": 169.99, "categoria": "Postres Fríos", "disponible": True},
        {"codigo": "ENT-001", "nombre": "Empanadas x6", "descripcion": "Empanadas de carne cortada a cuchillo", "precio": 199.99, "categoria": "Entradas", "disponible": True},
        {"codigo": "ENT-002", "nombre": "Papas Fritas", "descripcion": "Papas fritas crocantes con ketchup y mayo", "precio": 89.99, "categoria": "Entradas", "disponible": True},
        {"codigo": "ENT-003", "nombre": "Tabla de Fiambres", "descripcion": "Selección de fiambres y quesos importados", "precio": 349.99, "categoria": "Entradas", "disponible": False},
    ]

    productos: dict[str, Producto] = {}
    for producto_data in productos_seed:
        categoria = categorias[producto_data["categoria"]]
        producto = session.exec(
            select(Producto).where(Producto.codigo == producto_data["codigo"])
        ).first()
        if not producto:
            producto = Producto(
                nombre=producto_data["nombre"],
                descripcion=producto_data["descripcion"],
                precio_venta=producto_data["precio"],
                categoria_id=categoria.id,
                codigo=producto_data["codigo"],
                disponible=producto_data["disponible"],
                deleted_at=None,
            )
            session.add(producto)
            session.flush()
        else:
            producto.nombre = producto_data["nombre"]
            producto.descripcion = producto_data["descripcion"]
            producto.precio = producto_data["precio"]
            producto.categoria_id = categoria.id
            producto.codigo = producto_data["codigo"]
            producto.disponible = producto_data["disponible"]
            producto.deleted_at = None
            producto.updated_at = datetime.now(timezone.utc)
            session.add(producto)
            session.flush()

        productos[producto.codigo] = producto

    return productos


def _seed_producto_categorias(
    session: Session,
    productos: dict[str, Producto],
    categorias: dict[str, Categoria],
) -> None:
    relaciones = {
        "PIZZA-001": ["Pizzas", "Pizzas Clásicas"],
        "PIZZA-002": ["Pizzas", "Pizzas Especiales"],
        "PIZZA-003": ["Pizzas", "Pizzas Clásicas"],
        "PIZZA-004": ["Pizzas", "Pizzas Especiales"],
        "PIZZA-005": ["Pizzas", "Pizzas Especiales"],
        "BEB-001": ["Bebidas", "Bebidas Frías"],
        "BEB-002": ["Bebidas", "Bebidas Frías"],
        "BEB-003": ["Bebidas", "Bebidas Frías"],
        "BEB-004": ["Bebidas", "Bebidas Frías"],
        "POST-001": ["Postres", "Postres Fríos"],
        "POST-002": ["Postres", "Postres Fríos"],
        "POST-003": ["Postres"],
        "POST-004": ["Postres", "Postres Fríos"],
        "ENT-001": ["Entradas"],
        "ENT-002": ["Entradas"],
        "ENT-003": ["Entradas"],
    }

    for codigo, categoria_names in relaciones.items():
        producto = productos[codigo]
        desired_categoria_ids = {categorias[name].id for name in categoria_names}
        existing_relations = session.exec(
            select(ProductoCategoria).where(ProductoCategoria.producto_id == producto.id)
        ).all()

        existing_categoria_ids = {relation.categoria_id for relation in existing_relations}
        for relation in existing_relations:
            if relation.categoria_id not in desired_categoria_ids:
                session.delete(relation)

        for category_name in categoria_names:
            categoria = categorias[category_name]
            if categoria.id not in existing_categoria_ids:
                session.add(
                    ProductoCategoria(
                        producto_id=producto.id,
                        categoria_id=categoria.id,
                        es_principal=categoria.id == producto.categoria_id,
                    )
                )
            else:
                relation = next(
                    item for item in existing_relations if item.categoria_id == categoria.id
                )
                relation.es_principal = categoria.id == producto.categoria_id
                session.add(relation)

    session.flush()


def _seed_producto_ingredientes(
    session: Session,
    productos: dict[str, Producto],
    ingredientes: dict[str, Ingrediente],
) -> None:
    relaciones = {
        "PIZZA-001": [
            ("Salsa de Tomate", False, False),
            ("Queso Mozzarella", True, False),
            ("Orégano", True, True),
        ],
        "PIZZA-002": [
            ("Queso Mozzarella", True, False),
            ("Pepperoni", True, False),
        ],
        "PIZZA-003": [
            ("Salsa de Tomate", False, False),
            ("Queso Mozzarella", True, False),
            ("Tomate", True, False),
            ("Cebolla", True, True),
            ("Morron", True, True),
        ],
        "PIZZA-004": [
            ("Pollo", True, False),
            ("Salsa BBQ", False, False),
            ("Cebolla", True, True),
            ("Queso Mozzarella", True, False),
        ],
        "PIZZA-005": [
            ("Queso Mozzarella", True, False),
            ("Brie", True, False),
            ("Parmesano", True, False),
            ("Roquefort", True, False),
        ],
        "POST-001": [
            ("Mascarpone", False, False),
            ("Cafe", False, False),
        ],
        "POST-002": [("Vainilla", False, False)],
        "POST-003": [
            ("Chocolate", False, False),
            ("Nueces", True, True),
        ],
        "POST-004": [("Frutos Rojos", True, False)],
        "ENT-001": [
            ("Carne", False, False),
            ("Empanada Masa", False, False),
        ],
        "ENT-002": [
            ("Papa", False, False),
            ("Ketchup", True, True),
            ("Mayonesa", True, True),
        ],
        "ENT-003": [
            ("Fiambres", True, False),
            ("Quesos Importados", True, False),
        ],
    }

    for codigo, ingredient_rows in relaciones.items():
        producto = productos[codigo]
        desired_ingredient_ids = {ingredientes[name].id for name, _, _ in ingredient_rows}
        existing_relations = session.exec(
            select(ProductoDetalle).where(ProductoDetalle.producto_id == producto.id)
        ).all()

        existing_ingredient_ids = {relation.ingrediente_id for relation in existing_relations}
        for relation in existing_relations:
            if relation.ingrediente_id not in desired_ingredient_ids:
                session.delete(relation)

        for ingredient_name, es_removible, es_opcional in ingredient_rows:
            ingrediente = ingredientes[ingredient_name]
            relation = next(
                (item for item in existing_relations if item.ingrediente_id == ingrediente.id),
                None,
            )
            if relation:
                relation.es_removible = es_removible
                relation.es_opcional = es_opcional
                session.add(relation)
            elif ingrediente.id not in existing_ingredient_ids:
                session.add(
                    ProductoDetalle(
                        producto_id=producto.id,
                        ingrediente_id=ingrediente.id,
                        cantidad=1,
                        unidad_medida=ingrediente.unidad_medida,
                        es_removible=es_removible,
                        es_opcional=es_opcional,
                    )
                )

    session.flush()


def _seed_formas_pago(session: Session) -> dict[str, FormaPago]:
    formas_pago: dict[str, FormaPago] = {}
    for forma_data in FORMAS_PAGO_SEED:
        forma_pago = session.exec(
            select(FormaPago).where(FormaPago.nombre == forma_data["nombre"])
        ).first()
        if not forma_pago:
            forma_pago = FormaPago(**forma_data)
            session.add(forma_pago)
            session.flush()
        else:
            forma_pago.codigo = forma_data["codigo"]
            forma_pago.descripcion = forma_data["descripcion"]
            forma_pago.activo = forma_data["activo"]
            forma_pago.updated_at = datetime.now(timezone.utc)
            session.add(forma_pago)
            session.flush()
        formas_pago[forma_pago.nombre] = forma_pago
    return formas_pago


def _seed_estados_pedido(session: Session) -> None:
    for estado_data in ESTADOS_PEDIDO_SEED:
        estado = session.exec(
            select(EstadoPedido).where(EstadoPedido.nombre == estado_data["nombre"])
        ).first()
        if not estado:
            estado = EstadoPedido(**estado_data)
            session.add(estado)
            session.flush()
        else:
            estado.codigo = estado_data["codigo"]
            estado.descripcion = estado_data["descripcion"]
            estado.orden = estado_data["orden"]
            estado.es_terminal = estado_data["es_terminal"]
            estado.updated_at = datetime.now(timezone.utc)
            session.add(estado)
            session.flush()


def _seed_unidades_medida(session: Session) -> None:
    for data in UNIDADES_MEDIDA_SEED:
        unidad = session.exec(
            select(UnidadMedidaCatalogo).where(UnidadMedidaCatalogo.simbolo == data["simbolo"])
        ).first()
        if not unidad:
            unidad = UnidadMedidaCatalogo(**data)
        else:
            unidad.nombre = data["nombre"]
            unidad.tipo = data["tipo"]
            unidad.updated_at = datetime.now(timezone.utc)
        session.add(unidad)
        session.flush()


def _seed_pedidos_demo(
    session: Session,
    usuarios: dict[str, Usuario],
    direcciones: dict[str, DireccionEntrega],
    formas_pago: dict[str, FormaPago],
    productos: dict[str, Producto],
) -> None:
    cliente = usuarios["cliente@foodstore.com"]
    admin = usuarios["admin@foodstore.com"]
    operador = usuarios["pedidos@foodstore.com"]
    casa = direcciones["cliente@foodstore.com:Casa"]
    trabajo = direcciones["cliente@foodstore.com:Trabajo"]

    pedidos_seed = [
        {
            "nota": "SEED-DEMO-ORDER-1",
            "estado_actual": "ENTREGADO",
            "forma_pago": "MERCADOPAGO",
            "direccion": casa,
            "lineas": [("PIZZA-002", 1), ("BEB-001", 1), ("POST-001", 1)],
            "historial": [
                (None, "PENDIENTE", cliente, "Pedido creado desde seed demo"),
                ("PENDIENTE", "CONFIRMADO", admin, "Confirmado por administración"),
                ("CONFIRMADO", "EN_PREP", operador, "Preparación iniciada"),
                ("EN_PREP", "EN_CAMINO", operador, "Sale con repartidor"),
                ("EN_CAMINO", "ENTREGADO", operador, "Pedido entregado correctamente"),
            ],
            "created_offset_hours": 6,
        },
        {
            "nota": "SEED-DEMO-ORDER-2",
            "estado_actual": "CONFIRMADO",
            "forma_pago": "EFECTIVO",
            "direccion": trabajo,
            "lineas": [("PIZZA-005", 1), ("ENT-002", 2), ("BEB-002", 2)],
            "historial": [
                (None, "PENDIENTE", cliente, "Pedido creado desde seed demo"),
                ("PENDIENTE", "CONFIRMADO", operador, "Pago validado, listo para cocina"),
            ],
            "created_offset_hours": 2,
        },
    ]

    for pedido_seed in pedidos_seed:
        pedido = session.exec(
            select(Pedido).where(Pedido.notas == pedido_seed["nota"])
        ).first()
        created_at = datetime.now(timezone.utc) - timedelta(hours=pedido_seed["created_offset_hours"])
        subtotal = sum(ProductoService.calcular_precio_final(productos[codigo]) * cantidad for codigo, cantidad in pedido_seed["lineas"])
        descuento = 0
        costo_envio = 0
        total = subtotal - descuento + costo_envio

        if not pedido:
            pedido = Pedido(
                usuario_id=cliente.id,
                direccion_entrega_id=pedido_seed["direccion"].id,
                forma_pago_id=formas_pago[pedido_seed["forma_pago"]].id,
                estado_actual=pedido_seed["estado_actual"],
                subtotal=round(subtotal, 2),
                descuento=round(descuento, 2),
                costo_envio=round(costo_envio, 2),
                total=round(total, 2),
                notas=pedido_seed["nota"],
                created_at=created_at,
                updated_at=created_at,
            )
            session.add(pedido)
            session.flush()
        else:
            pedido.usuario_id = cliente.id
            pedido.direccion_entrega_id = pedido_seed["direccion"].id
            pedido.forma_pago_id = formas_pago[pedido_seed["forma_pago"]].id
            pedido.estado_actual = pedido_seed["estado_actual"]
            pedido.subtotal = round(subtotal, 2)
            pedido.descuento = round(descuento, 2)
            pedido.costo_envio = round(costo_envio, 2)
            pedido.total = round(total, 2)
            pedido.created_at = created_at
            pedido.updated_at = datetime.now(timezone.utc)
            session.add(pedido)
            session.flush()

        _sync_detalles_pedido(session, pedido, pedido_seed["lineas"], productos)
        _sync_historial_pedido(session, pedido, pedido_seed["historial"])


def _sync_detalles_pedido(
    session: Session,
    pedido: Pedido,
    lineas: list[tuple[str, int]],
    productos: dict[str, Producto],
) -> None:
    existing_details = session.exec(
        select(DetallePedido).where(DetallePedido.pedido_id == pedido.id)
    ).all()
    existing_by_product_id = {detail.producto_id: detail for detail in existing_details}
    desired_product_ids = {productos[codigo].id for codigo, _ in lineas}

    for detail in existing_details:
        if detail.producto_id not in desired_product_ids:
            session.delete(detail)

    for codigo, cantidad in lineas:
        producto = productos[codigo]
        precio_unitario = ProductoService.calcular_precio_final(producto)
        subtotal = round(precio_unitario * cantidad, 2)
        detail = existing_by_product_id.get(producto.id)
        if detail:
            detail.cantidad = cantidad
            detail.precio_unitario_snapshot = precio_unitario
            detail.nombre_producto_snapshot = producto.nombre
            detail.subtotal = subtotal
            session.add(detail)
        else:
            session.add(
                DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario_snapshot=precio_unitario,
                    nombre_producto_snapshot=producto.nombre,
                    subtotal=subtotal,
                )
            )

    session.flush()


def _sync_historial_pedido(
    session: Session,
    pedido: Pedido,
    historial_seed: list[tuple[str | None, str, Usuario, str]],
) -> None:
    existing_entries = session.exec(
        select(HistorialEstadoPedido).where(HistorialEstadoPedido.pedido_id == pedido.id)
    ).all()
    existing_by_key = {
        (entry.estado_anterior, entry.estado_nuevo, entry.usuario_id, entry.observacion): entry
        for entry in existing_entries
    }
    desired_keys = {
        (estado_anterior, estado_nuevo, usuario.id, observacion)
        for estado_anterior, estado_nuevo, usuario, observacion in historial_seed
    }

    for entry in existing_entries:
        key = (entry.estado_anterior, entry.estado_nuevo, entry.usuario_id, entry.observacion)
        if key not in desired_keys:
            session.delete(entry)

    base_time = pedido.created_at
    for index, (estado_anterior, estado_nuevo, usuario, observacion) in enumerate(historial_seed):
        key = (estado_anterior, estado_nuevo, usuario.id, observacion)
        fecha = base_time + timedelta(minutes=index * 12)
        entry = existing_by_key.get(key)
        if entry:
            entry.fecha = fecha
            session.add(entry)
        else:
            session.add(
                HistorialEstadoPedido(
                    pedido_id=pedido.id,
                    estado_anterior=estado_anterior,
                    estado_nuevo=estado_nuevo,
                    fecha=fecha,
                    usuario_id=usuario.id,
                    observacion=observacion,
                )
            )

    pedido.updated_at = base_time + timedelta(minutes=max(len(historial_seed) - 1, 0) * 12)
    session.add(pedido)
    session.flush()
