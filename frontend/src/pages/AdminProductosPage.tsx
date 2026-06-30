import React, { useCallback, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { useProductos, useDarDeBaja, useReactivar, useToggleDisponibilidad } from '@hooks/useProductos'
import { useWebSocket, WsMessage } from '@hooks/useWebSocket'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'
import { Producto } from '@models/index'
import { useAuthStore } from '@store/authStore'
import { hasAnyRole } from '@/auth/permissions'
import { getCloudinaryProductImageUrl, getProductoImagenPrincipal, getProductoPrecioFinal, getProductoStockDisponible } from '@/utils/producto'

type MargenEstilo = { badge: string; text: string; label: string }

function getMargenEstilo(producto: Producto): MargenEstilo | null {
  const costo = Number(producto.precio_costo_calculado) || 0
  if (costo <= 0) return null
  const precioFinal = getProductoPrecioFinal(producto)
  const margen = ((precioFinal - costo) / costo) * 100
  if (margen <= 0) return { badge: 'bg-red-100 text-red-700', text: 'text-red-700', label: `${margen.toFixed(0)}%` }
  if (margen < 20) return { badge: 'bg-orange-100 text-orange-700', text: 'text-orange-700', label: `+${margen.toFixed(0)}%` }
  return { badge: 'bg-green-100 text-green-700', text: 'text-green-700', label: `+${margen.toFixed(0)}%` }
}

export const AdminProductosPage: React.FC = () => {
  const usuario = useAuthStore((state) => state.usuario)
  const isAdmin = hasAnyRole(usuario?.roles, ['ADMIN'])
  const canToggleDisponibilidad = hasAnyRole(usuario?.roles, ['ADMIN', 'STOCK'])
  const qc = useQueryClient()

  const handleWsMessage = useCallback((msg: WsMessage) => {
    if (msg.event === 'productos_updated') {
      qc.invalidateQueries({ queryKey: ['productos'] })
    }
  }, [qc])

  useWebSocket({ enabled: isAdmin, onMessage: handleWsMessage })

  const { data: productosData, isLoading, error } = useProductos({
    page: 1,
    size: 100,
    incluir_baja: true,
  })

  const bajaMutation = useDarDeBaja()
  const reactivarMutation = useReactivar()
  const disponibilidadMutation = useToggleDisponibilidad()

  const handleBaja = (producto: Producto) => {
    if (!window.confirm(`Dar de baja el producto "${producto.nombre}"?`)) return
    bajaMutation.mutate(producto.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo dar de baja el producto')
      },
    })
  }

  const handleReactivar = (producto: Producto) => {
    if (!window.confirm(`Reactivar el producto "${producto.nombre}"?`)) return
    reactivarMutation.mutate(producto.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo reactivar el producto')
      },
    })
  }

  const handleToggleDisponibilidad = (producto: Producto) => {
    const nextLabel = producto.disponible ? 'marcar como no disponible' : 'marcar como disponible'
    if (!window.confirm(`${nextLabel} el producto "${producto.nombre}"?`)) return
    disponibilidadMutation.mutate(producto.id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo actualizar la disponibilidad')
      },
    })
  }

  const [busqueda, setBusqueda] = useState('')
  const [categoriaFiltro, setCategoriaFiltro] = useState<number | null>(null)

  const categoriasDisponibles = useMemo(() => {
    const map = new Map<number, string>()
    ;(productosData?.items ?? []).forEach((p) => {
      p.categorias?.forEach((c) => {
        if (!map.has(c.categoria_id)) map.set(c.categoria_id, c.categoria.nombre)
      })
    })
    return [...map.entries()].sort((a, b) => a[1].localeCompare(b[1]))
  }, [productosData])

  const hayFiltros = busqueda.trim() !== '' || categoriaFiltro !== null

  const productos = useMemo(() => {
    const lista = [...(productosData?.items ?? [])]
    lista.sort((a, b) => a.nombre.localeCompare(b.nombre))
    return lista.filter((p) => {
      if (busqueda.trim()) {
        const q = busqueda.toLowerCase()
        if (!p.nombre.toLowerCase().includes(q) && !p.codigo.toLowerCase().includes(q)) return false
      }
      if (categoriaFiltro !== null) {
        if (!p.categorias?.some((c) => c.categoria_id === categoriaFiltro)) return false
      }
      return true
    })
  }, [productosData, busqueda, categoriaFiltro])

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error cargando productos</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Productos</h1>
          <p className="text-gray-600">{productos.length} productos</p>
        </div>
        {isAdmin && (
          <Link to="/productos/nuevo">
            <Button>+ Nuevo Producto</Button>
          </Link>
        )}
      </div>

      <div className="mb-4 flex flex-wrap gap-3 items-center">
        <input
          type="text"
          placeholder="Buscar por nombre o código..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="flex-1 min-w-[200px] max-w-sm rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <select
          value={categoriaFiltro ?? ''}
          onChange={(e) => setCategoriaFiltro(e.target.value ? Number(e.target.value) : null)}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">Todas las categorías</option>
          {categoriasDisponibles.map(([id, nombre]) => (
            <option key={id} value={id}>{nombre}</option>
          ))}
        </select>
        {hayFiltros && (
          <button
            onClick={() => { setBusqueda(''); setCategoriaFiltro(null) }}
            className="text-sm text-gray-500 border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
          >
            Limpiar filtros
          </button>
        )}
      </div>

       {isLoading ? (
         <div className="py-12"><Spinner /></div>
       ) : (
         <div className="space-y-6">
           <div className="bg-white rounded-lg shadow-md p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
             <div>
               <p className="text-xs uppercase text-gray-500">Activos</p>
               <p className="text-xl font-semibold text-gray-800">
                 {productos.filter((p) => !p.deleted_at).length}
               </p>
             </div>
             <div>
               <p className="text-xs uppercase text-gray-500">En baja</p>
               <p className="text-xl font-semibold text-gray-800">
                 {productos.filter((p) => p.deleted_at).length}
               </p>
             </div>
             <div>
               <p className="text-xs uppercase text-gray-500">Disponibles</p>
               <p className="text-xl font-semibold text-gray-800">
                 {productos.filter((p) => p.disponible).length}
               </p>
             </div>
             <div>
               <p className="text-xs uppercase text-gray-500">No disponibles</p>
               <p className="text-xl font-semibold text-gray-800">
                 {productos.filter((p) => !p.disponible).length}
               </p>
             </div>
           </div>

            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <table className="w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                     <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                       Imagen
                     </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                     <th className="w-28 px-5 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                       Estado
                     </th>
                    <th className="w-20 px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Disponible
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Producto
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Código
                    </th>
                     <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                       Tipo / stock
                     </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Costo producción
                    </th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Precio de venta
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {productos.map((producto) => (
                     <tr key={producto.id} className="hover:bg-gray-50">
                       <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                         {getProductoImagenPrincipal(producto) ? (
                           <img
                             src={getCloudinaryProductImageUrl(getProductoImagenPrincipal(producto), 'f_auto,q_auto,c_fill,w_160,h_96') || ''}
                            alt={producto.nombre}
                            className="h-14 w-20 rounded object-cover border border-gray-200"
                          />
                        ) : (
                          <div className="h-14 w-20 rounded border border-dashed border-gray-300 flex items-center justify-center text-[10px] text-gray-400">
                            Sin imagen
                          </div>
                        )}
                      </td>
                       <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                         {producto.id}
                       </td>
                      <td className={`w-28 px-5 py-4 text-sm text-center font-medium ${producto.deleted_at ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                        {producto.deleted_at ? 'Baja' : 'Activo'}
                      </td>
                      <td className={`w-20 px-3 py-4 text-center text-sm font-medium ${producto.disponible ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700'}`}>
                        {producto.disponible ? 'Sí' : 'No'}
                      </td>
                       <td className="px-4 py-4 text-sm font-medium text-gray-900">
                         <div className="font-semibold">{producto.nombre}</div>
                       </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {producto.codigo}
                      </td>
                       <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                         <div>{producto.tipo_producto}</div>
                         <div className="text-xs text-gray-400">Disp.: {getProductoStockDisponible(producto)}</div>
                       </td>
                       <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                         ${(Number(producto.precio_costo_calculado) || 0).toFixed(2)}
                       </td>
                       <td className="px-2 py-4 whitespace-nowrap text-sm">
                         {(() => {
                           const margenEstilo = getMargenEstilo(producto)
                           const precio = getProductoPrecioFinal(producto)
                          return (
                            <div>
                              <div className={margenEstilo ? `font-medium ${margenEstilo.text}` : 'text-gray-700'}>
                                ${precio.toFixed(2)}
                              </div>
                              {margenEstilo && (
                                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium mt-0.5 ${margenEstilo.badge}`}>
                                  {margenEstilo.label}
                                </span>
                              )}
                            </div>
                          )
                        })()}
                      </td>
                       <td className="px-4 py-4 text-sm font-medium">
                         <div className="flex items-center justify-end gap-3 whitespace-nowrap">
                           {isAdmin && (
                             <Link
                               to={`/productos/editar/${producto.id}`}
                               className="text-blue-600 hover:text-blue-900"
                             >
                               Editar
                             </Link>
                           )}
                           {canToggleDisponibilidad && (
                             <button
                               onClick={() => handleToggleDisponibilidad(producto)}
                               className="text-amber-600 hover:text-amber-900"
                             >
                               {producto.disponible ? 'No disponible' : 'Disponible'}
                             </button>
                           )}
                           {isAdmin && (
                             producto.deleted_at ? (
                               <button
                                 onClick={() => handleReactivar(producto)}
                                 className="text-emerald-600 hover:text-emerald-900"
                               >
                                 Reactivar
                               </button>
                             ) : (
                               <button
                                 onClick={() => handleBaja(producto)}
                                 className="text-red-600 hover:text-red-900"
                               >
                                 Dar de baja
                               </button>
                             )
                           )}
                         </div>
                       </td>
                   </tr>
                 ))}
               </tbody>
              </table>
            </div>
         </div>
       )}
    </div>
  )
}
