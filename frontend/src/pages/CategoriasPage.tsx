import { FormEvent, useMemo, useState } from 'react'
import {
  useBajaCategoria,
  useCategoriasList,
  useCategoriasTree,
  useCreateCategoria,
  useReactivarCategoria,
  useUpdateCategoria,
} from '@hooks/useCategorias'
import { Categoria } from '@models/index'
import { CategoriaCreateInput, CategoriaUpdateInput } from '@api/categoriasApi'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'

interface CategoriaNodeProps {
  categoria: Categoria
  level?: number
}

function CategoriaNode({ categoria, level = 0 }: CategoriaNodeProps) {
  const [open, setOpen] = useState(true)
  const hasChildren = (categoria.subcategorias?.length || 0) > 0

  return (
    <div className="border-l border-gray-200 pl-3" style={{ marginLeft: level * 12 }}>
      <div className="py-1 text-sm text-gray-700 flex items-center gap-2">
        {hasChildren ? (
          <button type="button" onClick={() => setOpen((prev) => !prev)} className="text-xs text-gray-400 hover:text-gray-700">
            {open ? '▾' : '▸'}
          </button>
        ) : (
          <span className="w-3" />
        )}
        <span className="font-medium">{categoria.nombre}</span>
        {categoria.deleted_at && <span className="ml-2 text-xs text-red-600">dada de baja</span>}
      </div>
      {open && categoria.subcategorias?.map((subcategoria) => (
        <CategoriaNode key={subcategoria.id} categoria={subcategoria} level={level + 1} />
      ))}
    </div>
  )
}

const emptyForm: CategoriaCreateInput = {
  nombre: '',
  descripcion: '',
  parent_id: null,
}

export function CategoriasPage() {
  const [incluirBaja, setIncluirBaja] = useState(true)
  const { data: categorias = [], isLoading, error } = useCategoriasList({
    incluir_baja: incluirBaja,
    size: 100,
  })
  const { data: categoriasTree = [] } = useCategoriasTree()
  const createMutation = useCreateCategoria()
  const updateMutation = useUpdateCategoria()
  const bajaMutation = useBajaCategoria()
  const reactivarMutation = useReactivarCategoria()

  const [showForm, setShowForm] = useState(false)
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null)
  const [form, setForm] = useState<CategoriaCreateInput>(emptyForm)
  const [formError, setFormError] = useState('')

  const categoriasActivas = useMemo(
    () => categorias.filter((categoria) => !categoria.deleted_at),
    [categorias],
  )

  const categoriasRaiz = useMemo(() => categoriasTree, [categoriasTree])

  const parentOptions = useMemo(
    () => categoriasActivas.filter((categoria) => categoria.id !== editingCategoria?.id),
    [categoriasActivas, editingCategoria?.id],
  )

  const resetForm = () => {
    setForm(emptyForm)
    setEditingCategoria(null)
    setFormError('')
    setShowForm(false)
  }

  const handleEdit = (categoria: Categoria) => {
    setEditingCategoria(categoria)
    setForm({
      nombre: categoria.nombre,
      descripcion: categoria.descripcion || '',
      parent_id: categoria.parent_id ?? null,
    })
    setFormError('')
    setShowForm(true)
  }

  const handleBaja = (categoria: Categoria) => {
    if (!window.confirm(`¿Dar de baja la categoría "${categoria.nombre}"?`)) return
    bajaMutation.mutate(categoria.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo dar de baja la categoría')
      },
    })
  }

  const handleReactivar = (categoria: Categoria) => {
    reactivarMutation.mutate(categoria.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo reactivar la categoría')
      },
    })
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError('')

    const nombre = form.nombre.trim()
    if (!nombre) return setFormError('El nombre es requerido')

    const payload: CategoriaCreateInput = {
      nombre,
      descripcion: form.descripcion?.trim() || undefined,
      parent_id: form.parent_id || null,
    }

    try {
      if (editingCategoria) {
        const updateData: CategoriaUpdateInput = payload
        await updateMutation.mutateAsync({ id: editingCategoria.id, data: updateData })
      } else {
        await createMutation.mutateAsync(payload)
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
          <p className="text-gray-600">
            {categorias.length} categorías {incluirBaja ? 'incluyendo bajas' : 'activas'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={incluirBaja}
              onChange={(e) => setIncluirBaja(e.target.checked)}
            />
            Incluir bajas
          </label>
          <Button onClick={() => { resetForm(); setShowForm(true) }}>
            + Nueva Categoría
          </Button>
        </div>
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
                Categoría padre
              </label>
              <select
                value={form.parent_id ?? ''}
                onChange={(e) => setForm((prev) => ({
                  ...prev,
                  parent_id: e.target.value ? Number(e.target.value) : null,
                }))}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="">Sin padre</option>
                {parentOptions.map((categoria) => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.nombre}
                  </option>
                ))}
              </select>
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
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Padre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {categorias.map((categoria) => {
                  const parent = categorias.find((item) => item.id === categoria.parent_id)
                  return (
                    <tr
                      key={categoria.id}
                      className={categoria.deleted_at ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-gray-50'}
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        <div>{categoria.nombre}</div>
                        <div className="text-xs text-gray-500">{categoria.descripcion || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {parent?.nombre || 'Raíz'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {categoria.deleted_at ? (
                          <span className="text-red-700 font-medium">Baja</span>
                        ) : (
                          <span className="text-green-700 font-medium">Activa</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEdit(categoria)}
                          disabled={!!categoria.deleted_at}
                          className="text-blue-600 hover:text-blue-900 mr-3 disabled:text-gray-400"
                        >
                          Editar
                        </button>
                        {categoria.deleted_at ? (
                          <button
                            onClick={() => handleReactivar(categoria)}
                            className="text-green-600 hover:text-green-900"
                          >
                            Reactivar
                          </button>
                        ) : (
                          <button
                            onClick={() => handleBaja(categoria)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Baja
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <aside className="bg-white rounded-lg shadow-md p-4 h-fit">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Jerarquía</h2>
            {categoriasRaiz.length ? (
              categoriasRaiz.map((categoria) => (
                <CategoriaNode key={categoria.id} categoria={categoria} />
              ))
            ) : (
              <p className="text-sm text-gray-500">No hay categorías raíz.</p>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}
