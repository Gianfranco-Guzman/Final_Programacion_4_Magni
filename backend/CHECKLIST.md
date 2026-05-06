# ✅ Checklist de Verificación - DÍA 1

## Pre-requisitos

- [ ] Python 3.11+ instalado (`python --version`)
- [ ] Docker & Docker Compose instalado (`docker --version`)
- [ ] Git configurado (opcional pero recomendado)

## Setup (5-10 minutos)

### 1. PostgreSQL

```bash
# Levanta PostgreSQL en Docker
docker-compose up -d

# Verificar que está running
docker ps
# Deberías ver: foodstore_postgres - healthy
```

- [ ] `docker ps` muestra `foodstore_postgres` como `running`
- [ ] No hay errores de puerto 5432 en uso

### 2. Dependencias Python

```bash
# Crear virtualenv
python -m venv venv

# Activar virtualenv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

- [ ] `pip list` muestra todas las librerías (fastapi, sqlmodel, pyjwt, etc.)
- [ ] No hay errores de instalación

### 3. Base de Datos

```bash
# Crear tablas
python -c "from app.db.base import create_all_tables; create_all_tables(); print('✓ Tablas creadas')"

# Poblar seed data
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"
```

- [ ] Ver mensajes "✓ Tablas creadas" y "✓ Seed data poblado exitosamente"
- [ ] No hay errores de conexión a PostgreSQL

### 4. Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

- [ ] Ver mensaje "Uvicorn running on http://127.0.0.1:8000"
- [ ] Ver logs de startup (crear tablas, seed data)
- [ ] No hay errores en la terminal

## Testing de Endpoints (2-3 minutos)

### 1. Verificar Swagger UI

```bash
# En el navegador:
http://localhost:8000/docs
```

- [ ] Se abre Swagger UI
- [ ] Ver los 3 endpoints de auth listados
- [ ] Ver botón "Try it out" en cada endpoint

### 2. POST /api/v1/auth/login

En Swagger UI, expandir `/api/v1/auth/login`:

```json
{
  "email": "admin@foodstore.local",
  "password": "admin123"
}
```

- [ ] Click "Execute"
- [ ] Response: 200 OK
- [ ] Response body contiene `access_token`, `token_type`, `expires_in`
- [ ] Copiar el `access_token` (sin comillas)

### 3. GET /api/v1/auth/me

En Swagger UI, expandir `/api/v1/auth/me`:

```
Authorization: Bearer <PEGA_TU_TOKEN_AQUI>
```

- [ ] Pegar token en el input de Authorization
- [ ] Click "Execute"
- [ ] Response: 200 OK
- [ ] Response body: `{ "id": 1, "email": "admin@foodstore.local", ... }`
- [ ] Verificar que la información del usuario es correcta

### 4. POST /api/v1/auth/register

En Swagger UI, expandir `/api/v1/auth/register`:

```json
{
  "email": "testuser@example.com",
  "password": "testpass123",
  "nombre": "Test User"
}
```

- [ ] Click "Execute"
- [ ] Response: 201 Created
- [ ] Response body contiene el nuevo usuario con `id` generado
- [ ] El email es el que enviaste

### 5. Validar Login con nuevo usuario

```json
{
  "email": "testuser@example.com",
  "password": "testpass123"
}
```

- [ ] Click Execute en `/login`
- [ ] Response: 200 OK
- [ ] Obtiene un token válido (diferente al del admin)

## Testing con cURL (opcional)

Si prefieres cURL en lugar de Swagger:

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@foodstore.local","password":"admin123"}' | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Get me
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 3. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"curltest@example.com","password":"curltestpass123","nombre":"CURL Test"}'
```

- [ ] Todos los curls retornan respuestas válidas
- [ ] No hay errores 4xx o 5xx

## Validación de Errores

### 1. Credenciales inválidas

POST `/login` con:
```json
{
  "email": "admin@foodstore.local",
  "password": "wrongpassword"
}
```

- [ ] Response: 401 Unauthorized
- [ ] Message: "Email o contraseña inválidos"

### 2. Email duplicado

POST `/register` con el mismo email dos veces:

```json
{
  "email": "duplicate@example.com",
  "password": "password123",
  "nombre": "Duplicate"
}
```

- [ ] Primera vez: 201 Created
- [ ] Segunda vez: 422 Unprocessable Entity
- [ ] Message: "El email ya está registrado"

### 3. Token inválido

GET `/me` con:
```
Authorization: Bearer invalid_token_here
```

- [ ] Response: 401 Unauthorized
- [ ] Message: "Token inválido o expirado"

### 4. Sin autenticación

GET `/me` sin header Authorization:

- [ ] Response: 403 Forbidden (HTTPBearer automático)

## Verificación de Datos en BD (opcional)

Si tienes psql instalado:

```bash
psql -U foodstore -d foodstore_db -h localhost

# En psql:
SELECT * FROM usuario;
SELECT * FROM rol;
SELECT * FROM usuario_rol;
```

- [ ] Ver 1 usuario (admin)
- [ ] Ver 4 roles (ADMIN, CLIENT, STOCK, PEDIDOS)
- [ ] Ver relación usuario_rol con admin → ADMIN

## Docker (opcional)

Si quieres verificar que funciona en Docker:

```bash
# Construir imagen
docker build -t foodstore-api:latest .

# Verificar imagen
docker images | grep foodstore

# Correr en Docker
docker run -p 8000:8000 \
  --env-file .env \
  --network host \
  foodstore-api:latest
```

- [ ] Build sin errores
- [ ] Imagen creada correctamente
- [ ] Container corre y se puede acceder a /docs

## Verificación de Archivos

```bash
# Contar archivos creados
find backend -type f -name "*.py" | wc -l
# Debería ser ~18 archivos Python

# Verificar estructura
ls -R backend/app/
# Debería mostrar toda la estructura de directorios
```

- [ ] 18+ archivos Python creados
- [ ] Estructura de directorios completa
- [ ] No faltan archivos `.py` o de configuración

## Próximos Pasos

Cuando TODO este checklist esté completado:

1. [ ] Commit de todo el backend a git
2. [ ] Comenzar con frontend (Fase 2)
3. [ ] Integración frontend ↔ backend
4. [ ] Testing E2E
5. [ ] Deployment (Fase 3)

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "could not connect to server" | `docker-compose ps` + `docker-compose up -d` |
| "Email o contraseña inválidos" | Verificar que seed data se ejecutó |
| "No module named 'app'" | Asegurate de estar en `backend/` con venv activo |
| Token inválido o expirado | El token tiene 30 minutos de validez |
| CORS error en navegador | Verificar `CORS_ORIGINS` en `.env` |
| Puerto 5432 en uso | Cambiar puerto en `docker-compose.yml` |

## Éxito 🎉

Si todos los checks están completados, tienes:

✅ Backend completamente funcional
✅ Autenticación JWT working
✅ 3 endpoints testados
✅ Base de datos poblada
✅ Documentación con Swagger
✅ Docker ready
✅ Production-ready code

**Tiempo total: 15-20 minutos**

Listo para integrar con el frontend.
