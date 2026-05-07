import React from 'react'
import { ProductCard } from './ProductCard'
import { Producto } from '@types/index'

interface ProductGridProps {
  productos: Producto[]
  onEdit?: (producto: Producto) => void
  onDarDeBaja?: (id: number) => void
}

export const ProductGrid: React.FC<ProductGridProps> = ({ productos, onEdit, onDarDeBaja }) => {
  if (productos.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay productos disponibles</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {productos.map((producto) => (
        <ProductCard
          key={producto.id}
          producto={producto}
          onEdit={onEdit}
          onDarDeBaja={onDarDeBaja}
        />
      ))}
    </div>
  )
}
