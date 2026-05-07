import React from 'react'
import { Card } from '@components/Card'
import { Producto } from '@types/index'

interface ProductCardProps {
  producto: Producto
  onEdit?: (producto: Producto) => void
  onDarDeBaja?: (id: number) => void
}

export const ProductCard: React.FC<ProductCardProps> = ({ producto, onEdit, onDarDeBaja }) => {
  const isDeleted = producto.deleted_at != null
  const stockDisplay = producto.stock_cantidad > 0 ? `${producto.stock_cantidad} en stock` : 'Sin stock'
  const stockColor = producto.stock_cantidad > 0 ? 'text-green-600' : 'text-red-600'

  return (
    <Card className={`h-full flex flex-col ${isDeleted ? 'bg-red-50 border-red-300' : ''}`}>
      {isDeleted && (
        <div className="mb-2">
          <span className="inline-block bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded">
            DADO DE BAJA
          </span>
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

        {producto.categoria && (
          <p className="text-xs text-gray-500 mb-2">
            {producto.categoria.nombre}
          </p>
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
          </div>
        </div>

        <div className="mt-2 text-xs text-gray-500">
          Código: {producto.codigo}
        </div>

        {!isDeleted && (onEdit || onDarDeBaja) && (
          <div className="flex gap-2 mt-3">
            {onEdit && (
              <button
                onClick={() => onEdit(producto)}
                className="flex-1 text-xs bg-blue-50 text-blue-600 border border-blue-200 rounded px-2 py-1 hover:bg-blue-100"
              >
                Editar
              </button>
            )}
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
