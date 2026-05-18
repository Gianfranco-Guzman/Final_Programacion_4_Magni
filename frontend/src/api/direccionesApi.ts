import axiosClient from './axiosClient'
import { DireccionEntrega } from '@models/index'

export interface DireccionEntregaInput {
  etiqueta?: string
  linea1: string
  linea2?: string
  ciudad: string
  latitud?: number | null
  longitud?: number | null
  es_principal?: boolean
}

export type DireccionEntregaUpdateInput = Partial<DireccionEntregaInput>

export const direccionesApi = {
  getDirecciones: async (): Promise<DireccionEntrega[]> => {
    const response = await axiosClient.get<DireccionEntrega[]>('/direcciones/')
    return response.data
  },

  createDireccion: async (data: DireccionEntregaInput): Promise<DireccionEntrega> => {
    const response = await axiosClient.post<DireccionEntrega>('/direcciones/', data)
    return response.data
  },

  updateDireccion: async (id: number, data: DireccionEntregaUpdateInput): Promise<DireccionEntrega> => {
    const response = await axiosClient.put<DireccionEntrega>(`/direcciones/${id}`, data)
    return response.data
  },

  deleteDireccion: async (id: number): Promise<DireccionEntrega> => {
    const response = await axiosClient.delete<DireccionEntrega>(`/direcciones/${id}`)
    return response.data
  },

  marcarPrincipal: async (id: number): Promise<DireccionEntrega> => {
    const response = await axiosClient.patch<DireccionEntrega>(`/direcciones/${id}/principal`)
    return response.data
  },
}
