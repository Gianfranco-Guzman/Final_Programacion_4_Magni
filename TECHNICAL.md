# FOOD STORE — Documentación Técnica

## 1. Visión General

**FOOD STORE** es una aplicación web full-stack para la gestión de un negocio de comidas. Permite a clientes explorar catálogos, gestionar carrito, realizar pedidos y hacer seguimiento en tiempo real. Los administradores gestionan productos, stock, pedidos y usuarios desde un panel centralizado.

**Stack:** React + TypeScript | FastAPI + SQLModel | PostgreSQL

---

## 2. Arquitectura

### 2.1 Backend: Patrón Capas + Unit of Work

La arquitectura backend sigue un patrón de capas con **flujo unidireccional de dependencias**:

```
Router → Service → UoW → Repository → Model
```

#### Capas (Responsabilidades)

| Capa | Archivo | Rol |
|---|---|---|
| **Router** | `router.py` | HTTP puro: parsear request, validar Pydantic, delegar al Service |
| **Service** | `service.py` | Lógica de negocio: orquesta operaciones, lanza HTTPException |
| **UoW** | `core/uow.py` | Gestión transacción: abre sesión BD, commit/rollback automático |
| **Repository** | `repository.py` | Acceso BD: queries sin lógica de negocio, hereda BaseRepository[T] |
| **Model** | `model.py` | SQLModel tables + relaciones, cero imports de capas superiores |

**Regla de Oro:** Las capas inferiores NUNCA importan de las capas superiores. Un Model nunca importa un Service. Un Repository nunca importa un Router.

#### Unit of Work (UoW)

El UoW garantiza atomicidad transaccional. Ejemplo:

```python
# En router
with UnitOfWork() as uow:
    resultado = service.crear_pedido(uow, body, usuario_id)
    # Auto-commit al salir sin excepción, auto-rollback si hay error

# En service (NUNCA hacer commit/rollback aquí)
def crear_pedido(uow, body, usuario_id):
    pedido = Pedido(usuario_id=usuario_id, total=body.total)
    uow.pedidos.create(pedido)
    
    for item in body.items:
        detalle = DetallePedido(pedido_id=pedido.id, ...)
        uow.detalles_pedido.create(detalle)
    
    uow.flush()  # obtiene IDs sin commit
    return pedido
    # El UoW del router hace commit aquí
```

### 2.2 Frontend: Separación Zustand ≠ TanStack Query

**Zustand** = Estado del **cliente** (lo que el usuario está haciendo):
- Carrito de compras
- Sesión autenticada
- Estado UI (modales abiertos, sidebar desplegado)
- Proceso de pago en curso

**TanStack Query** = Estado del **servidor** (lo que existe en la BD):
- Listados productos, pedidos, usuarios
- Detalles de entidades
- Caché automático + refetch

**NUNCA mezclar ambos** en el mismo store — antipatrón arquitectónico que causa sincronización inconsistente.

#### Estructura de carpetas

```
src/
├── pages/                    # Solo definen rutas, delegan a features
│   ├── CatalogoPage.tsx
│   ├── AdminPage.tsx
│   └── NotFoundPage.tsx
├── features/                 # Dominio: auth, store, pedidos, admin
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── useAuthLogic.tsx
│   ├── store/
│   │   ├── CatalogoGrid.tsx
│   │   ├── ProductFilters.tsx
│   │   └── useProductLogic.tsx
│   ├── pedidos/
│   │   ├── PedidosList.tsx
│   │   └── usePedidosLogic.tsx
│   └── admin/
│       ├── Dashboard.tsx
│       ├── ProductManagement.tsx
│       └── useAdminLogic.tsx
├── components/               # Primitivos reutilizables, SIN lógica negocio
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   ├── Badge.tsx
│   └── Pagination.tsx
├── hooks/                    # TanStack Query hooks por dominio
│   ├── useAuth.ts            # useLogin, useRegister
│   ├── useProductos.ts       # useQueryProductos, useCreateProducto
│   ├── usePedidos.ts         # usePedidos, usePedidoDetail
│   └── usePagos.ts           # usePago, useMercadopago
├── store/                    # Zustand SOLO para estado cliente
│   ├── authStore.ts          # token, usuario, isAuth, login(), logout()
│   ├── cartStore.ts          # items[], addItem(), removeItem()
│   ├── paymentStore.ts       # estado checkout MercadoPago
│   └── uiStore.ts            # sidebarOpen, modalOpen
├── api/                      # Funciones Axios puras (SIN estado, SIN hooks)
│   ├── axiosClient.ts        # Instancia con interceptors JWT
│   ├── authApi.ts            # login(), register(), me()
│   ├── productosApi.ts       # getProductos(), createProducto(), etc
│   ├── pedidosApi.ts         # getPedidos(), getPedidoDetail()
│   └── pagosApi.ts           # crearPago(), confirmarPago()
├── types/                    # Interfaces TypeScript globales
│   ├── index.ts              # Usuario, Producto, Pedido, CartItem
│   └── api.ts                # Respuestas API
└── App.tsx                   # Router principal + providers
```

---

## 3. Stack Tecnológico

### Backend

| Tecnología | Versión | Rol |
|---|---|---|
| **FastAPI** | 0.111+ | Framework REST + OpenAPI automático |
| **SQLModel** | 0.0.19+ | ORM + Schemas Pydantic integrados |
| **PostgreSQL** | 15+ | Base de datos relacional |
| **Alembic** | 1.13+ | Migraciones versionadas |
| **PyJWT** / **python-jose** | — | Generación y validación JWT |
| **Passlib (bcrypt)** | — | Hashing contraseñas (cost factor ≥ 12) |
| **mercadopago** | 2.3.0+ | SDK oficial MercadoPago |
| **slowapi** | 0.1.9+ | Rate limiting por IP |

### Frontend

| Tecnología | Versión | Rol |
|---|---|---|
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Vite** | 5.x | Build tool + dev server |
| **Tailwind CSS** | 3.x | Estilos utility-first responsive |
| **TanStack Query** | 5.x | Fetching, caché, sincronización servidor |
| **TanStack Form** | 0.x | Gestión formularios con validación |
| **Zustand** | 4.x | Estado global cliente (carrito, sesión, UI) |
| **Axios** | 1.x | Cliente HTTP con interceptors JWT |
| **recharts** | 2.x | Gráficos dashboard admin |

---

## 4. Autenticación y Autorización

- **Método:** JWT (JSON Web Tokens)
- **Tokens:**
  - Access token: 30 minutos (en Zustand + localStorage)
  - Refresh token: 7 días (en httpOnly cookie, más seguro)
- **Roles:** ADMIN, GESTOR_STOCK, GESTOR_PEDIDOS, CLIENTE
- **RBAC:** Validar rol en dependencias FastAPI

**Flujo:**
1. Cliente POST `/api/v1/auth/login` → Backend valida password (bcrypt)
2. Backend retorna `{access_token, token_type: "bearer"}`
3. Frontend guarda en `authStore` (Zustand)
4. Cada request incluye `Authorization: Bearer <token>`
5. Backend valida en `get_current_user()` dependency

---

## 5. Soft Delete y Código Único

### Soft Delete

Productos "eliminados" no se borran de la BD, solo se marca con `deleted_at`:

```python
# En modelo
class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    deleted_at: datetime | None = Field(default=None, index=True)

# En queries (automáticamente filtrar activos)
def get_productos(uow):
    return uow.session.query(Producto).filter(Producto.deleted_at.is_(None))
```

### Código Único con Reutilización

Requisito: Código PIZZA001 puede reutilizarse tras eliminar el producto original.

**Solución:** UNIQUE INDEX condicional:

```sql
CREATE UNIQUE INDEX idx_producto_codigo_active 
ON productos(codigo) 
WHERE deleted_at IS NULL;
```

**Comportamiento:**
- Crear PIZZA001 → ✅ OK (deleted_at = NULL)
- Eliminar PIZZA001 → ✅ OK (deleted_at = 2024-05-05 14:30:00)
- Crear otro PIZZA001 → ✅ OK (nuevo registro con deleted_at = NULL)
- "Reactivar" el primero → ❌ FALLA (código ya existe con deleted_at = NULL)

---

## 6. Paginación y Filtros

Todas las queries de listado usan paginación **obligatoria**:

```http
GET /api/v1/productos?page=1&size=20&categoria_id=2&search=pizza&disponible=true
```

**Query params:**
- `page`: número de página (1-indexed)
- `size`: cantidad items por página (max: 100)
- `categoria_id`: filtro por categoría (opcional)
- `search`: búsqueda por nombre (opcional, ILIKE)
- `disponible`: filtro por disponibilidad (opcional, boolean)

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

---

## 7. Máquina de Estados de Pedidos (Fase 2)

6 estados posibles:

```
PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO
                     ↓
                 CANCELADO (desde cualquier estado)
```

Cada transición de estado se registra en `historial_estado_pedido` (append-only, sin UPDATE/DELETE):

```python
class HistorialEstadoPedido(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_anterior: str
    estado_nuevo: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    usuario_id: int | None = Field(foreign_key="usuario.id")  # Quién hizo el cambio
    motivo: str | None  # Ej: "Cliente canceló"
```

---

## 8. Integración MercadoPago (Fase 2)

- **Checkout API:** Múltiples medios de pago (tarjeta, Rapipago, Pago Fácil, Billetera MP)
- **Webhooks IPN:** Confirmación automática de pagos
- **Tokenización PCI:** SDK oficial @mercadopago/sdk-react

---

## 9. Cómo Correr Localmente

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m alembic upgrade head

# Crear .env
echo "DATABASE_URL=postgresql://user:pass@localhost/foodstore" > .env
echo "JWT_SECRET=tu-secret-aqui" >> .env

# Correr servidor
uvicorn app.main:app --reload
# OpenAPI en http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Vite en http://localhost:5173
```

---

## 10. Estructura de Carpetas (Inicial - Fase 1)

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORSMiddleware
│   │   ├── core/
│   │   │   ├── config.py        # Settings desde .env
│   │   │   ├── security.py      # hash, verify, create_token
│   │   │   ├── dependencies.py  # get_current_user, require_role
│   │   │   ├── uow.py           # UnitOfWork context manager
│   │   │   ├── base_repository.py
│   │   │   └── exceptions.py    # HTTPException handlers
│   │   ├── db/
│   │   │   ├── base.py          # engine, Base.metadata
│   │   │   ├── session.py       # get_session()
│   │   │   ├── seed.py          # Seed data inicial
│   │   │   └── models/
│   │   │       ├── usuario.py
│   │   │       ├── rol.py
│   │   │       ├── producto.py
│   │   │       └── categoria.py
│   │   └── modules/
│   │       ├── auth/
│   │       │   ├── router.py
│   │       │   ├── service.py
│   │       │   └── schemas.py
│   │       └── productos/
│   │           ├── router.py
│   │           ├── service.py
│   │           ├── repository.py
│   │           └── schemas.py
│   ├── migrations/              # Alembic versions
│   ├── requirements.txt
│   ├── .env
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── store/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── features/
│   │   ├── components/
│   │   └── types/
│   ├── .env
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
├── docs/
│   ├── ROADMAP.LOCAL.md         # Guía local (NO COMMITEAR)
│   └── TECHNICAL.md             # Este archivo
└── .gitignore
```

---

## 11. Commits al GitHub

Una vez la aplicación esté en GitHub, commits en español natural:

```bash
git commit -m "creo login con JWT"
git commit -m "agrego grilla de productos"
git commit -m "implemento CRUD insumos"
git commit -m "integro filtros: categoría, búsqueda"
git commit -m "agrego soft delete con visualización"
git commit -m "creo menú hamburguesa"
```

**NUNCA:**
- "implement feature XYZ"
- "update components"
- "AI-generated scaffolding"
- "fix bugs"

---

## Referencias

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLModel: https://sqlmodel.tiangolo.com
- Zustand: https://github.com/pmndrs/zustand
- TanStack Query: https://tanstack.com/query
- Tailwind CSS: https://tailwindcss.com
- PostgreSQL: https://www.postgresql.org/docs
