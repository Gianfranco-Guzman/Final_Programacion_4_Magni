Necesito adaptar un proyecto YA EXISTENTE (frontend + backend) para incorporar correctamente las nuevas entidades Categoria e Ingrediente, respetando COMPLETAMENTE la arquitectura, estructura, convenciones y forma de programar actual del proyecto. NO quiero refactors innecesarios, NO cambiar patrones existentes y NO romper funcionalidades actuales.

IMPORTANTE:

- El proyecto ya tiene una estructura modular implementada.
- Ya existen carpetas creadas para Categoria e Ingrediente.
- La implementación nueva debe seguir EXACTAMENTE el mismo patrón que usan los módulos existentes.
- Mantener naming conventions, estructura de archivos, estilo visual y flujo actual.
- No inventar nuevas arquitecturas ni patrones distintos.
- Todo debe integrarse sobre lo existente.

========================================
ESTRUCTURA ACTUAL BACKEND
========================================

Backend modular tipo:

modules/
auth/
productos/
Categoria/
categoriaModel.py
categoriaSchema.py
categoriaService.py
categoriaRouter.py
Ingrediente/
ingredienteModel.py
ingredienteSchema.py
ingredienteService.py
ingredienteRouter.py

La arquitectura actual trabaja separando:

- Model
- Schema
- Service
- Router

Debe mantenerse exactamente igual.

========================================
OBJETIVO FUNCIONAL
========================================

Actualmente:

- Los ingredientes de un producto se escriben manualmente dentro de la descripción.
- Eso está MAL y debe corregirse.

Nuevo comportamiento requerido:

- Los ingredientes deben existir previamente en la base de datos.
- Un Producto debe seleccionar Ingredientes desde una lista existente.
- Un Producto debe pertenecer obligatoriamente a una Categoria.
- No se deben escribir ingredientes manualmente en texto libre.

Flujo correcto:

1. Crear Categorias
2. Crear Ingredientes
3. Recién después crear Productos usando:
   - una Categoria existente
   - una lista de Ingredientes existentes

========================================
BACKEND - REQUERIMIENTOS
========================================

Implementar/adaptar:

## Categoria

CRUD completo:

- crear categoria
- listar categorias
- obtener categoria por id
- editar categoria
- eliminar categoria (soft delete si el proyecto ya usa eso)

Campos:

- id
- nombre
- descripcion
- imagen_url si ya está contemplado

Validaciones:

- nombre único
- no permitir categorías vacías

========================================

## Ingrediente

CRUD completo:

- crear ingrediente
- listar ingredientes
- obtener ingrediente por id
- editar ingrediente
- eliminar ingrediente

Campos:

- id
- nombre
- descripcion
- es_alergeno

Validaciones:

- nombre único
- evitar duplicados

========================================

## Producto

ADAPTAR módulo existente de productos.

Actualmente:

- ingredientes están en descripcion

Nuevo comportamiento:

- Producto debe relacionarse con:
  - Categoria
  - Ingredientes

Agregar relaciones necesarias.

Producto debe:

- requerir categoria_id
- requerir lista de ingredientes

NO usar ingredientes como texto.

========================================
RELACIONES
========================================

Categoria:

- una categoria tiene muchos productos

Ingrediente:

- un producto puede tener muchos ingredientes
- un ingrediente puede estar en muchos productos

Implementar relación many-to-many correctamente.

NO romper modelos actuales.

========================================
BASE DE DATOS
========================================

Adaptar:

- modelos
- relaciones
- foreign keys
- tablas intermedias necesarias
- migraciones/alembic

Mantener compatibilidad con la base existente.

NO borrar datos actuales.

========================================
SCHEMAS
========================================

Actualizar schemas de Producto:

- requests
- responses
- validaciones

Producto response debe devolver:

- categoria
- lista de ingredientes

Ejemplo esperado:

{
"id": 1,
"nombre": "Pizza Especial",
"categoria": {
"id": 2,
"nombre": "Pizzas"
},
"ingredientes": [
{
"id": 1,
"nombre": "Queso"
},
{
"id": 2,
"nombre": "Tomate"
}
]
}

========================================
SERVICES
========================================

Toda la lógica debe mantenerse en Services.

Validar:

- categoria existente
- ingredientes existentes
- ids válidos
- evitar ingredientes repetidos

No poner lógica de negocio en Router. NO hacer commits en el service, los commit se deben hacer en el uow

========================================
ROUTERS
========================================

Mantener el mismo estilo de endpoints existente.

Agregar:

- endpoints Categoria
- endpoints Ingrediente
- adaptar endpoints Producto

No cambiar rutas actuales innecesariamente.

========================================
FRONTEND - REQUERIMIENTOS
========================================

Adaptar el frontend existente SIN romper el diseño actual.

IMPORTANTE:

- Mantener exactamente la misma estructura visual.
- Mantener mismos componentes, estilos y flujo UX.
- NO inventar pantallas nuevas innecesarias.
- NO cambiar el layout general.
- Todo debe verse integrado naturalmente al sistema existente.

========================================
FRONTEND - CATEGORIAS
========================================

Agregar:

- listado de categorias
- formulario crear categoria
- editar categoria
- eliminar categoria

Usar mismos componentes visuales existentes:

- tablas
- modales
- inputs
- botones
- alerts
- toasts

========================================
FRONTEND - INGREDIENTES
========================================

Agregar:

- listado ingredientes
- crear ingrediente
- editar ingrediente
- eliminar ingrediente

Campo:

- es_alergeno con checkbox/switch siguiendo UI actual

========================================
FRONTEND - PRODUCTOS
========================================

Modificar formulario de Producto existente.

Actualmente:

- ingredientes van en descripcion

Nuevo comportamiento:

- Categoria:
  select desplegable
- Ingredientes:
  multiselect / checkboxes / selector múltiple
  usando ingredientes existentes de la DB

La descripcion del producto:

- NO debe usarse para ingredientes
- solo descripción real del producto

========================================
FORMULARIO PRODUCTO
========================================

Debe:

- cargar categorias desde API
- cargar ingredientes desde API
- validar selección obligatoria
- permitir seleccionar múltiples ingredientes

Mantener misma estética visual.

========================================
API INTEGRATION
========================================

Adaptar:

- services
- hooks
- requests
- DTOs
- tipados/interfaces si existen

Mantener patrón actual del frontend.

========================================
IMPORTANTE
========================================

NO:

- cambiar arquitectura
- refactorizar todo
- inventar patrones nuevos
- cambiar nombres innecesariamente
- romper endpoints existentes
- romper frontend existente
- cambiar diseño visual general

SÍ:

- integrarlo respetando el proyecto actual
- reutilizar componentes existentes
- seguir el mismo patrón de código
- mantener consistencia completa

========================================
OBJETIVO FINAL
========================================

El sistema debe permitir:

1. Crear Categorias
2. Crear Ingredientes
3. Crear Productos seleccionando:
   - una Categoria
   - múltiples Ingredientes existentes

Todo integrado correctamente entre:

- base de datos
- backend
- frontend

Y respetando completamente la estructura y estilo ya existente del proyecto.
