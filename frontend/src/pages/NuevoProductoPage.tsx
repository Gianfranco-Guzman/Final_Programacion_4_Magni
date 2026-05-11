import React from 'react'
import { useCategoriasList } from '@hooks/useCategorias'
import { useIngredientes } from '@hooks/useIngredientes'
import { ProductoFormPage } from '@features/store/ProductoFormPage'
import { Spinner } from '@components/Spinner'

export const NuevoProductoPage: React.FC = () => {
  const { data: categorias = [], isLoading: catsLoading } = useCategoriasList()
  const { data: ingredientes = [], isLoading: ingLoading } = useIngredientes()

  if (catsLoading || ingLoading) {
    return (
      <div className="py-12 flex justify-center">
        <Spinner />
      </div>
    )
  }

  return (
    <ProductoFormPage
      categorias={categorias}
      ingredientes={ingredientes}
      title="Nuevo Producto"
    />
  )
}
