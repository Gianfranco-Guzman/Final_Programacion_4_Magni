import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Producto } from '@models/index'

export interface CartItemState {
  producto: Producto
  cantidad: number
}

interface CartState {
  items: CartItemState[]
  isOpen: boolean
  addItem: (producto: Producto) => void
  removeItem: (productoId: number) => void
  increase: (productoId: number) => void
  decrease: (productoId: number) => void
  clearCart: () => void
  openCart: () => void
  closeCart: () => void
  toggleCart: () => void
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      isOpen: false,

      addItem: (producto) =>
        set((state) => {
          const existing = state.items.find((i) => i.producto.id === producto.id)
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.producto.id === producto.id ? { ...i, cantidad: i.cantidad + 1 } : i,
              ),
              isOpen: true,
            }
          }
          return { items: [...state.items, { producto, cantidad: 1 }], isOpen: true }
        }),

      removeItem: (productoId) =>
        set((state) => ({ items: state.items.filter((i) => i.producto.id !== productoId) })),

      increase: (productoId) =>
        set((state) => ({
          items: state.items.map((i) =>
            i.producto.id === productoId ? { ...i, cantidad: i.cantidad + 1 } : i,
          ),
        })),

      decrease: (productoId) =>
        set((state) => ({
          items: state.items
            .map((i) =>
              i.producto.id === productoId ? { ...i, cantidad: i.cantidad - 1 } : i,
            )
            .filter((i) => i.cantidad > 0),
        })),

      clearCart: () => set({ items: [] }),
      openCart: () => set({ isOpen: true }),
      closeCart: () => set({ isOpen: false }),
      toggleCart: () => set((state) => ({ isOpen: !state.isOpen })),
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({ items: state.items }),
    },
  ),
)

export const selectCartTotal = (state: CartState) =>
  state.items.reduce((sum, item) => sum + item.producto.precio * item.cantidad, 0)

export const selectCartItemCount = (state: CartState) =>
  state.items.reduce((sum, item) => sum + item.cantidad, 0)
