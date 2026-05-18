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
  created_at: string
  updated_at: string
}

export interface Ingrediente {
  id: number
  nombre: string
  descripcion?: string
  es_alergeno: boolean
  created_at: string
  updated_at: string
}

export interface ProductoIngredienteConfig {
  ingrediente_id: number
  es_removible: boolean
  es_opcional: boolean
  ingrediente: Ingrediente
}

export interface Producto {
  id: number
  nombre: string
  descripcion?: string
  precio: number
  stock_cantidad: number
  categoria_id: number
  codigo: string
  disponible: boolean
  deleted_at?: string | null
  created_at: string
  updated_at: string
  categoria?: Categoria
  ingredientes?: ProductoIngredienteConfig[]
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
