import React from 'react'
import { Link } from 'react-router-dom'
import { useProductos, useCategorias, useDarDeBaja, useReactivar, useExportarProductos } from '@hooks/useProductos'
import { useProductosContext } from '@context/ProductosContext'
import { ProductGrid } from '@features/store/ProductGrid'
import { ProductFilters } from '@features/store/ProductFilters'
import { Spinner } from '@components/Spinner'
import { Button } from '@components/Button'
import { useAuthStore } from '@store/authStore'
import { hasAnyRole } from '@/auth/permissions'

export const ListaPage: React.FC = () => {
  const { state, dispatch } = useProductosContext()
  const usuario = useAuthStore((currentState) => currentState.usuario)
  const canManageCatalog = hasAnyRole(usuario?.roles, ['ADMIN', 'STOCK'])

  const { data: productosData, isLoading, error } = useProductos({
    page: state.page,
    size: 8,
    search: state.search || undefined,
    categoria_id: state.categoriaId || undefined,
    disponible: state.disponible ?? undefined,
    incluir_baja: canManageCatalog ? state.showDeleted : false,
  })

  const { data: categorias = [] } = useCategorias()
  const darDeBajaMutation = useDarDeBaja()
  const reactivarMutation = useReactivar()
  const exportarMutation = useExportarProductos()

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

  const handleExportar = () => {
    exportarMutation.mutate(
      state.search || undefined,
      {
        onSuccess: (blob) => {
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `productos_${new Date().toISOString().split('T')[0]}.xlsx`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        },
        onError: () => {
          alert('Error al exportar los productos')
        },
      },
    )
  }

  const handleResetFilters = () => {
    dispatch({ type: 'RESET_FILTROS' })
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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Catálogo</h1>
          <p className="text-gray-600">
            {productosData ? `${productosData.total} productos` : 'Cargando...'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleExportar} disabled={exportarMutation.isPending}>
            {exportarMutation.isPending ? 'Exportando...' : 'Exportar a Excel'}
          </Button>
          {canManageCatalog && (
            <Link to="/productos/nuevo">
              <Button>+ Nuevo Producto</Button>
            </Link>
          )}
        </div>
      </div>

      <ProductFilters
        search={state.search}
        onSearchChange={(v) => dispatch({ type: 'SET_SEARCH', payload: v })}
        categoriaId={state.categoriaId}
        onCategoriaChange={(v) => dispatch({ type: 'SET_CATEGORIA', payload: v })}
        categorias={categorias}
        disponible={state.disponible}
        onDisponibleChange={(v) => dispatch({ type: 'SET_DISPONIBLE', payload: v })}
        onResetFilters={handleResetFilters}
      />

      {canManageCatalog && (
        <div className="flex items-center gap-2 mb-4">
          <input
            type="checkbox"
            id="show-deleted"
            checked={state.showDeleted}
            onChange={(e) => dispatch({ type: 'SET_SHOW_DELETED', payload: e.target.checked })}
            className="w-4 h-4 rounded accent-red-500"
          />
          <label htmlFor="show-deleted" className="text-sm text-gray-600 cursor-pointer">
            Mostrar dados de baja
          </label>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : (
        <>
          {productosData && (
            <ProductGrid
              productos={productosData.items}
              onDarDeBaja={canManageCatalog ? handleDarDeBaja : undefined}
              onReactivar={canManageCatalog ? handleReactivar : undefined}
            />
          )}

          {productosData && productosData.pages > 1 && (
            <div className="flex justify-center gap-2 mt-8 mb-8">
              <Button
                onClick={() => dispatch({ type: 'SET_PAGE', payload: Math.max(1, state.page - 1) })}
                disabled={state.page === 1}
              >
                Anterior
              </Button>
              <span className="flex items-center text-gray-600">
                Página {state.page} de {productosData.pages}
              </span>
              <Button
                onClick={() => dispatch({ type: 'SET_PAGE', payload: Math.min(productosData.pages, state.page + 1) })}
                disabled={state.page === productosData.pages}
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
