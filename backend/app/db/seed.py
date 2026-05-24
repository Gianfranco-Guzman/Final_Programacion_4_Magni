from sqlmodel import Session, select
from app.db.base import engine
from app.db.models.rol import Rol
from app.db.models.usuario import Usuario, UsuarioRol
from app.db.models.direccion_entrega import DireccionEntrega
from app.db.models.categoria import Categoria
from app.db.models.producto import Producto
from app.db.models.producto_categoria import ProductoCategoria
from app.db.models.ingrediente import Ingrediente
from app.db.models.producto_ingrediente import ProductoIngrediente
from app.db.models.forma_pago import FormaPago
from app.db.models.estado_pedido import EstadoPedido
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
            password_hash=hash_password("admin1234"),
            nombre="Administrador",
            apellido="FoodStore",
            celular="3510000000",
            is_active=True,
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        stock_rol = session.exec(select(Rol).where(Rol.nombre == "STOCK")).first()
        pedidos_rol = session.exec(select(Rol).where(Rol.nombre == "PEDIDOS")).first()

        roles_admin = [r for r in [admin_rol, stock_rol, pedidos_rol] if r]
        for rol in roles_admin:
            session.add(UsuarioRol(usuario_id=admin_user.id, rol_id=rol.id))
        session.commit()

        # Usuario de prueba con rol CLIENT
        client_rol = session.exec(select(Rol).where(Rol.nombre == "CLIENT")).first()
        client_user = Usuario(
            email="juan@example.com",
            password_hash=hash_password("Juan1234!"),
            nombre="Juan Pérez",
            apellido="Cliente",
            celular="3511111111",
            is_active=True,
        )
        session.add(client_user)
        session.commit()
        session.refresh(client_user)

        if client_rol:
            session.add(UsuarioRol(usuario_id=client_user.id, rol_id=client_rol.id))
            session.commit()

        direcciones_seed = [
            DireccionEntrega(
                usuario_id=admin_user.id,
                etiqueta="Oficina",
                linea1="Av. Central 123",
                ciudad="Córdoba",
                es_principal=True,
            ),
            DireccionEntrega(
                usuario_id=client_user.id,
                etiqueta="Casa",
                linea1="San Martín 456",
                ciudad="Córdoba",
                es_principal=True,
            ),
        ]
        for direccion in direcciones_seed:
            session.add(direccion)
        session.commit()

        categorias_padre = [
            Categoria(nombre="Pizzas", descripcion="Pizzas tradicionales y especiales"),
            Categoria(nombre="Bebidas", descripcion="Bebidas frias y calientes"),
            Categoria(nombre="Postres", descripcion="Postres y dulces"),
            Categoria(nombre="Entradas", descripcion="Entradas y snacks"),
        ]
        for cat in categorias_padre:
            session.add(cat)
        session.commit()

        pizzas = session.exec(select(Categoria).where(Categoria.nombre == "Pizzas")).first()
        bebidas = session.exec(select(Categoria).where(Categoria.nombre == "Bebidas")).first()
        postres = session.exec(select(Categoria).where(Categoria.nombre == "Postres")).first()
        entradas = session.exec(select(Categoria).where(Categoria.nombre == "Entradas")).first()

        subcategorias_data = [
            Categoria(nombre="Pizzas Clásicas", descripcion="Pizzas tradicionales", parent_id=pizzas.id),
            Categoria(nombre="Pizzas Especiales", descripcion="Pizzas con combinaciones especiales", parent_id=pizzas.id),
            Categoria(nombre="Bebidas Frías", descripcion="Gaseosas, aguas y jugos", parent_id=bebidas.id),
            Categoria(nombre="Postres Fríos", descripcion="Postres refrigerados y helados", parent_id=postres.id),
        ]
        for subcategoria in subcategorias_data:
            session.add(subcategoria)
        session.commit()

        # Crear ingredientes
        ingredientes_data = [
            Ingrediente(nombre="Queso Mozzarella", descripcion="Queso mozzarella fresco", es_alergeno=True),
            Ingrediente(nombre="Salsa de Tomate", descripcion="Salsa de tomate natural"),
            Ingrediente(nombre="Pepperoni", descripcion="Rodajas de pepperoni picante"),
            Ingrediente(nombre="Orégano", descripcion="Orégano seco"),
            Ingrediente(nombre="Cebolla", descripcion="Cebolla fresca"),
            Ingrediente(nombre="Morron", descripcion="Morron rojo y verde"),
            Ingrediente(nombre="Pollo", descripcion="Pollo desmenuzado"),
            Ingrediente(nombre="Salsa BBQ", descripcion="Salsa barbacoa ahumada"),
            Ingrediente(nombre="Brie", descripcion="Queso brie importado", es_alergeno=True),
            Ingrediente(nombre="Parmesano", descripcion="Queso parmesano rallado", es_alergeno=True),
            Ingrediente(nombre="Roquefort", descripcion="Queso roquefort", es_alergeno=True),
            Ingrediente(nombre="Tomate", descripcion="Tomate fresco"),
            Ingrediente(nombre="Lechuga", descripcion="Lechuga criolla"),
            Ingrediente(nombre="Mascarpone", descripcion="Queso mascarpone", es_alergeno=True),
            Ingrediente(nombre="Cafe", descripcion="Cafe espresso"),
            Ingrediente(nombre="Chocolate", descripcion="Chocolate amargo", es_alergeno=True),
            Ingrediente(nombre="Vainilla", descripcion="Extracto de vainilla"),
            Ingrediente(nombre="Nueces", descripcion="Nueces picadas", es_alergeno=True),
            Ingrediente(nombre="Frutos Rojos", descripcion="Mezcla de frutos rojos"),
            Ingrediente(nombre="Carne", descripcion="Carne cortada a cuchillo"),
            Ingrediente(nombre="Empanada Masa", descripcion="Masa para empanadas"),
            Ingrediente(nombre="Papa", descripcion="Papas frescas"),
            Ingrediente(nombre="Ketchup", descripcion="Salsa ketchup"),
            Ingrediente(nombre="Mayonesa", descripcion="Mayonesa casera"),
            Ingrediente(nombre="Fiambres", descripcion="Seleccion de fiambres"),
            Ingrediente(nombre="Quesos Importados", descripcion="Variedad de quesos importados", es_alergeno=True),
        ]
        for ing in ingredientes_data:
            session.add(ing)
        session.commit()

        # Obtener ingredientes para asignar a productos
        queso = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Queso Mozzarella")).first()
        salsa_tomate = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Salsa de Tomate")).first()
        pepperoni = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Pepperoni")).first()
        oregano = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Orégano")).first()
        cebolla = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Cebolla")).first()
        morron = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Morron")).first()
        pollo = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Pollo")).first()
        salsa_bbq = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Salsa BBQ")).first()
        brie = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Brie")).first()
        parmesano = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Parmesano")).first()
        roquefort = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Roquefort")).first()
        tomate = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Tomate")).first()
        lechuga = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Lechuga")).first()
        mascarpone = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Mascarpone")).first()
        cafe = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Cafe")).first()
        chocolate = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Chocolate")).first()
        vainilla = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Vainilla")).first()
        nueces = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Nueces")).first()
        frutos_rojos = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Frutos Rojos")).first()
        carne = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Carne")).first()
        masa = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Empanada Masa")).first()
        papa = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Papa")).first()
        ketchup = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Ketchup")).first()
        mayonesa = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Mayonesa")).first()
        fiambres = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Fiambres")).first()
        quesos = session.exec(select(Ingrediente).where(Ingrediente.nombre == "Quesos Importados")).first()

        productos_data = [
            Producto(nombre="Pizza Clasica", descripcion="Pizza con salsa, queso y oregano", precio=299.99, stock_cantidad=50, categoria_id=pizzas.id, codigo="PIZZA-001", disponible=True),
            Producto(nombre="Pizza Pepperoni", descripcion="Pizza con queso mozzarella y pepperoni", precio=349.99, stock_cantidad=45, categoria_id=pizzas.id, codigo="PIZZA-002", disponible=True),
            Producto(nombre="Pizza Vegetariana", descripcion="Pizza con verduras frescas: tomate, cebolla, morron", precio=329.99, stock_cantidad=40, categoria_id=pizzas.id, codigo="PIZZA-003", disponible=True),
            Producto(nombre="Pizza BBQ", descripcion="Pizza con pollo, salsa BBQ y cebolla", precio=379.99, stock_cantidad=30, categoria_id=pizzas.id, codigo="PIZZA-004", disponible=True),
            Producto(nombre="Pizza 4 Quesos", descripcion="Pizza con mozzarella, brie, parmesano y roquefort", precio=399.99, stock_cantidad=25, categoria_id=pizzas.id, codigo="PIZZA-005", disponible=True),
            Producto(nombre="Coca Cola 2L", descripcion="Bebida gaseosa, botella de 2 litros", precio=89.99, stock_cantidad=120, categoria_id=bebidas.id, codigo="BEB-001", disponible=True),
            Producto(nombre="Agua Mineral", descripcion="Agua mineral sin gas, 1.5L", precio=49.99, stock_cantidad=200, categoria_id=bebidas.id, codigo="BEB-002", disponible=True),
            Producto(nombre="Cerveza Artesanal", descripcion="Cerveza artesanal premium, 355ml", precio=129.99, stock_cantidad=80, categoria_id=bebidas.id, codigo="BEB-003", disponible=True),
            Producto(nombre="Jugo de Naranja", descripcion="Jugo natural exprimido, 500ml", precio=79.99, stock_cantidad=60, categoria_id=bebidas.id, codigo="BEB-004", disponible=False),
            Producto(nombre="Tiramisu", descripcion="Postre italiano clasico con mascarpone", precio=149.99, stock_cantidad=25, categoria_id=postres.id, codigo="POST-001", disponible=True),
            Producto(nombre="Helado Vainilla", descripcion="Helado de vainilla artesanal, 500ml", precio=99.99, stock_cantidad=35, categoria_id=postres.id, codigo="POST-002", disponible=True),
            Producto(nombre="Brownie de Chocolate", descripcion="Brownie casero con nueces", precio=79.99, stock_cantidad=50, categoria_id=postres.id, codigo="POST-003", disponible=True),
            Producto(nombre="Cheesecake", descripcion="Cheesecake de frutos rojos", precio=169.99, stock_cantidad=20, categoria_id=postres.id, codigo="POST-004", disponible=True),
            Producto(nombre="Empanadas x6", descripcion="Empanadas de carne cortada a cuchillo", precio=199.99, stock_cantidad=40, categoria_id=entradas.id, codigo="ENT-001", disponible=True),
            Producto(nombre="Papas Fritas", descripcion="Papas fritas crocantes con ketchup y mayo", precio=89.99, stock_cantidad=70, categoria_id=entradas.id, codigo="ENT-002", disponible=True),
            Producto(nombre="Tabla de Fiambres", descripcion="Seleccion de fiambres y quesos importados", precio=349.99, stock_cantidad=15, categoria_id=entradas.id, codigo="ENT-003", disponible=False),
        ]
        for p in productos_data:
            session.add(p)
        session.commit()

        producto_categorias_data = [
            ProductoCategoria(producto_id=producto.id, categoria_id=producto.categoria_id, es_principal=True)
            for producto in productos_data
        ]
        for producto_categoria in producto_categorias_data:
            session.add(producto_categoria)
        session.commit()

        # Asignar ingredientes a productos
        producto_ingrediente_data = [
            # Pizza Clasica: salsa, queso, oregano
            ProductoIngrediente(producto_id=productos_data[0].id, ingrediente_id=salsa_tomate.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[0].id, ingrediente_id=queso.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[0].id, ingrediente_id=oregano.id, es_removible=True, es_opcional=True),
            # Pizza Pepperoni: queso, pepperoni
            ProductoIngrediente(producto_id=productos_data[1].id, ingrediente_id=queso.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[1].id, ingrediente_id=pepperoni.id, es_removible=True, es_opcional=False),
            # Pizza Vegetariana: salsa, queso, tomate, cebolla, morron
            ProductoIngrediente(producto_id=productos_data[2].id, ingrediente_id=salsa_tomate.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[2].id, ingrediente_id=queso.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[2].id, ingrediente_id=tomate.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[2].id, ingrediente_id=cebolla.id, es_removible=True, es_opcional=True),
            ProductoIngrediente(producto_id=productos_data[2].id, ingrediente_id=morron.id, es_removible=True, es_opcional=True),
            # Pizza BBQ: pollo, salsa bbq, cebolla, queso
            ProductoIngrediente(producto_id=productos_data[3].id, ingrediente_id=pollo.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[3].id, ingrediente_id=salsa_bbq.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[3].id, ingrediente_id=cebolla.id, es_removible=True, es_opcional=True),
            ProductoIngrediente(producto_id=productos_data[3].id, ingrediente_id=queso.id, es_removible=True, es_opcional=False),
            # Pizza 4 Quesos: mozzarella, brie, parmesano, roquefort
            ProductoIngrediente(producto_id=productos_data[4].id, ingrediente_id=queso.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[4].id, ingrediente_id=brie.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[4].id, ingrediente_id=parmesano.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[4].id, ingrediente_id=roquefort.id, es_removible=True, es_opcional=False),
            # Tiramisu: mascarpone, cafe
            ProductoIngrediente(producto_id=productos_data[9].id, ingrediente_id=mascarpone.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[9].id, ingrediente_id=cafe.id, es_removible=False, es_opcional=False),
            # Helado Vainilla: vainilla
            ProductoIngrediente(producto_id=productos_data[10].id, ingrediente_id=vainilla.id, es_removible=False, es_opcional=False),
            # Brownie: chocolate, nueces
            ProductoIngrediente(producto_id=productos_data[11].id, ingrediente_id=chocolate.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[11].id, ingrediente_id=nueces.id, es_removible=True, es_opcional=True),
            # Cheesecake: frutos rojos
            ProductoIngrediente(producto_id=productos_data[12].id, ingrediente_id=frutos_rojos.id, es_removible=True, es_opcional=False),
            # Empanadas: carne, masa
            ProductoIngrediente(producto_id=productos_data[13].id, ingrediente_id=carne.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[13].id, ingrediente_id=masa.id, es_removible=False, es_opcional=False),
            # Papas Fritas: papa, ketchup, mayonesa
            ProductoIngrediente(producto_id=productos_data[14].id, ingrediente_id=papa.id, es_removible=False, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[14].id, ingrediente_id=ketchup.id, es_removible=True, es_opcional=True),
            ProductoIngrediente(producto_id=productos_data[14].id, ingrediente_id=mayonesa.id, es_removible=True, es_opcional=True),
            # Tabla de Fiambres: fiambres, quesos
            ProductoIngrediente(producto_id=productos_data[15].id, ingrediente_id=fiambres.id, es_removible=True, es_opcional=False),
            ProductoIngrediente(producto_id=productos_data[15].id, ingrediente_id=quesos.id, es_removible=True, es_opcional=False),
        ]
        for pi in producto_ingrediente_data:
            session.add(pi)
        session.commit()

        formas_pago_data = [
            FormaPago(nombre="EFECTIVO", descripcion="Pago en efectivo al recibir el pedido"),
            FormaPago(nombre="TARJETA", descripcion="Pago con tarjeta de débito o crédito"),
            FormaPago(nombre="TRANSFERENCIA", descripcion="Transferencia bancaria o Mercado Pago"),
        ]
        for fp in formas_pago_data:
            session.add(fp)
        session.commit()

        estados_pedido_data = [
            EstadoPedido(nombre="PENDIENTE", descripcion="Pedido recibido, pendiente de confirmación", orden=1),
            EstadoPedido(nombre="CONFIRMADO", descripcion="Pedido confirmado, en espera de preparación", orden=2),
            EstadoPedido(nombre="EN_PREP", descripcion="Pedido en preparación", orden=3),
            EstadoPedido(nombre="EN_CAMINO", descripcion="Pedido en camino al cliente", orden=4),
            EstadoPedido(nombre="ENTREGADO", descripcion="Pedido entregado al cliente", orden=5),
            EstadoPedido(nombre="CANCELADO", descripcion="Pedido cancelado", orden=6),
        ]
        for ep in estados_pedido_data:
            session.add(ep)
        session.commit()

        print("Seed data poblado: 4 roles, admin@foodstore.com, juan@example.com, 4 categorias, 26 ingredientes, 16 productos con ingredientes, 3 formas de pago, 6 estados de pedido")

    except Exception as e:
        session.rollback()
        print(f"Error en seed: {e}")
        raise
    finally:
        session.close()
