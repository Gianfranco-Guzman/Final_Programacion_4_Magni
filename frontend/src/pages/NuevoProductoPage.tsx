import React from 'react'
import { useCategorias } from '@hooks/useProductos'
import { ProductoFormPage } from '@features/store/ProductoFormPage'
import { Spinner } from '@components/Spinner'

export const NuevoProductoPage: React.FC = () => {
  const { data: categorias = [], isLoading } = useCategorias()

  if (isLoading) {
    return (
      <div className="py-12 flex justify-center">
        <Spinner />
      </div>
    )
  }

  return (
    <ProductoFormPage
      categorias={categorias}
      title="Nuevo Producto"
    />
  )
}
