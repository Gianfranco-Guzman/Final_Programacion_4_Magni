import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { categoriasApi, CategoriaUpdateInput } from '@api/categoriasApi'

export const useCategoriasList = () => {
  return useQuery({
    queryKey: ['categorias'],
    queryFn: categoriasApi.getCategorias,
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

export const useDeleteCategoria = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: categoriasApi.deleteCategoria,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categorias'] }),
  })
}
