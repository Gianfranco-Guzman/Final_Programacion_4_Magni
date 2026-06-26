import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '@api/authApi'
import { Button } from '@components/Button'
import { Card } from '@components/Card'
import { Input } from '@components/Input'

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState({ nombre: '', apellido: '', email: '', password: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [serverError, setServerError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const validate = (): boolean => {
    const next: Record<string, string> = {}
    if (!form.nombre.trim()) next.nombre = 'El nombre es requerido'
    if (!form.apellido.trim()) next.apellido = 'El apellido es requerido'
    if (!form.email.trim()) next.email = 'El email es requerido'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = 'Email inválido'
    if (!form.password) next.password = 'La contraseña es requerida'
    else if (form.password.length < 8) next.password = 'Mínimo 8 caracteres'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleChange = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setServerError('')
    setIsLoading(true)
    try {
      await authApi.register({
        nombre: form.nombre.trim(),
        apellido: form.apellido.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      navigate('/login', { state: { registered: true } })
    } catch (err: unknown) {
      setServerError(err instanceof Error ? err.message : 'No se pudo crear la cuenta. Intentá de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-800">Food Store</h1>
          <p className="text-gray-600 mt-1">Creá tu cuenta</p>
        </div>

        {serverError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{serverError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Nombre"
              type="text"
              placeholder="Juan"
              value={form.nombre}
              onChange={handleChange('nombre')}
              error={errors.nombre}
            />
            <Input
              label="Apellido"
              type="text"
              placeholder="Pérez"
              value={form.apellido}
              onChange={handleChange('apellido')}
              error={errors.apellido}
            />
          </div>
          <Input
            label="Email"
            type="email"
            placeholder="juan@email.com"
            value={form.email}
            onChange={handleChange('email')}
            error={errors.email}
          />
          <Input
            label="Contraseña"
            type="password"
            placeholder="Mínimo 8 caracteres"
            value={form.password}
            onChange={handleChange('password')}
            error={errors.password}
          />
          <Button type="submit" variant="primary" size="lg" isLoading={isLoading} className="w-full">
            {isLoading ? 'Creando cuenta...' : 'Crear cuenta'}
          </Button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            ¿Ya tenés cuenta?{' '}
            <a href="/login" className="text-blue-600 hover:underline font-medium">
              Ingresá
            </a>
          </p>
        </div>
      </Card>
    </div>
  )
}
