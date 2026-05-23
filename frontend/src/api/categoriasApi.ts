import axiosClient from './axiosClient'
import { Categoria } from '@models/index'

export interface CategoriaCreateInput {
  nombre: string
  descripcion?: string
}

export type CategoriaUpdateInput = Partial<CategoriaCreateInput>

export const categoriasApi = {
  getCategorias: async (): Promise<Categoria[]> => {
    const response = await axiosClient.get<Categoria[]>('/categorias/')
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

  deleteCategoria: async (id: number): Promise<Categoria> => {
    const response = await axiosClient.delete<Categoria>(`/categorias/${id}`)
    return response.data
  },
}
