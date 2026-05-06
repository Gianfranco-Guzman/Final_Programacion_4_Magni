# PASO A PASO: VERIFICACIÓN Y EJECUCIÓN DÍA 2

Este documento te guía paso a paso para verificar que todo funciona.

## ⚙️ PREREQUISITOS

- Node.js 20+ instalado (`node --version`)
- Docker instalado (`docker --version`)
- PostgreSQL image descargada (se descarga automáticamente)

## 🚀 PASO 1: Backend - PostgreSQL

```bash
cd backend
docker-compose up -d postgres
```

**Espera: ~5 segundos**

Verifica:
```bash
docker-compose ps
# Deberías ver: postgres ... Up
```

## 🚀 PASO 2: Backend - Instala dependencias

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

**Espera: ~30 segundos**

Verifica: debería decir "Successfully installed ..."

## 🚀 PASO 3: Backend - Inicia servidor

```bash
# Desde backend/ con venv activado
uvicorn app.main:app --reload
```

**Espera: ~5 segundos**

Verifica:
```
✓ Uvicorn running on http://127.0.0.1:8000
✓ Tablas creadas
✓ Seed data poblado
  - Roles creados: 4
  - Usuario admin: admin@foodstore.local / admin123
  - Categorías: 3
  - Productos: 10
```

**Prueba rápida:** http://localhost:8000/docs (Swagger UI)

## 🚀 PASO 4: Frontend - Instala dependencias

```bash
# Otra terminal
cd frontend
npm install
```

**Espera: ~2 minutos** (primera vez descarga mucho)

Verifica: debería decir "up to date" al final

## 🚀 PASO 5: Frontend - Inicia dev server

```bash
# Desde frontend/
npm run dev
```

**Espera: ~5 segundos**

Verifica:
```
✓ VITE v5.x.x ready in xxx ms
✓ Local: http://localhost:5173/
```

## ✅ PASO 6: TESTEA EN NAVEGADOR

### Test 1: Login

1. Abre http://localhost:5173
2. Deberías ver: **LoginForm** con email + password inputs
3. Ingresa:
   - Email: `admin@foodstore.local`
   - Password: `admin123`
4. Click "Ingresar"

**Resultado esperado:**
- ✅ Loading spinner temporal
- ✅ Redirect a /catalogo
- ✅ Navbar con "Administrador" + botón "Salir"

### Test 2: Catálogo

En la página /catalogo deberías ver:

- ✅ **Título:** "Catálogo"
- ✅ **Total:** "10 productos disponibles"
- ✅ **Filtros:**
  - Search input (buscar producto)
  - Select Categoría (Pizza, Bebidas, Postres)
  - Select Disponibilidad (Todos, Disponibles, Sin stock)

- ✅ **Grilla de productos:** 10 tarjetas
  - 3 columnas en desktop
  - 2 columnas en tablet
  - 1 columna en móvil

- ✅ **Cada tarjeta muestra:**
  - Imagen placeholder gris
  - Nombre producto
  - Descripción (línea 2 máximo)
  - Categoría (badge)
  - Precio en azul (grande)
  - Stock (verde si hay, rojo si no)
  - Código SKU

### Test 3: Filtros

1. **Search:** Escribe "pizza" → filtra por nombre
2. **Categoría:** Selecciona "Bebidas" → muestra 3 productos
3. **Disponibilidad:** Selecciona "Disponibles" → solo stock > 0

**Resultado:** El filtro se aplica al instante sin reload

### Test 4: Paginación

- Cambios de página funcionan
- Botones Anterior/Siguiente deshabilitados en límites
- Texto "Página X de Y" actualizado

### Test 5: Logout

1. Click botón "Salir" en navbar
2. Redirect a /login
3. LocalStorage limpio (si inspecciónas, no hay token)

## 🔧 TROUBLESHOOTING

### Error: "psycopg2: can't adapt type 'NoneType'"

**Causa:** SQLModel relacionando modelos sin importar Categoria primero

**Solución:** Ya está arreglado en el código. Si falla, verifica que imports en `seed.py`:
```python
from app.db.models.categoria import Categoria
from app.db.models.producto import Producto
```

### Error: "VITE_API_BASE_URL not defined"

**Causa:** .env missing

**Solución:**
```bash
cd frontend
# Verifica que exista .env con:
cat .env
# Debería mostrar: VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Error: "TypeError: Cannot read property 'accessToken' of undefined"

**Causa:** Zustand store no inicializado

**Solución:** Ya está handled en el código. Si ocurre, limpia:
```bash
# Chrome DevTools -> Application -> LocalStorage -> http://localhost:5173
# Borra todas las entries
```

### Backend devuelve 422 Validation Error

**Causa:** Datos mal formados en query params

**Solución:** Verifica que CatalogoPage envía params correctamente

```javascript
// Esto es correcto:
{
  page: 1,
  size: 20,
  search: "pizza" || undefined,
  categoria_id: 1 || undefined
}
```

### Frontend no conecta al backend (CORS error)

**Causa:** Backend no corriendo en 8000

**Solución:**
```bash
# Verifica que backend está listening:
curl -i http://localhost:8000/health

# Debería devolver 200 OK
```

## 📋 CHECKLIST FINAL

- [ ] Docker PostgreSQL running
- [ ] Backend corriendo en 8000
- [ ] Frontend corriendo en 5173
- [ ] LoginForm visible en /login
- [ ] Login exitoso → redirect /catalogo
- [ ] Catálogo carga 10 productos
- [ ] Filtros responden al instante
- [ ] Paginación funciona
- [ ] Navbar muestra usuario + Salir
- [ ] Logout → redirect /login

## 🎉 ¡LISTO!

Si todo paso, DÍA 2 está **100% funcional** y listo para demostración.

**Próximos pasos:**
- DÍA 3: Mejorar grilla, más filtros, detalles productos
- DÍA 4: CRUD backend (POST, PUT, DELETE)
- DÍA 5: CRUD frontend, menú hamburguesa, soft delete UI
