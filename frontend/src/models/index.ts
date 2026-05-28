import { RoleInfo } from '@/auth/permissions'

export interface Usuario {
  id: number
  email: string
  nombre: string
  apellido: string
  celular?: string | null
  is_active: boolean
  roles: RoleInfo[]
}

export interface AdminUsuario extends Usuario {
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export interface DireccionEntrega {
  id: number
  usuario_id: number
  etiqueta?: string | null
  linea1: string
  linea2?: string | null
  ciudad: string
  latitud?: number | null
  longitud?: number | null
  es_principal: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export interface CartItem {
  producto_id: number
  cantidad: number
}

export interface Categoria {
  id: number
  nombre: string
  descripcion?: string
  parent_id?: number | null
  deleted_at?: string | null
  created_at: string
  updated_at: string
  subcategorias?: Categoria[]
}

export interface Ingrediente {
  id: number
  nombre: string
  descripcion?: string
  es_alergeno: boolean
  deleted_at?: string | null
  created_at: string
  updated_at: string
}

export interface ProductoIngredienteConfig {
  ingrediente_id: number
  es_removible: boolean
  es_opcional: boolean
  ingrediente: Ingrediente
}

export interface ProductoCategoriaConfig {
  categoria_id: number
  es_principal: boolean
  categoria: Categoria
}

export interface Producto {
  id: number
  nombre: string
  descripcion?: string
  precio: number
  stock_cantidad: number
  categoria_principal_id?: number | null
  codigo: string
  disponible: boolean
  deleted_at?: string | null
  created_at: string
  updated_at: string
  categorias?: ProductoCategoriaConfig[]
  ingredientes?: ProductoIngredienteConfig[]
}

export interface DetallePedido {
  id: number
  pedido_id: number
  producto_id: number
  cantidad: number
  precio_unitario_snapshot: number
  nombre_producto_snapshot: string
  subtotal: number
}

export interface HistorialEstadoPedido {
  id: number
  pedido_id: number
  estado_anterior: string | null
  estado_nuevo: string
  fecha: string
  usuario_id: number
  observacion: string | null
}

export interface Pedido {
  id: number
  usuario_id: number
  direccion_entrega_id: number
  forma_pago_id: number
  estado_actual: string
  total: number
  notas: string | null
  created_at: string
  updated_at: string
  detalles?: DetallePedido[]
  historial?: HistorialEstadoPedido[]
}

export interface FormaPago {
  id: number
  nombre: string
  descripcion?: string | null
  activo: boolean
  created_at: string
  updated_at: string
}

export interface EstadoPedido {
  id: number
  nombre: string
  descripcion?: string | null
  orden: number
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SessionResponse {
  message: string
}

export interface RegisterRequest {
  email: string
  password: string
  nombre: string
  apellido: string
  celular?: string | null
}

export interface RegisterResponse {
  id: number
  email: string
  nombre: string
  apellido: string
  celular?: string | null
  is_active: boolean
}
