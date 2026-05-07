import React, { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useCategorias, useProductos } from '@hooks/useProductos'
import { ProductoFormPage } from '@features/store/ProductoFormPage'
import { Spinner } from '@components/Spinner'

export const EditarProductoPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: categorias = [], isLoading: catsLoading } = useCategorias()
  const { data: productosData, isLoading: prodLoading } = useProductos({
    page: 1,
    size: 100,
  })

  const producto = productosData?.items.find((p) => p.id === Number(id))

  useEffect(() => {
    if (!prodLoading && !producto) {
      navigate('/catalogo')
    }
  }, [producto, prodLoading, navigate])

  if (catsLoading || prodLoading) {
    return (
      <div className="py-12 flex justify-center">
        <Spinner />
      </div>
    )
  }

  if (!producto) {
    return null
  }

  return (
    <ProductoFormPage
      producto={producto}
      categorias={categorias}
      title="Editar Producto"
    />
  )
}
