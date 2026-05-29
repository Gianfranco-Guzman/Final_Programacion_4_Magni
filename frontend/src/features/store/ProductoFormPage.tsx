import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Categoria, Ingrediente, Producto, ProductoDetalleConfig, TipoProducto } from '@models/index'
import { useCreateProducto, useUpdateProducto } from '@hooks/useProductos'
import { ProductoCreateInput, ProductoDetalleInput, ProductoUpdateInput } from '@api/productosApi'
import { calcularCostoProducto, calcularStockMaximoProducto } from '@/utils/producto'

interface ProductoFormPageProps {
  producto?: Producto
  categorias: Categoria[]
  ingredientes: Ingrediente[]
  title: string
}

const empty: ProductoCreateInput = {
  nombre: '',
  codigo: '',
  precio_venta: 0,
  descripcion: '',
  disponible: true,
  tipo_producto: 'FABRICADO',
  descuento_porcentaje: 0,
  categorias: [],
  ingredientes: [],
}

const buildIngredienteInput = (ingrediente: Ingrediente, orden: number): ProductoDetalleInput => ({
  ingrediente_id: ingrediente.id,
  cantidad: 1,
  unidad_medida: ingrediente.unidad_medida,
  orden,
  es_removible: true,
  es_opcional: false,
})

export const ProductoFormPage: React.FC<ProductoFormPageProps> = ({ producto, categorias, ingredientes, title }) => {
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
        precio_venta: producto.precio_venta,
        descripcion: producto.descripcion || '',
        disponible: producto.disponible,
        tipo_producto: producto.tipo_producto,
        descuento_porcentaje: producto.descuento_porcentaje,
        categorias: producto.categorias?.map((item) => ({ categoria_id: item.categoria_id, es_principal: item.es_principal })) || [],
        ingredientes: producto.ingredientes?.map((item) => ({
          ingrediente_id: item.ingrediente_id,
          cantidad: Number(item.cantidad),
          unidad_medida: item.unidad_medida,
          orden: item.orden,
          es_removible: item.es_removible,
          es_opcional: item.es_opcional,
        })) || [],
      })
      return
    }

    const defaultCategoryId = categorias[0]?.id
    setForm({
      ...empty,
      categorias: defaultCategoryId ? [{ categoria_id: defaultCategoryId, es_principal: true }] : [],
    })
  }, [producto, categorias])

  const selectedIngredienteConfigs = useMemo<ProductoDetalleConfig[]>(() => {
    return (form.ingredientes || []).map((item) => ({
      ...item,
      ingrediente: ingredientes.find((ing) => ing.id === item.ingrediente_id)!,
    })).filter((item) => item.ingrediente)
  }, [form.ingredientes, ingredientes])

  const costoCalculado = useMemo(() => calcularCostoProducto(selectedIngredienteConfigs), [selectedIngredienteConfigs])
  const stockMaximo = useMemo(() => calcularStockMaximoProducto(selectedIngredienteConfigs), [selectedIngredienteConfigs])
  const precioFinal = useMemo(() => Number((form.precio_venta * (1 - (form.descuento_porcentaje || 0) / 100)).toFixed(2)), [form.precio_venta, form.descuento_porcentaje])

  const setField = (field: keyof ProductoCreateInput) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const value = e.target.type === 'number' ? Number(e.target.value) : e.target.value
    setForm((prev) => ({ ...prev, [field]: value }))
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
        categorias: [...categoriasConfig, { categoria_id: categoriaId, es_principal: categoriasConfig.length === 0 }],
      }
    })
  }

  const isCategoriaSelected = (categoriaId: number) => (form.categorias || []).some((item) => item.categoria_id === categoriaId)
  const categoriaPrincipalId = (form.categorias || []).find((item) => item.es_principal)?.categoria_id ?? null

  const setCategoriaPrincipal = (categoriaId: number) => {
    setForm((prev) => ({
      ...prev,
      categorias: (prev.categorias || []).map((item) => ({ ...item, es_principal: item.categoria_id === categoriaId })),
    }))
  }

  const updateIngredienteConfig = (ingredienteId: number, updater: (current: ProductoDetalleInput) => ProductoDetalleInput) => {
    setForm((prev) => ({
      ...prev,
      ingredientes: (prev.ingredientes || []).map((item) => item.ingrediente_id === ingredienteId ? updater(item) : item),
    }))
  }

  const removeIngrediente = (ingredienteId: number) => {
    setForm((prev) => ({ ...prev, ingredientes: (prev.ingredientes || []).filter((item) => item.ingrediente_id !== ingredienteId) }))
  }

  const toggleIngredienteFabricado = (ingrediente: Ingrediente) => {
    setForm((prev) => {
      const exists = (prev.ingredientes || []).some((item) => item.ingrediente_id === ingrediente.id)
      if (exists) {
        return { ...prev, ingredientes: (prev.ingredientes || []).filter((item) => item.ingrediente_id !== ingrediente.id) }
      }
      return {
        ...prev,
        ingredientes: [...(prev.ingredientes || []), buildIngredienteInput(ingrediente, (prev.ingredientes?.length || 0) + 1)],
      }
    })
  }

  const setIngredienteReventa = (ingredienteId: number) => {
    const ingrediente = ingredientes.find((item) => item.id === ingredienteId)
    if (!ingrediente) return
    setForm((prev) => ({ ...prev, ingredientes: [buildIngredienteInput(ingrediente, 1)] }))
  }

  const handleTipoProductoChange = (tipo: TipoProducto) => {
    setForm((prev) => ({
      ...prev,
      tipo_producto: tipo,
      ingredientes: tipo === 'REVENTA' ? prev.ingredientes.slice(0, 1) : prev.ingredientes,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!form.nombre.trim()) return setError('El nombre es requerido')
    if (!form.codigo.trim()) return setError('El código es requerido')
    if (form.precio_venta <= 0) return setError('El precio de venta debe ser mayor a 0')
    if (form.descuento_porcentaje < 0 || form.descuento_porcentaje > 100) return setError('El descuento debe estar entre 0 y 100')
    if (!form.categorias.length) return setError('Seleccioná al menos una categoría')
    if (!form.categorias.some((item) => item.es_principal)) return setError('Definí una categoría principal')
    if (!form.ingredientes.length) return setError('Debés cargar al menos un ingrediente')
    if (form.tipo_producto === 'REVENTA' && form.ingredientes.length !== 1) return setError('Un producto de reventa debe tener exactamente un ingrediente asociado')
    if ((form.ingredientes || []).some((item) => item.cantidad <= 0)) return setError('Todas las cantidades deben ser mayores a 0')

    try {
      if (isEdit) {
        const updateData: ProductoUpdateInput = {
          ...form,
          ingredientes: form.ingredientes?.map((item) => {
            const ing = ingredientes.find((i) => i.id === item.ingrediente_id)
            return { ...item, unidad_medida: ing?.unidad_medida || item.unidad_medida }
          }),
        }
        await updateMutation.mutateAsync({ id: producto!.id, data: updateData })
      } else {
        await createMutation.mutateAsync(form)
      }
      navigate('/catalogo')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al guardar el producto')
    }
  }

  const ingredienteSeleccionadoReventa = form.ingredientes[0]?.ingrediente_id ?? null

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
        <button onClick={() => navigate('/catalogo')} className="text-sm text-gray-600 underline hover:text-gray-800">Volver al catálogo</button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6">
        <div className="bg-white rounded-lg shadow-md">
          <form onSubmit={handleSubmit} className="px-6 py-6 flex flex-col gap-5">
            {error && <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                <input type="text" required value={form.nombre} onChange={setField('nombre')} className="w-full rounded border border-gray-300 px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Código *</label>
                <input type="text" required value={form.codigo} onChange={setField('codigo')} className="w-full rounded border border-gray-300 px-3 py-2 text-sm" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de producto *</label>
                <select value={form.tipo_producto} onChange={(e) => handleTipoProductoChange(e.target.value as TipoProducto)} className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                  <option value="FABRICADO">Fabricado</option>
                  <option value="REVENTA">Reventa</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Precio de venta *</label>
                <input type="number" min="0.01" step="0.01" value={form.precio_venta} onChange={setField('precio_venta')} className="w-full rounded border border-gray-300 px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descuento %</label>
                <input type="number" min="0" max="100" step="0.01" value={form.descuento_porcentaje} onChange={setField('descuento_porcentaje')} className="w-full rounded border border-gray-300 px-3 py-2 text-sm" />
              </div>
            </div>

            <label className="inline-flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" checked={form.disponible} onChange={(e) => setForm((prev) => ({ ...prev, disponible: e.target.checked }))} className="w-4 h-4 rounded accent-blue-500" />
              Mostrar producto como disponible en catálogo
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <textarea rows={2} value={form.descripcion} onChange={setField('descripcion')} className="w-full rounded border border-gray-300 px-3 py-2 text-sm resize-none" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categorías *</label>
              <div className="max-h-48 overflow-y-auto rounded border border-gray-300 px-3 py-2">
                {categorias.map((categoria) => (
                  <div key={categoria.id} className="border-b border-gray-100 py-2 last:border-b-0">
                    <label className="flex items-center gap-2 text-sm text-gray-700">
                      <input type="checkbox" checked={isCategoriaSelected(categoria.id)} onChange={() => toggleCategoria(categoria.id)} className="w-4 h-4 rounded accent-blue-500" />
                      {categoria.nombre}
                    </label>
                    {isCategoriaSelected(categoria.id) && (
                      <label className="ml-6 mt-2 inline-flex items-center gap-2 text-xs text-gray-600">
                        <input type="radio" name="categoria_principal" checked={categoriaPrincipalId === categoria.id} onChange={() => setCategoriaPrincipal(categoria.id)} className="w-4 h-4 accent-blue-500" />
                        Categoría principal
                      </label>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Detalle de ingredientes *</label>
              {form.tipo_producto === 'FABRICADO' ? (
                <div className="rounded border border-gray-300 p-3">
                  <div className="mb-3 max-h-52 overflow-y-auto space-y-2">
                    {ingredientes.map((ingrediente) => {
                      const selected = (form.ingredientes || []).some((item) => item.ingrediente_id === ingrediente.id)
                      return (
                        <label key={ingrediente.id} className="flex items-center gap-2 text-sm text-gray-700">
                          <input type="checkbox" checked={selected} onChange={() => toggleIngredienteFabricado(ingrediente)} className="w-4 h-4 rounded accent-blue-500" />
                          <span>{ingrediente.nombre}</span>
                          <span className="text-xs text-gray-400">{ingrediente.unidad_medida} · stock {Math.round(Number(ingrediente.stock_actual))}</span>
                        </label>
                      )
                    })}
                  </div>

                  {selectedIngredienteConfigs.length > 0 && (
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-sm">
                        <thead>
                          <tr className="text-left text-gray-500">
                            <th className="pb-2 pr-3">Ingrediente</th>
                            <th className="pb-2 pr-3">Cantidad</th>
                            <th className="pb-2 pr-3">Unidad</th>
                            <th className="pb-2 pr-3">Orden</th>
                            <th className="pb-2 pr-3">Opcional</th>
                            <th className="pb-2 pr-3">Removible</th>
                            <th className="pb-2 text-right">Acción</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedIngredienteConfigs.map((item) => (
                            <tr key={item.ingrediente_id} className="border-t border-gray-100">
                              <td className="py-2 pr-3">
                                <div className="font-medium text-gray-800">{item.ingrediente.nombre}</div>
                                <div className="text-xs text-gray-400">Costo ${Number(item.ingrediente.costo_unitario).toFixed(1)}</div>
                              </td>
                              <td className="py-2 pr-3"><input type="number" min="0.1" step={item.ingrediente.permite_fraccion ? '0.1' : '1'} value={item.cantidad} onChange={(e) => updateIngredienteConfig(item.ingrediente_id, (current) => ({ ...current, cantidad: Number(e.target.value), unidad_medida: item.ingrediente.unidad_medida }))} className="w-24 rounded border border-gray-300 px-2 py-1" /></td>
                              <td className="py-2 pr-3"><input type="text" disabled value={item.ingrediente.unidad_medida} className="w-28 rounded border border-gray-200 bg-gray-50 px-2 py-1 text-gray-500" /></td>
                              <td className="py-2 pr-3"><input type="number" min="1" step="1" value={item.orden} onChange={(e) => updateIngredienteConfig(item.ingrediente_id, (current) => ({ ...current, orden: Number(e.target.value) }))} className="w-20 rounded border border-gray-300 px-2 py-1" /></td>
                              <td className="py-2 pr-3"><input type="checkbox" checked={item.es_opcional} onChange={(e) => updateIngredienteConfig(item.ingrediente_id, (current) => ({ ...current, es_opcional: e.target.checked }))} className="w-4 h-4 accent-blue-500" /></td>
                              <td className="py-2 pr-3"><input type="checkbox" checked={item.es_removible} onChange={(e) => updateIngredienteConfig(item.ingrediente_id, (current) => ({ ...current, es_removible: e.target.checked }))} className="w-4 h-4 accent-blue-500" /></td>
                              <td className="py-2 text-right"><button type="button" onClick={() => removeIngrediente(item.ingrediente_id)} className="text-xs text-red-600 hover:text-red-800">Quitar</button></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded border border-gray-300 p-3 space-y-2">
                  <p className="text-sm text-gray-600">Producto de reventa: elegí exactamente un ingrediente base de stock.</p>
                  <div className="max-h-52 overflow-y-auto space-y-2">
                    {ingredientes.map((ingrediente) => (
                      <label key={ingrediente.id} className="flex items-center gap-2 text-sm text-gray-700">
                        <input type="radio" name="ingrediente_reventa" checked={ingredienteSeleccionadoReventa === ingrediente.id} onChange={() => setIngredienteReventa(ingrediente.id)} className="w-4 h-4 accent-blue-500" />
                        <span>{ingrediente.nombre}</span>
                        <span className="text-xs text-gray-400">{ingrediente.unidad_medida} · stock {Math.round(Number(ingrediente.stock_actual))}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button type="button" onClick={() => navigate('/catalogo')} className="flex-1 rounded border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Cancelar</button>
              <button type="submit" disabled={isPending} className="flex-1 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
                {isPending ? 'Guardando...' : isEdit ? 'Guardar cambios' : 'Crear producto'}
              </button>
            </div>
          </form>
        </div>

        <aside className="h-fit rounded-lg bg-white p-4 shadow-md">
          <h2 className="mb-3 text-lg font-semibold text-gray-800">Resumen del producto</h2>
          <div className="space-y-2 text-sm text-gray-700">
            <p><span className="font-medium">Tipo:</span> {form.tipo_producto}</p>
            <p><span className="font-medium">Ingredientes:</span> {selectedIngredienteConfigs.length}</p>
            <p><span className="font-medium">Costo calculado:</span> ${costoCalculado.toFixed(2)}</p>
            <p><span className="font-medium">Precio final:</span> ${precioFinal.toFixed(2)}</p>
            <p><span className="font-medium">Máximo producible:</span> {stockMaximo}</p>
          </div>
        </aside>
      </div>
    </div>
  )
}
