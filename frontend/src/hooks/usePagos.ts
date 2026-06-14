import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { pagosApi, PagoCreateInput } from '@api/pagosApi'

export const useCreatePago = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (data: PagoCreateInput) => pagosApi.createPago(data),
    onSuccess: (pago) => {
      qc.invalidateQueries({ queryKey: ['pagos', pago.pedido_id] })
      qc.invalidateQueries({ queryKey: ['pedidos'] })
    },
  })
}

export const usePago = (pedidoId: number) => {
  return useQuery({
    queryKey: ['pagos', pedidoId],
    queryFn: () => pagosApi.getPagoByPedidoId(pedidoId),
    enabled: !!pedidoId,
  })
}
