import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  adminApi,
  AdminUsuarioCreateInput,
  AdminUsuarioRolesInput,
  AdminUsuariosParams,
  AdminUsuarioUpdateInput,
} from '@api/adminApi'

export const useCreateAdminUsuario = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: AdminUsuarioCreateInput) => adminApi.createUsuario(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'usuarios'] }),
  })
}

export const useAdminUsuarios = (params: AdminUsuariosParams) => {
  return useQuery({
    queryKey: ['admin', 'usuarios', params],
    queryFn: () => adminApi.getUsuarios(params),
  })
}

export const useUpdateAdminUsuario = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AdminUsuarioUpdateInput }) =>
      adminApi.updateUsuario(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'usuarios'] }),
  })
}

export const useBajaAdminUsuario = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: adminApi.bajaUsuario,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'usuarios'] }),
  })
}

export const useReactivarAdminUsuario = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: adminApi.reactivarUsuario,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'usuarios'] }),
  })
}

export const useUpdateAdminUsuarioRoles = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AdminUsuarioRolesInput }) =>
      adminApi.updateRoles(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'usuarios'] }),
  })
}
