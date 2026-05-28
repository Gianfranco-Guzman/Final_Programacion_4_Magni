import type { ReactNode } from 'react'

type Variant = 'error' | 'info' | 'success'

interface FeedbackAlertProps {
  title?: string
  children: ReactNode
  variant?: Variant
}

const VARIANT_STYLES: Record<Variant, string> = {
  error: 'bg-red-50 border-red-200 text-red-700',
  info: 'bg-blue-50 border-blue-200 text-blue-700',
  success: 'bg-green-50 border-green-200 text-green-700',
}

export function FeedbackAlert({ title, children, variant = 'error' }: FeedbackAlertProps) {
  return (
    <div className={`border rounded-lg px-4 py-3 text-sm ${VARIANT_STYLES[variant]}`} role="alert">
      {title && <p className="font-semibold mb-1">{title}</p>}
      <div>{children}</div>
    </div>
  )
}
