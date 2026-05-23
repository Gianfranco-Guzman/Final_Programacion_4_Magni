import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import { authApi } from '@api/authApi'
import { LoginRequest, RegisterRequest } from '@models/index'

export const useAuth = () => {
  const navigate = useNavigate()
  const { login: storeLogin, logout: storeLogout } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      await storeLogin(credentials.email, credentials.password)
    },
    onSuccess: () => {
      navigate('/catalogo')
    },
  })

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterRequest) => {
      return await authApi.register(data)
    },
    onSuccess: () => {
      navigate('/login')
    },
  })

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      storeLogout()
    }
  }

  return {
    login: loginMutation.mutate,
    loginLoading: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    registerLoading: registerMutation.isPending,
    registerError: registerMutation.error,
    logout,
  }
}
