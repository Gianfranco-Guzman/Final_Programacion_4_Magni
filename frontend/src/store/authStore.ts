import { create } from 'zustand'
import { Usuario } from '@models/index'
import { authApi } from '@api/authApi'

interface AuthState {
  usuario: Usuario | null
  isAuthenticated: boolean
  initialized: boolean
  loading: boolean
  error: string | null

  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: Usuario) => void
  setLoading: (loading: boolean) => void
  clearError: () => void
  fetchMe: () => Promise<void>
  initializeSession: () => Promise<void>
}

export const useAuthStore = create<AuthState>()((set) => ({
  usuario: null,
  isAuthenticated: false,
  initialized: false,
  loading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ loading: true, error: null })
    try {
      await authApi.login({ email, password })
      const user = await authApi.me()
      set({
        usuario: user,
        isAuthenticated: true,
        initialized: true,
        loading: false,
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error en login'
      set({
        usuario: null,
        isAuthenticated: false,
        initialized: true,
        error: message,
        loading: false,
      })
      throw err
    }
  },

  logout: () => {
    set({
      usuario: null,
      isAuthenticated: false,
      initialized: true,
      loading: false,
      error: null,
    })
  },

  setUser: (user: Usuario) => {
    set({ usuario: user, isAuthenticated: true, initialized: true })
  },

  setLoading: (loading: boolean) => {
    set({ loading })
  },

  clearError: () => {
    set({ error: null })
  },

  fetchMe: async () => {
    try {
      const user = await authApi.me()
      set({ usuario: user, isAuthenticated: true, initialized: true })
    } catch (err) {
      set({ usuario: null, isAuthenticated: false, initialized: true })
      throw err
    }
  },

  initializeSession: async () => {
    set({ loading: true, error: null })
    try {
      const user = await authApi.me()
      set({
        usuario: user,
        isAuthenticated: true,
        initialized: true,
        loading: false,
      })
    } catch {
      set({
        usuario: null,
        isAuthenticated: false,
        initialized: true,
        loading: false,
      })
    }
  },
}))
