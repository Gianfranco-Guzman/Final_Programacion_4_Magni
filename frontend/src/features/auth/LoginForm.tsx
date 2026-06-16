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
    } else if (password.length < 8) {
      newErrors.password = 'Contraseña debe tener al menos 8 caracteres'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

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
            placeholder="admin@foodstore.com"
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

        <div className="mt-6">
          <p className="text-xs text-gray-400 text-center mb-3">Usuarios de prueba</p>
          <div className="grid grid-cols-2 gap-2">
             {[
                { label: 'Admin', email: 'admin@foodstore.com', password: 'Admin1234!', color: 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100' },
                { label: 'Cliente', email: 'cliente@foodstore.com', password: 'cliente123', color: 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100' },
                { label: 'Stock', email: 'stock@foodstore.com', password: 'stock123', color: 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100' },
                { label: 'Pedidos', email: 'pedidos@foodstore.com', password: 'pedidos123', color: 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100' },
              ].map((u) => (
              <button
                key={u.email}
                type="button"
                onClick={() => { setEmail(u.email); setPassword(u.password); setErrors({}); setDisplayError(null) }}
                className={`border rounded-lg px-3 py-2 text-left transition-colors ${u.color}`}
              >
                <p className="font-semibold text-xs">{u.label}</p>
                <p className="font-mono text-xs opacity-75 truncate">{u.email}</p>
              </button>
            ))}
          </div>
        </div>
      </Card>
    </div>
  )
}
