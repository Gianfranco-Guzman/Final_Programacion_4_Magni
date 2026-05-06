import React from 'react'
import { useAuthStore } from '@store/authStore'
import { useAuth } from '@hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import { Button } from '@components/Button'

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const usuario = useAuthStore((state) => state.usuario)
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-blue-600">🍕 Food Store</h1>
            </div>

            {/* Center - Links */}
            <div className="flex-1 flex justify-center gap-8">
              <a
                href="/catalogo"
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                Catálogo
              </a>
            </div>

            {/* Right - User & Logout */}
            <div className="flex items-center gap-4">
              {usuario && (
                <div className="text-sm text-gray-700">
                  <span className="font-medium">{usuario.nombre}</span>
                </div>
              )}
              <Button variant="secondary" size="sm" onClick={handleLogout}>
                Salir
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-100 border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
          <p>&copy; 2026 Food Store. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  )
}
