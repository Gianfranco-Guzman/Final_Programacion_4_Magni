import axiosClient from './axiosClient'
import { Ingrediente } from '@models/index'

export interface IngredienteCreateInput {
  nombre: string
  descripcion?: string
  es_alergeno: boolean
}

export type IngredienteUpdateInput = Partial<IngredienteCreateInput>

export const ingredientesApi = {
  getIngredientes: async (): Promise<Ingrediente[]> => {
    const response = await axiosClient.get<Ingrediente[]>('/ingredientes/')
    return response.data
  },

  getIngredienteById: async (id: number): Promise<Ingrediente> => {
    const response = await axiosClient.get<Ingrediente>(`/ingredientes/${id}`)
    return response.data
  },

  createIngrediente: async (data: IngredienteCreateInput): Promise<Ingrediente> => {
    const response = await axiosClient.post<Ingrediente>('/ingredientes/', data)
    return response.data
  },

  updateIngrediente: async (id: number, data: IngredienteUpdateInput): Promise<Ingrediente> => {
    const response = await axiosClient.put<Ingrediente>(`/ingredientes/${id}`, data)
    return response.data
  },

  bajaIngrediente: async (id: number): Promise<Ingrediente> => {
    const response = await axiosClient.patch<Ingrediente>(`/ingredientes/${id}/baja`)
    return response.data
  },

  reactivarIngrediente: async (id: number): Promise<Ingrediente> => {
    const response = await axiosClient.patch<Ingrediente>(`/ingredientes/${id}/reactivar`)
    return response.data
  },
}
