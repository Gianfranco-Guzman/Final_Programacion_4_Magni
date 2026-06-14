import { useMutation, useQueryClient } from '@tanstack/react-query'
import { pedidosApi, PedidoCreateInput } from '@api/pedidosApi'

export const useCheckout = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (data: PedidoCreateInput) => pedidosApi.createPedido(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pedidos'] })
    },
  })
}
