import React, { useState } from 'react'
import { useIngredientes, useCreateIngrediente, useUpdateIngrediente, useBajaIngrediente, useReactivarIngrediente } from '@hooks/useIngredientes'
import { Ingrediente } from '@models/index'
import { IngredienteCreateInput, IngredienteUpdateInput } from '@api/ingredientesApi'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'

export const IngredientesPage: React.FC = () => {
  const { data: ingredientes = [], isLoading, error } = useIngredientes()
  const createMutation = useCreateIngrediente()
  const updateMutation = useUpdateIngrediente()
  const bajaMutation = useBajaIngrediente()
  const reactivarMutation = useReactivarIngrediente()

  const [showForm, setShowForm] = useState(false)
  const [editingIngrediente, setEditingIngrediente] = useState<Ingrediente | null>(null)
  const [form, setForm] = useState<IngredienteCreateInput>({ nombre: '', descripcion: '', es_alergeno: false })
  const [formError, setFormError] = useState('')

  const resetForm = () => {
    setForm({ nombre: '', descripcion: '', es_alergeno: false })
    setEditingIngrediente(null)
    setFormError('')
    setShowForm(false)
  }

  const handleEdit = (ingrediente: Ingrediente) => {
    setEditingIngrediente(ingrediente)
    setForm({
      nombre: ingrediente.nombre,
      descripcion: ingrediente.descripcion || '',
      es_alergeno: ingrediente.es_alergeno,
    })
    setShowForm(true)
  }

  const handleBaja = (ingrediente: Ingrediente) => {
    if (!window.confirm(`¿Dar de baja el ingrediente "${ingrediente.nombre}"?`)) return
    bajaMutation.mutate(ingrediente.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo dar de baja el ingrediente')
      },
    })
  }

  const handleReactivar = (ingrediente: Ingrediente) => {
    if (!window.confirm(`¿Reactivar el ingrediente "${ingrediente.nombre}"?`)) return
    reactivarMutation.mutate(ingrediente.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo reactivar el ingrediente')
      },
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')

    if (!form.nombre.trim()) return setFormError('El nombre es requerido')

    try {
      if (editingIngrediente) {
        const updateData: IngredienteUpdateInput = { ...form }
        await updateMutation.mutateAsync({ id: editingIngrediente.id, data: updateData })
      } else {
        await createMutation.mutateAsync(form)
      }
      resetForm()
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Error al guardar el ingrediente')
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error cargando ingredientes</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Ingredientes</h1>
          <p className="text-gray-600">{ingredientes.length} ingredientes</p>
        </div>
        <Button onClick={() => { resetForm(); setShowForm(true) }}>
          + Nuevo Ingrediente
        </Button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md max-w-lg mb-6">
          <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-4">
            <h2 className="text-lg font-semibold text-gray-800">
              {editingIngrediente ? 'Editar Ingrediente' : 'Nuevo Ingrediente'}
            </h2>

            {formError && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2">
                {formError}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={form.nombre}
                onChange={(e) => setForm((prev) => ({ ...prev, nombre: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción
              </label>
              <textarea
                rows={2}
                value={form.descripcion}
                onChange={(e) => setForm((prev) => ({ ...prev, descripcion: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="es_alergeno"
                checked={form.es_alergeno}
                onChange={(e) => setForm((prev) => ({ ...prev, es_alergeno: e.target.checked }))}
                className="w-4 h-4 rounded accent-red-500"
              />
              <label htmlFor="es_alergeno" className="text-sm text-gray-700 cursor-pointer">
                Es alérgeno
              </label>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={resetForm}
                className="flex-1 border border-gray-300 text-gray-700 rounded px-4 py-2 text-sm hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isPending}
                className="flex-1 bg-blue-600 text-white rounded px-4 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {isPending ? 'Guardando...' : editingIngrediente ? 'Guardar cambios' : 'Crear ingrediente'}
              </button>
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Descripción
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Alérgeno
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ingredientes.map((ingrediente) => (
                <tr key={ingrediente.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {ingrediente.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {ingrediente.deleted_at ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Baja
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Activo
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {ingrediente.nombre}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {ingrediente.descripcion || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {ingrediente.es_alergeno ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Sí
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        No
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(ingrediente)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Editar
                    </button>
                    {ingrediente.deleted_at ? (
                      <button
                        onClick={() => handleReactivar(ingrediente)}
                        className="text-emerald-600 hover:text-emerald-900"
                      >
                        Reactivar
                      </button>
                    ) : (
                      <button
                        onClick={() => handleBaja(ingrediente)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Dar de baja
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
