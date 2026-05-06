import React, { useState, useEffect } from 'react'
import { useAuth } from '@hooks/useAuth'
import { Input } from '@components/Input'
import { Button } from '@components/Button'
import { Card } from '@components/Card'

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [displayError, setDisplayError] = useState<string | null>(null)

  const { login, loginLoading, loginError } = useAuth()

  // Capturar error y guardarlo en estado LOCAL (no se limpia automáticamente)
  useEffect(() => {
    if (loginError) {
      const errorMessage = loginError instanceof Error ? loginError.message : 'Error en login'
      setDisplayError(errorMessage)
      console.error('❌ Error de Login:', errorMessage)
    }
  }, [loginError])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!email) {
      newErrors.email = 'Email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Email inválido'
    }

    if (!password) {
      newErrors.password = 'Contraseña es requerida'
    } else if (password.length < 3) {
      newErrors.password = 'Contraseña debe tener al menos 3 caracteres'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    // Limpiar error ANTES de intentar de nuevo
    setDisplayError(null)
    login({ email, password })
  }

  const getErrorMessage = (): string | null => {
    return displayError
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-800">Food Store</h1>
          <p className="text-gray-600 mt-1">Ingresa a tu cuenta</p>
        </div>

        {getErrorMessage() && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{getErrorMessage()}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="admin@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={errors.email}
          />

          <Input
            label="Contraseña"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={errors.password}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={loginLoading}
            className="w-full"
          >
            {loginLoading ? 'Ingresando...' : 'Ingresar'}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Usuario de prueba:</p>
          <p className="font-mono text-xs mt-2">
            admin@example.com / admin123
          </p>
        </div>
      </Card>
    </div>
  )
}
