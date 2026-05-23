import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { DireccionEntregaUpdateInput, direccionesApi } from '@api/direccionesApi'

export const useDirecciones = () => {
  return useQuery({
    queryKey: ['direcciones'],
    queryFn: direccionesApi.getDirecciones,
    staleTime: 1000 * 60 * 5,
  })
}

export const useCreateDireccion = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: direccionesApi.createDireccion,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['direcciones'] }),
  })
}

export const useUpdateDireccion = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: DireccionEntregaUpdateInput }) =>
      direccionesApi.updateDireccion(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['direcciones'] }),
  })
}

export const useDeleteDireccion = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: direccionesApi.deleteDireccion,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['direcciones'] }),
  })
}

export const useMarcarDireccionPrincipal = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: direccionesApi.marcarPrincipal,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['direcciones'] }),
  })
}
