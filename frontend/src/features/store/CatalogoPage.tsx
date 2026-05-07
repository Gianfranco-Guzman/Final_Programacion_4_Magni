import React, { useState } from 'react'
import { useProductos, useCategorias, useDarDeBaja, useReactivar } from '@hooks/useProductos'
import { ProductGrid } from './ProductGrid'
import { ProductFilters } from './ProductFilters'
import { ProductForm } from './ProductForm'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'
import { Producto } from '@types/index'

export const CatalogoPage: React.FC = () => {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoriaId, setCategoriaId] = useState<number | null>(null)
  const [disponible, setDisponible] = useState<boolean | null>(null)
  const [showDeleted, setShowDeleted] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [editingProducto, setEditingProducto] = useState<Producto | null>(null)

  const { data: productosData, isLoading, error } = useProductos({
    page,
    size: 8,
    search: search || undefined,
    categoria_id: categoriaId || undefined,
    disponible: disponible ?? undefined,
    incluir_baja: showDeleted,
  })

  const { data: categorias = [] } = useCategorias()
  const darDeBajaMutation = useDarDeBaja()
  const reactivarMutation = useReactivar()

  const handleSearchChange = (value: string) => { setSearch(value); setPage(1) }
  const handleCategoriaChange = (catId: number | null) => { setCategoriaId(catId); setPage(1) }
  const handleDisponibleChange = (disp: boolean | null) => { setDisponible(disp); setPage(1) }

  const handleEdit = (producto: Producto) => {
    setEditingProducto(producto)
    setFormOpen(true)
  }

  const handleDarDeBaja = (id: number) => {
    if (!window.confirm('¿Dar de baja este producto?')) return
    darDeBajaMutation.mutate(id)
  }

  const handleReactivar = (id: number) => {
    if (!window.confirm('¿Reactivar este producto?')) return
    reactivarMutation.mutate(id, {
      onError: (err: unknown) => {
        alert(err instanceof Error ? err.message : 'No se pudo reactivar el producto')
      },
    })
  }

  const handleNuevoProducto = () => {
    setEditingProducto(null)
    setFormOpen(true)
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
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Catálogo</h1>
          <p className="text-gray-600">
            {productosData ? `${productosData.total} productos` : 'Cargando...'}
          </p>
        </div>
        <Button onClick={handleNuevoProducto}>+ Nuevo Producto</Button>
      </div>

      {/* Filters */}
      <ProductFilters
        search={search}
        onSearchChange={handleSearchChange}
        categoriaId={categoriaId}
        onCategoriaChange={handleCategoriaChange}
        categorias={categorias}
        disponible={disponible}
        onDisponibleChange={handleDisponibleChange}
      />

      {/* Show deleted toggle */}
      <div className="flex items-center gap-2 mb-4">
        <input
          type="checkbox"
          id="show-deleted"
          checked={showDeleted}
          onChange={(e) => { setShowDeleted(e.target.checked); setPage(1) }}
          className="w-4 h-4 rounded accent-red-500"
        />
        <label htmlFor="show-deleted" className="text-sm text-gray-600 cursor-pointer">
          Mostrar dados de baja
        </label>
      </div>

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : (
        <>
          {productosData && (
            <ProductGrid
              productos={productosData.items}
              onEdit={handleEdit}
              onDarDeBaja={handleDarDeBaja}
              onReactivar={handleReactivar}
            />
          )}

          {productosData && productosData.pages > 1 && (
            <div className="flex justify-center gap-2 mt-8 mb-8">
              <Button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                Anterior
              </Button>
              <span className="flex items-center text-gray-600">
                Página {page} de {productosData.pages}
              </span>
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

      {/* Product Form Modal */}
      {formOpen && (
        <ProductForm
          producto={editingProducto ?? undefined}
          categorias={categorias}
          onClose={() => setFormOpen(false)}
          onSuccess={() => setFormOpen(false)}
        />
      )}
    </div>
  )
}
