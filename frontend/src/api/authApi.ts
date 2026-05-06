import axiosClient from './axiosClient'
import { LoginRequest, LoginResponse, Usuario, RegisterRequest, RegisterResponse } from '@types/index'

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await axiosClient.post<LoginResponse>('/auth/login', credentials)
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
