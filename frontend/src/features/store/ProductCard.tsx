import React from 'react'
import { Card } from '@components/Card'
import { Producto } from '@types/index'

interface ProductCardProps {
  producto: Producto
}

export const ProductCard: React.FC<ProductCardProps> = ({ producto }) => {
  const stockDisplay = producto.stock_cantidad > 0 ? `${producto.stock_cantidad} en stock` : 'Sin stock'
  const stockColor = producto.stock_cantidad > 0 ? 'text-green-600' : 'text-red-600'

  return (
    <Card className="h-full flex flex-col">
      <div className="mb-3">
        <div className="w-full h-40 bg-gray-200 rounded-lg flex items-center justify-center mb-2">
          <span className="text-gray-400 text-center px-2">Sin imagen</span>
        </div>
      </div>

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
      </div>
    </Card>
  )
}
