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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ingredientes'] })
      qc.invalidateQueries({ queryKey: ['productos'] })
    },
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

export const useCargarStock = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, cantidad, unidad_entrada }: { id: number; cantidad: number; unidad_entrada: string }) =>
      ingredientesApi.cargarStock(id, { cantidad, unidad_entrada }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ingredientes'] })
      qc.invalidateQueries({ queryKey: ['mis-cargas'] })
    },
  })
}

export const useMisCargas = () => {
  return useQuery({
    queryKey: ['mis-cargas'],
    queryFn: ingredientesApi.getMisCargas,
  })
}

export const useCorregirEntrada = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ingredientesApi.corregirEntrada,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ingredientes'] })
      qc.invalidateQueries({ queryKey: ['mis-cargas'] })
    },
  })
}
