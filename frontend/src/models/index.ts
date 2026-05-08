export interface Usuario {
  id: number
  email: string
  nombre: string
  is_active: boolean
  created_at: string
  updated_at: string
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
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
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
