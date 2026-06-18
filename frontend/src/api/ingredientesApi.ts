import axiosClient from './axiosClient'
import { Ingrediente, UnidadMedida } from '@models/index'

export interface MovimientoEntrada {
  id: number
  ingrediente_id: number
  tipo_movimiento: string
  cantidad: number
  stock_anterior: number
  stock_posterior: number
  observacion: string | null
  created_at: string
  movimiento_referencia_id: number | null
  ya_corregido_total: number
}

export interface IngredienteCreateInput {
  nombre: string
  descripcion?: string
  es_alergeno: boolean
  unidad_medida: UnidadMedida
  stock_actual: number
  stock_minimo: number
  costo_unitario: number
  permite_fraccion: boolean
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

  cargarStock: async (id: number, data: { cantidad: number; unidad_entrada: string }): Promise<Ingrediente> => {
    const response = await axiosClient.patch<Ingrediente>(`/ingredientes/${id}/cargar-stock`, data)
    return response.data
  },

  getMisCargas: async (): Promise<MovimientoEntrada[]> => {
    const response = await axiosClient.get<MovimientoEntrada[]>('/ingredientes/mis-cargas')
    return response.data
  },

  corregirEntrada: async (data: {
    movimiento_id: number
    cantidad: number
    unidad_entrada: string
    motivo: string
  }): Promise<MovimientoEntrada> => {
    const response = await axiosClient.post<MovimientoEntrada>('/ingredientes/movimientos/corregir', data)
    return response.data
  },
}
