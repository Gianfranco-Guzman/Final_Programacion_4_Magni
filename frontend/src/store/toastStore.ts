import { create } from 'zustand'

interface ToastItem {
  id: number
  message: string
}

interface ToastState {
  toasts: ToastItem[]
  showToast: (message: string) => void
}

let nextToastId = 0

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  showToast: (message) => {
    const id = nextToastId++
    set((state) => ({ toasts: [...state.toasts, { id, message }] }))
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((toast) => toast.id !== id) }))
    }, 2500)
  },
}))
