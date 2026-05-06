# CONTENIDOS CLAVE - DÍA 2

Este archivo documenta el contenido de todos los archivos creados para fácil revisión.

## BACKEND - app/db/models/categoria.py

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Categoria(SQLModel, table=True):
    """Modelo de categorías de productos"""
    __tablename__ = "categoria"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relación con productos
    productos: list["Producto"] = Relationship(back_populates="categoria")
```

## BACKEND - app/db/models/producto.py

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Producto(SQLModel, table=True):
    """Modelo de productos del catálogo"""
    __tablename__ = "producto"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(gt=0)
    stock_cantidad: int = Field(ge=0)
    categoria_id: int = Field(foreign_key="categoria.id")
    codigo: str = Field(unique=True, index=True, max_length=50)
    deleted_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relación con categoría
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

## BACKEND - app/modules/productos/router.py (RESUMEN)

**GET /api/v1/productos/**
- Query params: page, size, categoria_id, search, disponible
- Retorna: PaginatedResponse con items, total, page, size, pages
- Soft delete automático: WHERE deleted_at IS NULL
- Full-text search en nombre + código

**GET /api/v1/productos/{id}**
- Retorna producto específico

**GET /api/v1/productos/categorias/**
- Retorna lista de categorías

## FRONTEND - src/store/authStore.ts

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  accessToken: string | null
  usuario: Usuario | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      usuario: null,
      isAuthenticated: false,
      
      login: async (email, password) => {
        const response = await authApi.login({ email, password })
        set({ accessToken: response.access_token, isAuthenticated: true })
        const user = await authApi.me()
        set({ usuario: user })
      },
      
      logout: () => {
        set({
          accessToken: null,
          usuario: null,
          isAuthenticated: false,
        })
      },
      
      setToken: (token: string) => {
        set({ accessToken: token, isAuthenticated: true })
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ accessToken: state.accessToken }),
    }
  )
)
```

## FRONTEND - src/api/axiosClient.ts

```typescript
import axios from 'axios'
import { useAuthStore } from '@store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
})

// Request interceptor: Agregar JWT
axiosClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: 401 → logout
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

## FRONTEND - src/App.tsx

```typescript
export default function App() {
  // Routes setup:
  // /login → LoginPage (público)
  // /catalogo → CatalogoPage (protegida)
  // / → redirect /catalogo
  // * → redirect /catalogo
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/catalogo"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CatalogoPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
```

## FRONTEND - src/features/store/CatalogoPage.tsx

**Funcionalidades:**
- useProductos hook con paginación
- ProductFilters: search, categoría, disponibilidad
- ProductGrid: 3 cols desktop, 2 tablet, 1 móvil
- Paginación: Anterior/Siguiente
- Loading state
- Error handling

## FRONTEND - package.json

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-router-dom": "^6.21.0",
    "zustand": "^4.4.1",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.28.0",
    "@tanstack/react-form": "^0.5.0",
    "tailwindcss": "^3.4.1"
  }
}
```

## FRONTEND - vite.config.ts

```typescript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@api': resolve(__dirname, './src/api'),
      '@store': resolve(__dirname, './src/store'),
      // ... more aliases
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## FRONTEND - tailwind.config.ts

```typescript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        error: '#EF4444',
      },
    },
  },
}
```

---

## ESTRUCTURA DE DIRECTORIOS

```
frontend/
├── src/
│   ├── api/
│   │   ├── axiosClient.ts      ← JWT interceptor
│   │   ├── authApi.ts
│   │   └── productosApi.ts
│   ├── store/
│   │   ├── authStore.ts        ← Zustand con persistence
│   │   └── uiStore.ts
│   ├── hooks/
│   │   ├── useAuth.ts          ← Mutations login/register
│   │   └── useProductos.ts     ← Queries GET productos
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Spinner.tsx
│   ├── features/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx   ← Form con validaciones
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── LoginPage.tsx
│   │   └── store/
│   │       ├── CatalogoPage.tsx ← GET + filtros
│   │       ├── ProductGrid.tsx  ← Responsive 3/2/1 cols
│   │       ├── ProductCard.tsx
│   │       └── ProductFilters.tsx
│   ├── layouts/
│   │   └── MainLayout.tsx      ← Navbar + layout
│   ├── types/
│   │   └── index.ts            ← Interfaces
│   ├── App.tsx                 ← Router
│   ├── main.tsx
│   └── index.css               ← Tailwind
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── index.html
└── Dockerfile

backend/
├── app/
│   ├── db/
│   │   ├── models/
│   │   │   ├── categoria.py    ← NEW
│   │   │   └── producto.py     ← NEW
│   │   └── seed.py             ← UPDATED
│   ├── modules/
│   │   └── productos/          ← NEW
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── __init__.py
│   └── main.py                 ← UPDATED
```

---

## SEED DATA CREADO

### Categorías
1. Pizza — "Pizzas tradicionales y especiales"
2. Bebidas — "Bebidas frías y calientes"
3. Postres — "Postres y dulces"

### Productos (10 total)
- 4 Pizza: Clásica, Pepperoni, Vegetariana, BBQ
- 3 Bebidas: Coca Cola 2L, Agua, Cerveza
- 3 Postres: Tiramisu, Helado, Brownie

Precios: $49.99 a $379.99
Stock: 25 a 200 unidades

---

## ENDPOINTS DISPONIBLES

### Auth (Ya existían)
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/me`

### Productos (NUEVOS)
- `GET /api/v1/productos/`
  - ?page=1&size=20
  - ?categoria_id=1
  - ?search=pizza
  - ?disponible=true
- `GET /api/v1/productos/{id}`
- `GET /api/v1/productos/categorias/`

---

## VALIDACIONES

### Frontend (LoginForm)
- Email: formato válido
- Password: mínimo 3 caracteres

### Backend (Pydantic)
- Email: único, formato válido
- Password: hash bcrypt factor 12
- Precio: > 0
- Stock: >= 0
- Código: único

---

## ARCHIVOS DE CONFIGURACIÓN

### .env (Frontend)
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### .env (Backend - ya existe)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/foodstore
JWT_SECRET=tu-super-secret-key
CORS_ORIGINS=["http://localhost:5173"]
```

---

**Generado:** DÍA 2 COMPLETADO
**Total de archivos:** 29 (frontend) + 6 (backend updates)
**Líneas de código:** ~2,000
