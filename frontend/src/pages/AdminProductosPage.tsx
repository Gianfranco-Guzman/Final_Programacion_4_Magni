import React from 'react'
import { Link } from 'react-router-dom'
import { useProductos, useDarDeBaja, useReactivar, useToggleDisponibilidad } from '@hooks/useProductos'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'
import { Producto } from '@models/index'
import { useAuthStore } from '@store/authStore'
import { hasAnyRole } from '@/auth/permissions'

export const AdminProductosPage: React.FC = () => {
  const usuario = useAuthStore((state) => state.usuario)
  const isAdmin = hasAnyRole(usuario?.roles, ['ADMIN'])
  const canToggleDisponibilidad = hasAnyRole(usuario?.roles, ['ADMIN', 'STOCK'])
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

  const productos = productosData?.items ?? []

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
                     Disponible
                   </th>
                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                     Producto
                   </th>
                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                     Código
                   </th>
                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                     Stock
                   </th>
                   <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                     Acciones
                   </th>
                 </tr>
               </thead>
               <tbody className="bg-white divide-y divide-gray-200">
                 {productos.map((producto) => (
                   <tr key={producto.id} className="hover:bg-gray-50">
                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                       {producto.id}
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap text-sm">
                       {producto.deleted_at ? (
                         <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                           Baja
                         </span>
                       ) : (
                         <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                           Activo
                         </span>
                       )}
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap text-sm">
                       {producto.disponible ? (
                         <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                           Sí
                         </span>
                       ) : (
                         <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                           No
                         </span>
                       )}
                     </td>
                     <td className="px-6 py-4 text-sm font-medium text-gray-900">
                       <div className="font-semibold">{producto.nombre}</div>
                       <div className="text-xs text-gray-500">${producto.precio.toFixed(2)}</div>
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                       {producto.codigo}
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                       {producto.stock_cantidad}
                     </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {isAdmin && (
                          <Link
                            to={`/productos/editar/${producto.id}`}
                            className="text-blue-600 hover:text-blue-900 mr-3"
                          >
                            Editar
                          </Link>
                        )}
                        {canToggleDisponibilidad && (
                          <button
                            onClick={() => handleToggleDisponibilidad(producto)}
                            className="text-amber-600 hover:text-amber-900 mr-3"
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
