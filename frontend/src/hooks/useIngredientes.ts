import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ingredientesApi, IngredienteUpdateInput } from '@api/ingredientesApi'

export const useIngredientes = () => {
  return useQuery({
    queryKey: ['ingredientes'],
    queryFn: ingredientesApi.getIngredientes,
    staleTime: 1000 * 60 * 30,
  })
}

export const useIngrediente = (id: number) => {
  return useQuery({
    queryKey: ['ingredientes', id],
    queryFn: () => ingredientesApi.getIngredienteById(id),
    enabled: !!id,
  })
}

export const useCreateIngrediente = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ingredientesApi.createIngrediente,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ingredientes'] }),
  })
}

export const useUpdateIngrediente = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteUpdateInput }) =>
      ingredientesApi.updateIngrediente(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ingredientes'] }),
  })
}

export const useBajaIngrediente = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ingredientesApi.bajaIngrediente,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ingredientes'] }),
  })
}

export const useReactivarIngrediente = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ingredientesApi.reactivarIngrediente,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ingredientes'] }),
  })
}
