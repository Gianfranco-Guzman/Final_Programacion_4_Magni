import React, { useEffect, useMemo, useState } from 'react'

import { DireccionEntregaInput } from '@api/direccionesApi'
import { Button } from '@components/Button'
import { Spinner } from '@components/Spinner'
import {
  useCreateDireccion,
  useDeleteDireccion,
  useDirecciones,
  useMarcarDireccionPrincipal,
  useUpdateDireccion,
} from '@hooks/useDirecciones'
import { DireccionEntrega } from '@models/index'

const emptyForm: DireccionEntregaInput = {
  etiqueta: '',
  linea1: '',
  linea2: '',
  ciudad: '',
  latitud: null,
  longitud: null,
  es_principal: false,
}

export const DireccionesPage: React.FC = () => {
  const { data: direcciones = [], isLoading, error } = useDirecciones()
  const createMutation = useCreateDireccion()
  const updateMutation = useUpdateDireccion()
  const deleteMutation = useDeleteDireccion()
  const principalMutation = useMarcarDireccionPrincipal()

  const [showForm, setShowForm] = useState(false)
  const [editingDireccion, setEditingDireccion] = useState<DireccionEntrega | null>(null)
  const [form, setForm] = useState<DireccionEntregaInput>(emptyForm)
  const [formError, setFormError] = useState('')

  const isPending = useMemo(
    () => createMutation.isPending || updateMutation.isPending || principalMutation.isPending,
    [createMutation.isPending, updateMutation.isPending, principalMutation.isPending],
  )

  useEffect(() => {
    if (!showForm) {
      setForm(emptyForm)
      setEditingDireccion(null)
      setFormError('')
    }
  }, [showForm])

  const resetForm = () => {
    setShowForm(false)
  }

  const handleEdit = (direccion: DireccionEntrega) => {
    setEditingDireccion(direccion)
    setForm({
      etiqueta: direccion.etiqueta || '',
      linea1: direccion.linea1,
      linea2: direccion.linea2 || '',
      ciudad: direccion.ciudad,
      latitud: direccion.latitud ?? null,
      longitud: direccion.longitud ?? null,
      es_principal: direccion.es_principal,
    })
    setShowForm(true)
  }

  const handleChange = (field: keyof DireccionEntregaInput) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { type, value } = event.target
    if (type === 'checkbox') {
      const inputTarget = event.target as HTMLInputElement
      setForm((prev) => ({ ...prev, [field]: inputTarget.checked }))
      return
    }

    const normalizedValue = type === 'number'
      ? (value === '' ? null : Number(value))
      : value

    setForm((prev) => ({ ...prev, [field]: normalizedValue }))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setFormError('')

    if (!form.linea1.trim()) return setFormError('La línea principal es obligatoria')
    if (!form.ciudad.trim()) return setFormError('La ciudad es obligatoria')

    try {
      if (editingDireccion) {
        await updateMutation.mutateAsync({ id: editingDireccion.id, data: form })
      } else {
        await createMutation.mutateAsync(form)
      }
      resetForm()
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'No se pudo guardar la dirección')
    }
  }

  const handleDelete = (direccion: DireccionEntrega) => {
    if (!window.confirm(`¿Eliminar la dirección ${direccion.etiqueta || direccion.linea1}?`)) return
    deleteMutation.mutate(direccion.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo eliminar la dirección')
      },
    })
  }

  const handleSetPrincipal = (direccion: DireccionEntrega) => {
    if (direccion.es_principal) return
    principalMutation.mutate(direccion.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo marcar como principal')
      },
    })
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error cargando direcciones</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Mis direcciones</h1>
          <p className="text-gray-600">{direcciones.length} dirección(es) activas</p>
        </div>
        <Button onClick={() => setShowForm(true)}>+ Nueva dirección</Button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md max-w-2xl mb-6">
          <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-4">
            <h2 className="text-lg font-semibold text-gray-800">
              {editingDireccion ? 'Editar dirección' : 'Nueva dirección'}
            </h2>

            {formError && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2">
                {formError}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Etiqueta</label>
                <input
                  type="text"
                  value={form.etiqueta || ''}
                  onChange={handleChange('etiqueta')}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                  placeholder="Casa, trabajo, etc."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ciudad *</label>
                <input
                  type="text"
                  required
                  value={form.ciudad}
                  onChange={handleChange('ciudad')}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Dirección principal *</label>
              <input
                type="text"
                required
                value={form.linea1}
                onChange={handleChange('linea1')}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Complemento</label>
              <textarea
                rows={2}
                value={form.linea2 || ''}
                onChange={handleChange('linea2')}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Latitud</label>
                <input
                  type="number"
                  step="0.000001"
                  value={form.latitud ?? ''}
                  onChange={handleChange('latitud')}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Longitud</label>
                <input
                  type="number"
                  step="0.000001"
                  value={form.longitud ?? ''}
                  onChange={handleChange('longitud')}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
            </div>

            <label className="inline-flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={Boolean(form.es_principal)}
                onChange={handleChange('es_principal')}
                className="w-4 h-4 rounded accent-blue-500"
              />
              Marcar como dirección principal
            </label>

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
                {isPending ? 'Guardando...' : editingDireccion ? 'Guardar cambios' : 'Crear dirección'}
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {direcciones.map((direccion) => (
            <div key={direccion.id} className="bg-white rounded-lg shadow-md p-5 border border-gray-100">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {direccion.etiqueta || 'Sin etiqueta'}
                    </h3>
                    {direccion.es_principal && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                        Principal
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700">{direccion.linea1}</p>
                  {direccion.linea2 && <p className="text-sm text-gray-500">{direccion.linea2}</p>}
                  <p className="text-sm text-gray-500 mt-1">{direccion.ciudad}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {!direccion.es_principal && (
                    <button
                      onClick={() => handleSetPrincipal(direccion)}
                      className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded px-2 py-1 hover:bg-blue-100"
                    >
                      Hacer principal
                    </button>
                  )}
                  <button
                    onClick={() => handleEdit(direccion)}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDelete(direccion)}
                    className="text-sm text-red-600 hover:text-red-800"
                    disabled={deleteMutation.isPending}
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          ))}

          {direcciones.length === 0 && (
            <div className="col-span-full bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
              Todavía no tenés direcciones guardadas.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
