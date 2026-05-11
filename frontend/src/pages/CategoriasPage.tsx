import React, { useState } from 'react'
import { useCategoriasList, useCreateCategoria, useUpdateCategoria, useDeleteCategoria } from '@hooks/useCategorias'
import { Categoria } from '@models/index'
import { CategoriaCreateInput, CategoriaUpdateInput } from '@api/categoriasApi'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'

export const CategoriasPage: React.FC = () => {
  const { data: categorias = [], isLoading, error } = useCategoriasList()
  const createMutation = useCreateCategoria()
  const updateMutation = useUpdateCategoria()
  const deleteMutation = useDeleteCategoria()

  const [showForm, setShowForm] = useState(false)
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null)
  const [form, setForm] = useState<CategoriaCreateInput>({ nombre: '', descripcion: '' })
  const [formError, setFormError] = useState('')

  const resetForm = () => {
    setForm({ nombre: '', descripcion: '' })
    setEditingCategoria(null)
    setFormError('')
    setShowForm(false)
  }

  const handleEdit = (categoria: Categoria) => {
    setEditingCategoria(categoria)
    setForm({ nombre: categoria.nombre, descripcion: categoria.descripcion || '' })
    setShowForm(true)
  }

  const handleDelete = (categoria: Categoria) => {
    if (!window.confirm(`¿Eliminar la categoría "${categoria.nombre}"?`)) return
    deleteMutation.mutate(categoria.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo eliminar la categoría')
      },
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')

    if (!form.nombre.trim()) return setFormError('El nombre es requerido')

    try {
      if (editingCategoria) {
        const updateData: CategoriaUpdateInput = { ...form }
        await updateMutation.mutateAsync({ id: editingCategoria.id, data: updateData })
      } else {
        await createMutation.mutateAsync(form)
      }
      resetForm()
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Error al guardar la categoría')
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error cargando categorías</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Categorías</h1>
          <p className="text-gray-600">{categorias.length} categorías</p>
        </div>
        <Button onClick={() => { resetForm(); setShowForm(true) }}>
          + Nueva Categoría
        </Button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md max-w-lg mb-6">
          <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-4">
            <h2 className="text-lg font-semibold text-gray-800">
              {editingCategoria ? 'Editar Categoría' : 'Nueva Categoría'}
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
                {isPending ? 'Guardando...' : editingCategoria ? 'Guardar cambios' : 'Crear categoría'}
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
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Descripción
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {categorias.map((categoria) => (
                <tr key={categoria.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {categoria.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {categoria.nombre}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {categoria.descripcion || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(categoria)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDelete(categoria)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Eliminar
                    </button>
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
