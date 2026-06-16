import React, { useEffect, useState } from 'react'
import { useToastStore } from '@store/toastStore'

const ToastItem: React.FC<{ message: string }> = ({ message }) => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const frame = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(frame)
  }, [])

  return (
    <div
      className={`bg-emerald-600 text-white text-sm px-4 py-3 rounded-lg shadow-lg transition-all duration-200 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      {message}
    </div>
  )
}

export const ToastContainer: React.FC = () => {
  const toasts = useToastStore((state) => state.toasts)

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[60] flex flex-col items-center gap-2">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} message={toast.message} />
      ))}
    </div>
  )
}
