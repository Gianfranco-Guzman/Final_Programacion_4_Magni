import { useEffect, useRef, type ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@store/authStore'
import { ProductosProvider } from '@context/ProductosContext'
import { ProtectedRoute } from '@features/auth/ProtectedRoute'
import { ScrollToTop } from '@components/ScrollToTop'
import { LoginPage } from '@features/auth/LoginPage'
import { ListaPage } from '@pages/ListaPage'
import { NuevoProductoPage } from '@pages/NuevoProductoPage'
import { EditarProductoPage } from '@pages/EditarProductoPage'
import { CategoriasPage } from '@pages/CategoriasPage'
import { DireccionesPage } from '@pages/DireccionesPage'
import { IngredientesPage } from '@pages/IngredientesPage'
import { AdminProductosPage } from '@pages/AdminProductosPage'
import { AdminDashboardPage } from '@pages/AdminDashboardPage'
import { AdminUsuariosPage } from '@pages/AdminUsuariosPage'
import { MisPedidosPage } from '@pages/MisPedidosPage'
import { PedidoDetallePage } from '@pages/PedidoDetallePage'
import { CajeroPage } from '@pages/CajeroPage'
import { AdminStockPage } from '@pages/AdminStockPage'
import { CheckoutPage } from '@features/store/checkout/CheckoutPage'
import { MainLayout } from '@layouts/MainLayout'

const MANAGEMENT_ROLES = ['ADMIN', 'STOCK']
const ADMIN_ROLES = ['ADMIN']
const CAJERO_ROLES = ['ADMIN', 'PEDIDOS']

const queryClient = new QueryClient()

function RoleGuard({ children }: { children: ReactNode }) {
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const initialized = useAuthStore((s) => s.initialized)
  const usuario = useAuthStore((s) => s.usuario)

  if (!initialized || !isAuthenticated || !usuario) return <>{children}</>

  const roles = usuario.roles?.map((r) => r.nombre) ?? []
  const isAdmin = roles.includes('ADMIN')

  if (!isAdmin && roles.includes('PEDIDOS') && location.pathname !== '/cajero' && !location.pathname.startsWith('/pedidos/')) {
    return <Navigate to="/cajero" replace />
  }
  if (!isAdmin && roles.includes('STOCK') && location.pathname !== '/admin/stock') {
    return <Navigate to="/admin/stock" replace />
  }

  return <>{children}</>
}

function App() {
  const initializeSession = useAuthStore((state) => state.initializeSession)
  const initializedRef = useRef(false)

  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true

    initializeSession().catch((error) => {
      console.error('Error restaurando sesión:', error)
    })
  }, [initializeSession])

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ScrollToTop />
        <RoleGuard>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/catalogo"
            element={
              <ProductosProvider>
                <MainLayout>
                  <ListaPage />
                </MainLayout>
              </ProductosProvider>
            }
          />
          <Route
            path="/productos/nuevo"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <ProductosProvider>
                  <MainLayout>
                    <NuevoProductoPage />
                  </MainLayout>
                </ProductosProvider>
              </ProtectedRoute>
            }
          />
          <Route
            path="/productos/editar/:id"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <ProductosProvider>
                  <MainLayout>
                    <EditarProductoPage />
                  </MainLayout>
                </ProductosProvider>
              </ProtectedRoute>
            }
          />
          <Route
            path="/categorias"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <Navigate to="/admin/categorias" replace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/categorias"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <MainLayout>
                  <CategoriasPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/direcciones"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <DireccionesPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/ingredientes"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <Navigate to="/admin/ingredientes" replace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/ingredientes"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <MainLayout>
                  <IngredientesPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <MainLayout>
                  <AdminDashboardPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/productos"
            element={
              <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
                <MainLayout>
                  <AdminProductosPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/usuarios"
            element={
              <ProtectedRoute allowedRoles={ADMIN_ROLES}>
                <MainLayout>
                  <AdminUsuariosPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/pedidos"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <MisPedidosPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/pedidos/:pedidoId"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PedidoDetallePage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/cajero"
            element={
              <ProtectedRoute allowedRoles={CAJERO_ROLES}>
                <MainLayout>
                  <CajeroPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/stock"
            element={
              <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
                <MainLayout>
                  <AdminStockPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/checkout"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CheckoutPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/catalogo" replace />} />

          <Route path="*" element={<Navigate to="/catalogo" replace />} />
        </Routes>
        </RoleGuard>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
