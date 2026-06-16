import React from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import { useUIStore } from '@store/uiStore'
import { useWsStore } from '@store/wsStore'
import { useCartStore, selectCartItemCount } from '@store/cartStore'
import { useAuth } from '@hooks/useAuth'
import { Button } from '@components/Button'
import { hasAnyRole } from '@/auth/permissions'
import { CarritoDrawer } from '@features/store/carrito/CarritoDrawer'

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const usuario = useAuthStore((state) => state.usuario)
  const { logout } = useAuth()
  const { sidebarOpen, toggleSidebar, closeSidebar } = useUIStore()
  const toggleCart = useCartStore((state) => state.toggleCart)
  const cartCount = useCartStore(selectCartItemCount)
  const wsStatus = useWsStore((state) => state.status)
  const canManageCatalog = hasAnyRole(usuario?.roles, ['ADMIN', 'STOCK'])
  const isAdmin = hasAnyRole(usuario?.roles, ['ADMIN'])
  const isCajero = hasAnyRole(usuario?.roles, ['PEDIDOS'])
  const isClient = hasAnyRole(usuario?.roles, ['CLIENT'])
  const displayName = [usuario?.nombre, usuario?.apellido].filter(Boolean).join(' ')

  const wsBadge = (() => {
    if (wsStatus === 'connected') return { label: 'Tiempo real activo', className: 'bg-green-100 text-green-700' }
    if (wsStatus === 'reconnecting' || wsStatus === 'connecting') return { label: 'Reconectando tiempo real', className: 'bg-amber-100 text-amber-700' }
    if (wsStatus === 'error') return { label: 'Tiempo real con error', className: 'bg-red-100 text-red-700' }
    return { label: 'Tiempo real inactivo', className: 'bg-gray-100 text-gray-600' }
  })()

  const handleLogout = async () => {
    await logout()
    navigate('/catalogo')
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200 z-30 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={toggleSidebar}
                className="flex flex-col justify-center items-center w-10 h-10 rounded hover:bg-gray-100 gap-1.5"
                aria-label="Menú"
              >
                <span className="block w-6 h-0.5 bg-gray-700" />
                <span className="block w-6 h-0.5 bg-gray-700" />
                <span className="block w-6 h-0.5 bg-gray-700" />
              </button>
              <h1 className="text-xl font-bold text-blue-600">Food Store</h1>
            </div>

            <div className="flex items-center gap-3">
              <span className={`hidden md:inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${wsBadge.className}`}>
                {wsBadge.label}
              </span>
              {usuario && (
                <span className="text-sm text-gray-700 font-medium hidden sm:inline">{displayName}</span>
              )}
              {(isClient || !usuario) && (
                <button
                  onClick={toggleCart}
                  className="relative flex items-center justify-center w-10 h-10 rounded hover:bg-gray-100"
                  aria-label="Carrito"
                >
                  <span className="text-xl">🛒</span>
                  {cartCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-blue-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                      {cartCount > 9 ? '9+' : cartCount}
                    </span>
                  )}
                </button>
              )}
              {usuario ? (
                <Button variant="secondary" size="sm" onClick={handleLogout}>
                  Salir
                </Button>
              ) : (
                <Button variant="secondary" size="sm" onClick={() => navigate('/login')}>
                  Iniciar sesión
                </Button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40"
          onClick={closeSidebar}
        />
      )}

      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-white shadow-xl z-50 transform transition-transform duration-200 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-4 h-16 border-b border-gray-200">
          <span className="text-lg font-bold text-blue-600">Food Store</span>
          <button
            onClick={closeSidebar}
            className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-100 text-gray-500"
          >
            ✕
          </button>
        </div>

        <nav className="p-4 flex flex-col gap-2">
          <Link to="/catalogo" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
            Catálogo
          </Link>
          {isClient && (
            <>
              <Link to="/pedidos" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                Mis pedidos
              </Link>
              <Link to="/direcciones" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                Direcciones
              </Link>
            </>
          )}

          {(isAdmin || isCajero) && (
            <Link to="/cajero" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
              Panel cajero
            </Link>
          )}

          {canManageCatalog && (
            <>
              {isAdmin && (
                <>
                  <Link to="/admin/dashboard" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                    Dashboard admin
                  </Link>
                  <Link to="/admin/productos" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                    Admin productos
                  </Link>
                  <Link to="/admin/categorias" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                    Admin categorías
                  </Link>
                  <Link to="/admin/ingredientes" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                    Admin ingredientes
                  </Link>
                  <Link to="/admin/usuarios" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                    Admin usuarios
                  </Link>
                </>
              )}
              {!isAdmin && (
                <Link to="/admin/productos" onClick={closeSidebar} className="px-3 py-2 rounded text-gray-700 hover:bg-blue-50 hover:text-blue-600 font-medium">
                  Productos y disponibilidad
                </Link>
              )}
            </>
          )}
        </nav>

        {usuario && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Sesión: {displayName}</p>
            <button
              onClick={() => { closeSidebar(); void handleLogout() }}
              className="w-full text-left px-3 py-2 rounded text-red-600 hover:bg-red-50 font-medium text-sm"
            >
              Cerrar sesión
            </button>
          </div>
        )}
      </aside>

      <CarritoDrawer />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      <footer className="bg-gray-100 border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
          <p>&copy; 2026 Food Store. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  )
}
