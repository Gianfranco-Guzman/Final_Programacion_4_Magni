import axiosClient from './axiosClient'
import { LoginRequest, SessionResponse, Usuario, RegisterRequest, RegisterResponse } from '@models/index'

export const authApi = {
  login: async (credentials: LoginRequest): Promise<SessionResponse> => {
    const response = await axiosClient.post<SessionResponse>('/auth/login', credentials)
    return response.data
  },

  logout: async (): Promise<SessionResponse> => {
    const response = await axiosClient.post<SessionResponse>('/auth/logout')
    return response.data
  },

  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await axiosClient.post<RegisterResponse>('/auth/register', data)
    return response.data
  },

  me: async (): Promise<Usuario> => {
    const response = await axiosClient.get<Usuario>('/auth/me')
    return response.data
  },
}
