import { Link } from 'react-router-dom'
import { Card } from '@components/Card'
import { Producto } from '@models/index'
import { getCloudinaryProductImageUrl, getProductoImagenPrincipal, getProductoPrecioBase, getProductoPrecioFinal, getProductoStockDisponible, isProductoOperativamenteDisponible } from '@/utils/producto'

interface ProductCardProps {
  producto: Producto
  onDarDeBaja?: (id: number) => void
  onReactivar?: (id: number) => void
  onAgregarAlCarrito?: (producto: Producto) => void
}

export const ProductCard: React.FC<ProductCardProps> = ({ producto, onDarDeBaja, onReactivar, onAgregarAlCarrito }) => {
  const isAdminView = !!onDarDeBaja
  const isDeleted = producto.deleted_at != null
  const isOperationallyAvailable = isProductoOperativamenteDisponible(producto)
  const categoriaPrincipal = producto.categorias?.find((item) => item.es_principal)?.categoria
  const alergenos = producto.ingredientes?.filter((item) => item.ingrediente?.es_alergeno).map((item) => item.ingrediente!.nombre) || []
  const precioFinal = getProductoPrecioFinal(producto)
  const precioBase = getProductoPrecioBase(producto)
  const stockDisponible = getProductoStockDisponible(producto)
  const imagenPrincipal = getCloudinaryProductImageUrl(getProductoImagenPrincipal(producto), 'f_auto,q_auto,c_fill,w_600,h_320')

  return (
    <Card className={`h-full flex flex-col ${isDeleted ? 'bg-red-50 border-red-300' : ''}`}>
      {imagenPrincipal && (
        <div className="mb-3 overflow-hidden rounded-lg border border-gray-100">
          <img src={imagenPrincipal} alt={producto.nombre} className="h-40 w-full object-cover" />
        </div>
      )}
      {isDeleted && (
        <div className="flex items-center justify-between mb-2">
          <span className="inline-block bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded">
            DADO DE BAJA
          </span>
          {onReactivar && (
            <button
              onClick={() => onReactivar(producto.id)}
              className="text-xs bg-green-50 text-green-700 border border-green-300 rounded px-2 py-0.5 hover:bg-green-100"
            >
              Reactivar
            </button>
          )}
        </div>
      )}

      <div className="flex-1">
        <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
          {producto.nombre}
        </h3>

        {producto.descripcion && (
          <p className="text-xs text-gray-600 mb-2 line-clamp-2">
            {producto.descripcion}
          </p>
        )}

        {categoriaPrincipal && (
          <p className="text-xs text-gray-500 mb-1">
            {categoriaPrincipal.nombre}
          </p>
        )}

        {producto.ingredientes && producto.ingredientes.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {producto.ingredientes.filter((item) => item.ingrediente).slice(0, 3).map((item) => (
              <span
                key={item.ingrediente_id}
                className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
              >
                {item.ingrediente!.nombre}
              </span>
            ))}
            {producto.ingredientes.length > 3 && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                +{producto.ingredientes.length - 3}
              </span>
            )}
          </div>
        )}

        {alergenos.length > 0 && (
          <p className="text-xs text-red-700 mb-2 font-medium">
            Alérgenos: {alergenos.join(', ')}
          </p>
        )}
      </div>

      <div className="border-t pt-3 mt-3">
        <div className="flex justify-between items-end">
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <p className="text-2xl font-bold text-blue-600">${precioFinal.toFixed(2)}</p>
              {producto.descuento_porcentaje > 0 && (
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-red-100 text-red-700">
                  -{producto.descuento_porcentaje}%
                </span>
              )}
            </div>
            {producto.descuento_porcentaje > 0 && (
              <p className="text-xs text-gray-400 line-through mb-1">${precioBase.toFixed(2)}</p>
            )}
            {isAdminView && <p className="text-xs text-gray-500 mb-1">{producto.tipo_producto}</p>}
            {isAdminView && (
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${isOperationallyAvailable ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {isOperationallyAvailable ? 'Disponible' : 'Sin stock'}
              </span>
            )}
            {isAdminView && <p className="text-xs text-gray-400 mt-1">Stock calculado: {stockDisponible}</p>}
            {isAdminView && !producto.disponible && (
              <p className="text-xs text-amber-600 font-medium mt-1">
                Oculto del flujo de compra
              </p>
            )}
          </div>
        </div>

        {isAdminView && (
          <div className="mt-2 text-xs text-gray-500">
            Código: {producto.codigo}
          </div>
        )}

        {!isDeleted && onAgregarAlCarrito && isOperationallyAvailable && (
          <button
            onClick={() => onAgregarAlCarrito(producto)}
            className="w-full mt-3 bg-blue-600 text-white text-sm font-semibold py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Agregar al carrito
          </button>
        )}

        {!isDeleted && onDarDeBaja && (
          <div className="flex gap-2 mt-3">
            <Link
              to={`/productos/editar/${producto.id}`}
              className="flex-1 text-center text-xs bg-blue-50 text-blue-600 border border-blue-200 rounded px-2 py-1 hover:bg-blue-100"
            >
              Editar
            </Link>
            <button
              onClick={() => onDarDeBaja(producto.id)}
              className="flex-1 text-xs bg-red-50 text-red-600 border border-red-200 rounded px-2 py-1 hover:bg-red-100"
            >
              Dar de baja
            </button>
          </div>
        )}
      </div>
    </Card>
  )
}
