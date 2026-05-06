# Arquitectura - Food Store API - DÍA 1

## Flujo de Autenticación

```
┌─────────────┐
│  CLIENTE    │
│(Navegador)  │
└──────┬──────┘
       │ 1. POST /login { email, password }
       ▼
┌─────────────────────────────────────┐
│         FastAPI Router              │
│  POST /auth/login                   │
│  POST /auth/register                │
│  GET  /auth/me                      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      AuthService.autenticar()       │
│  1. Buscar usuario por email        │
│  2. verify_password(plain, hash)    │
│  3. Retornar usuario                │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   create_access_token(user_id)      │
│  1. Crear payload: {sub, exp, iat}  │
│  2. Sign con HS256 + SECRET_KEY     │
│  3. Retornar JWT string             │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      CLIENTE (con token)            │
│  GET /me                            │
│  Headers: Authorization: Bearer JWT │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    get_current_user() Dependency    │
│  1. Extraer token del header        │
│  2. decode_token(jwt)               │
│  3. Validar expiration              │
│  4. Obtener usuario de BD           │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Endpoint protegido ejecutado     │
│  Con usuario inyectado automático   │
└─────────────────────────────────────┘
```

## Arquitectura de Capas

```
┌──────────────────────────────────────────────────┐
│                   HTTP REQUEST                   │
│            (Cliente / Navegador)                 │
└────────────────────┬─────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │    FASTAPI ROUTER       │ (app/modules/auth/router.py)
        │  HTTP -> Python         │
        │  (3 endpoints)          │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   BUSINESS LOGIC        │ (app/modules/auth/service.py)
        │  AuthService            │
        │  (autenticar, crear)    │
        └────────────┬────────────┘
                     │
    ┌────────┬───────┴─────────┬─────────┐
    │        │                 │         │
    ▼        ▼                 ▼         ▼
┌─────┐ ┌─────────┐      ┌────────┐ ┌──────────┐
│HASH │ │  TOKEN  │      │SESSION │ │VALIDATION│
│     │ │CREATION │      │MGMT    │ │PYDANTIC  │
└─────┘ └─────────┘      └────────┘ └──────────┘
   │         │                │           │
   └─────────┼────────────────┼───────────┘
             │
        ┌────▼──────────────────────────┐
        │  DATABASE ABSTRACTION LAYER   │ (app/db/)
        │  SQLModel ORM                 │
        │  Sessions, Models             │
        └────┬──────────────────────────┘
             │
        ┌────▼─────────────────────────┐
        │  SQL & PostgreSQL DRIVER     │
        │  Psycopg2 + SQLAlchemy       │
        └────┬──────────────────────────┘
             │
        ┌────▼──────────────────┐
        │  PostgreSQL Database  │
        │  (Containerizado)     │
        └───────────────────────┘
```

## Estructura de Directorios

```
backend/
│
├── 📋 CONFIGURACIÓN
│   ├── .env                 # Variables (desarrollo)
│   ├── .env.example         # Template (sin secrets)
│   ├── requirements.txt     # Dependencias Python
│   ├── docker-compose.yml   # PostgreSQL + volumen
│   ├── Dockerfile           # Imagen API
│   ├── alembic.ini         # Migraciones config
│   └── .gitignore          # Git exclusions
│
├── 📚 DOCUMENTACIÓN
│   ├── START_HERE.md        # Punto de entrada ⭐
│   ├── QUICKSTART.md        # Setup rápido
│   ├── README.md            # Docs completa
│   ├── CHECKLIST.md         # Validación
│   └── ESTRUCTURA.txt       # Detalles técnicos
│
├── 🔧 SCRIPTS
│   ├── run.sh              # Setup Linux/Mac
│   ├── run.bat             # Setup Windows
│   └── test_setup.py       # Validación automática
│
├── 🐍 CÓDIGO PRINCIPAL
│   └── app/
│       │
│       ├── main.py         # 🔥 FastAPI app
│       │                   # - CORS middleware
│       │                   # - Lifespan (startup/shutdown)
│       │                   # - Include routers
│       │
│       ├── core/           # Infraestructura & Seguridad
│       │   ├── config.py   # Settings desde .env
│       │   ├── security.py # hash, verify, JWT sign/decode
│       │   ├── dependencies.py # get_current_user, require_role
│       │   └── __init__.py # Exports
│       │
│       ├── db/             # Persistencia
│       │   ├── base.py     # Engine + sessions
│       │   ├── seed.py     # populate_seed_data()
│       │   ├── __init__.py # Exports
│       │   └── models/
│       │       ├── usuario.py   # SQLModel: Usuario + UsuarioRol
│       │       ├── rol.py       # SQLModel: Rol
│       │       └── __init__.py
│       │
│       ├── modules/        # Módulos de negocio
│       │   ├── __init__.py
│       │   └── auth/       # 🔐 Autenticación
│       │       ├── router.py    # 3 endpoints
│       │       ├── service.py   # AuthService
│       │       ├── schemas.py   # Pydantic validators
│       │       └── __init__.py
│       │
│       └── __init__.py
│
└── alembic/                # Migraciones
    ├── env.py             # SQLModel config
    ├── script.py.mako     # Template migración
    ├── versions/          # Migraciones versionadas
    ├── __init__.py        # Package marker
    └── versions/__init__.py
```

## Flujo de Datos - POST /login

```
CLIENT REQUEST
│
│ POST /api/v1/auth/login
│ Content-Type: application/json
│ {
│   "email": "admin@foodstore.local",
│   "password": "admin123"
│ }
▼
┌────────────────────────────────────────┐
│ FastAPI Router (router.py)             │
│ @router.post("/login")                 │
│ Parámetros:                            │
│  - request: LoginRequest (Pydantic)    │
│  - session: Session (inyectada)        │
└────────────────────┬───────────────────┘
                     │
▼
┌────────────────────────────────────────┐
│ AuthService.autenticar()               │
│                                        │
│ 1. SELECT * FROM usuario               │
│    WHERE email = 'admin@...'           │
│                                        │
│ 2. IF usuario NOT FOUND:               │
│    RAISE 401 Unauthorized              │
│                                        │
│ 3. verify_password(                    │
│      'admin123',                       │
│      usuario.password_hash             │
│    )                                   │
│                                        │
│ 4. IF NOT matches:                     │
│    RAISE 401 Unauthorized              │
│                                        │
│ 5. RETURN usuario object               │
└────────────────────┬───────────────────┘
                     │
▼
┌────────────────────────────────────────┐
│ create_access_token({"sub": 1})        │
│                                        │
│ payload = {                            │
│   "sub": 1,           # user ID        │
│   "exp": 1714953847,  # expiration     │
│   "iat": 1714950247   # issued at      │
│ }                                      │
│                                        │
│ token = JWT.encode(                    │
│   payload,                             │
│   SECRET_KEY,                          │
│   HS256                                │
│ )                                      │
│                                        │
│ RETURN token                           │
└────────────────────┬───────────────────┘
                     │
▼
┌────────────────────────────────────────┐
│ Response (200 OK)                      │
│ {                                      │
│   "access_token": "eyJhbGc...",       │
│   "token_type": "bearer",              │
│   "expires_in": 1800                   │
│ }                                      │
└────────────────────────────────────────┘
                     │
                     ▼
                CLIENT STORAGE
                (localStorage /
                 sessionStorage)
```

## Flujo de Datos - GET /me (Protegido)

```
CLIENT REQUEST
│
│ GET /api/v1/auth/me
│ Authorization: Bearer eyJhbGc...
│
▼
┌────────────────────────────────────────┐
│ HTTPBearer Security Scheme             │
│ (middleware de FastAPI)                │
│                                        │
│ 1. Extract header Authorization       │
│ 2. Parse "Bearer <token>"              │
│ 3. Pass credentials to dependency      │
└────────────────────┬───────────────────┘
                     │
▼
┌────────────────────────────────────────┐
│ get_current_user() Dependency          │
│ (dependencies.py)                      │
│                                        │
│ 1. token = credentials.credentials     │
│                                        │
│ 2. payload = decode_token(token)       │
│    - JWT.decode(token, SECRET_KEY)     │
│    - Validate signature & expiration   │
│    - IF invalid: RAISE 401             │
│                                        │
│ 3. user_id = payload.get("sub")        │
│    IF None: RAISE 401                  │
│                                        │
│ 4. SELECT * FROM usuario               │
│    WHERE id = user_id                  │
│                                        │
│ 5. IF NOT found: RAISE 401             │
│                                        │
│ 6. IF NOT is_active: RAISE 401         │
│                                        │
│ 7. RETURN usuario object               │
└────────────────────┬───────────────────┘
                     │
▼
┌────────────────────────────────────────┐
│ FastAPI Router (router.py)             │
│ @router.get("/me")                     │
│ current_user inyectado automático      │
│                                        │
│ Endpoint ejecutado con:                │
│  - current_user: Usuario object        │
│  - session: Session (inyectada)        │
└────────────────────┬───────────────────┘
                     │
▼
┌────────────────────────────────────────┐
│ Response (200 OK)                      │
│ {                                      │
│   "id": 1,                             │
│   "email": "admin@foodstore.local",    │
│   "nombre": "Administrador",           │
│   "is_active": true,                   │
│   "roles": []                          │
│ }                                      │
└────────────────────────────────────────┘
```

## Modelo de Base de Datos

```
┌──────────────┐                ┌──────────────┐
│  usuario     │                │    rol       │
├──────────────┤                ├──────────────┤
│ id (PK)      │◀──┐           │ id (PK)      │
│ email (UQ)   │   │      ┌────▶│ nombre (UQ)  │
│ password_    │   │      │     │ descripcion  │
│  hash        │   │      │     │ created_at   │
│ nombre       │   └─────┬┴─────┘ updated_at   │
│ is_active    │         │        └──────────────┘
│ created_at   │    ┌────┴──────┐
│ updated_at   │    │usuario_rol│
│ deleted_at   │    ├───────────┤
└──────────────┘    │usuario_id │
                    │(FK)       │
                    │rol_id (FK)│
                    └───────────┘
```

## Flujo de Startup

```
docker-compose up -d
    │
    ▼
PostgreSQL inicia en puerto 5432
    │
    ▼
uvicorn app.main:app --reload
    │
    ▼
┌──────────────────────────────┐
│ FastAPI lifespan() - STARTUP │
└───────┬──────────────────────┘
        │
        ├─► create_all_tables()
        │   └─ SQLModel.metadata.create_all(engine)
        │      • Crea tabla usuario
        │      • Crea tabla rol
        │      • Crea tabla usuario_rol
        │
        └─► populate_seed_data()
            └─ Si no existen:
               • INSERT 4 roles
               • INSERT usuario admin
               • INSERT usuario_rol (admin → ADMIN)
                │
                ▼
        ✅ Server listo en http://localhost:8000/docs
```

## Seguridad - Layers

```
┌─────────────────────────────────────┐
│      CORS Middleware                │ ← Validar origen
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   HTTPBearer (si endpoint requiere)  │ ← Validar header
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    JWT Decode & Validation          │ ← Validar token
│  • Signature (HS256)                │   • Expiration
│  • Payload integrity                │   • Payload structure
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    get_current_user() Lookup        │ ← Validar usuario
│  • Existe en BD                     │   • Está activo
│  • No fue deletado                  │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Pydantic Validation              │ ← Validar input
│  • Email formato                    │   • Constraints
│  • Password length                  │   • Types
└─────────────────────────────────────┘
```

## Error Handling HTTP

```
Event                    HTTP Status   Message
───────────────────────  ────────────  ─────────────────────────
Email/password invalido     401       "Email o contraseña inválidos"
Token expirado              401       "Token inválido o expirado"
Sin token                   403       (HTTPBearer automático)
Email duplicado             422       "El email ya está registrado"
Validación fallida          422       (Pydantic auto)
Error servidor              500       (Log + respuesta genérica)
```

---

## Integración Completa: Cliente → Backend → BD

```
┌──────────────────┐
│  CLIENTE         │
│  (React SPA)     │
└────┬─────────────┘
     │ 1. fetch POST /login
     ▼
┌──────────────────────────────────────┐
│    CAPA HTTP                         │
│  Swagger: /docs                      │
│  CORS: http://localhost:3000         │
│  Content-Type: application/json      │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│    CAPA APPLICATION                  │
│  FastAPI Router                      │
│  Pydantic Validation                 │
│  Dependency Injection                │
│  Error Handling                      │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│    CAPA NEGOCIO                      │
│  AuthService                         │
│  Password Hashing                    │
│  JWT Creation                        │
│  User Lookup                         │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│    CAPA PERSISTENCIA                 │
│  SQLModel ORM                        │
│  Database Sessions                   │
│  Transaction Management              │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│    CAPA STORAGE                      │
│  PostgreSQL 15                       │
│  Tablas: usuario, rol, usuario_rol   │
│  Índices, constraints                │
└──────────────────────────────────────┘
```

---

**Última actualización: DÍA 1 - 100% Funcional**
