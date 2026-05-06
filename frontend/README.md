# Food Store Frontend

React + TypeScript frontend para la aplicación Food Store.

## Setup Rápido

### Prerrequisitos

- Node.js 20+
- npm o yarn

### Instalación

```bash
cd frontend
npm install
```

### Desarrollo

```bash
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173) en tu navegador.

### Build

```bash
npm run build
```

## Estructura

```
frontend/
├── src/
│   ├── api/               # Clientes HTTP (axios)
│   ├── components/        # Componentes primitivos reutilizables
│   ├── features/          # Dominios (auth, store)
│   ├── hooks/             # Custom hooks (TanStack Query)
│   ├── layouts/           # Layouts principales
│   ├── store/             # Zustand stores (authStore, uiStore)
│   ├── types/             # TypeScript interfaces
│   ├── App.tsx            # Router principal
│   ├── main.tsx           # Entry point
│   └── index.css          # Tailwind styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

## Arquitectura

### Estado

- **Zustand (authStore)**: Estado del cliente (token, usuario, auth state)
- **TanStack Query (useProductos)**: Estado del servidor (productos, paginación)

### API

- `axiosClient.ts`: Cliente HTTP con interceptor JWT automático
- `authApi.ts`: Endpoints de autenticación
- `productosApi.ts`: Endpoints de productos

### Seguridad

- Token JWT almacenado en localStorage
- Interceptor automático: agrega Authorization header
- 401 → logout automático + redirect /login

## Variables de Entorno

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Credenciales de Prueba

```
Email: admin@foodstore.local
Password: admin123
```

## Tecnologías

- **React 18.3** + TypeScript 5
- **Vite 5** (build tool)
- **TanStack Query 5** (server state)
- **Zustand 4.4** (client state)
- **Axios 1.6** (HTTP)
- **Tailwind CSS 3.4** (estilos)
- **React Router 6.21** (routing)
