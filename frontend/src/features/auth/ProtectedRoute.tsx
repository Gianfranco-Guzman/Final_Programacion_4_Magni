import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import { Spinner } from '@components/Spinner'
import { hasAnyRole } from '@/auth/permissions'
import type { Usuario } from '@models/index'

interface ProtectedRouteProps {
  children: ReactNode
  allowedRoles?: string[]
}

function FullScreenSpinner() {
  return (
    <div className="flex items-center justify-center h-screen">
      <Spinner />
    </div>
  )
}

function getHomeRoute(usuario: Usuario | null): string {
  const roles = usuario?.roles?.map((r) => r.nombre) ?? []
  if (roles.includes('ADMIN')) return '/catalogo'
  if (roles.includes('STOCK')) return '/admin/stock'
  if (roles.includes('PEDIDOS')) return '/cajero'
  return '/catalogo'
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const location = useLocation()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const initialized = useAuthStore((state) => state.initialized)
  const loading = useAuthStore((state) => state.loading)
  const usuario = useAuthStore((state) => state.usuario)

  if (loading || !initialized) {
    return <FullScreenSpinner />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles?.length && !usuario) {
    return <FullScreenSpinner />
  }

  if (allowedRoles?.length && !hasAnyRole(usuario?.roles, allowedRoles)) {
    return <Navigate to={getHomeRoute(usuario)} replace />
  }

  return <>{children}</>
}
