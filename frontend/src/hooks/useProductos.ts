import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { productosApi, GetProductosParams, ProductoUpdateInput } from '@api/productosApi'

export const useProductos = (params?: GetProductosParams) => {
  return useQuery({
    queryKey: ['productos', params],
    queryFn: () => productosApi.getProductos(params),
    staleTime: 1000 * 60 * 5,
  })
}

export const useCategorias = () => {
  return useQuery({
    queryKey: ['categorias'],
    queryFn: () => productosApi.getCategorias(),
    staleTime: 1000 * 60 * 30,
  })
}

export const useCreateProducto = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: productosApi.createProducto,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['productos'] }),
  })
}

export const useUpdateProducto = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoUpdateInput }) =>
      productosApi.updateProducto(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['productos'] }),
  })
}

export const useDarDeBaja = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: productosApi.darDeBajaProducto,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['productos'] }),
  })
}

export const useReactivar = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: productosApi.reactivarProducto,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['productos'] }),
  })
}

export const useToggleDisponibilidad = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: productosApi.toggleDisponibilidad,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['productos'] }),
  })
}

export const useExportarProductos = () => {
  return useMutation({
    mutationFn: (search?: string) => productosApi.exportarProductos(search),
  })
}
