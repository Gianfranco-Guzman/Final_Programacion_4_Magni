import { useEffect, useRef } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@store/authStore'
import { ProductosProvider } from '@context/ProductosContext'
import { ProtectedRoute } from '@features/auth/ProtectedRoute'
import { LoginPage } from '@features/auth/LoginPage'
import { ListaPage } from '@pages/ListaPage'
import { NuevoProductoPage } from '@pages/NuevoProductoPage'
import { EditarProductoPage } from '@pages/EditarProductoPage'
import { CategoriasPage } from '@pages/CategoriasPage'
import { IngredientesPage } from '@pages/IngredientesPage'
import { MainLayout } from '@layouts/MainLayout'

const MANAGEMENT_ROLES = ['ADMIN', 'STOCK']

const queryClient = new QueryClient()

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
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/catalogo"
            element={
              <ProtectedRoute>
                <ProductosProvider>
                  <MainLayout>
                    <ListaPage />
                  </MainLayout>
                </ProductosProvider>
              </ProtectedRoute>
            }
          />
          <Route
            path="/productos/nuevo"
            element={
              <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
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
              <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
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
              <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
                <MainLayout>
                  <CategoriasPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/ingredientes"
            element={
              <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
                <MainLayout>
                  <IngredientesPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/catalogo" replace />} />

          <Route path="*" element={<Navigate to="/catalogo" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
