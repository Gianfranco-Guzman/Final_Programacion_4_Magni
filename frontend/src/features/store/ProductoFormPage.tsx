import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Categoria, Ingrediente, Producto, ProductoDetalleConfig, TipoProducto } from '@models/index'
import { useCreateProducto, useUpdateProducto } from '@hooks/useProductos'
import { useDeleteImagen, useUploadImagen } from '@hooks/useUploads'
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
  imagenes_url: [],
  categorias: [],
  ingredientes: [],
}

const deriveCloudinaryPublicId = (url: string): string | null => {
  const marker = '/upload/'
  const uploadIndex = url.indexOf(marker)
  if (uploadIndex === -1) return null

  const afterUpload = url.slice(uploadIndex + marker.length)
  const segments = afterUpload.split('/').filter(Boolean)
  if (segments.length === 0) return null

  const cleanedSegments = segments[0].startsWith('v') && /^v\d+$/.test(segments[0])
    ? segments.slice(1)
    : segments
  if (cleanedSegments.length === 0) return null

  const fileName = cleanedSegments[cleanedSegments.length - 1].replace(/\.[^.]+$/, '')
  return [...cleanedSegments.slice(0, -1), fileName].join('/')
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
  const [ingredientSearch, setIngredientSearch] = useState('')

  const createMutation = useCreateProducto()
  const updateMutation = useUpdateProducto()
  const uploadMutation = useUploadImagen()
  const deleteImagenMutation = useDeleteImagen()
  const isPending = createMutation.isPending || updateMutation.isPending || uploadMutation.isPending || deleteImagenMutation.isPending

  useEffect(() => {
    if (producto) {
      setForm({
        nombre: producto.nombre,
        codigo: producto.codigo,
        precio_venta: Number(producto.precio_venta) || 0,
        descripcion: producto.descripcion || '',
        disponible: producto.disponible,
        tipo_producto: producto.tipo_producto,
        descuento_porcentaje: Number(producto.descuento_porcentaje) || 0,
        imagenes_url: producto.imagenes_url || [],
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

    setForm({ ...empty })
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
  const precioSugerido = useMemo(() => Number((costoCalculado * 1.15).toFixed(2)), [costoCalculado])
  const ganancia = useMemo(() => Number((form.precio_venta - costoCalculado).toFixed(2)), [form.precio_venta, costoCalculado])

  const sortedCategorias = useMemo(
    () => [...categorias].sort((a, b) => a.nombre.localeCompare(b.nombre)),
    [categorias],
  )

  const leafCategorias = useMemo(() => {
    const parentIds = new Set(categorias.filter((c) => c.parent_id != null).map((c) => c.parent_id!))
    return sortedCategorias.filter((c) => !parentIds.has(c.id))
  }, [sortedCategorias, categorias])

  const sortedIngredientes = useMemo(
    () => [...ingredientes].sort((a, b) => a.nombre.localeCompare(b.nombre)),
    [ingredientes],
  )

  const filteredIngredientes = useMemo(() => {
    if (!ingredientSearch.trim()) return sortedIngredientes
    const q = ingredientSearch.toLowerCase()
    return sortedIngredientes.filter((ing) => ing.nombre.toLowerCase().includes(q))
  }, [sortedIngredientes, ingredientSearch])

  const setField = (field: keyof ProductoCreateInput) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const value = e.target.type === 'number' ? Number(e.target.value) : e.target.value
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleUploadImagen = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')

    try {
      const uploaded = await uploadMutation.mutateAsync({ file, folder: 'foodstore/productos' })
      setForm((prev) => ({
        ...prev,
        imagenes_url: [...(prev.imagenes_url || []), uploaded.secure_url],
      }))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al subir la imagen')
    } finally {
      e.target.value = ''
    }
  }

  const handleRemoveImagen = async (url: string) => {
    setError('')
    const publicId = deriveCloudinaryPublicId(url)

    try {
      if (publicId) {
        await deleteImagenMutation.mutateAsync(publicId)
      }
      setForm((prev) => ({
        ...prev,
        imagenes_url: (prev.imagenes_url || []).filter((item) => item !== url),
      }))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al eliminar la imagen')
    }
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
          imagenes_url: form.imagenes_url || [],
          ingredientes: form.ingredientes?.map((item) => {
            const ing = ingredientes.find((i) => i.id === item.ingrediente_id)
            return { ...item, unidad_medida: ing?.unidad_medida || item.unidad_medida }
          }),
        }
        await updateMutation.mutateAsync({ id: producto!.id, data: updateData })
      } else {
        await createMutation.mutateAsync({
          ...form,
          imagenes_url: form.imagenes_url || [],
        })
      }
      navigate('/admin/productos')
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de producto *</label>
              <select value={form.tipo_producto} onChange={(e) => handleTipoProductoChange(e.target.value as TipoProducto)} className="w-full rounded border border-gray-300 px-3 py-2 text-sm">
                <option value="FABRICADO">Fabricado</option>
                <option value="REVENTA">Reventa</option>
              </select>
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Imágenes del producto</label>
              <div className="rounded border border-gray-300 p-3 flex flex-col gap-3">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleUploadImagen}
                  disabled={uploadMutation.isPending}
                  className="block w-full text-sm text-gray-700"
                />
                <p className="text-xs text-gray-500">
                  Formatos permitidos: JPG, PNG, WEBP. Máximo 5 MB.
                </p>
                {(form.imagenes_url || []).length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {(form.imagenes_url || []).map((url) => (
                      <div key={url} className="rounded border border-gray-200 p-2">
                        <img src={url} alt="Producto" className="w-full h-28 object-cover rounded" />
                        <button
                          type="button"
                          onClick={() => handleRemoveImagen(url)}
                          disabled={deleteImagenMutation.isPending}
                          className="mt-2 w-full text-xs text-red-600 hover:text-red-800 disabled:opacity-50"
                        >
                          Eliminar imagen
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categorías *</label>
              <div className="max-h-48 overflow-y-auto rounded border border-gray-300 px-3 py-2">
                {leafCategorias.map((categoria) => (
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
                  <input
                    type="text"
                    placeholder="Buscar ingrediente..."
                    value={ingredientSearch}
                    onChange={(e) => setIngredientSearch(e.target.value)}
                    className="mb-2 w-full rounded border border-gray-300 px-3 py-1.5 text-sm"
                  />
                  <div className="mb-3 max-h-52 overflow-y-auto space-y-2">
                    {filteredIngredientes.map((ingrediente) => {
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
                              <td className="py-2 pr-3"><input type="number" min={item.ingrediente.permite_fraccion ? '0.1' : '1'} step={item.ingrediente.permite_fraccion ? '0.1' : '1'} value={item.cantidad} onChange={(e) => updateIngredienteConfig(item.ingrediente_id, (current) => ({ ...current, cantidad: Number(e.target.value), unidad_medida: item.ingrediente.unidad_medida }))} className="w-24 rounded border border-gray-300 px-2 py-1" /></td>
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
                    {sortedIngredientes.map((ingrediente) => (
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

            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Precio de venta</p>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Costo de producción</p>
                  <p className="text-2xl font-bold text-gray-700">${costoCalculado.toFixed(2)}</p>
                  <p className="text-xs text-gray-400 mt-0.5">calculado automáticamente</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Precio sugerido (+15%)</p>
                  <p className="text-2xl font-bold text-indigo-600">${precioSugerido.toFixed(2)}</p>
                  <p className="text-xs text-gray-400 mt-0.5">referencia de ganancia</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Tu precio de venta *</p>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    required
                    value={form.precio_venta}
                    onChange={setField('precio_venta')}
                    className={`w-full text-center text-2xl font-bold rounded border px-2 py-1 focus:outline-none focus:ring-2 ${
                      costoCalculado > 0 && form.precio_venta > 0 && form.precio_venta < costoCalculado
                        ? 'border-red-300 bg-red-50 text-red-700 focus:ring-red-200'
                        : costoCalculado > 0 && form.precio_venta >= precioSugerido
                          ? 'border-green-300 bg-green-50 text-green-700 focus:ring-green-200'
                          : 'border-gray-300 bg-white text-gray-800 focus:ring-blue-200'
                    }`}
                  />
                  {costoCalculado > 0 && form.precio_venta > 0 && form.precio_venta < costoCalculado && (
                    <p className="text-xs text-red-600 mt-1">Por debajo del costo de producción</p>
                  )}
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-200 flex items-center gap-3">
                <label className="text-xs font-medium text-gray-500 whitespace-nowrap">Descuento (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={form.descuento_porcentaje}
                  onChange={setField('descuento_porcentaje')}
                  className="w-28 rounded border border-gray-300 px-2 py-1 text-sm"
                />
                {form.descuento_porcentaje > 0 && (
                  <span className="text-xs text-gray-500">
                    Precio con descuento: <span className="font-medium text-gray-700">${precioFinal.toFixed(2)}</span>
                  </span>
                )}
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button type="button" onClick={() => navigate('/catalogo')} className="flex-1 rounded border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Cancelar</button>
              <button type="submit" disabled={isPending} className="flex-1 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
                {isPending ? 'Guardando...' : isEdit ? 'Guardar cambios' : 'Crear producto'}
              </button>
            </div>
          </form>
        </div>

        <aside className="h-fit rounded-lg bg-white p-4 shadow-md xl:sticky xl:top-20">
          <h2 className="mb-3 text-lg font-semibold text-gray-800">Resumen</h2>
          <div className="space-y-2 text-sm text-gray-700">
            <p><span className="font-medium">Tipo:</span> {form.tipo_producto}</p>
            <p><span className="font-medium">Ingredientes:</span> {selectedIngredienteConfigs.length}</p>
            <p><span className="font-medium">Máximo producible:</span> {stockMaximo}</p>
          </div>

          <div className="mt-3 pt-3 border-t border-gray-100 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Costo de producción</span>
              <span className="font-medium text-gray-700">${costoCalculado.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Precio de venta</span>
              <span className="font-medium text-gray-700">${form.precio_venta.toFixed(2)}</span>
            </div>
            {form.descuento_porcentaje > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-500">Con descuento ({form.descuento_porcentaje}%)</span>
                <span className="font-medium text-gray-700">${precioFinal.toFixed(2)}</span>
              </div>
            )}
            <div className={`flex justify-between rounded px-2 py-1.5 ${ganancia >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
              <span className={`font-medium ${ganancia >= 0 ? 'text-green-700' : 'text-red-700'}`}>Ganancia</span>
              <span className={`font-bold ${ganancia >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {ganancia >= 0 ? '+' : ''}{ganancia.toFixed(2)}
              </span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
