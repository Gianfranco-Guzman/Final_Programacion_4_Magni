import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Usuario, LoginRequest, LoginResponse } from '@types/index'
import { authApi } from '@api/authApi'

interface AuthState {
  accessToken: string | null
  usuario: Usuario | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
  setUser: (user: Usuario) => void
  clearError: () => void
  fetchMe: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      usuario: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ loading: true, error: null })
        try {
          const response = await authApi.login({ email, password })
          set({
            accessToken: response.access_token,
            isAuthenticated: true,
            loading: false,
          })

          // Fetch user info
          const user = await authApi.me()
          set({ usuario: user })
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Error en login'
          set({ error: message, loading: false })
          throw err
        }
      },

      logout: () => {
        set({
          accessToken: null,
          usuario: null,
          isAuthenticated: false,
          error: null,
        })
      },

      setToken: (token: string) => {
        set({
          accessToken: token,
          isAuthenticated: true,
        })
      },

      setUser: (user: Usuario) => {
        set({ usuario: user, isAuthenticated: true })
      },

      clearError: () => {
        set({ error: null })
      },

      fetchMe: async () => {
        try {
          const user = await authApi.me()
          set({ usuario: user, isAuthenticated: true })
        } catch (err) {
          set({ isAuthenticated: false })
          throw err
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        accessToken: state.accessToken,
      }),
    }
  )
)
