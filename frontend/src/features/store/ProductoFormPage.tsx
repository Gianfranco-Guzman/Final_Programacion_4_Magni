import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Producto, Categoria } from '@models/index'
import { useCreateProducto, useUpdateProducto } from '@hooks/useProductos'
import { ProductoCreateInput } from '@api/productosApi'

interface ProductoFormPageProps {
  producto?: Producto
  categorias: Categoria[]
  title: string
}

const empty: ProductoCreateInput = {
  nombre: '',
  codigo: '',
  precio: 0,
  stock_cantidad: 0,
  categoria_id: 0,
  descripcion: '',
}

export const ProductoFormPage: React.FC<ProductoFormPageProps> = ({
  producto,
  categorias,
  title,
}) => {
  const navigate = useNavigate()
  const isEdit = producto != null
  const [form, setForm] = useState<ProductoCreateInput>(empty)
  const [error, setError] = useState('')

  const createMutation = useCreateProducto()
  const updateMutation = useUpdateProducto()
  const isPending = createMutation.isPending || updateMutation.isPending

  useEffect(() => {
    if (producto) {
      setForm({
        nombre: producto.nombre,
        codigo: producto.codigo,
        precio: producto.precio,
        stock_cantidad: producto.stock_cantidad,
        categoria_id: producto.categoria_id,
        descripcion: producto.descripcion || '',
      })
    } else {
      setForm({ ...empty, categoria_id: categorias[0]?.id ?? 0 })
    }
  }, [producto, categorias])

  const set = (field: keyof ProductoCreateInput) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const val = e.target.type === 'number' ? Number(e.target.value) : e.target.value
    setForm((prev) => ({ ...prev, [field]: val }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!form.nombre.trim()) return setError('El nombre es requerido')
    if (!form.codigo.trim()) return setError('El código es requerido')
    if (form.precio <= 0) return setError('El precio debe ser mayor a 0')
    if (form.stock_cantidad < 0) return setError('El stock no puede ser negativo')
    if (!form.categoria_id || form.categoria_id === 0) return setError('Seleccioná una categoría')

    try {
      if (isEdit) {
        await updateMutation.mutateAsync({ id: producto!.id, data: form })
      } else {
        await createMutation.mutateAsync(form)
      }
      navigate('/catalogo')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al guardar el producto')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
        <button
          onClick={() => navigate('/catalogo')}
          className="text-sm text-gray-600 hover:text-gray-800 underline"
        >
          Volver al catálogo
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md max-w-lg">
        <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2">
              {error}
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
              onChange={set('nombre')}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Código <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={form.codigo}
              onChange={set('codigo')}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Precio <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                required
                min="0.01"
                step="0.01"
                value={form.precio}
                onChange={set('precio')}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stock
              </label>
              <input
                type="number"
                min="0"
                value={form.stock_cantidad}
                onChange={set('stock_cantidad')}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoría <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={form.categoria_id}
              onChange={set('categoria_id')}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value={0} disabled>Seleccionar...</option>
              {categorias.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
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
              onChange={set('descripcion')}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => navigate('/catalogo')}
              className="flex-1 border border-gray-300 text-gray-700 rounded px-4 py-2 text-sm hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 bg-blue-600 text-white rounded px-4 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {isPending ? 'Guardando...' : isEdit ? 'Guardar cambios' : 'Crear producto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
