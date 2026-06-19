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
  unidad_medida: UnidadMedida
  stock_actual: number
  stock_minimo: number
  costo_unitario: number
  permite_fraccion: boolean
  deleted_at?: string | null
  created_at: string
  updated_at: string
}

export type UnidadMedida = 'UNIDAD' | 'GRAMO' | 'KILOGRAMO' | 'MILILITRO' | 'LITRO'

export type TipoProducto = 'FABRICADO' | 'REVENTA'

export interface ProductoDetalleConfig {
  id?: number | null
  ingrediente_id: number
  cantidad: number
  unidad_medida: UnidadMedida
  orden: number
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
  precio_venta: number
  precio_costo_calculado: number
  descuento_porcentaje: number
  precio_final: number
  tipo_producto: TipoProducto
  stock_disponible_calculado: number
  puede_fabricarse: boolean
  categoria_principal_id?: number | null
  codigo: string
  disponible: boolean
  imagenes_url?: string[] | null
  unidad_venta_id?: number | null
  deleted_at?: string | null
  created_at: string
  updated_at: string
  categorias?: ProductoCategoriaConfig[]
  ingredientes?: ProductoDetalleConfig[]
}

export interface DetallePedido {
  id: number
  pedido_id: number
  producto_id: number
  cantidad: number
  precio_unitario_snapshot: number
  nombre_producto_snapshot: string
  subtotal: number
  personalizacion?: number[] | null
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

export type TipoEntrega = 'domicilio' | 'sucursal'

export interface Pedido {
  id: number
  usuario_id: number
  tipo_entrega: TipoEntrega
  direccion_entrega_id: number | null
  forma_pago_id: number
  estado_actual: string
  subtotal?: number
  descuento?: number
  costo_envio?: number
  total: number
  notas: string | null
  created_at: string
  updated_at: string
  detalles?: DetallePedido[]
  historial?: HistorialEstadoPedido[]
}

export interface FormaPago {
  id: number
  codigo?: string | null
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
  access_token?: string | null
  refresh_token?: string | null
  token_type?: string
  expires_in?: number | null
  refresh_expires_in?: number | null
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

export interface Pago {
  id: number
  pedido_id: number
  mp_payment_id?: number | null
  mp_status: string
  mp_status_detail?: string | null
  transaction_amount: number
  payment_method_id?: string | null
  external_reference: string
  idempotency_key: string
  created_at: string
  updated_at: string
}
