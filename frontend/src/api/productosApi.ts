import axiosClient from './axiosClient'
import { Producto } from '@types/index'

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
}
