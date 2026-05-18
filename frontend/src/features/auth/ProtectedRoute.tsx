import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import { Spinner } from '@components/Spinner'
import { hasAnyRole } from '@/auth/permissions'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

function FullScreenSpinner() {
  return (
    <div className="flex items-center justify-center h-screen">
      <Spinner />
    </div>
  )
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const initialized = useAuthStore((state) => state.initialized)
  const loading = useAuthStore((state) => state.loading)
  const usuario = useAuthStore((state) => state.usuario)

  if (loading || !initialized) {
    return <FullScreenSpinner />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles?.length && !usuario) {
    return <FullScreenSpinner />
  }

  if (allowedRoles?.length && !hasAnyRole(usuario?.roles, allowedRoles)) {
    return <Navigate to="/catalogo" replace />
  }

  return <>{children}</>
}
