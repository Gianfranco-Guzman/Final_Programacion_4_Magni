# ✅ VERIFICACIÓN DÍA 1 — Backend Funcional

> Ejecuta esto para confirmar que todo está bien

---

## 🔍 STEP 1: Verificar Docker

```bash
# Verificar que Docker está instalado
docker --version
# Esperado: Docker version 20.10+ 

# Verificar que Docker Compose está instalado
docker-compose --version
# Esperado: Docker Compose version 2.0+
```

---

## 🔍 STEP 2: Levantar PostgreSQL

```bash
cd backend

# Levantar Base de Datos
docker-compose up -d

# Verificar que postgres está corriendo
docker-compose ps

# Esperado:
# NAME              STATUS
# foodstore-db      Up 10 seconds
```

---

## 🔍 STEP 3: Setup Backend

**Opción A: Automático (RECOMENDADO)**

```bash
# Windows
run.bat

# Linux/Mac
bash run.sh

# El script hace:
# 1. python -m venv venv
# 2. source venv/bin/activate
# 3. pip install -r requirements.txt
# 4. Crea tablas + seed data
# 5. Levanta uvicorn
```

**Opción B: Manual**

```bash
# Crear virtual environment
python -m venv venv

# Activar venv
source venv/bin/activate
# (Windows: venv\Scripts\activate)

# Instalar dependencias
pip install -r requirements.txt

# Crear tablas
python -c "from app.db.base import create_all_tables; create_all_tables()"

# Poblar seed data
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

# Levantar servidor
uvicorn app.main:app --reload
```

**Esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

---

## 🔍 STEP 4: Testing en Swagger UI

Abre en navegador: **http://localhost:8000/docs**

Debería ver:
- Swagger UI con endpoints documentados
- 3 endpoints visibles:
  - POST /api/v1/auth/login
  - POST /api/v1/auth/register
  - GET /api/v1/auth/me

---

## 🔍 STEP 5: Test Endpoints

### Test 5.1: Login

1. Click en **POST /api/v1/auth/login**
2. Click en **"Try it out"**
3. Ingresa en el body:
```json
{
  "email": "admin@foodstore.local",
  "password": "admin123"
}
```
4. Click **"Execute"**

**Esperado - Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Copiar el `access_token` para el siguiente test**

---

### Test 5.2: Get Current User

1. Click en **GET /api/v1/auth/me**
2. Click en **"Try it out"**
3. En el campo **"Authorization"**, pega el token del test anterior:
   - Formato: `Bearer YOUR_TOKEN_HERE`
4. Click **"Execute"**

**Esperado - Response 200:**
```json
{
  "id": 1,
  "email": "admin@foodstore.local",
  "nombre": "Admin",
  "is_active": true,
  "created_at": "2026-05-05T19:35:00.000",
  "roles": [
    {
      "id": 1,
      "nombre": "ADMIN"
    }
  ]
}
```

---

### Test 5.3: Register New User

1. Click en **POST /api/v1/auth/register**
2. Click en **"Try it out"**
3. Ingresa en el body:
```json
{
  "email": "testuser@example.com",
  "password": "password123",
  "nombre": "Test User"
}
```
4. Click **"Execute"**

**Esperado - Response 201:**
```json
{
  "id": 2,
  "email": "testuser@example.com",
  "nombre": "Test User",
  "is_active": true,
  "created_at": "2026-05-05T19:36:00.000",
  "roles": [
    {
      "id": 3,
      "nombre": "CLIENT"
    }
  ]
}
```

---

### Test 5.4: Login con Nuevo Usuario

1. POST /login con:
```json
{
  "email": "testuser@example.com",
  "password": "password123"
}
```

**Esperado - Response 200:** Token nuevo

---

## 🔍 STEP 6: Verificar Seed Data

```bash
# Verificar que se crearon las tablas
python -c "
from app.db.base import SessionLocal
session = SessionLocal()
from app.db.models import Usuario, Rol
usuarios = session.query(Usuario).all()
print(f'Total usuarios: {len(usuarios)}')
for u in usuarios:
    print(f'  - {u.email}')
"

# Esperado:
# Total usuarios: 1
#   - admin@foodstore.local
```

---

## 🔍 STEP 7: Verificar Base de Datos Directamente

```bash
# Conectar a PostgreSQL (requerir psql instalado)
psql -U postgres -d foodstore -c "SELECT * FROM usuario;"

# Esperado:
# id |          email          | nombre |        password_hash         | is_active |           created_at           |          updated_at            | deleted_at
# ---+-------------------------+--------+------------------------------+-----------+--------------------------------+--------------------------------+------------
#  1 | admin@foodstore.local   | Admin  | $2b$12$... (bcrypt hash)... | t         | 2026-05-05 19:35:00.000000 | 2026-05-05 19:35:00.000000 |
```

---

## ✅ CHECKLIST VERIFICACIÓN

- [ ] Docker running: `docker-compose ps`
- [ ] PostgreSQL healthy: `docker-compose logs postgres | grep "database system is ready"`
- [ ] Servidor running: `http://localhost:8000/` retorna status 200
- [ ] Swagger UI: `http://localhost:8000/docs` abre sin errores
- [ ] Login admin: POST /login retorna 200 + token
- [ ] Get me: GET /me (con token) retorna 200 + user data
- [ ] Register new: POST /register retorna 201
- [ ] Login nuevo user: POST /login (nuevo) retorna 200
- [ ] Seed data: tabla usuario tiene 2 registros
- [ ] Roles: tabla rol tiene 4 registros (ADMIN, CLIENT, STOCK, PEDIDOS)

---

## 🚨 TROUBLESHOOTING

### Error: "could not connect to server"

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Si no está, levantar:
docker-compose up -d

# Ver logs de postgres
docker-compose logs postgres

# Si error de puerto (5432 ya en uso):
# Cambiar en docker-compose.yml: ports: ["5433:5432"]
# Y en .env: DATABASE_URL=postgresql://postgres:postgres@localhost:5433/foodstore
```

### Error: "Email o contraseña inválidos"

```bash
# Verificar que seed data se ejecutó
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

# Verificar usuario en BD
python -c "
from app.db.base import SessionLocal
from app.db.models import Usuario
session = SessionLocal()
user = session.query(Usuario).filter(Usuario.email == 'admin@foodstore.local').first()
if user:
    print('Usuario encontrado')
    # Puede hacer login
else:
    print('Usuario NO encontrado - correr seed again')
"
```

### Error: "No module named 'app'"

```bash
# Asegurate de:
# 1. Estar en directorio backend/
cd backend

# 2. venv activado
source venv/bin/activate  # o venv\Scripts\activate en Windows

# 3. Estar en backend/ NO en root
pwd  # debería mostrar .../backend
```

### Error: "psycopg2 no encontrado"

```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt

# O instalar solo psycopg2
pip install psycopg2-binary==2.9.9
```

---

## 🎉 CUANDO TODO FUNCIONA

Si pasaste todos los tests arriba:

✅ Backend está 100% funcional  
✅ Base de datos está creada y poblada  
✅ JWT authentication funciona  
✅ Listo para integración frontend (DÍA 2)

**Próximo paso:** Delegar DÍA 2 (Frontend login + Catálogo backend)

---

**¿Todo pasó?** ✅ Continúa leyendo `DIA_1_COMPLETADO.md`
