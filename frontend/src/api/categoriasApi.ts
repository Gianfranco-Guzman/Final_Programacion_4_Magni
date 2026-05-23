import axiosClient from './axiosClient'
import { Categoria } from '@models/index'

export interface CategoriasListParams {
  page?: number
  size?: number
  parent_id?: number | null
  incluir_baja?: boolean
}

export interface CategoriasListResponse {
  items: Categoria[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CategoriaCreateInput {
  nombre: string
  descripcion?: string
  parent_id?: number | null
}

export type CategoriaUpdateInput = Partial<CategoriaCreateInput>

export const categoriasApi = {
  getCategorias: async (params?: CategoriasListParams): Promise<CategoriasListResponse> => {
    const response = await axiosClient.get<CategoriasListResponse>('/categorias/', {
      params: params || {},
    })
    return response.data
  },

  getCategoriasTree: async (): Promise<Categoria[]> => {
    const response = await axiosClient.get<Categoria[]>('/categorias/tree')
    return response.data
  },

  getCategoriaById: async (id: number): Promise<Categoria> => {
    const response = await axiosClient.get<Categoria>(`/categorias/${id}`)
    return response.data
  },

  createCategoria: async (data: CategoriaCreateInput): Promise<Categoria> => {
    const response = await axiosClient.post<Categoria>('/categorias/', data)
    return response.data
  },

  updateCategoria: async (id: number, data: CategoriaUpdateInput): Promise<Categoria> => {
    const response = await axiosClient.put<Categoria>(`/categorias/${id}`, data)
    return response.data
  },

  bajaCategoria: async (id: number): Promise<Categoria> => {
    const response = await axiosClient.patch<Categoria>(`/categorias/${id}/baja`)
    return response.data
  },

  reactivarCategoria: async (id: number): Promise<Categoria> => {
    const response = await axiosClient.patch<Categoria>(`/categorias/${id}/reactivar`)
    return response.data
  },
}
