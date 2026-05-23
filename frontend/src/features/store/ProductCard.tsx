import { Link } from 'react-router-dom'
import { Card } from '@components/Card'
import { Producto } from '@models/index'

interface ProductCardProps {
  producto: Producto
  onDarDeBaja?: (id: number) => void
  onReactivar?: (id: number) => void
}

export const ProductCard: React.FC<ProductCardProps> = ({ producto, onDarDeBaja, onReactivar }) => {
  const isDeleted = producto.deleted_at != null
  const isOperationallyAvailable = producto.disponible && producto.stock_cantidad > 0
  const categoriaPrincipal = producto.categorias?.find((item) => item.es_principal)?.categoria
  const categoriasSecundarias = producto.categorias?.filter((item) => !item.es_principal).map((item) => item.categoria.nombre) || []
  const stockDisplay = !producto.disponible
    ? 'No disponible'
    : producto.stock_cantidad > 0
      ? `${producto.stock_cantidad} en stock`
      : 'Sin stock'
  const stockColor = isOperationallyAvailable ? 'text-green-600' : 'text-red-600'

  return (
    <Card className={`h-full flex flex-col ${isDeleted ? 'bg-red-50 border-red-300' : ''}`}>
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

        {categoriasSecundarias.length > 0 && (
          <p className="text-xs text-gray-400 mb-2">
            También en: {categoriasSecundarias.join(', ')}
          </p>
        )}

        {producto.ingredientes && producto.ingredientes.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {producto.ingredientes.slice(0, 3).map((item) => (
              <span
                key={item.ingrediente_id}
                className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium ${
                  item.ingrediente.es_alergeno
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {item.ingrediente.nombre}
              </span>
            ))}
            {producto.ingredientes.length > 3 && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                +{producto.ingredientes.length - 3}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="border-t pt-3 mt-3">
        <div className="flex justify-between items-end">
          <div>
            <p className="text-2xl font-bold text-blue-600">
              ${producto.precio.toFixed(2)}
            </p>
            <p className={`text-xs ${stockColor} font-medium`}>
              {stockDisplay}
            </p>
            {!producto.disponible && (
              <p className="text-xs text-amber-600 font-medium mt-1">
                Oculto del flujo de compra
              </p>
            )}
          </div>
        </div>

        <div className="mt-2 text-xs text-gray-500">
          Código: {producto.codigo}
        </div>

        {!isDeleted && (onDarDeBaja) && (
          <div className="flex gap-2 mt-3">
            <Link
              to={`/productos/editar/${producto.id}`}
              className="flex-1 text-center text-xs bg-blue-50 text-blue-600 border border-blue-200 rounded px-2 py-1 hover:bg-blue-100"
            >
              Editar
            </Link>
            {onDarDeBaja && (
              <button
                onClick={() => onDarDeBaja(producto.id)}
                className="flex-1 text-xs bg-red-50 text-red-600 border border-red-200 rounded px-2 py-1 hover:bg-red-100"
              >
                Dar de baja
              </button>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}
