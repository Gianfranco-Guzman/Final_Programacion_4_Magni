import axiosClient from './axiosClient'
import { Producto } from '@models/index'

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface GetProductosParams {
  page?: number
  size?: number
  categoria_id?: number | null
  search?: string
  disponible?: boolean
  incluir_baja?: boolean
}

export interface ProductoCreateInput {
  nombre: string
  descripcion?: string
  precio: number
  stock_cantidad: number
  categoria_id: number
  codigo: string
  ingredientes_ids: number[]
}

export interface ProductoUpdateInput {
  nombre?: string
  descripcion?: string
  precio?: number
  stock_cantidad?: number
  categoria_id?: number
  codigo?: string
  ingredientes_ids?: number[]
}

export const productosApi = {
  getProductos: async (params?: GetProductosParams): Promise<PaginatedResponse<Producto>> => {
    const response = await axiosClient.get<PaginatedResponse<Producto>>(
      '/productos/',
      { params: params || {} }
    )
    return response.data
  },

  getProductoById: async (id: number): Promise<Producto> => {
    const response = await axiosClient.get<Producto>(`/productos/${id}`)
    return response.data
  },

  getCategorias: async () => {
    const response = await axiosClient.get('/productos/categorias/')
    return response.data
  },

  createProducto: async (data: ProductoCreateInput): Promise<Producto> => {
    const response = await axiosClient.post<Producto>('/productos/', data)
    return response.data
  },

  updateProducto: async (id: number, data: ProductoUpdateInput): Promise<Producto> => {
    const response = await axiosClient.put<Producto>(`/productos/${id}`, data)
    return response.data
  },

  darDeBajaProducto: async (id: number): Promise<Producto> => {
    const response = await axiosClient.patch<Producto>(`/productos/${id}/baja`)
    return response.data
  },

  reactivarProducto: async (id: number): Promise<Producto> => {
    const response = await axiosClient.patch<Producto>(`/productos/${id}/reactivar`)
    return response.data
  },

  exportarProductos: async (search?: string): Promise<Blob> => {
    const params: Record<string, string> = {}
    if (search) {
      params.search = search
    }
    const response = await axiosClient.get('/productos/exportar', {
      params,
      responseType: 'blob',
    })
    return response.data
  },
}
