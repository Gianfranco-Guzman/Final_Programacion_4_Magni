import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, variant = 'primary', size = 'md', isLoading = false, ...props }, ref) => {
    const baseStyles = 'font-medium transition-colors duration-200 rounded disabled:opacity-50 disabled:cursor-not-allowed'

    const variantStyles = {
      primary: 'bg-blue-500 text-white hover:bg-blue-600',
      secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
      danger: 'bg-red-500 text-white hover:bg-red-600',
    }

    const sizeStyles = {
      sm: 'px-3 py-1 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }

    return (
      <button
        ref={ref}
        disabled={isLoading || props.disabled}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]}`}
        {...props}
      >
        {isLoading ? '...' : children}
      </button>
    )
  }
)

Button.displayName = 'Button'
