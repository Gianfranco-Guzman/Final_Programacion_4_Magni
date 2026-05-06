# Food Store API - Backend

API REST con autenticación JWT para el sistema de gestión de tienda de alimentos.

## Stack Tecnológico

- **FastAPI** 0.111.0 - Framework web async
- **SQLModel** 0.0.19 - ORM con validación Pydantic
- **PostgreSQL** 15 - Base de datos relacional
- **JWT** - Autenticación sin estado
- **Alembic** - Migraciones de schema
- **Docker** - Containerización

## Requisitos Previos

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15 (o usar el docker-compose)

## Instalación y Setup

### 1. Clonar y preparar ambiente

```bash
# Navegar al directorio backend
cd backend

# Crear virtualenv (recomendado)
python -m venv venv

# Activar virtualenv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Levantar PostgreSQL con Docker

```bash
# Desde el directorio backend/
docker-compose up -d

# Verificar que está running
docker ps
# Deberías ver: foodstore_postgres con puerto 5432
```

Espera 5-10 segundos para que PostgreSQL esté listo.

### 3. Variables de entorno

El archivo `.env` ya tiene valores de desarrollo. Si necesitas cambiarlos:

```bash
# Copiar template si necesitas
cp .env.example .env

# Editar .env con tus valores
# IMPORTANTE: En producción cambiar SECRET_KEY y POSTGRES_PASSWORD
```

### 4. Crear base de datos y seed

```bash
# Crear tablas desde SQLModel
python -c "from app.db.base import create_all_tables; create_all_tables(); print('✓ Tablas creadas')"

# Poblar datos iniciales (roles + usuario admin)
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

# Output esperado:
# ✓ Seed data poblado exitosamente
#   - Roles creados: 4 (ADMIN, CLIENT, STOCK, PEDIDOS)
#   - Usuario admin: admin@foodstore.local / admin123
```

Alternativa: todo se ejecuta automáticamente al iniciar el server (ver paso 5).

### 5. Iniciar servidor FastAPI

```bash
# Desarrollo con auto-reload
uvicorn app.main:app --reload

# Output esperado:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# 🚀 Iniciando Food Store API...
# ✓ Tablas creadas
# ✓ Seed data poblado exitosamente
# INFO:     Application startup complete
```

## Documentación API

Una vez que el servidor está running, accede a:

- **Swagger UI (OpenAPI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Endpoints Implementados

### POST /api/v1/auth/login

Autenticar usuario y obtener JWT token.

**Request:**
```json
{
  "email": "admin@foodstore.local",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /api/v1/auth/register

Registrar nuevo usuario (rol CLIENT automático).

**Request:**
```json
{
  "email": "cliente@example.com",
  "password": "password123",
  "nombre": "Juan Pérez"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "email": "cliente@example.com",
  "nombre": "Juan Pérez",
  "is_active": true,
  "roles": []
}
```

### GET /api/v1/auth/me

Obtener información del usuario autenticado.

**Headers requeridos:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "admin@foodstore.local",
  "nombre": "Administrador",
  "is_active": true,
  "roles": []
}
```

## Testing con cURL

### 1. Login y obtener token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@foodstore.local",
    "password": "admin123"
  }'
```

Guarda el `access_token` de la respuesta.

### 2. Obtener usuario actual

```bash
# Reemplaza YOUR_TOKEN con el token obtenido arriba
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Registrar nuevo usuario

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "nombre": "Nuevo Usuario"
  }'
```

## Estructura del Proyecto

```
backend/
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Orquestación de servicios
├── requirements.txt           # Dependencias Python
├── .env                       # Variables de entorno (dev)
├── .env.example              # Template de variables
├── alembic.ini               # Configuración de migraciones
├── README.md                 # Este archivo
│
├── alembic/                  # Migraciones de base de datos
│   ├── env.py                # Configuración de Alembic
│   ├── script.py.mako        # Template de migración
│   └── versions/             # Migraciones versionadas
│
└── app/
    ├── main.py               # Aplicación FastAPI principal
    ├── core/                 # Configuración y utilidades
    │   ├── config.py         # Settings desde .env
    │   ├── security.py       # Funciones de seguridad (hash, JWT)
    │   └── dependencies.py   # Inyección de dependencias
    ├── db/                   # Base de datos
    │   ├── base.py           # Engine y sesiones
    │   ├── seed.py           # Datos iniciales
    │   └── models/           # Modelos SQLModel
    │       ├── usuario.py    # Modelo Usuario
    │       └── rol.py        # Modelo Rol
    └── modules/              # Módulos de la API
        └── auth/             # Módulo de autenticación
            ├── router.py     # Endpoints
            ├── service.py    # Lógica de negocio
            └── schemas.py    # Esquemas Pydantic
```

## Características Implementadas (Día 1)

✅ **Autenticación JWT**
- Login con email + password
- Token expira en 30 minutos
- Hash bcrypt con factor 12

✅ **Registro de usuarios**
- Email único
- Validación de contraseña (min 8 caracteres)
- Rol CLIENT asignado automáticamente

✅ **Obtener usuario actual**
- Requiere token válido en header Authorization
- Retorna información del usuario

✅ **Modelos y migraciones**
- SQLModel con validación Pydantic
- Relación N:M Usuario-Rol
- Seed data con 4 roles + usuario admin

✅ **Documentación**
- Swagger OpenAPI en /docs
- ReDoc en /redoc
- Type hints en toda la codebase

✅ **Docker y compose**
- PostgreSQL 15 con volumen persistente
- Dockerfile para API
- Ambiente completamente containerizable

## Configuración de Seguridad

### En Desarrollo
- SECRET_KEY: key simple (cambiar en producción)
- DEBUG: true
- CORS: permite localhost

### En Producción (TODO)
- ✗ Cambiar SECRET_KEY a valor seguro (min 32 caracteres)
- ✗ DEBUG: false
- ✗ CORS: restringir origins
- ✗ HTTPS only
- ✗ Refresh tokens con httpOnly cookies
- ✗ Rate limiting
- ✗ CSRF protection

## Troubleshooting

### Error: "psycopg2.OperationalError: could not connect to server"

Asegurate de que PostgreSQL está running:
```bash
docker-compose ps
# Deberías ver: foodstore_postgres - running
```

Si no está, levanta:
```bash
docker-compose up -d
```

### Error: "Email o contraseña inválidos"

Verifica que el usuario existe en seed data:
```bash
# Email: admin@foodstore.local
# Password: admin123
```

### Error: "No module named 'app'"

Asegurate de estar en el directorio `backend/` y que el virtualenv está activado:
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

## Próximos Pasos (Fases posteriores)

- [ ] **Refresh tokens**: Token rotation con httpOnly cookies
- [ ] **Roles y permisos**: Validación de roles en endpoints
- [ ] **Email verification**: Confirmación de registro vía email
- [ ] **Password reset**: Recuperación de contraseña
- [ ] **2FA**: Autenticación de dos factores
- [ ] **Rate limiting**: Protección contra fuerza bruta
- [ ] **Audit logs**: Registro de acciones
- [ ] **API keys**: Autenticación de aplicaciones

## Licencia

Interno - TPI Programación 4
