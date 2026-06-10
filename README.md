# FOOD STORE — TPI Programacion 4

Sistema de gestion de pedidos de comida construido con:

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLModel
- Base de datos: PostgreSQL

## Integrantes

- Gianfranco Guzman
- Bruno Racconto
- Alexander Filchel

## Video

- https://youtu.be/u8AqXBbrxMg

## Estado actual del repo

Implementado de forma sustancial:

- autenticacion JWT con roles
- CRUD de productos, categorias, ingredientes, direcciones y formas de pago
- modulo admin base
- pedidos con historial y websocket base
- frontend cliente/admin base

Pendiente respecto de la especificacion v6:

- MercadoPago
- Cloudinary
- Estadisticas
- tests backend de integracion
- cierre completo de entrega

Ver tambien:

- `TPI_PROG4_FOOD_STORE_v6.md` — especificacion tecnica objetivo
- `CHANGES.md` — roadmap operativo de implementacion
- `backend/README.md` — setup especifico del backend

## Requisitos

- Python 3.11+
- Node 18+
- PostgreSQL 15+
- npm

## Estructura real del proyecto

```text
.
├── README.md
├── CHANGES.md
├── TPI_PROG4_FOOD_STORE_v6.md
├── .env.example
├── backend/
│   ├── README.md
│   ├── .env.example
│   ├── requirements.txt
│   ├── alembic/
│   ├── app/
│   └── tests/
└── frontend/
    ├── .env.example
    ├── package.json
    └── src/
```

## Variables de entorno

### Raiz del proyecto

`/.env.example` existe como referencia general del proyecto y para setup global/local.

### Backend

Copiar:

```powershell
Copy-Item backend/.env.example backend/.env
```

Variables activamente usadas hoy por backend:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `DEBUG`
- `APP_NAME`
- `APP_VERSION`
- `API_PREFIX`
- `CORS_ORIGINS`
- `AUTH_COOKIE_NAME`
- `AUTH_COOKIE_SECURE`
- `AUTH_COOKIE_SAMESITE`

Variables reservadas para fases futuras de la especificacion:

- `MP_ACCESS_TOKEN`
- `MP_PUBLIC_KEY`
- `MP_NOTIFICATION_URL`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

### Frontend

Copiar:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Variable principal actual:

- `VITE_API_URL`

## Ejecucion local

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Backend disponible en:

- `http://localhost:8000`
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend disponible en:

- `http://localhost:5173`

## Seed y credenciales base

El proyecto espera seed de datos para roles, estados, formas de pago y usuario admin.

Credencial administrativa historicamente usada en el proyecto:

- `admin@foodstore.com`

La contraseña exacta puede depender del estado actual de la base local/seed ejecutado. Si no funciona, regenerar la BD y correr seed nuevamente.

## Tests

Politica acordada para este proyecto:

- solo backend
- solo tests de integracion
- no agregar tests unitarios
- objetivo: entre 5 y 10 tests por modulo backend cubierto

La carpeta base esperada para esta fase es:

- `backend/tests/`

## Verificacion minima antes de continuar

- backend levanta sin errores
- frontend levanta sin errores
- `/docs` responde
- login responde
- `CHANGES.md` refleja el plan vigente

## Notas

- El roadmap oficial de trabajo actual esta en `CHANGES.md`.
- La especificacion objetivo completa esta en `TPI_PROG4_FOOD_STORE_v6.md`.
