# ROADMAP — Parcial 2

Objetivo: completar `Parcial_2.md` respetando la arquitectura y la forma de programar ya existente en el proyecto.

Este roadmap asume **un solo frontend React**. Aunque el enunciado menciona “2 proyectos consumen un backend”, para esta implementación se resuelve como **un único frontend modular** con áreas separadas:

- `auth`: login, registro y sesión.
- `store`: home, catálogo, carrito, checkout y pedidos del cliente.
- `admin`: ABM de categorías, ingredientes, productos y usuarios.
- `cajero`: gestión operativa de pedidos y cambios de estado.

La prioridad es entregar una demo completa, coherente y defendible en video: backend con relaciones reales, seed, PostgreSQL, server state con TanStack Query, rutas, roles y flujo completo de compra.

---

## Estado real de partida

Actualmente existen:

- Backend FastAPI con `main.py`, CORS, Swagger y `/health`.
- SQLModel con modelos base:
  - `Usuario`
  - `Rol`
  - `UsuarioRol`
  - `Categoria`
  - `Producto`
- Módulos backend:
  - `auth`
  - `productos`
- Unit of Work simple en `backend/app/db/unit_of_work.py`.
- Seed inicial en `backend/app/db/seed.py`.
- Frontend React + TypeScript + Vite.
- Axios client con interceptor.
- Zustand para auth.
- TanStack Query para productos.
- Rutas básicas con `react-router-dom`.

Actualmente NO existen todavía:

- `DireccionEntrega`.
- `Ingrediente` y relación producto-ingrediente con `es_alergeno`.
- Categorías jerárquicas con `parent_id`.
- `FormaPago`.
- `EstadoPedido`.
- `Pedido`.
- `DetallePedido`.
- `HistorialEstadoPedido`.
- Cookie `httpOnly` para auth.
- Panel admin completo.
- Carrito y checkout.
- Pantalla cajero.
- Migraciones Alembic reales versionadas.

---

## Convenciones obligatorias para implementar

Para no romper el estilo del proyecto, cada cambio debe respetar estas reglas:

### Backend

- Modelos en `backend/app/db/models/<nombre>.py`.
- Exportar modelos nuevos desde `backend/app/db/models/__init__.py`.
- Cada módulo funcional debe tener:
  - `router.py`
  - `schemas.py`
  - `service.py`
  - `__init__.py`
- Registrar routers en `backend/app/main.py` con prefijo `/api/v1`.
- Mantener lógica de negocio en `service.py`, no en routers.
- Usar `SqlModelUnitOfWork` y `get_uow` como ya está implementado.
- Usar `HTTPException` con códigos claros: `400`, `401`, `403`, `404`, `409`, `422`.
- Usar `Relationship` y `back_populates` en relaciones SQLModel.
- Mantener soft delete con `deleted_at` donde aplique.
- Mantener nombres de módulos en minúscula: `categorias`, `ingredientes`, `direcciones`, `pedidos`, `admin`.

### Frontend

- API clients en `frontend/src/api/<modulo>Api.ts`.
- Hooks TanStack Query en `frontend/src/hooks/use<Modulo>.ts`.
- Estado cliente en `frontend/src/store`.
- Componentes por dominio en `frontend/src/features/<modulo>`.
- Rutas en `frontend/src/App.tsx`.
- Tipos compartidos en `frontend/src/types/index.ts`.
- Mantener Tailwind CSS para la UI.
- Usar `invalidateQueries` después de mutations que cambien datos.
- No usar mock data para la demo final: todo debe venir del backend.

---

## Change 1 — Auth con cookie httpOnly + RBAC real

Motivo: el parcial exige login con cookie `access_token` httpOnly, endpoint `/me` y roles con permisos diferenciados.

### Backend

- `backend/app/modules/auth/router.py`
  - Cambiar `POST /auth/login` para que setee cookie `access_token` con:
    - `httponly=True`
    - `samesite="lax"`
    - `secure=False` en desarrollo
    - expiración de 30 minutos
  - Mantener response simple con datos mínimos del usuario o mensaje de éxito.
  - Agregar `POST /auth/logout` para borrar cookie.
  - Mantener `GET /auth/me`.
- `backend/app/core/dependencies.py`
  - Cambiar lectura de token: primero cookie `access_token`.
  - Opcionalmente mantener compatibilidad temporal con `Authorization: Bearer` para no romper desarrollo.
  - Corregir `require_role` para aceptar uso consistente: `require_role("ADMIN")`, `require_role("ADMIN", "STOCK")`.
- `backend/app/modules/auth/service.py`
  - Mantener creación automática de rol `CLIENT` en registro.
  - Validar usuario activo y no eliminado (`deleted_at is None`).
- `backend/app/modules/auth/schemas.py`
  - Asegurar que `UsuarioResponse` exponga roles como lista de strings o ajustar frontend para estructura actual.

### Frontend

- `frontend/src/api/axiosClient.ts`
  - Agregar `withCredentials: true`.
  - Eliminar dependencia fuerte de token en localStorage para auth.
  - Mantener interceptor de response para `401` → logout/redirección.
- `frontend/src/store/authStore.ts`
  - Persistir solo datos mínimos de UI si hace falta, pero NO persistir access token.
  - `fetchMe()` debe reconstruir sesión desde cookie.
- `frontend/src/hooks/useAuth.ts`
  - Login debe llamar backend y luego `me`.
  - Logout debe llamar `/auth/logout`.
- `frontend/src/features/auth/ProtectedRoute.tsx`
  - Agregar soporte para roles permitidos: `roles?: string[]`.

### Criterios de aceptación

- Login crea cookie httpOnly.
- `/auth/me` funciona sin mandar token manual desde el frontend.
- Ruta protegida bloquea usuario no autenticado.
- Ruta por rol bloquea usuario autenticado sin permisos.

---

## Change 2 — Categorías jerárquicas con CRUD ADMIN

Motivo: el parcial pide `/api/v1/categorias/`, jerarquía por `parent_id`, consulta pública, soft delete y validación HTTP 409 si tiene productos activos.

### Backend

- `backend/app/db/models/categoria.py`
  - Agregar `parent_id: Optional[int]` con FK a `categoria.id`.
  - Agregar `deleted_at: Optional[datetime]`.
  - Agregar relación autorreferencial:
    - `parent`
    - `subcategorias`
  - Mantener relación con productos.
- Crear módulo `backend/app/modules/categorias/`:
  - `schemas.py`
  - `service.py`
  - `router.py`
  - `__init__.py`
- `router.py`
  - `GET /api/v1/categorias/` público con `page`, `size`, `parent_id`.
  - `GET /api/v1/categorias/tree` público para árbol recursivo.
  - `POST /api/v1/categorias/` solo `ADMIN`.
  - `PUT /api/v1/categorias/{categoria_id}` solo `ADMIN`.
  - `PATCH /api/v1/categorias/{categoria_id}/baja` solo `ADMIN`.
  - `PATCH /api/v1/categorias/{categoria_id}/reactivar` solo `ADMIN`.
- `service.py`
  - Validar existencia de `parent_id`.
  - Evitar ciclos simples: una categoría no puede ser su propio parent.
  - Soft delete con `deleted_at`.
  - Si tiene productos activos, responder `HTTP 409`.

### Frontend

- `frontend/src/api/categoriasApi.ts`.
- `frontend/src/hooks/useCategorias.ts`.
- `frontend/src/features/admin/categorias/`:
  - listado
  - formulario
  - acciones crear/editar/baja/reactivar
  - visualización de jerarquía
- Agregar ruta admin:
  - `/admin/categorias`

### Criterios de aceptación

- Se pueden listar categorías públicas con paginación.
- Se puede filtrar por `parent_id`.
- Admin puede crear, editar, dar de baja y reactivar.
- No se puede eliminar una categoría con productos activos: `409`.

---

## Change 3 — Ingredientes + relación ProductoIngrediente

Motivo: el parcial pide gestión de ingredientes asociados al producto, incluyendo `es_alergeno`.

### Backend

- Crear `backend/app/db/models/ingrediente.py`:
  - `id`
  - `nombre`
  - `descripcion`
  - `es_alergeno`
  - `deleted_at`
  - `created_at`
  - `updated_at`
- Crear `backend/app/db/models/producto_ingrediente.py`:
  - `producto_id`
  - `ingrediente_id`
  - `es_removible`
  - `es_opcional`
- Ajustar `Producto` para relationship con ingredientes.
- Crear módulo `backend/app/modules/ingredientes/`.
- Endpoints:
  - `GET /api/v1/ingredientes/` público o autenticado según UI.
  - `POST /api/v1/ingredientes/` solo `ADMIN`.
  - `PUT /api/v1/ingredientes/{id}` solo `ADMIN`.
  - `PATCH /api/v1/ingredientes/{id}/baja` solo `ADMIN`.
  - `PATCH /api/v1/ingredientes/{id}/reactivar` solo `ADMIN`.

### Frontend

- `frontend/src/api/ingredientesApi.ts`.
- `frontend/src/hooks/useIngredientes.ts`.
- `frontend/src/features/admin/ingredientes/`.
- Ruta:
  - `/admin/ingredientes`

### Criterios de aceptación

- Admin puede hacer CRUD lógico de ingredientes.
- Producto puede exponer ingredientes asociados.
- UI muestra alérgenos claramente.

---

## Change 4 — Productos completos: disponibilidad, categoría e ingredientes

Motivo: completar `/api/v1/productos/` según parcial: filtros, CRUD ADMIN, stock, disponibilidad, ingredientes y soft delete.

### Backend

- `backend/app/db/models/producto.py`
  - Agregar campo `disponible: bool = True`.
  - Mantener `stock_cantidad`.
  - Evaluar si se mantiene `categoria_id` simple o se agrega relación many-to-many. Para llegar al parcial, alcanza con categoría principal simple, salvo que el equipo quiera mostrar múltiples categorías.
- `backend/app/modules/productos/router.py`
  - Listado público con filtros:
    - `categoria_id`
    - `disponible`
    - `search`
    - `page`
    - `size`
  - CRUD completo solo `ADMIN`.
  - `PATCH /api/v1/productos/{producto_id}/disponibilidad` para `ADMIN` y `STOCK`.
- `backend/app/modules/productos/service.py`
  - Mover validaciones de negocio al service.
  - Validar categoría existente.
  - Validar ingredientes existentes si se mandan.
  - Soft delete con `deleted_at`.

### Frontend

- Ajustar `frontend/src/api/productosApi.ts`.
- Ajustar `frontend/src/hooks/useProductos.ts`.
- `frontend/src/features/store/`:
  - catálogo público
  - card de producto
  - filtros
- `frontend/src/features/admin/productos/`:
  - listado admin
  - formulario crear/editar
  - baja/reactivar
  - toggle disponibilidad
  - selección de categoría e ingredientes
- Rutas:
  - `/store`
  - `/admin/productos`

### Criterios de aceptación

- Catálogo lista productos reales del backend.
- Se filtra por texto, categoría y disponibilidad.
- Admin puede crear, editar y dar de baja.
- Admin/STOCK puede cambiar disponibilidad.
- Se visualiza relación producto → categoría → ingredientes.

---

## Change 5 — Direcciones de entrega

Motivo: el parcial exige `/api/v1/direcciones/`, CRUD por usuario autenticado, dirección principal única, soft delete y alias.

### Backend

- Crear `backend/app/db/models/direccion_entrega.py`:
  - `id`
  - `usuario_id`
  - `alias`
  - `calle`
  - `numero`
  - `localidad`
  - `provincia`
  - `codigo_postal`
  - `referencias`
  - `es_principal`
  - `deleted_at`
  - `created_at`
  - `updated_at`
- Crear módulo `backend/app/modules/direcciones/`.
- Endpoints:
  - `GET /api/v1/direcciones/` lista solo direcciones del usuario autenticado.
  - `POST /api/v1/direcciones/` crea dirección del usuario.
  - `PUT /api/v1/direcciones/{id}` solo si pertenece al usuario.
  - `PATCH /api/v1/direcciones/{id}/principal` marca una sola principal por usuario.
  - `PATCH /api/v1/direcciones/{id}/baja` soft delete.

### Frontend

- `frontend/src/api/direccionesApi.ts`.
- `frontend/src/hooks/useDirecciones.ts`.
- `frontend/src/features/store/direcciones/` o `frontend/src/features/profile/direcciones/`.
- Usar direcciones en checkout.

### Criterios de aceptación

- Usuario ve solo sus direcciones.
- Solo una dirección queda marcada como principal.
- Checkout permite seleccionar dirección.

---

## Change 6 — FormaPago + EstadoPedido

Motivo: seed obligatorio y soporte para pedidos.

### Backend

- Crear `backend/app/db/models/forma_pago.py`:
  - `id`
  - `nombre`
  - `descripcion`
  - `activo`
  - `created_at`
  - `updated_at`
- Crear `backend/app/db/models/estado_pedido.py`:
  - `id`
  - `nombre`
  - `descripcion`
  - `orden`
  - `created_at`
  - `updated_at`
- Exportar en `backend/app/db/models/__init__.py`.
- Crear endpoint público/autenticado para formas de pago:
  - `GET /api/v1/formas-pago/`
- Seed obligatorio:
  - `EFECTIVO`
  - `TARJETA`
  - `TRANSFERENCIA`
  - estados: `PENDIENTE`, `CONFIRMADO`, `EN_PREP`, `EN_CAMINO`, `ENTREGADO`, `CANCELADO`.

### Frontend

- `frontend/src/api/formasPagoApi.ts`.
- `frontend/src/hooks/useFormasPago.ts`.
- Usar en checkout.

### Criterios de aceptación

- Las formas de pago vienen del backend.
- Los estados existen en base y se pueden mostrar en pedidos.

---

## Change 7 — Pedidos, detalle, historial, Unit of Work y máquina de estados

Motivo: es el núcleo del parcial.

### Backend

- Crear `backend/app/db/models/pedido.py`:
  - `id`
  - `usuario_id`
  - `direccion_entrega_id`
  - `forma_pago_id`
  - `estado_actual`
  - `total`
  - `notas`
  - `created_at`
  - `updated_at`
- Crear `backend/app/db/models/detalle_pedido.py`:
  - `id`
  - `pedido_id`
  - `producto_id`
  - `cantidad`
  - `precio_unitario_snapshot`
  - `nombre_producto_snapshot`
  - `subtotal`
- Crear `backend/app/db/models/historial_estado_pedido.py`:
  - `id`
  - `pedido_id`
  - `estado_anterior`
  - `estado_nuevo`
  - `fecha`
  - `usuario_id`
  - `observacion`
- Crear módulo `backend/app/modules/pedidos/`.
- Endpoints:
  - `POST /api/v1/pedidos/` crea pedido desde carrito.
  - `GET /api/v1/pedidos/`:
    - `CLIENT` ve solo sus pedidos.
    - `ADMIN` y `PEDIDOS` ven todos.
    - filtros por estado, page, size.
  - `GET /api/v1/pedidos/{pedido_id}` detalle con historial.
  - `PATCH /api/v1/pedidos/{pedido_id}/estado` avanza estado. Solo `ADMIN` o `PEDIDOS`.
  - `PATCH /api/v1/pedidos/{pedido_id}/cancelar` permite cancelar al cliente si está `PENDIENTE` o `CONFIRMADO`.

### Reglas obligatorias en service

- La máquina de estados vive en `service.py`, no en el router.
- Transiciones válidas:
  - `PENDIENTE → CONFIRMADO`
  - `CONFIRMADO → EN_PREP`
  - `EN_PREP → EN_CAMINO`
  - `EN_CAMINO → ENTREGADO`
  - `PENDIENTE → CANCELADO`
  - `CONFIRMADO → CANCELADO`
- Crear pedido debe ser transaccional:
  - crear `Pedido`
  - crear `DetallePedido`
  - guardar snapshots de precio y nombre
  - calcular total
  - insertar primer historial
- `HistorialEstadoPedido` es append-only:
  - nunca actualizar registros existentes
  - nunca eliminarlos desde lógica de negocio

### Frontend

- `frontend/src/api/pedidosApi.ts`.
- `frontend/src/hooks/usePedidos.ts`.
- `frontend/src/features/store/pedidos/`:
  - mis pedidos
  - detalle de pedido
  - cancelar pedido
- `frontend/src/features/cajero/`:
  - listado de pedidos activos
  - avanzar estado
  - ver historial
- Rutas:
  - `/pedidos`
  - `/pedidos/:pedidoId`
  - `/cajero`

### Criterios de aceptación

- Cliente crea pedido desde carrito.
- Pedido guarda snapshots.
- Historial registra cada transición.
- Cliente solo ve sus pedidos.
- Cajero/Admin ve todos y avanza estados.
- Transición inválida devuelve error claro.

---

## Change 8 — Carrito + checkout en el único frontend

Motivo: el parcial pide módulo Store con carrito persistido, pantalla de pedidos y realización de pedido sin pasarela.

### Frontend

- `frontend/src/store/cartStore.ts`
  - Usar `zustand/middleware` con `persist` a `localStorage`.
  - Acciones:
    - `addItem(producto)`
    - `removeItem(productoId)`
    - `increase(productoId)`
    - `decrease(productoId)`
    - `clearCart()`
    - `getTotal()`
- `frontend/src/features/store/cart/`:
  - `CartDrawer.tsx`
  - `CartItem.tsx`
  - `CartSummary.tsx`
- `frontend/src/features/store/checkout/`:
  - `CheckoutPage.tsx`
  - selector de dirección
  - selector de forma de pago
  - resumen del pedido
  - botón confirmar pedido
- `frontend/src/hooks/useCheckout.ts`
  - `useMutation` para `POST /pedidos/`.
  - `invalidateQueries` de `['pedidos']`.
  - limpiar carrito al confirmar.
- Rutas:
  - `/store`
  - `/checkout`

### Criterios de aceptación

- El carrito persiste al recargar navegador.
- Checkout crea pedido real en backend.
- Después de confirmar, aparece en `/pedidos`.

---

## Change 9 — Panel Admin unificado

Motivo: el parcial pide módulo administración: login, protección por rol, ABM de categorías/subcategorías, ingredientes, productos y gestión de usuarios.

### Backend

- Crear módulo `backend/app/modules/admin/` o extender `auth` con prefijo claro `/api/v1/admin`.
- Endpoints:
  - `GET /api/v1/admin/usuarios/` con `page`, `size`, `rol`.
  - `PUT /api/v1/admin/usuarios/{usuario_id}` actualización básica.
  - `PATCH /api/v1/admin/usuarios/{usuario_id}/baja` soft delete.
  - `PATCH /api/v1/admin/usuarios/{usuario_id}/reactivar`.
  - `PUT /api/v1/admin/usuarios/{usuario_id}/roles` asignación de roles.
- Solo `ADMIN`.

### Frontend

- `frontend/src/api/adminApi.ts`.
- `frontend/src/hooks/useAdmin.ts`.
- `frontend/src/features/admin/usuarios/`.
- Layout/sidebar debe mostrar links según rol:
  - `ADMIN`: productos, categorías, ingredientes, usuarios, cajero.
  - `STOCK`: productos modo lectura + disponibilidad.
  - `PEDIDOS`: cajero.
  - `CLIENT`: store, carrito, pedidos.
- Rutas:
  - `/admin/usuarios`
  - `/admin/categorias`
  - `/admin/ingredientes`
  - `/admin/productos`

### Criterios de aceptación

- Admin gestiona usuarios y roles.
- Empleado sin rol admin no ve acciones de escritura.
- Las rutas bloquean acceso indebido aunque el usuario escriba la URL manualmente.

---

## Change 10 — Seed completo y demo reproducible

Motivo: el parcial exige mostrar seed obligatorio funcionando.

### Backend

- `backend/app/db/seed.py` debe crear de forma idempotente:
  - roles: `ADMIN`, `CLIENT`, `STOCK`, `PEDIDOS`.
  - estados de pedido: `PENDIENTE`, `CONFIRMADO`, `EN_PREP`, `EN_CAMINO`, `ENTREGADO`, `CANCELADO`.
  - formas de pago: `EFECTIVO`, `TARJETA`, `TRANSFERENCIA`.
  - usuario admin por defecto.
  - usuario cliente de prueba.
  - usuario stock de prueba.
  - usuario pedidos/cajero de prueba.
  - categorías padre e hijas.
  - ingredientes, incluyendo alérgenos.
  - productos con categoría, stock, disponible e ingredientes.
  - direcciones de prueba para cliente.
  - 1 o 2 pedidos de ejemplo con detalle e historial.

### Credenciales sugeridas para demo

- Admin:
  - `admin@foodstore.local`
  - `admin123`
- Cliente:
  - `cliente@foodstore.local`
  - `cliente123`
- Stock:
  - `stock@foodstore.local`
  - `stock123`
- Cajero/Pedidos:
  - `pedidos@foodstore.local`
  - `pedidos123`

### Criterios de aceptación

- Levantar backend crea datos necesarios sin duplicar.
- El video puede mostrar seed, tablas en PostgreSQL y flujo completo sin carga manual excesiva.

---

## Change 11 — Alembic y persistencia PostgreSQL

Motivo: el parcial pide persistencia real y visualización de tablas en PostgreSQL. Aunque el proyecto hoy usa `create_all_tables()`, conviene tener migraciones para defender mejor la entrega.

### Backend

- Crear migración inicial o migraciones por bloque para:
  - usuarios/roles si no están versionadas
  - categorías jerárquicas
  - ingredientes
  - productos ajustados
  - direcciones
  - formas de pago
  - estados
  - pedidos/detalles/historial
- Mantener `create_all_tables()` si el equipo lo necesita para desarrollo rápido, pero para la demo conviene explicar Alembic o al menos tener migraciones creadas.

### Criterios de aceptación

- Las tablas existen en PostgreSQL.
- Se pueden mostrar desde pgAdmin/DBeaver.
- El equipo puede explicar cómo se versiona el schema.

---

## Change 12 — Pulido de demo, validaciones y video

Motivo: el parcial evalúa claridad técnica, integración, diseño, validaciones y resolución de problemas.

### Backend

- Revisar validaciones Pydantic:
  - strings requeridos
  - precios `gt=0`
  - stock `ge=0`
  - cantidades de pedido `gt=0`
- Revisar errores:
  - `401` no autenticado
  - `403` sin rol
  - `404` no encontrado
  - `409` conflicto de negocio
  - `422` validación

### Frontend

- Mostrar mensajes de error del backend.
- Agregar loading states con `Spinner` donde aplique.
- Confirmar responsive básico con Tailwind.
- Mostrar relaciones en UI:
  - producto → categoría
  - producto → ingredientes/alérgenos
  - pedido → detalles
  - pedido → historial

### Guion mínimo del video

1. Presentación de integrantes.
2. Backend:
   - modelos SQLModel
   - relaciones `Relationship` / `back_populates`
   - seed
   - endpoint con `Query`
   - HTTPException
   - PostgreSQL en DBeaver/pgAdmin
3. Frontend:
   - estructura modular en un solo proyecto
   - axios + interceptor
   - TanStack Query `useQuery`
   - mutation + `invalidateQueries`
   - rutas y params dinámicos
   - protección por auth y rol
4. Demo completa:
   - login cliente
   - navegar store
   - agregar al carrito
   - checkout
   - ver pedido
   - login cajero/admin
   - avanzar estado
   - CRUD admin de producto/categoría/ingrediente
   - validación fallida

### Criterios de aceptación

- La demo se puede hacer sin datos mock.
- Cada integrante tiene algo técnico concreto para explicar.
- El flujo completo entra en 15 minutos.

---

## Orden recomendado de ejecución

```text
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12
```

### Dependencias

- `Change 7` depende de `Change 5` y `Change 6`.
- `Change 8` depende de `Change 4`, `Change 5`, `Change 6` y `Change 7`.
- `Change 9` puede avanzar en paralelo después de `Change 1`.
- `Change 10` se completa al final, pero se puede ir actualizando en cada change.
- `Change 11` puede hacerse incrementalmente por cada bloque de modelos.

---

## Prioridad si falta tiempo

Si el tiempo aprieta, NO intenten hacer todo perfecto. Prioricen lo que más puntúa en el parcial:

1. Auth cookie httpOnly + roles.
2. Productos/categorías/ingredientes con relaciones visibles.
3. Carrito + checkout + pedido real.
4. Historial de estados del pedido.
5. Admin/cajero con protección por rol.
6. Seed completo.
7. UI prolija y demo ensayada.

Si hay que recortar, recortar primero:

- CRUD admin hiper sofisticado.
- Muchas variantes visuales.
- Múltiples categorías por producto.
- Migraciones perfectas, siempre que PostgreSQL y tablas se puedan mostrar bien.

Pero NO recortar:

- Pedido real.
- Carrito persistido.
- Roles.
- Relaciones.
- Seed.
- Uso de TanStack Query.
