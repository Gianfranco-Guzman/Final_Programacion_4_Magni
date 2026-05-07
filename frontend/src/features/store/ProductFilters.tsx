import React from 'react'
import { Input } from '@components/Input'
import { Categoria } from '@types/index'

interface ProductFiltersProps {
  search?: string
  onSearchChange: (search: string) => void
  categoriaId?: number | null
  onCategoriaChange: (categoriaId: number | null) => void
  categorias: Categoria[]
  disponible?: boolean | null
  onDisponibleChange: (disponible: boolean | null) => void
  onResetFilters: () => void
}

export const ProductFilters: React.FC<ProductFiltersProps> = ({
  search = '',
  onSearchChange,
  categoriaId,
  onCategoriaChange,
  categorias,
  disponible,
  onDisponibleChange,
  onResetFilters,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <h2 className="font-semibold text-gray-800 mb-4">Filtros</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          label="Buscar producto"
          placeholder="Nombre o código..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Categoría</label>
          <select
            value={categoriaId || ''}
            onChange={(e) => onCategoriaChange(e.target.value ? Number(e.target.value) : null)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas las categorías</option>
            {categorias.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Disponibilidad</label>
          <select
            value={disponible === null ? '' : disponible ? 'available' : 'unavailable'}
            onChange={(e) => {
              if (e.target.value === '') onDisponibleChange(null)
              else if (e.target.value === 'available') onDisponibleChange(true)
              else onDisponibleChange(false)
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="available">Disponibles</option>
            <option value="unavailable">Sin stock</option>
          </select>
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={onResetFilters}
          className="text-sm text-gray-600 hover:text-gray-800 underline"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
  )
}
