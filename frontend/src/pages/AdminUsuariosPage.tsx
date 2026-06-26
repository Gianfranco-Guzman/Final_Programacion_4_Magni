import React, { useMemo, useState } from 'react'
import { Button } from '@components/Button'
import { Spinner } from '@components/Spinner'
import {
  useAdminUsuarios,
  useBajaAdminUsuario,
  useCreateAdminUsuario,
  useReactivarAdminUsuario,
  useUpdateAdminUsuario,
  useUpdateAdminUsuarioRoles,
} from '@hooks/useAdmin'
import { AdminUsuario } from '@models/index'

const AVAILABLE_ROLES = ['ADMIN', 'CLIENT', 'STOCK', 'PEDIDOS'] as const

type UserRole = (typeof AVAILABLE_ROLES)[number]

interface FormState {
  email: string
  nombre: string
  apellido: string
  celular: string
  is_active: boolean
  roles: UserRole[]
}

interface CreateFormState {
  email: string
  password: string
  nombre: string
  apellido: string
  celular: string
  roles: UserRole[]
}

const emptyForm: FormState = {
  email: '',
  nombre: '',
  apellido: '',
  celular: '',
  is_active: true,
  roles: ['CLIENT'],
}

const emptyCreateForm: CreateFormState = {
  email: '',
  password: '',
  nombre: '',
  apellido: '',
  celular: '',
  roles: ['CLIENT'],
}

export const AdminUsuariosPage: React.FC = () => {
  const [page, setPage] = useState(1)
  const [roleFilter, setRoleFilter] = useState('')
  const [editingUser, setEditingUser] = useState<AdminUsuario | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [formError, setFormError] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [createForm, setCreateForm] = useState<CreateFormState>(emptyCreateForm)
  const [createError, setCreateError] = useState('')

  const queryParams = useMemo(
    () => ({ page, size: 10, rol: roleFilter || undefined }),
    [page, roleFilter],
  )

  const { data, isLoading, error } = useAdminUsuarios(queryParams)
  const createMutation = useCreateAdminUsuario()
  const updateMutation = useUpdateAdminUsuario()
  const updateRolesMutation = useUpdateAdminUsuarioRoles()
  const bajaMutation = useBajaAdminUsuario()
  const reactivarMutation = useReactivarAdminUsuario()

  const usuarios = data?.items ?? []

  const resetForm = () => {
    setEditingUser(null)
    setForm(emptyForm)
    setFormError('')
  }

  const resetCreateForm = () => {
    setIsCreating(false)
    setCreateForm(emptyCreateForm)
    setCreateError('')
  }

  const handleCreateRoleToggle = (role: UserRole) => {
    setCreateForm((current) => ({
      ...current,
      roles: current.roles.includes(role)
        ? current.roles.filter((r) => r !== role)
        : [...current.roles, role],
    }))
  }

  const handleCreateSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setCreateError('')
    if (!createForm.email.trim() || !createForm.nombre.trim() || !createForm.apellido.trim() || !createForm.password) {
      setCreateError('Email, nombre, apellido y contraseña son obligatorios')
      return
    }
    if (createForm.password.length < 6) {
      setCreateError('La contraseña debe tener al menos 6 caracteres')
      return
    }
    if (!createForm.roles.length) {
      setCreateError('Asigná al menos un rol')
      return
    }
    try {
      await createMutation.mutateAsync({
        email: createForm.email.trim(),
        password: createForm.password,
        nombre: createForm.nombre.trim(),
        apellido: createForm.apellido.trim(),
        celular: createForm.celular.trim() || null,
        roles: createForm.roles,
      })
      resetCreateForm()
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'No se pudo crear el usuario')
    }
  }

  const openEdit = (usuario: AdminUsuario) => {
    setEditingUser(usuario)
    setForm({
      email: usuario.email,
      nombre: usuario.nombre,
      apellido: usuario.apellido,
      celular: usuario.celular ?? '',
      is_active: usuario.is_active,
      roles: usuario.roles
        .map((role) => role.nombre)
        .filter((role): role is UserRole => AVAILABLE_ROLES.includes(role as UserRole)),
    })
    setFormError('')
  }

  const handleRoleToggle = (role: UserRole) => {
    setForm((current) => {
      const exists = current.roles.includes(role)
      if (exists) {
        return {
          ...current,
          roles: current.roles.filter((item) => item !== role),
        }
      }

      return {
        ...current,
        roles: [...current.roles, role],
      }
    })
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!editingUser) return

    setFormError('')

    if (!form.email.trim() || !form.nombre.trim() || !form.apellido.trim()) {
      setFormError('Email, nombre y apellido son obligatorios')
      return
    }

    if (!form.roles.length) {
      setFormError('Tenés que dejar al menos un rol asignado')
      return
    }

    try {
      await updateMutation.mutateAsync({
        id: editingUser.id,
        data: {
          email: form.email.trim(),
          nombre: form.nombre.trim(),
          apellido: form.apellido.trim(),
          celular: form.celular.trim() || null,
          is_active: form.is_active,
        },
      })

      await updateRolesMutation.mutateAsync({
        id: editingUser.id,
        data: { roles: form.roles },
      })

      resetForm()
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'No se pudo guardar el usuario')
    }
  }

  const handleBaja = (usuario: AdminUsuario) => {
    if (!window.confirm(`¿Dar de baja a ${usuario.email}?`)) return
    bajaMutation.mutate(usuario.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo dar de baja el usuario')
      },
    })
  }

  const handleReactivar = (usuario: AdminUsuario) => {
    if (!window.confirm(`¿Reactivar a ${usuario.email}?`)) return
    reactivarMutation.mutate(usuario.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo reactivar el usuario')
      },
    })
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error cargando usuarios</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Admin usuarios</h1>
          <p className="text-gray-600">
            {data ? `${data.total} usuarios registrados` : 'Cargando usuarios...'}
          </p>
        </div>

        <div className="flex items-end gap-3">
          <Button
            onClick={() => { resetForm(); setIsCreating(true) }}
            disabled={isCreating}
          >
            + Nuevo usuario
          </Button>
          <div className="w-full md:w-64">
          <label className="block text-sm font-medium text-gray-700 mb-1">Filtrar por rol</label>
            <select
              value={roleFilter}
              onChange={(event) => {
                setRoleFilter(event.target.value)
                setPage(1)
              }}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="">Todos</option>
              {AVAILABLE_ROLES.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isCreating && (
        <div className="bg-white rounded-lg shadow-md max-w-3xl">
          <form onSubmit={handleCreateSubmit} className="px-6 py-6 flex flex-col gap-4">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-lg font-semibold text-gray-800">Nuevo usuario</h2>
              <Button type="button" variant="secondary" onClick={resetCreateForm}>Cancelar</Button>
            </div>

            {createError && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2">
                {createError}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                <input
                  type="text"
                  value={createForm.nombre}
                  onChange={(e) => setCreateForm((c) => ({ ...c, nombre: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
                <input
                  type="text"
                  value={createForm.apellido}
                  onChange={(e) => setCreateForm((c) => ({ ...c, apellido: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={createForm.email}
                  onChange={(e) => setCreateForm((c) => ({ ...c, email: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Celular</label>
                <input
                  type="text"
                  value={createForm.celular}
                  onChange={(e) => setCreateForm((c) => ({ ...c, celular: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                <input
                  type="password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm((c) => ({ ...c, password: e.target.value }))}
                  placeholder="Mínimo 6 caracteres"
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Roles</p>
              <div className="flex flex-wrap gap-3">
                {AVAILABLE_ROLES.map((role) => (
                  <label key={role} className="inline-flex items-center gap-2 rounded border border-gray-200 px-3 py-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={createForm.roles.includes(role)}
                      onChange={() => handleCreateRoleToggle(role)}
                      className="w-4 h-4 rounded accent-blue-600"
                    />
                    {role}
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Creando...' : 'Crear usuario'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {editingUser && (
        <div className="bg-white rounded-lg shadow-md max-w-3xl">
          <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-4">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-lg font-semibold text-gray-800">Editar usuario #{editingUser.id}</h2>
              <Button type="button" variant="secondary" onClick={resetForm}>Cancelar</Button>
            </div>

            {formError && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2">
                {formError}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Celular</label>
                <input
                  type="text"
                  value={form.celular}
                  onChange={(event) => setForm((current) => ({ ...current, celular: event.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(event) => setForm((current) => ({ ...current, nombre: event.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
                <input
                  type="text"
                  value={form.apellido}
                  onChange={(event) => setForm((current) => ({ ...current, apellido: event.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                id="user-active"
                type="checkbox"
                checked={form.is_active}
                onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))}
                className="w-4 h-4 rounded accent-blue-600"
              />
              <label htmlFor="user-active" className="text-sm text-gray-700 cursor-pointer">
                Usuario activo
              </label>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Roles</p>
              <div className="flex flex-wrap gap-3">
                {AVAILABLE_ROLES.map((role) => (
                  <label key={role} className="inline-flex items-center gap-2 rounded border border-gray-200 px-3 py-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={form.roles.includes(role)}
                      onChange={() => handleRoleToggle(role)}
                      className="w-4 h-4 rounded accent-blue-600"
                    />
                    {role}
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={updateMutation.isPending || updateRolesMutation.isPending}>
                {updateMutation.isPending || updateRolesMutation.isPending ? 'Guardando...' : 'Guardar cambios'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Roles</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actualizado</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usuarios.map((usuario) => (
                <tr key={usuario.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {usuario.deleted_at ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Baja</span>
                    ) : usuario.is_active ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Activo</span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Inactivo</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="font-semibold">{usuario.nombre} {usuario.apellido}</div>
                    <div className="text-xs text-gray-500">{usuario.email}</div>
                    <div className="text-xs text-gray-500">{usuario.celular || 'Sin celular'}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    <div className="flex flex-wrap gap-2">
                      {usuario.roles.map((role) => (
                        <span key={`${usuario.id}-${role.nombre}`} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {role.nombre}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(usuario.updated_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onClick={() => openEdit(usuario)} className="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
                    {usuario.deleted_at ? (
                      <button onClick={() => handleReactivar(usuario)} className="text-emerald-600 hover:text-emerald-900">Reactivar</button>
                    ) : (
                      <button onClick={() => handleBaja(usuario)} className="text-red-600 hover:text-red-900">Dar de baja</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {usuarios.length === 0 && (
            <div className="px-6 py-8 text-center text-sm text-gray-500">
              No hay usuarios para el filtro seleccionado.
            </div>
          )}
        </div>
      )}

      {data && data.pages > 1 && (
        <div className="flex justify-center gap-2">
          <Button onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1}>
            Anterior
          </Button>
          <span className="flex items-center text-gray-600 text-sm">
            Página {data.page} de {data.pages}
          </span>
          <Button onClick={() => setPage((current) => Math.min(data.pages, current + 1))} disabled={page === data.pages}>
            Siguiente
          </Button>
        </div>
      )}
    </div>
  )
}
