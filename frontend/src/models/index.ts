import { RoleInfo } from '@/auth/permissions'

export interface Usuario {
  id: number
  email: string
  nombre: string
  is_active: boolean
  roles: RoleInfo[]
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

export interface Producto {
  id: number
  nombre: string
  descripcion?: string
  precio: number
  stock_cantidad: number
  categoria_id: number
  codigo: string
  deleted_at?: string | null
  created_at: string
  updated_at: string
  categoria?: Categoria
  ingredientes?: Ingrediente[]
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
}

export interface RegisterResponse {
  id: number
  email: string
  nombre: string
  is_active: boolean
}
