import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Producto, Categoria, Ingrediente } from '@models/index'
import { useCreateProducto, useUpdateProducto } from '@hooks/useProductos'
import {
  ProductoCreateInput,
  ProductoIngredienteInput,
  ProductoUpdateInput,
} from '@api/productosApi'

interface ProductoFormPageProps {
  producto?: Producto
  categorias: Categoria[]
  ingredientes: Ingrediente[]
  title: string
}

const empty: ProductoCreateInput = {
  nombre: '',
  codigo: '',
  precio: 0,
  stock_cantidad: 0,
  descripcion: '',
  disponible: true,
  categorias: [],
  ingredientes: [],
}

export const ProductoFormPage: React.FC<ProductoFormPageProps> = ({
  producto,
  categorias,
  ingredientes,
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
        descripcion: producto.descripcion || '',
        disponible: producto.disponible,
        categorias: producto.categorias?.map((item) => ({
          categoria_id: item.categoria_id,
          es_principal: item.es_principal,
        })) || [],
        ingredientes: producto.ingredientes?.map((item) => ({
          ingrediente_id: item.ingrediente_id,
          es_removible: item.es_removible,
          es_opcional: item.es_opcional,
        })) || [],
      })
    } else {
      const defaultCategoryId = categorias[0]?.id
      setForm({
        ...empty,
        categorias: defaultCategoryId ? [{ categoria_id: defaultCategoryId, es_principal: true }] : [],
      })
    }
  }, [producto, categorias])

  const set = (field: keyof ProductoCreateInput) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const val = e.target.type === 'number' ? Number(e.target.value) : e.target.value
    setForm((prev) => ({ ...prev, [field]: val }))
  }

  const toggleIngrediente = (ingredienteId: number) => {
    setForm((prev) => {
      const ingredientesConfig = prev.ingredientes || []
      const exists = ingredientesConfig.some((item) => item.ingrediente_id === ingredienteId)
      if (exists) {
        return {
          ...prev,
          ingredientes: ingredientesConfig.filter((item) => item.ingrediente_id !== ingredienteId),
        }
      } else {
        return {
          ...prev,
          ingredientes: [
            ...ingredientesConfig,
            {
              ingrediente_id: ingredienteId,
              es_removible: true,
              es_opcional: false,
            },
          ],
        }
      }
    })
  }

  const updateIngredienteConfig = (
    ingredienteId: number,
    field: keyof Omit<ProductoIngredienteInput, 'ingrediente_id'>,
    value: boolean,
  ) => {
    setForm((prev) => ({
      ...prev,
      ingredientes: (prev.ingredientes || []).map((item) =>
        item.ingrediente_id === ingredienteId ? { ...item, [field]: value } : item,
      ),
    }))
  }

  const toggleCategoria = (categoriaId: number) => {
    setForm((prev) => {
      const categoriasConfig = prev.categorias || []
      const exists = categoriasConfig.some((item) => item.categoria_id === categoriaId)

      if (exists) {
        const nextCategorias = categoriasConfig.filter((item) => item.categoria_id !== categoriaId)
        if (nextCategorias.length > 0 && !nextCategorias.some((item) => item.es_principal)) {
          nextCategorias[0] = { ...nextCategorias[0], es_principal: true }
        }
        return { ...prev, categorias: nextCategorias }
      }

      return {
        ...prev,
        categorias: [
          ...categoriasConfig,
          {
            categoria_id: categoriaId,
            es_principal: categoriasConfig.length === 0,
          },
        ],
      }
    })
  }

  const isCategoriaSelected = (categoriaId: number) =>
    (form.categorias || []).some((item) => item.categoria_id === categoriaId)

  const setCategoriaPrincipal = (categoriaId: number) => {
    setForm((prev) => ({
      ...prev,
      categorias: (prev.categorias || []).map((item) => ({
        ...item,
        es_principal: item.categoria_id === categoriaId,
      })),
    }))
  }

  const categoriaPrincipalId = (form.categorias || []).find((item) => item.es_principal)?.categoria_id ?? null

  const isIngredienteSelected = (ingredienteId: number) =>
    (form.ingredientes || []).some((item) => item.ingrediente_id === ingredienteId)

  const getIngredienteConfig = (ingredienteId: number) =>
    (form.ingredientes || []).find((item) => item.ingrediente_id === ingredienteId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!form.nombre.trim()) return setError('El nombre es requerido')
    if (!form.codigo.trim()) return setError('El código es requerido')
    if (form.precio <= 0) return setError('El precio debe ser mayor a 0')
    if (form.stock_cantidad < 0) return setError('El stock no puede ser negativo')
    if (!form.categorias || form.categorias.length === 0) return setError('Seleccioná al menos una categoría')
    if (!form.categorias.some((item) => item.es_principal)) return setError('Definí una categoría principal')
    if (!form.ingredientes || form.ingredientes.length === 0) return setError('Seleccioná al menos un ingrediente')

    try {
      if (isEdit) {
        const updateData: ProductoUpdateInput = { ...form }
        await updateMutation.mutateAsync({ id: producto!.id, data: updateData })
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

          <label className="inline-flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={form.disponible}
              onChange={(e) => setForm((prev) => ({ ...prev, disponible: e.target.checked }))}
              className="w-4 h-4 rounded accent-blue-500"
            />
            Mostrar producto como disponible en catálogo
          </label>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categorías <span className="text-red-500">*</span>
            </label>
            <div className="border border-gray-300 rounded px-3 py-2 max-h-48 overflow-y-auto">
              {categorias.length === 0 ? (
                <p className="text-sm text-gray-500">No hay categorías disponibles</p>
              ) : (
                categorias.map((categoria) => (
                  <div
                    key={categoria.id}
                    className="py-2 px-1 rounded hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                  >
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={isCategoriaSelected(categoria.id)}
                        onChange={() => toggleCategoria(categoria.id)}
                        className="w-4 h-4 rounded accent-blue-500"
                      />
                      <span className="text-sm text-gray-700">{categoria.nombre}</span>
                    </label>

                    {isCategoriaSelected(categoria.id) && (
                      <label className="inline-flex items-center gap-2 mt-2 ml-6 text-xs text-gray-600">
                        <input
                          type="radio"
                          name="categoria_principal"
                          checked={categoriaPrincipalId === categoria.id}
                          onChange={() => setCategoriaPrincipal(categoria.id)}
                          className="w-4 h-4 accent-blue-500"
                        />
                        Categoría principal
                      </label>
                    )}
                  </div>
                ))
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {(form.categorias || []).length} categoría(s) seleccionada(s)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ingredientes <span className="text-red-500">*</span>
            </label>
            <div className="border border-gray-300 rounded px-3 py-2 max-h-48 overflow-y-auto">
              {ingredientes.length === 0 ? (
                <p className="text-sm text-gray-500">No hay ingredientes disponibles</p>
              ) : (
                ingredientes.map((ing) => (
                  <div
                    key={ing.id}
                    className="py-2 px-1 rounded hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                  >
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={isIngredienteSelected(ing.id)}
                        onChange={() => toggleIngrediente(ing.id)}
                        className="w-4 h-4 rounded accent-blue-500"
                      />
                      <span className="text-sm text-gray-700">{ing.nombre}</span>
                      {ing.es_alergeno && (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Alérgeno
                        </span>
                      )}
                    </label>

                    {isIngredienteSelected(ing.id) && (() => {
                      const config = getIngredienteConfig(ing.id)
                      return (
                        <div className="ml-6 mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-600">
                          <label className="inline-flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={config?.es_removible ?? true}
                              onChange={(e) => updateIngredienteConfig(ing.id, 'es_removible', e.target.checked)}
                              className="w-4 h-4 rounded accent-blue-500"
                            />
                            Se puede remover
                          </label>
                          <label className="inline-flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={config?.es_opcional ?? false}
                              onChange={(e) => updateIngredienteConfig(ing.id, 'es_opcional', e.target.checked)}
                              className="w-4 h-4 rounded accent-blue-500"
                            />
                            Es opcional
                          </label>
                        </div>
                      )
                    })()}
                  </div>
                ))
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {(form.ingredientes || []).length} ingrediente(s) seleccionado(s)
            </p>
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
