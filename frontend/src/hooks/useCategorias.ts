import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { categoriasApi, CategoriaUpdateInput, CategoriasListParams } from '@api/categoriasApi'

export const useCategoriasList = (params?: CategoriasListParams) => {
  return useQuery({
    queryKey: ['categorias', params],
    queryFn: () => categoriasApi.getCategorias(params),
    select: (data) => data.items,
    staleTime: 1000 * 60 * 30,
  })
}

export const useCategoriasTree = () => {
  return useQuery({
    queryKey: ['categorias', 'tree'],
    queryFn: categoriasApi.getCategoriasTree,
    staleTime: 1000 * 60 * 30,
  })
}

export const useCategoria = (id: number) => {
  return useQuery({
    queryKey: ['categorias', id],
    queryFn: () => categoriasApi.getCategoriaById(id),
    enabled: !!id,
  })
}

export const useCreateCategoria = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: categoriasApi.createCategoria,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categorias'] }),
  })
}

export const useUpdateCategoria = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaUpdateInput }) =>
      categoriasApi.updateCategoria(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categorias'] }),
  })
}

export const useBajaCategoria = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: categoriasApi.bajaCategoria,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categorias'] }),
  })
}

export const useReactivarCategoria = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: categoriasApi.reactivarCategoria,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categorias'] }),
  })
}

export const useDeleteCategoria = useBajaCategoria
