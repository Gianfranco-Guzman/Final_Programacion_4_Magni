import React from 'react'
import { CartItemState, useCartStore } from '@store/cartStore'
import { getProductoPrecioFinal, getProductoStockDisponible } from '@/utils/producto'

interface ItemCarritoProps {
  item: CartItemState
}

export const ItemCarrito: React.FC<ItemCarritoProps> = ({ item }) => {
  const { increase, decrease, removeItem } = useCartStore()
  const precioFinal = getProductoPrecioFinal(item.producto)
  const subtotal = precioFinal * item.cantidad
  const stockDisponible = getProductoStockDisponible(item.producto)

  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-gray-800 truncate">{item.producto.nombre}</p>
        <p className="text-xs text-gray-500">${precioFinal.toFixed(2)} c/u</p>
        <p className="text-[11px] text-gray-400">Disponibles: {stockDisponible}</p>
        <p className="text-sm font-bold text-blue-600 mt-0.5">${subtotal.toFixed(2)}</p>
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={() => decrease(item.producto.id)}
          className="w-7 h-7 flex items-center justify-center rounded border border-gray-300 text-gray-600 hover:bg-gray-100 text-sm font-bold"
        >
          −
        </button>
        <span className="w-6 text-center text-sm font-semibold text-gray-800">{item.cantidad}</span>
          <button
            onClick={() => increase(item.producto.id)}
            disabled={item.cantidad >= stockDisponible}
            className="w-7 h-7 flex items-center justify-center rounded border border-gray-300 text-gray-600 hover:bg-gray-100 text-sm font-bold"
          >
          +
        </button>
        <button
          onClick={() => removeItem(item.producto.id)}
          className="w-7 h-7 flex items-center justify-center text-red-400 hover:text-red-600 ml-1"
          title="Quitar"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
