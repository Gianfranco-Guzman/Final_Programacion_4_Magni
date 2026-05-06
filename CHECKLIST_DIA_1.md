# 🎯 CHECKLIST DÍA 1 — Setup + Auth Backend

> Status: EN PROGRESO (delegado a subagente)

**Objetivo:** Tener POST /login, POST /register, GET /me funcionales + PostgreSQL en Docker

---

## ✅ Tasks

### Infraestructura
- [ ] docker-compose.yml con PostgreSQL 15-alpine
- [ ] .env configurado (DATABASE_URL, JWT_SECRET)
- [ ] Backend Dockerfile creado
- [ ] Alembic configurado (env.py + migration base)

### Backend Core
- [ ] `app/core/config.py` — Settings desde pydantic-settings
- [ ] `app/core/security.py` — hash/verify/create_token/decode_token
- [ ] `app/core/dependencies.py` — get_current_user, require_role
- [ ] `app/db/base.py` — engine, create_all
- [ ] `app/db/session.py` — get_session generator
- [ ] `app/db/seed.py` — populate roles + admin user

### Modelos
- [ ] `app/db/models/usuario.py` — Usuario table + validaciones
- [ ] `app/db/models/rol.py` — Rol table (enum: ADMIN, STOCK, PEDIDOS, CLIENT)
- [ ] Alembic migration (auto-generate)

### Autenticación
- [ ] `app/modules/auth/router.py` — POST /login, POST /register, GET /me
- [ ] `app/modules/auth/service.py` — autenticar, crear_usuario, obtener_usuario_actual
- [ ] `app/modules/auth/schemas.py` — Pydantic schemas (LoginRequest, etc)

### FastAPI
- [ ] `app/main.py` — FastAPI app + CORS + lifespan seed
- [ ] OpenAPI Swagger en /docs
- [ ] Error handlers (400, 401, 422, 500)

### Testing
- [ ] PostgreSQL levanta con docker-compose up -d postgres
- [ ] Migraciones corren: alembic upgrade head
- [ ] Seed data poblado (admin user creado)
- [ ] Endpoints testeables en Postman/Swagger

---

## 📝 Comandos para Verificar

```bash
# 1. Levantar DB
docker-compose up -d postgres

# 2. Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload

# 3. Test endpoints
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"pass123","nombre":"Admin"}'

# 4. Swagger
# http://localhost:8000/docs
```

---

## 🔗 Links de Referencia

- FastAPI: https://fastapi.tiangolo.com/
- SQLModel: https://sqlmodel.tiangolo.com/
- Pydantic Settings: https://docs.pydantic.dev/latest/api/pydantic_settings/
- PyJWT: https://pyjwt.readthedocs.io/

---

**ESTADO:** Esperando delegación...
