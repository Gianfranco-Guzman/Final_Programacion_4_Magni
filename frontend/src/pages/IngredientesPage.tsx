import React, { useMemo, useState } from 'react'
import { useIngredientes, useCreateIngrediente, useUpdateIngrediente, useBajaIngrediente, useReactivarIngrediente } from '@hooks/useIngredientes'
import { Ingrediente, UnidadMedida } from '@models/index'
import { IngredienteCreateInput, IngredienteUpdateInput } from '@api/ingredientesApi'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'

const UNIDADES: UnidadMedida[] = ['UNIDAD', 'GRAMO', 'KILOGRAMO', 'MILILITRO', 'LITRO']

const emptyForm: IngredienteCreateInput = {
  nombre: '',
  descripcion: '',
  es_alergeno: false,
  unidad_medida: 'UNIDAD',
  stock_actual: 0,
  stock_minimo: 0,
  costo_unitario: 0,
  permite_fraccion: false,
}

const unidadLabel: Record<UnidadMedida, string> = {
  UNIDAD: 'Unidad',
  GRAMO: 'Gramo',
  KILOGRAMO: 'Kilogramo',
  MILILITRO: 'Mililitro',
  LITRO: 'Litro',
}

export const IngredientesPage: React.FC = () => {
  const { data: ingredientes = [], isLoading, error } = useIngredientes()
  const createMutation = useCreateIngrediente()
  const updateMutation = useUpdateIngrediente()
  const bajaMutation = useBajaIngrediente()
  const reactivarMutation = useReactivarIngrediente()

  const [showForm, setShowForm] = useState(false)
  const [editingIngrediente, setEditingIngrediente] = useState<Ingrediente | null>(null)
  const [form, setForm] = useState<IngredienteCreateInput>(emptyForm)
  const [formError, setFormError] = useState('')
  const [soloActivos, setSoloActivos] = useState(false)
  const [soloStockBajo, setSoloStockBajo] = useState(false)
  const [unidadFiltro, setUnidadFiltro] = useState<UnidadMedida | ''>('')
  const [busqueda, setBusqueda] = useState('')

  const resetForm = () => {
    setForm(emptyForm)
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
      unidad_medida: ingrediente.unidad_medida,
      stock_actual: Number(ingrediente.stock_actual),
      stock_minimo: Number(ingrediente.stock_minimo),
      costo_unitario: Number(ingrediente.costo_unitario),
      permite_fraccion: ingrediente.permite_fraccion,
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
    if (form.stock_actual < 0) return setFormError('El stock actual no puede ser negativo')
    if (form.stock_minimo < 0) return setFormError('El stock mínimo no puede ser negativo')
    if (form.costo_unitario < 0) return setFormError('El costo unitario no puede ser negativo')
    if (form.unidad_medida === 'UNIDAD' && form.permite_fraccion) {
      return setFormError('Un ingrediente medido en unidad no puede permitir fracción')
    }

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

  const ingredientesFiltrados = useMemo(() => {
    const q = busqueda.toLowerCase()
    return [...ingredientes]
      .filter((ingrediente) => {
        if (soloActivos && ingrediente.deleted_at) return false
        if (soloStockBajo && Number(ingrediente.stock_actual) > Number(ingrediente.stock_minimo)) return false
        if (unidadFiltro && ingrediente.unidad_medida !== unidadFiltro) return false
        if (q && !ingrediente.nombre.toLowerCase().includes(q)) return false
        return true
      })
      .sort((a, b) => a.nombre.localeCompare(b.nombre))
  }, [ingredientes, soloActivos, soloStockBajo, unidadFiltro, busqueda])

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
          <p className="text-gray-600">{ingredientesFiltrados.length} ingredientes visibles</p>
        </div>
        <Button onClick={() => { resetForm(); setShowForm(true) }}>
          + Nuevo Ingrediente
        </Button>
      </div>

      <div className="mb-6 rounded-lg bg-white p-4 shadow-md flex flex-col gap-3">
        <input
          type="text"
          placeholder="Buscar ingrediente..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={soloActivos} onChange={(e) => setSoloActivos(e.target.checked)} />
            Solo activos
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={soloStockBajo} onChange={(e) => setSoloStockBajo(e.target.checked)} />
            Solo stock bajo
          </label>
          <select
            value={unidadFiltro}
            onChange={(e) => setUnidadFiltro((e.target.value as UnidadMedida) || '')}
            className="rounded border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Todas las unidades</option>
            {UNIDADES.map((unidad) => (
              <option key={unidad} value={unidad}>{unidadLabel[unidad]}</option>
            ))}
          </select>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md max-w-2xl mb-6">
          <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-4">
            <h2 className="text-lg font-semibold text-gray-800">
              {editingIngrediente ? 'Editar Ingrediente' : 'Nuevo Ingrediente'}
            </h2>

            {formError && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2">
                {formError}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                <input type="text" required value={form.nombre} onChange={(e) => setForm((prev) => ({ ...prev, nombre: e.target.value }))} className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unidad de medida *</label>
                <select value={form.unidad_medida} onChange={(e) => setForm((prev) => ({ ...prev, unidad_medida: e.target.value as UnidadMedida }))} className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
                  {UNIDADES.map((unidad) => <option key={unidad} value={unidad}>{unidadLabel[unidad]}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <textarea rows={2} value={form.descripcion} onChange={(e) => setForm((prev) => ({ ...prev, descripcion: e.target.value }))} className="w-full border border-gray-300 rounded px-3 py-2 text-sm resize-none" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stock actual *</label>
                <input type="number" min="0" step="1" value={form.stock_actual} onChange={(e) => setForm((prev) => ({ ...prev, stock_actual: Number(e.target.value) }))} className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stock mínimo *</label>
                <input type="number" min="0" step="1" value={form.stock_minimo} onChange={(e) => setForm((prev) => ({ ...prev, stock_minimo: Number(e.target.value) }))} className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Costo unitario *</label>
                <input type="number" min="0" step="0.1" value={form.costo_unitario} onChange={(e) => setForm((prev) => ({ ...prev, costo_unitario: Number(e.target.value) }))} className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
              </div>
            </div>

            <div className="flex flex-wrap gap-4 text-sm text-gray-700">
              <label className="inline-flex items-center gap-2">
                <input type="checkbox" checked={form.es_alergeno} onChange={(e) => setForm((prev) => ({ ...prev, es_alergeno: e.target.checked }))} />
                Es alérgeno
              </label>
              <label className="inline-flex items-center gap-2">
                <input type="checkbox" checked={form.permite_fraccion} disabled={form.unidad_medida === 'UNIDAD'} onChange={(e) => setForm((prev) => ({ ...prev, permite_fraccion: e.target.checked }))} />
                Permite fracción
              </label>
            </div>

            <div className="flex gap-3 pt-2">
              <button type="button" onClick={resetForm} className="flex-1 border border-gray-300 text-gray-700 rounded px-4 py-2 text-sm hover:bg-gray-50">Cancelar</button>
              <button type="submit" disabled={isPending} className="flex-1 bg-blue-600 text-white rounded px-4 py-2 text-sm hover:bg-blue-700 disabled:opacity-50">
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ingrediente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unidad</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Costo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Flags</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ingredientesFiltrados.map((ingrediente) => {
                const stockBajo = Number(ingrediente.stock_actual) <= Number(ingrediente.stock_minimo)
                return (
                  <tr key={ingrediente.id} className={stockBajo ? 'bg-amber-50 hover:bg-amber-100' : 'hover:bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {ingrediente.deleted_at ? <span className="inline-flex rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">Baja</span> : <span className="inline-flex rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">Activo</span>}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="font-medium">{ingrediente.nombre}</div>
                      <div className="text-xs text-gray-500">{ingrediente.descripcion || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{unidadLabel[ingrediente.unidad_medida]}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{Math.round(Number(ingrediente.stock_actual))}</div>
                      <div className={`text-xs ${stockBajo ? 'text-amber-700 font-medium' : 'text-gray-400'}`}>Mínimo: {Math.round(Number(ingrediente.stock_minimo))}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${Number(ingrediente.costo_unitario).toFixed(1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{ingrediente.es_alergeno ? 'Alérgeno' : 'Sin alérgeno'}</div>
                      <div className="text-xs text-gray-400">{ingrediente.permite_fraccion ? 'Con fracción' : 'Sin fracción'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => handleEdit(ingrediente)} className="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
                      {ingrediente.deleted_at ? (
                        <button onClick={() => handleReactivar(ingrediente)} className="text-emerald-600 hover:text-emerald-900">Reactivar</button>
                      ) : (
                        <button onClick={() => handleBaja(ingrediente)} className="text-red-600 hover:text-red-900">Dar de baja</button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
