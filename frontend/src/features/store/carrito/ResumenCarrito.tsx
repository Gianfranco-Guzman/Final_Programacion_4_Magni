import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore, selectCartTotal } from '@store/cartStore'

export const ResumenCarrito: React.FC = () => {
  const total = useCartStore(selectCartTotal)
  const closeCart = useCartStore((state) => state.closeCart)
  const navigate = useNavigate()

  const handleCheckout = () => {
    closeCart()
    navigate('/checkout')
  }

  return (
    <div className="border-t border-gray-200 p-4">
      <div className="flex justify-between items-center mb-4">
        <span className="font-semibold text-gray-700">Total</span>
        <span className="text-xl font-bold text-blue-600">${total.toFixed(2)}</span>
      </div>
      <button
        onClick={handleCheckout}
        className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Ir al checkout
      </button>
    </div>
  )
}
