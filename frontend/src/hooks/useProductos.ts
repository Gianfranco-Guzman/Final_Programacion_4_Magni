import { useQuery } from '@tanstack/react-query'
import { productosApi, GetProductosParams } from '@api/productosApi'

export const useProductos = (params?: GetProductosParams) => {
  return useQuery({
    queryKey: ['productos', params],
    queryFn: () => productosApi.getProductos(params),
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}

export const useCategorias = () => {
  return useQuery({
    queryKey: ['categorias'],
    queryFn: () => productosApi.getCategorias(),
    staleTime: 1000 * 60 * 30, // 30 minutos
  })
}
