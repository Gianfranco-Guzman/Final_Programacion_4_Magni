import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import { Spinner } from '@components/Spinner'

interface ProtectedRouteProps {
  children: React.ReactNode
}

function hasStoredToken(): boolean {
  try {
    const raw = localStorage.getItem('auth-store')
    if (!raw) return false
    const parsed = JSON.parse(raw)
    return !!parsed?.state?.accessToken
  } catch {
    return false
  }
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const loading = useAuthStore((state) => state.loading)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner />
      </div>
    )
  }

  if (!isAuthenticated && !hasStoredToken()) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
