# Quick Start - Testing the API

## Requisitos

- Docker & Docker Compose instalado
- Python 3.11+ con pip
- curl o Postman (para testing)

## Opción 1: Local sin Docker (Recomendado para desarrollo rápido)

### 1. PostgreSQL en Docker

```bash
docker-compose up -d
# Espera 5-10 segundos para que el servicio esté listo
```

### 2. Setup y levantar server

```bash
# Windows
run.bat

# Linux/Mac
bash run.sh

# O manual:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -c "from app.db.base import create_all_tables; create_all_tables()"
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"
uvicorn app.main:app --reload
```

### 3. Testing

Abre http://localhost:8000/docs en tu navegador para ver Swagger UI

#### cURL Testing

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@foodstore.local",
    "password": "admin123"
  }'

# Copiar el access_token de la respuesta y usarlo abajo:

# 2. Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# 3. Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "nombre": "New User"
  }'
```

## Opción 2: Con Docker (Recomendado para producción)

```bash
# Construir imagen
docker build -t foodstore-api:latest .

# Levantar con docker-compose
docker-compose up

# O solo API
docker run -p 8000:8000 \
  --env-file .env \
  --network host \
  foodstore-api:latest
```

## Verificación de Endpoints

| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET | `/` | No | Health check raíz |
| GET | `/health` | No | Health check |
| POST | `/api/v1/auth/login` | No | Login |
| POST | `/api/v1/auth/register` | No | Registro |
| GET | `/api/v1/auth/me` | Sí | Usuario actual |
| GET | `/docs` | No | Swagger OpenAPI |
| GET | `/redoc` | No | ReDoc |

## Credenciales de Testing

**Admin User (seed data):**
- Email: `admin@foodstore.local`
- Password: `admin123`

**Otros Roles Disponibles:**
- ADMIN
- CLIENT
- STOCK
- PEDIDOS

## Troubleshooting

### "could not connect to server"
```bash
docker-compose ps  # Verificar que postgres esté running
docker-compose up -d  # Levantar si no está
```

### "Email o contraseña inválidos"
```bash
# Verificar que la seed data se ejecutó:
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"
```

### "No module named 'app'"
```bash
# Asegurate de estar en el directorio backend/
cd backend
source venv/bin/activate
```

### PostgreSQL no responde
```bash
# Espera 10 segundos después de docker-compose up
# O revisa logs:
docker-compose logs postgres
```

## Siguientes Pasos

Una vez que todo funciona:

1. ✅ Verificar que los 3 endpoints funcionan en Swagger UI
2. ✅ Hacer login y guardar token
3. ✅ Usar token en GET /me
4. ✅ Registrar nuevo usuario
5. ✅ Login con nuevo usuario

## Deployment Notes

Para producción (no implementado en Día 1):

- [ ] Cambiar SECRET_KEY a valor seguro (min 32 caracteres)
- [ ] Cambiar POSTGRES_PASSWORD
- [ ] DEBUG=false
- [ ] CORS restringido a dominios específicos
- [ ] HTTPS only
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Audit logs

Ver `backend/README.md` para detalles completos.
