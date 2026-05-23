import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Extraer mensaje amigable del backend
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Error desconocido'

    const cleanError = new Error(message)

    if (error.response?.status === 401) {
      if (window.location.pathname !== '/login') {
        import('@store/authStore').then(({ useAuthStore }) => {
          useAuthStore.getState().logout()
        })
        window.location.href = '/login'
      }
    }

    return Promise.reject(cleanError)
  }
)

export default axiosClient
