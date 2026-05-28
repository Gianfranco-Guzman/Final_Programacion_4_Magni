import axiosClient from './axiosClient'
import { AdminUsuario } from '@models/index'

export interface AdminUsuariosParams {
  page?: number
  size?: number
  rol?: string
}

export interface AdminUsuariosResponse {
  items: AdminUsuario[]
  total: number
  page: number
  size: number
  pages: number
}

export interface AdminUsuarioUpdateInput {
  email?: string
  nombre?: string
  apellido?: string
  celular?: string | null
  is_active?: boolean
}

export interface AdminUsuarioRolesInput {
  roles: string[]
}

export interface AdminUsuarioActionResponse {
  message: string
  usuario: AdminUsuario
}

export const adminApi = {
  getUsuarios: async (params?: AdminUsuariosParams): Promise<AdminUsuariosResponse> => {
    const response = await axiosClient.get<AdminUsuariosResponse>('/admin/usuarios/', { params })
    return response.data
  },

  updateUsuario: async (id: number, data: AdminUsuarioUpdateInput): Promise<AdminUsuarioActionResponse> => {
    const response = await axiosClient.put<AdminUsuarioActionResponse>(`/admin/usuarios/${id}`, data)
    return response.data
  },

  bajaUsuario: async (id: number): Promise<AdminUsuarioActionResponse> => {
    const response = await axiosClient.patch<AdminUsuarioActionResponse>(`/admin/usuarios/${id}/baja`)
    return response.data
  },

  reactivarUsuario: async (id: number): Promise<AdminUsuarioActionResponse> => {
    const response = await axiosClient.patch<AdminUsuarioActionResponse>(`/admin/usuarios/${id}/reactivar`)
    return response.data
  },

  updateRoles: async (id: number, data: AdminUsuarioRolesInput): Promise<AdminUsuarioActionResponse> => {
    const response = await axiosClient.put<AdminUsuarioActionResponse>(`/admin/usuarios/${id}/roles`, data)
    return response.data
  },
}
