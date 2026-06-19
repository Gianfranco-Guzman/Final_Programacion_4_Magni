import { useMutation } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import { useCartStore } from '@store/cartStore'
import { authApi } from '@api/authApi'
import { LoginRequest } from '@models/index'

export const useAuth = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login: storeLogin, logout: storeLogout } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      await storeLogin(credentials.email, credentials.password)
    },
    onSuccess: () => {
      const from = (location.state as { from?: { pathname: string; search: string } } | null)?.from
      if (from) {
        navigate(`${from.pathname}${from.search}`, { replace: true })
        return
      }
      const roles = useAuthStore.getState().usuario?.roles?.map((r) => r.nombre) ?? []
      if (roles.includes('STOCK') && !roles.includes('ADMIN')) {
        navigate('/admin/stock', { replace: true })
      } else if (roles.includes('PEDIDOS') && !roles.includes('ADMIN')) {
        navigate('/cajero', { replace: true })
      } else {
        navigate('/catalogo', { replace: true })
      }
    },
  })

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      storeLogout()
      useCartStore.getState().clearCart()
    }
  }

  return {
    login: loginMutation.mutate,
    loginLoading: loginMutation.isPending,
    loginError: loginMutation.error,
    logout,
  }
}
