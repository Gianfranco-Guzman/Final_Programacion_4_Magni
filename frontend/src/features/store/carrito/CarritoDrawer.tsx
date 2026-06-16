import React from 'react'
import { useCartStore } from '@store/cartStore'
import { ItemCarrito } from './ItemCarrito'
import { ResumenCarrito } from './ResumenCarrito'

export const CarritoDrawer: React.FC = () => {
  const { items, isOpen, closeCart, clearCart } = useCartStore()

  return (
    <>
      <div
        className={`fixed inset-0 bg-black z-40 transition-opacity duration-200 ${
          isOpen ? 'opacity-30 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={closeCart}
      />

      <div
        className={`fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-50 flex flex-col transform transition-transform duration-200 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-4 h-16 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-800">Tu carrito</h2>
          <button
            onClick={closeCart}
            className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-100 text-gray-500"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4">
          {items.length === 0 ? (
            <div className="py-12 text-center text-gray-400">
              <p className="text-4xl mb-3">🛒</p>
              <p className="text-sm">El carrito está vacío</p>
            </div>
          ) : (
            items.map((item) => <ItemCarrito key={item.producto.id} item={item} />)
          )}
        </div>

        {items.length > 0 && (
          <>
            <div className="px-4 pb-2">
              <button
                onClick={clearCart}
                className="text-xs text-red-500 hover:text-red-700"
              >
                Vaciar carrito
              </button>
            </div>
            <ResumenCarrito />
          </>
        )}
      </div>
    </>
  )
}
