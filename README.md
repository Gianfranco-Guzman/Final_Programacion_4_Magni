# 🍔 FOOD STORE — TPI Programación 4

**Sistema de Gestión de Pedidos de Comida** — React + TypeScript + FastAPI + PostgreSQL


---
## INTEGRANTES

- Gianfranco Guzman
- Bruno Racconto
- Alexander Filchel

### LINK VIDEO

- https://youtu.be/u8AqXBbrxMg

---

## 📋 Requisitos

- **Docker** + **Docker Compose** (recomendado)
- O manualmente: **Python 3.10+**, **Node 18+**, **PostgreSQL 15+**
- **Git**

---

## 🚀 Inicio Rápido (Con Docker)

```bash
# 1. Clonar repositorio
git clone <url-repo>
cd foodstore

# 2. Crear archivo .env (copiar desde .env.example)
cp .env.example .env

# 3. Levantar PostgreSQL
docker-compose up -d postgres

# 4. Backend (en otra terminal)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Aplicar migraciones (incluye columnas nuevas como deleted_at)
python -m alembic upgrade head
uvicorn app.main:app --reload

# 5. Frontend (en otra terminal)
cd frontend
npm install
npm run dev

# Accesos:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## 📂 Estructura del Proyecto

```
.
├── docker-compose.yml          # Orchestración de servicios
├── .env.example                # Variables de entorno (ejemplo)
├── README.md                   # Este archivo
├── TECHNICAL.md                # Documentación arquitectónica
├── START_HERE.md               # Guía de inicio
├── ROADMAP.LOCAL.md            # Roadmap local (NO commitear)
│
├── backend/                    # FastAPI + SQLModel
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                    # Variables (crear desde .env.example)
│   ├── README.md               # Setup backend específico
│   ├── alembic/                # Migraciones BD
│   └── app/
│       ├── main.py             # FastAPI app
│       ├── core/               # Configuración, seguridad, dependencias
│       ├── db/                 # Modelos, sesiones, seed
│       └── modules/            # Features (auth, productos, etc)
│
└── frontend/                   # React + Vite
    ├── Dockerfile
    ├── .env                    # Variables (crear desde .env.example)
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    └── src/                    # Código React
        ├── App.tsx
        ├── store/              # Zustand stores
        ├── api/                # Funciones Axios
        ├── hooks/              # Custom hooks (TanStack Query)
        ├── features/           # Componentes de dominio
        ├── components/         # Componentes primitivos
        └── types/              # Interfaces TypeScript
```

---

## 🔧 Configuración Manual (Sin Docker)

### Backend

```bash
cd backend

# Setup Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Base de datos (PostgreSQL debe estar corriendo en tu máquina)
# Crear BD manualmente o dejar que Alembic la cree
python -m alembic upgrade head

# Correr servidor
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Variables de entorno
cp .env.example .env

# Dev server
npm run dev
```

---

## 📖 Documentación

- **TECHNICAL.md** — Arquitectura, patrones, decisiones de diseño
- **START_HERE.md** — Guía rápida para empezar
- **ROADMAP.LOCAL.md** — Timeline día a día (LOCAL, no commitear)
- **backend/README.md** — Setup específico del backend
- **frontend/README.md** — Setup específico del frontend

---

## 🔐 Roles y Permisos (RBAC)

El sistema tiene **4 roles** con distintos niveles de acceso:

| Rol | Acceso |
|-----|--------|
| **ADMIN** | Gestión completa: usuarios, productos, categorías, ingredientes |
| **STOCK** | Gestión de productos, categorías e ingredientes (sin admin de usuarios) |
| **CLIENT** | Solo lectura: ver productos, categorías e ingredientes |
| **PEDIDOS** | (Reservado para futura gestión de pedidos) |

### Endpoints protegidos por rol

| Método | Ruta | Roles requeridos |
|--------|------|------------------|
| POST/PUT/DELETE | `/api/v1/categorias/...` | ADMIN, STOCK |
| POST/PUT/PATCH | `/api/v1/productos/...` | ADMIN, STOCK |
| POST/PUT/DELETE | `/api/v1/ingredientes/...` | ADMIN, STOCK |
| GET/PATCH | `/api/v1/auth/admin/...` | ADMIN |
| GET | `/api/v1/auth/me` | Cualquier usuario autenticado |

### Usuarios pre-cargados (seed)

| Email | Contraseña | Roles |
|-------|-----------|-------|
| `admin@foodstore.com` | `admin1234` | ADMIN, STOCK, PEDIDOS |
| `juan@example.com` | `Juan1234!` | CLIENT |

> Al registrarse, los nuevos usuarios obtienen automáticamente el rol **CLIENT**.

---

## 🧪 Testing Manual

### Backend (Postman / Curl)

```bash
# 1. Registrar usuario (obtiene rol CLIENT automáticamente)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","nombre":"Test User"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 3. Get current user (reemplazar TOKEN)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"

# 4. [Admin] Listar usuarios
curl -X GET http://localhost:8000/api/v1/auth/admin/usuarios \
  -H "Authorization: Bearer TOKEN_ADMIN"

# 5. [Admin] Desactivar/activar usuario
curl -X PATCH http://localhost:8000/api/v1/auth/admin/usuarios/2/desactivar \
  -H "Authorization: Bearer TOKEN_ADMIN"

# Ver OpenAPI Swagger
# http://localhost:8000/docs
```

---

## 🐙 Git Workflow

### Commits

Commits en **español natural**, descriptivo:

```bash
git commit -m "creo login con JWT"
git commit -m "agrego grilla de productos con paginación"
git commit -m "implemento CRUD insumos"
```

### Branch Strategy

- `main` — Rama principal (producción)
- `dev` — Rama de desarrollo (integración)
- `feature/*` — Ramas de features individuales

---

## 📋 Checklist Antes de Entrega (Viernes)

- [ ] Docker levanta sin errores
- [ ] PostgreSQL corre en background
- [ ] Backend API en http://localhost:8000/docs funciona
- [ ] Frontend en http://localhost:5173 abre sin errores
- [ ] Login funciona (register → login → me)
- [ ] Grilla productos muestra ítems paginados
- [ ] Filtros funcionan (categoría, búsqueda, disponible)
- [ ] CRUD productos completo (crear, editar, eliminar) — requiere ADMIN o STOCK
- [ ] Solo ADMIN puede listar/desactivar/activar usuarios via `/api/v1/auth/admin/usuarios`
- [ ] Soft delete muestra fondo rojo
- [ ] Menú hamburguesa abre/cierra
- [ ] Todo responsive en mobile
- [ ] Git limpio (sin .env, node_modules, __pycache__)

---

## 🆘 Troubleshooting

### Error: "can't connect to PostgreSQL"

```bash
# Verificar que PostgreSQL esté corriendo
docker ps

# Si no está, levantarlo
docker-compose up -d postgres

# Ver logs
docker-compose logs postgres
```

### Error: "Address already in use (port 5432)"

```bash
# Puerto 5432 ya está ocupado, cambiar en .env y docker-compose.yml
# O matar proceso existente (cuidado)
lsof -ti:5432 | xargs kill -9
```

### Error: "ModuleNotFoundError"

```bash
# Asegurarse de estar en venv
source venv/bin/activate
# Reinstalar dependencias
pip install -r requirements.txt
```

---

## 🚀 Deployment (Después del viernes)

- Render, Railway, Vercel, DigitalOcean para hosting
- Variables de entorno en secrets del proveedor
- CI/CD con GitHub Actions

---

## 📞 Contacto / Ayuda

- Ver documentación en `docs/`
- Revisar `TECHNICAL.md` para decisiones arquitectónicas
- Consultar `START_HERE.md` si estás perdido

---

**¡Vamos a hacerlo!** 💪
