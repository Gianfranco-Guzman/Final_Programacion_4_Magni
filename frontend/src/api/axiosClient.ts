import axios, { InternalAxiosRequestConfig } from 'axios'

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api/v1` : 'http://localhost:8000/api/v1')

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

let isRefreshing = false
let pendingQueue: Array<{ resolve: () => void; reject: (err: unknown) => void }> = []

const processQueue = (error: unknown) => {
  pendingQueue.forEach((p) => (error ? p.reject(error) : p.resolve()))
  pendingQueue = []
}

const doLogout = () => {
  import('@store/authStore').then(({ useAuthStore }) => {
    useAuthStore.getState().logout()
  })
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const rawDetail = error.response?.data?.detail
    const message =
      (Array.isArray(rawDetail)
        ? rawDetail.map((e: { msg?: string }) => e.msg ?? String(e)).join(', ')
        : rawDetail) ||
      error.response?.data?.message ||
      error.message ||
      'Error desconocido'

    const cleanError = new Error(message)
    const config = error.config as RetryableConfig
    const isSessionProbe = config?.url?.includes('/auth/me')
    const isRefreshAttempt = config?.url?.includes('/auth/refresh')

    if (error.response?.status === 401 && !isSessionProbe && !isRefreshAttempt && !config?._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({
            resolve: () => resolve(axiosClient(config)),
            reject: (err) => reject(err),
          })
        })
      }

      config._retry = true
      isRefreshing = true

      try {
        await axiosClient.post('/auth/refresh')
        processQueue(null)
        return axiosClient(config)
      } catch {
        processQueue(new Error('Sesión expirada'))
        doLogout()
        return Promise.reject(cleanError)
      } finally {
        isRefreshing = false
      }
    }

    if (error.response?.status === 401 && !isSessionProbe) {
      doLogout()
    }

    return Promise.reject(cleanError)
  },
)

export default axiosClient
