import React, { useState } from 'react'
import { useProductos, useCategorias } from '@hooks/useProductos'
import { ProductGrid } from './ProductGrid'
import { ProductFilters } from './ProductFilters'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'

export const CatalogoPage: React.FC = () => {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoriaId, setCategoriaId] = useState<number | null>(null)
  const [disponible, setDisponible] = useState<boolean | null>(null)

  const { data: productosData, isLoading, error } = useProductos({
    page,
    size: 20,
    search: search || undefined,
    categoria_id: categoriaId || undefined,
    disponible,
  })

  const { data: categorias = [] } = useCategorias()

  const handleSearchChange = (value: string) => {
    setSearch(value)
    setPage(1)
  }

  const handleCategoriaChange = (catId: number | null) => {
    setCategoriaId(catId)
    setPage(1)
  }

  const handleDisponibleChange = (disp: boolean | null) => {
    setDisponible(disp)
    setPage(1)
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error cargando productos</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Catálogo</h1>
        <p className="text-gray-600">
          {productosData ? `${productosData.total} productos disponibles` : 'Cargando...'}
        </p>
      </div>

      <ProductFilters
        search={search}
        onSearchChange={handleSearchChange}
        categoriaId={categoriaId}
        onCategoriaChange={handleCategoriaChange}
        categorias={categorias}
        disponible={disponible}
        onDisponibleChange={handleDisponibleChange}
      />

      {isLoading ? (
        <div className="py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {productosData && <ProductGrid productos={productosData.items} />}

          {productosData && productosData.pages > 1 && (
            <div className="flex justify-center gap-2 mt-8 mb-8">
              <Button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                Anterior
              </Button>

              <div className="flex items-center gap-2">
                <span className="text-gray-600">
                  Página {page} de {productosData.pages}
                </span>
              </div>

              <Button
                onClick={() => setPage(Math.min(productosData.pages, page + 1))}
                disabled={page === productosData.pages}
              >
                Siguiente
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
