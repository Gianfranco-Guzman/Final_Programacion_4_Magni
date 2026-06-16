import { ProductCard } from './ProductCard'
import { Producto } from '@models/index'

interface ProductGridProps {
  productos: Producto[]
  onDarDeBaja?: (id: number) => void
  onReactivar?: (id: number) => void
  onAgregarAlCarrito?: (producto: Producto) => void
}

export const ProductGrid: React.FC<ProductGridProps> = ({ productos, onDarDeBaja, onReactivar, onAgregarAlCarrito }) => {
  if (productos.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay productos disponibles</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-start">
      {productos.map((producto) => (
        <ProductCard
          key={producto.id}
          producto={producto}
          onDarDeBaja={onDarDeBaja}
          onReactivar={onReactivar}
          onAgregarAlCarrito={onAgregarAlCarrito}
        />
      ))}
    </div>
  )
}
