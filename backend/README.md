# Food Store API — Backend

Backend del proyecto Food Store construido con FastAPI + SQLModel + PostgreSQL.

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- entorno virtual recomendado

## Setup local

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

## Endpoints utiles

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Variables de entorno activas

Definidas en `backend/app/core/config.py`:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `AUTH_COOKIE_NAME`
- `AUTH_COOKIE_SECURE`
- `AUTH_COOKIE_SAMESITE`
- `DEBUG`
- `APP_NAME`
- `APP_VERSION`
- `API_PREFIX`
- `CORS_ORIGINS`

Variables reservadas para fases futuras del roadmap:

- `MP_ACCESS_TOKEN`
- `MP_PUBLIC_KEY`
- `MP_NOTIFICATION_URL`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Tests

La politica acordada del proyecto para testing es:

- solo backend
- solo tests de integracion
- no tests unitarios
- entre 5 y 10 tests por modulo backend cubierto

La carpeta base de tests es:

- `backend/tests/`

## Estado actual

Implementado de forma sustancial:

- auth base con JWT
- repositories + unit of work
- CRUD de varias entidades
- pedidos con websocket base

Pendientes mayores segun roadmap:

- MercadoPago
- Cloudinary
- Estadisticas
- suite de tests backend de integracion
