import { useEffect } from 'react'
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

const queryClient = new QueryClient()

function App() {
  const accessToken = useAuthStore((state) => state.accessToken)
  const setToken = useAuthStore((state) => state.setToken)
  const fetchMe = useAuthStore((state) => state.fetchMe)
  const setLoading = useAuthStore((state) => state.setLoading)

  useEffect(() => {
    const restoreSession = async () => {
      if (!accessToken) return

      setLoading(true)
      try {
        setToken(accessToken)
        await fetchMe()
      } catch (error) {
        console.error('Error restaurando sesión:', error)
      } finally {
        setLoading(false)
      }
    }

    restoreSession()
  }, [accessToken, setToken, fetchMe, setLoading])

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
              <ProtectedRoute>
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
              <ProtectedRoute>
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
              <ProtectedRoute>
                <MainLayout>
                  <CategoriasPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/ingredientes"
            element={
              <ProtectedRoute>
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
