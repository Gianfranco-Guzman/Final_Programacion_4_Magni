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

## Implementado

- Autenticacion JWT con refresh token y revocacion
- RBAC con roles ADMIN, CLIENT, STOCK, PEDIDOS
- CRUD de productos, categorias, ingredientes, direcciones y formas de pago
- Imagenes con Cloudinary (upload y delete)
- Pedidos con FSM completa y websocket realtime
- Pagos con MercadoPago (checkout, webhook)
- Estadisticas administrativas (resumen, ventas, productos top, ingresos)
- Dashboard admin con graficos (recharts)
- Rate limiting en auth (5 intentos / 15 min)
- Tests de integracion backend (pytest)

## Especificacion y roadmap

- `TPI_PROG4_FOOD_STORE_v6.md` — especificacion tecnica objetivo
- `CHANGES.md` — roadmap operativo de implementacion

## Requisitos

- Python 3.11+
- Node 18+
- PostgreSQL 15+
- npm

## Estructura del proyecto

```text
.
├── README.md
├── CHANGES.md
├── TPI_PROG4_FOOD_STORE_v6.md
├── backend/
│   ├── README.md
│   ├── .env.example
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── alembic/
│   ├── app/
│   └── tests/
└── frontend/
    ├── .env.example
    ├── package.json
    └── src/
```

## Configuracion de entorno

### Backend

Copiar y completar variables:

```powershell
Copy-Item backend/.env.example backend/.env
```

Variables requeridas para funcionalidad completa:

```env
DATABASE_URL=postgresql://foodstore:foodstore_dev_pass_123@localhost:5433/foodstore_db
SECRET_KEY=una-clave-secreta-minimo-32-caracteres
MP_ACCESS_TOKEN=APP_USR-...         # cuenta MercadoPago sandbox
MP_PUBLIC_KEY=APP_USR-...           # clave publica MercadoPago
MP_NOTIFICATION_URL=https://...     # URL publica para webhooks (ngrok en local)
CLOUDINARY_CLOUD_NAME=nombre
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=secreto
```

### Frontend

Copiar:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Variable principal:

```env
VITE_API_URL=http://localhost:8000
VITE_MP_PUBLIC_KEY=APP_USR-...     # misma clave publica que el backend
```

## Ejecucion local

### Base de datos (Docker)

Levantar Postgres antes que el backend — sin esto, alembic y uvicorn van a fallar con "connection refused":

```powershell
docker-compose up -d
```

Postgres queda expuesto en el host en el puerto **5433** (ver `docker-compose.yml`), no 5432. Si usás `.env.example` tal cual, ajustá `DATABASE_URL` a `localhost:5433`.

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

> `alembic` se ejecuta directo (no con `python -m alembic` — el paquete no tiene `__main__.py` y falla con "No module named alembic.__main__").

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

## Seed y credenciales

El seed corre automaticamente al iniciar el backend. Credenciales de acceso:

| Rol     | Email                    | Password     |
|---------|--------------------------|--------------|
| ADMIN   | admin@foodstore.com      | Admin1234!   |
| CLIENT  | cliente@foodstore.com    | cliente123   |
| STOCK   | stock@foodstore.com      | stock123     |
| PEDIDOS | pedidos@foodstore.com    | pedidos123   |

## Tests de integracion

Los tests requieren una base de datos PostgreSQL accesible. Por defecto usan `DATABASE_URL`. Para usar una base dedicada:

```powershell
$env:TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/foodstore_test"
cd backend
.\venv\Scripts\Activate.ps1
pytest
```

Politica de tests:

- Solo backend
- Solo tests de integracion
- No tests unitarios
- Entre 5 y 10 tests por modulo critico

Modulos cubiertos: `auth`, `pedidos`, `pagos`, `uploads`, `estadisticas`

## MercadoPago sandbox

1. Crear cuenta en https://www.mercadopago.com.ar/developers
2. Obtener credenciales de prueba (Access Token y Public Key de sandbox)
3. Configurar `MP_ACCESS_TOKEN` y `MP_PUBLIC_KEY` en `backend/.env`
4. Configurar `VITE_MP_PUBLIC_KEY` en `frontend/.env`
5. Para webhooks locales: usar ngrok y configurar `MP_NOTIFICATION_URL`

Tarjetas de prueba disponibles en la documentacion de MercadoPago Developers.

## Cloudinary

1. Crear cuenta en https://cloudinary.com
2. Obtener `Cloud Name`, `API Key` y `API Secret` desde el dashboard
3. Configurar las tres variables en `backend/.env`
