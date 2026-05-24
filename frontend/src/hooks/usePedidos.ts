import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { pedidosApi, PedidoFiltros, PedidoCreateInput } from '@api/pedidosApi'

export const usePedidos = (params?: PedidoFiltros) => {
  return useQuery({
    queryKey: ['pedidos', params],
    queryFn: () => pedidosApi.getPedidos(params),
    staleTime: 1000 * 60 * 2,
  })
}

export const usePedido = (id: number) => {
  return useQuery({
    queryKey: ['pedidos', id],
    queryFn: () => pedidosApi.getPedidoById(id),
    enabled: !!id,
  })
}

export const useCreatePedido = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: PedidoCreateInput) => pedidosApi.createPedido(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pedidos'] }),
  })
}

export const useAvanzarEstado = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, observacion }: { id: number; observacion?: string }) =>
      pedidosApi.avanzarEstado(id, observacion),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pedidos'] }),
  })
}

export const useCancelarPedido = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, observacion }: { id: number; observacion?: string }) =>
      pedidosApi.cancelarPedido(id, observacion),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pedidos'] }),
  })
}
