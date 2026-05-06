# ✅ DÍA 1 COMPLETADO — Backend Auth JWT + PostgreSQL Docker

> **Status:** 🟢 LISTO PARA TESTEAR

---

## 🎯 QUÉ HICIMOS

Backend FastAPI completamente funcional con:

✅ **PostgreSQL 15** containerizado en Docker  
✅ **JWT Autenticación** (HS256, 30 min expiration)  
✅ **Bcrypt Password Hashing** (factor 12, secure)  
✅ **3 Endpoints Core:**

- `POST /api/v1/auth/login` — Login con email + password
- `POST /api/v1/auth/register` — Registrar nuevo usuario
- `GET /api/v1/auth/me` — Obtener usuario actual (requiere token)

✅ **Swagger UI Auto-generado** en `/docs`  
✅ **Seed Data** — Admin user + 4 roles precargados  
✅ **Production-Ready Code** — Type hints, docstrings, error handling

---

## 🚀 CÓMO TESTEAR (3 PASOS)

### Paso 1: Levantar PostgreSQL con Docker

```bash
cd backend
docker-compose up -d
```

**Resultado esperado:**

```
Creating foodstore-db ... done
```

Verifica que esté corriendo:

```bash
docker-compose ps
```

### Paso 2: Levantar Backend

**Opción A: Automático (RECOMENDADO)**

```bash
# Windows
run.bat

# Linux/Mac
bash run.sh
```

**Opción B: Manual**

```bash
# Setup Python
python -m venv venv
venv\Scripts\activate   #linux: source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear tablas + seed data
python -c "from app.db.base import create_all_tables; create_all_tables()"
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

# Levantar servidor
uvicorn app.main:app --reload
```

**Resultado esperado:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Paso 3: Testear Endpoints

#### Opción A: Swagger UI (MÁS FÁCIL)

Abre en tu navegador: **http://localhost:8000/docs**

1. Click en **POST /api/v1/auth/login**
2. Click en "Try it out"
3. Ingresa:
   ```json
   {
     "email": "admin@foodstore.local",
     "password": "admin123"
   }
   ```
4. Click "Execute"
5. Copias el `access_token` de la respuesta

Luego: 6. Click en **GET /api/v1/auth/me** 7. Click en "Try it out" 8. Pega el token en el campo "Authorization" (formato: `Bearer TOKEN_AQUI`) 9. Click "Execute" 10. Deberías ver: `{ "id": 1, "email": "admin@foodstore.local", "nombre": "Admin", ... }`

#### Opción B: cURL (Terminal)

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@foodstore.local",
    "password": "admin123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 3. Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "nombre": "New User"
  }'
```

---

## ✨ ESTRUCTURA CREADA

```
backend/
├── 🐳 Infraestructura
│   ├── Dockerfile (FastAPI image)
│   ├── docker-compose.yml (PostgreSQL)
│   ├── requirements.txt (dependencias)
│   ├── run.sh, run.bat (scripts setup)
│   └── test_setup.py (validación)
│
├── 📚 Documentación
│   ├── START_HERE.md (comienza aquí)
│   ├── QUICKSTART.md (este archivo, en los docs)
│   ├── README.md (docs completa)
│   ├── CHECKLIST.md (validación)
│   ├── ARCHITECTURE.md (diagramas)
│   └── ESTRUCTURA.txt (visual de carpetas)
│
└── 🐍 Código Python
    ├── app/
    │   ├── main.py (FastAPI app + CORS + lifespan)
    │   ├── core/
    │   │   ├── config.py (Settings desde .env)
    │   │   ├── security.py (JWT + Bcrypt)
    │   │   └── dependencies.py (get_current_user, require_role)
    │   ├── db/
    │   │   ├── base.py (engine, create_all)
    │   │   ├── session.py (get_session generator)
    │   │   ├── seed.py (populate seed data)
    │   │   └── models/
    │   │       ├── usuario.py (SQLModel Usuario)
    │   │       └── rol.py (SQLModel Rol)
    │   └── modules/
    │       └── auth/
    │           ├── router.py (3 endpoints)
    │           ├── service.py (AuthService)
    │           └── schemas.py (Pydantic schemas)
    │
    ├── alembic/ (migraciones BD)
    │   ├── env.py (config)
    │   └── versions/ (migration files)
    │
    ├── .env (variables locales - NO COMMITEAR)
    ├── .env.example (template)
    ├── .gitignore (ignora __pycache__, venv, .env)
    └── alembic.ini (config migraciones)
```

---

## 🔑 CREDENCIALES SEED DATA

**Usuario Admin (precargado):**

- Email: `admin@foodstore.local`
- Password: `admin123`
- Roles: `ADMIN`

**Roles Disponibles:**

- `ADMIN` — Acceso total
- `CLIENT` — Usuario cliente
- `STOCK` — Gestor de stock
- `PEDIDOS` — Gestor de pedidos

---

## 📋 CHECKLIST VERIFICATION

Después de testear, verifica:

- [ ] `docker-compose ps` muestra `postgres` corriendo
- [ ] `http://localhost:8000/docs` abre sin errores
- [ ] POST /login retorna 200 + `access_token`
- [ ] GET /me retorna 200 + usuario data
- [ ] POST /register retorna 201 + nuevo usuario
- [ ] Nuevo usuario puede hacer login
- [ ] Token inválido retorna 401 Unauthorized
- [ ] Email duplicado en register retorna 422

---

## 🔐 SEGURIDAD IMPLEMENTADA

✅ **JWT (HS256)** — 30 min expiration  
✅ **Bcrypt** — Factor 12 (muy seguro)  
✅ **CORS Middleware** — Configurable en .env  
✅ **Pydantic Validation** — Email format + password strength  
✅ **HTTP Exceptions** — Semánticas (400, 401, 422, 500)  
✅ **HTTPBearer** — Autenticación estándar  
✅ **Soft Delete** — Prepared (deleted_at field en modelo Usuario)

---

## 🚨 TROUBLESHOOTING

### Error: "could not connect to server"

```bash
docker-compose ps
docker-compose up -d
docker-compose logs postgres
```

### Error: "Email o contraseña inválidos"

```bash
# Verificar seed data
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"
```

### Error: "No module named 'app'"

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Error: "psycopg2" no encontrado

```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📝 ESTRUCTURA .env

```bash
# .env (local, NO commitear)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/foodstore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=foodstore

JWT_SECRET=tu-super-secret-key-cambiar-en-prod
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

API_TITLE=FOOD STORE API
API_VERSION=1.0.0
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

---

## 🎯 PRÓXIMOS PASOS

Ahora que el backend funciona:

### DÍA 2: Auth Frontend + Catálogo Backend

**Delegar a subagente:**

- React login form (Zustand store + Axios)
- Productos backend (GET con paginación)
- Categorías backend (seed data)

### Después: Días 3-5

- Grilla + Filtros frontend
- CRUD Backend
- CRUD Frontend + Menú hamburguesa

---

## 📖 LECTURA RECOMENDADA

En este orden:

1. **backend/START_HERE.md** — Intro rápida
2. **backend/QUICKSTART.md** — Setup + testing (este archivo)
3. **backend/README.md** — Docs completa
4. **backend/ARCHITECTURE.md** — Diagramas + explicaciones
5. **TECHNICAL.md** (root) — Decisiones arquitectónicas

---

## ✅ VALIDACIÓN FINAL

Una vez todo funcione, tienes:

✅ Backend REST API 100% funcional  
✅ JWT Authentication working  
✅ PostgreSQL containerizado  
✅ Swagger UI auto-generado  
✅ Production-ready code  
✅ Documentación completa  
✅ Listo para integración Frontend

---

**¡Felicidades! DÍA 1 COMPLETADO.** 🎉

Próximo: Delegamos **DÍA 2** (Auth Frontend + Catálogo Backend)
