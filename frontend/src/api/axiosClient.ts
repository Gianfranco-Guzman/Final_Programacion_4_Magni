import axios from 'axios'
import { useAuthStore } from '@store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Agregar token JWT
axiosClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: Manejar 401 y mejorar mensajes de error
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Extraer mensaje amigable del backend
    const message = 
      error.response?.data?.detail || 
      error.response?.data?.message ||
      error.message ||
      'Error desconocido'
    
    // Crear error con mensaje limpio
    const cleanError = new Error(message)
    
    if (error.response?.status === 401) {
      // Token inválido o expirado - logout
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(cleanError)
  }
)

export default axiosClient
