import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@store/authStore'
import { ProtectedRoute } from '@features/auth/ProtectedRoute'
import { LoginPage } from '@features/auth/LoginPage'
import { CatalogoPage } from '@features/store/CatalogoPage'
import { MainLayout } from '@layouts/MainLayout'

const queryClient = new QueryClient()

function App() {
  const accessToken = useAuthStore((state) => state.accessToken)
  const setToken = useAuthStore((state) => state.setToken)
  const fetchMe = useAuthStore((state) => state.fetchMe)

  // Recuperar token del localStorage y validar
  useEffect(() => {
    const restoreSession = async () => {
      try {
        if (accessToken) {
          setToken(accessToken)
          await fetchMe()
        }
      } catch (error) {
        console.error('Error restaurando sesión:', error)
      }
    }

    restoreSession()
  }, [accessToken, setToken, fetchMe])

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route
            path="/catalogo"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CatalogoPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          {/* Root - redirect */}
          <Route path="/" element={<Navigate to="/catalogo" replace />} />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/catalogo" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
